from transitions import Machine

from flaskd3.types.base_enum import BaseEnum
from flaskd3.types.type_info import ValueObjectField
from flaskd3.types.value_object import ValueObject
from flaskd3.common.constants import SUPER_ADMIN_ROLE_ID, SYSTEM_ROLE_ID
from flaskd3.common.exceptions import DCException, InvalidStateException


class StateTransition(ValueObject):

    trigger = ValueObjectField(BaseEnum)
    source = ValueObjectField(BaseEnum, many=True)
    destination = ValueObjectField(BaseEnum)
    is_hidden = ValueObjectField(bool, default=False, required=False)
    authorised_user_roles = ValueObjectField(str, many=True, unique=True)

    def parsed_data(self):
        return dict(
            trigger=self.trigger.value,
            source=[entry.value for entry in self.source],
            dest=self.destination.value,
        )


class StateMachine(object):
    def __init__(self, state_key, transitions, parent, state_type):
        self.state_key = state_key
        self.transitions = transitions
        self.parent = parent
        self.state_type = state_type
        self._machine = Machine(
            model=self,
            states=self.state_type.all(),
            initial=getattr(self.parent, self.state_key).value,
            transitions=[entry.parsed_data() for entry in self.transitions],
            after_state_change="update_state",
        )

    def update_state(self):
        setattr(self.parent, self.state_key, self.state_type(self.state))

    def is_authorised(self, trigger, user_roles=None):
        transistion = [transistion for transistion in self.transitions if trigger == transistion.trigger]
        if not transistion:
            raise DCException(description=f"Transition for state {trigger.value} is not present.")
        transistion = transistion[0]
        authorised_user_roles = transistion.authorised_user_roles.data()
        if not authorised_user_roles:
            return True
        if not user_roles:
            return False
        user_role_ids = [user_role.role_id for user_role in user_roles]
        if (SUPER_ADMIN_ROLE_ID in user_role_ids) or (SYSTEM_ROLE_ID in user_role_ids):
            return True
        return len(authorised_user_roles.intersection(user_role_ids)) > 0

    def get_visible_transitions(self):
        return [t for t in self.transitions if not t.is_hidden]


class StateMachineFactory(object):
    def __init__(self, state_key, transitions):
        self.state_key = state_key
        self.transitions = transitions

    def build(self, parent):
        state_type = parent._attributes_type_info[self.state_key].class_obj
        if not issubclass(state_type, BaseEnum):
            raise InvalidStateException("State machine key should be of type enum")

        return StateMachine(self.state_key, self.transitions, parent, state_type)
