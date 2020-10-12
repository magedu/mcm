from abc import ABC
from common.models import ProviderAccount, Region, Zone
from common.svc.mixins import ServiceMixIn, SyncServiceMixIn


class RegionService(ServiceMixIn, SyncServiceMixIn, ABC):
    service_type = 'Region'
    model = Region
    identities = ['provider', 'name']

    def __init__(self, account: ProviderAccount, *args, **kwargs):
        self._account = account


class ZoneService(ServiceMixIn, SyncServiceMixIn, ABC):
    service_type = 'Zone'
    model = Zone
    identities = ['region', 'name']

    def __init__(self, account: ProviderAccount, region: str, *args, **kwargs):
        self._account = account
        self.region = region
