class BaseDto(object):

    version = None

    def data(self):
        return self.__dict__
