from abc import ABC
from ..mixins import ServiceMixIn, SyncServiceMixIn
from ..models import Provider, Region, Zone


class Services:  # 存储实现类
    class_map = {}

    @classmethod
    def _key(cls, sdk_type, service_type):
        return f'{sdk_type}::{service_type}'

    @classmethod
    def register(cls, impl_class):
        if not issubclass(impl_class, ServiceMixIn):
            raise Exception()  # TODO
        if not (impl_class.service_type and impl_class.sdk_type):
            raise Exception()  # TODO

        cls.class_map[cls._key(impl_class.sdk_type, impl_class.service_type)] = impl_class
        return impl_class

    @classmethod
    def get(cls, impl_class, provider, region: str = '', *args, **kwargs):
        impl_class = cls.class_map[cls._key(provider.sdk, impl_class.service_type)]
        return impl_class(provider, region, *args, **kwargs)


class RegionService(ServiceMixIn, SyncServiceMixIn, ABC):
    service_type = 'Region'
    model = Region
    identities = ['provider', 'name']

    def __init__(self, provider: Provider, *args, **kwargs):
        self._provider = provider


class ZoneService(ServiceMixIn, SyncServiceMixIn, ABC):
    service_type = 'Zone'
    model = Zone
    identities = ['region', 'name']

    def __init__(self, provider: Provider, region: str, *args, **kwargs):
        self._provider = provider
        self.region = region
