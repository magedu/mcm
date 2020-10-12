from abc import ABC
from common.models import Provider, Region, Zone
from common.svc.mixins import ServiceMixIn, SyncServiceMixIn


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
