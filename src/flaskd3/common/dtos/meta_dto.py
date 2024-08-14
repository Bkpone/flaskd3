class Meta(object):
    start = 0
    limit = 20
    end = None
    count = None

    def __init__(self, start: int = None, limit: int = None, end: int = None):
        if start:
            self.start = int(start)
        if limit:
            self.limit = int(limit)
        if end:
            self.end = int(end)

    def to_dict(self):
        return dict(start=self.start, limit=self.limit, end=self.end, count=self.count)
