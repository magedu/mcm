class OffsetLimit:
    def __init__(self, offset, limit):
        self._offset = offset
        self._limit = limit
        if not self.clean():
            raise Exception()

    def clean_offset(self):
        return True

    def clean_limit(self):
        return True

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


class Filterable:  # 不可变对象
    def __init__(self, service, *filters):
        self.service = service
        self.filters = filters

    def filter(self, name, *values):  # 每次filter都会产生一个新的对象
        return Filterable(self.service, Filter(name, *values), *self.filters)

    def list(self, offset_limit=None):
        self.service.set_filters(self.filters)
        return self.service.list(offset_limit=offset_limit)

    def get(self):
        self.service.set_filters(self.filters)
        return self.service.get()

    def paginator(self, pre_page=20):
        self.service.set_filters(self.filters)
        return self.service.paginator(pre_page=pre_page)
