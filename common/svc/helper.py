class Pagination:
    def __init__(self, offset, limit):
        self._offset = offset
        self._limit = limit

    def clean_offset(self):
        return self._offset >= 0

    def clean_limit(self):
        return self._limit > 0

    def clean(self):
        return self.clean_offset() and self.clean_limit()

    @property
    def offset(self):
        return self._offset

    @property
    def limit(self):
        return self._limit


class Filter:
    def __init__(self, name, *values):
        self.name = name
        self.values = values
