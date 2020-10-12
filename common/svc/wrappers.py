import contextvars
from django.core.paginator import Paginator
from .helper import Filter
from .contexts import FILTERS
from common.svc.mixins import QueryServiceMixIn


class Filterable(QueryServiceMixIn):  # 不可变对象
    def __init__(self, service, *filters):
        self.service = service
        self.filters = filters
        self.service.filterable = True

    def filter(self, name, *values):  # 每次filter都会产生一个新的对象
        return Filterable(self.service, Filter(name, *values), *self.filters)

    def list(self, offset=0, limit=0):
        token = FILTERS.set(self.filters)
        try:
            return contextvars.copy_context().run(self.service.list, offset, limit)
        finally:
            FILTERS.reset(token)

    def get(self, identity=None):
        self.service.set_filters(self.filters)
        return self.service.get()

    def count(self):
        token = FILTERS.set(self.filters)
        try:
            return contextvars.copy_context().run(self.service.count)
        finally:
            FILTERS.reset(token)


class Pageable(QueryServiceMixIn):
    def __init__(self, service: QueryServiceMixIn):
        self.service = service
        self.service.pageable = True

    def __len__(self):
        return self.service.count()

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.service.list(offset=item, limit=1)
        if isinstance(item, slice):
            return self.service.list(item.start, item.stop - item.start)

    def list(self, offset=0, limit=0):
        return self.service.list(offset, limit)

    def count(self):
        return self.service.count()

    def paginator(self, pre_page=20):
        return Paginator(self, pre_page)
