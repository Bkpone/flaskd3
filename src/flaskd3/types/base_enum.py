from aenum import MultiValueEnum


class BaseEnum(MultiValueEnum):
    @classmethod
    def all(cls, exclude=None):
        if exclude:
            return [enum.value for enum in cls if enum not in exclude]
        else:
            return [enum.value for enum in cls]

    @classmethod
    def all_options(cls):
        return [enum for enum in cls]

    def __str__(self):
        return self.value

    @property
    def label(self):
        if len(self.values) > 1:
            return self.values[1]
        else:
            return self.value

    @property
    def bit_mask(self):
        return self.values[2]

    @classmethod
    def all_values(cls, labels=False):
        if labels:
            return [(enum.name, enum.label) for enum in cls]
        else:
            return [(enum.name, enum.value) for enum in cls]
