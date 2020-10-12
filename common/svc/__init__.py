from common.svc.mixins import ServiceMixIn


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
    def get(cls, impl_class, account, region: str = '', *args, **kwargs):
        impl_class = cls.class_map[cls._key(account.provider.sdk, impl_class.service_type)]
        return impl_class(account, region, *args, **kwargs)
