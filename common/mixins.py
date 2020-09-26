from abc import ABC
from django.core.paginator import Paginator
from tencentcloud.common import credential
from .shortcuts import remove_suffix, remove_prefix
from .svc.helper import OffsetLimit


class ServiceMixIn:  # 用于提供service_type和sdk_type
    service_type = None
    sdk_type = None

    @property
    def provider(self):  # 由于所有API调用,都需要provider 所以这里也提供都需要provider
        if hasattr(self, '_provider'):  # 魔法
            return self._provider
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
    filters_attribute = '_filters'
    __filters__ = {}
    offset_limit_class = OffsetLimit
    pageable = True

    def get(self):  # 查询单个数据
        result_set = self.list()
        if result_set:
            return result_set[0]

    def set_filters(self, filters):  # 魔法 MixIn不保存状态
        # self.__filters__[id(self)] = filters
        setattr(self, self.filters_attribute, filters)

    def clean_filters(self):
        if hasattr(self, self.filters_attribute):
            delattr(self, self.filters_attribute)

    def get_filters(self):
        # return self.__filters__.get(id(self), [])
        return getattr(self, self.filters_attribute, [])

    def do_list(self, offset_limit=None):
        raise NotImplementedError()

    def list(self, offset_limit=None):  # 查询数据列表
        try:
            return self.do_list(offset_limit)
        finally:
            self.clean_filters()

    def do_count(self):
        raise NotImplementedError()

    def count(self):  # 查询数据条数
        try:
            return self.do_count()
        finally:
            self.clean_filters()

    def __len__(self):
        return self.count()

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.list(self.offset_limit_class(item, 1))
        if isinstance(item, slice):
            ol = self.offset_limit_class(item.start, item.stop - item.start)
            return self.list(ol)

    def paginator(self, pre_page=20) -> Paginator:  # 分页查询
        if self.pageable:
            return Paginator(self, pre_page)
        return Paginator(self.list(), pre_page)


class SyncServiceMixIn(ModelServiceMixIn, QueryServiceMixIn, ABC):  # 从API查询数据， 保存到数据库
    batch_size = 20

    def sync_to_model(self):
        paginator = self.paginator(self.batch_size)
        for num in paginator.page_range:
            for obj in paginator.page(num):
                m = self.save(obj)
                print(m)


class TencentCloudMixIn(ServiceMixIn):  # 固化SDK type， 同时提供credential
    sdk_type = 'TencentCloud'

    @property
    def credential(self):
        return credential.Credential(self.provider.access_key, self.provider.access_secret)

    @property
    def client(self):
        raise NotImplementedError()


class TencentCloudQueryServiceMixIn(TencentCloudMixIn, QueryServiceMixIn, ABC):  # 对QueryServiceMixIn的特化
    request_class = None
    request_method = None
    result_set_attribute = ''

    def get_request_method(self):
        method = self.request_method
        if not method:
            method: str = self.request_class.__name__
            method = remove_suffix(method, 'Request')
        return getattr(self.client, method)

    def get_result_set(self, response):
        attribute = self.result_set_attribute
        if not attribute:
            attribute: str = self.request_class.__name__
            attribute = remove_suffix(attribute, 'Request')
            attribute = remove_prefix(attribute, 'Describe')
            if attribute[-1] == 's':
                attribute = f'{attribute[:-1]}Set'
        return getattr(response, attribute)

    def get_filters(self):  # 按照腾讯云API的要求 特化get_filters
        filters = super(TencentCloudQueryServiceMixIn, self).get_filters()
        return [{'Name': f.name, 'Values': f.values} for f in filters]

    def _list(self, offset_limit=None):
        request = self.request_class()
        if offset_limit:
            request.Offset = offset_limit.offset
            request.Limit = offset_limit.limit
        filters = self.get_filters()
        if filters:
            request.Filters = list(filters)
        method = self.get_request_method()
        return method(request)

    def do_list(self, offset_limit=None):
        response = self._list(offset_limit)
        return self.get_result_set(response)

    def do_count(self):
        return self._list().TotalCount
