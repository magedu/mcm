from abc import ABC
from tencentcloud.common import credential
from .mixins import ServiceMixIn, QueryServiceMixIn
from ..shortcuts import remove_suffix, remove_prefix


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
        filters = super(TencentCloudQueryServiceMixIn, self).get_filters() or []
        return [{'Name': f.name, 'Values': f.values} for f in filters]

    def _list(self, pagination=None):
        request = self.request_class()
        if pagination and pagination.clean() and getattr(self, 'pageable', False):
            request.Offset = pagination.offset
            request.Limit = pagination.limit
        filters = self.get_filters()
        if filters and getattr(self, 'filterable', False):
            request.Filters = list(filters)
        method = self.get_request_method()
        return method(request)

    def list(self, offset=0, limit=0):
        pagination = self.pagination_class(offset, limit)
        response = self._list(pagination)
        return self.get_result_set(response)

    def count(self):
        return self._list().TotalCount
