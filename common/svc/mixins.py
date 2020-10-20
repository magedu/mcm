import contextvars
from abc import ABC
from django.core.paginator import Paginator
from .helper import Pagination
from .contexts import FILTERS


class ServiceMixIn:  # 用于提供service_type和sdk_type
    service_type = None
    sdk_type = None

    @property
    def account(self):  # 由于所有API调用,都需要provider 所以这里也提供都需要provider
        if hasattr(self, '_account'):  # 魔法
            return self._account
        raise NotImplementedError()


class ModelServiceMixIn:  # 用于把API查询到的数据存入数据库
    model = None
    identities = []  # 需要知道模型是否已存在
    mapping = {}  # 字段映射

    def _get_value(self, mapping, key, obj):
        attr = mapping[key]
        if callable(attr):
            return attr()
        if isinstance(attr, str):
            if hasattr(obj, attr):
                return getattr(obj, attr)
            value = getattr(self, attr)
            if callable(value):
                return value()
            return value

    def get_identities(self, obj):
        mapping = self.get_mapping()
        kwargs = {}
        if self.identities:
            for identity in self.identities:
                value = self._get_value(mapping, identity, obj)
                kwargs[identity] = value
        return kwargs

    def get_mapping(self):
        return self.mapping

    def exist(self, obj):  # 判断模型是否存在
        m = self.model()
        exist = False
        try:
            m = self.model.objects.get(**self.get_identities(obj))
            exist = True
        except self.model.DoesNotExist:
            pass
        return m, exist

    def convert(self, obj):  # 用于数据类型转化
        m, _ = self.exist(obj)
        mapping = self.get_mapping()
        for key in mapping.keys():
            value = self._get_value(mapping, key, obj)
            setattr(m, key, value)
        return m

    def save(self, obj):  # 保存数据
        model = self.convert(obj)
        model.save()
        return model


class QueryServiceMixIn:  # 用于从API查询数据
    pagination_class = Pagination
    filterable = False
    pageable = False

    def get(self, identity=None):  # 查询单个数据
        result_set = self.list()
        if result_set:
            return result_set[0]

    def list(self, offset=0, limit=0):  # 查询数据列表
        raise NotImplementedError()

    def count(self):  # 查询数据条数
        raise NotImplementedError()

    def paginator(self, pre_page=20):
        return Paginator(self.list(), pre_page)

    def get_filters(self):
        return contextvars.copy_context().get(FILTERS)


class SyncServiceMixIn(ModelServiceMixIn, QueryServiceMixIn, ABC):  # 从API查询数据， 保存到数据库
    batch_size = 20

    def sync(self, model):
        pass

    def sync_to_model(self):
        paginator = self.paginator(self.batch_size)
        for num in paginator.page_range:
            for obj in paginator.page(num):
                m = self.save(obj)
                print(m)
