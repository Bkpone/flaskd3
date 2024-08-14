from flaskd3.common.constants import RelationshipStatus


class RelationshipManagementService:

    def __init__(self, relationship_aggregate_class, relationship_repository):
        self.relationship_aggregate_class = relationship_aggregate_class
        self.relationship_repository = relationship_repository

    def create_relationship(self, entity_1, entity_2, status=RelationshipStatus.ACTIVE):
        relationship_aggregate = self.relationship_aggregate_class.make_relationship(
            entity_1, entity_2, status)
        self.relationship_repository.save(relationship_aggregate)
        return relationship_aggregate

    def create_relationships(self, entity_1, entity_2_list):
        relationship_aggregates = list()
        for entity_2 in entity_2_list:
            relationship_aggregate = self.relationship_aggregate_class.make_relationship(
                entity_1, entity_2)
            relationship_aggregates.append(relationship_aggregate)
        self.relationship_repository.save_all(relationship_aggregates)
        return relationship_aggregates

    def update_relationship_status(self, relationship_ids, update_action_request):
        relationship_aggregates = self.relationship_repository.load_many(relationship_ids)
        for relationship_aggregate in relationship_aggregates:
            relationship_aggregate.act(update_action_request)
        self.relationship_repository.update_all(relationship_aggregates)
        return relationship_aggregates

    def find_all(self, entity_1, status=None):
        return self.relationship_repository.find_all(entity_1, status)
