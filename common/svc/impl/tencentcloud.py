from tencentcloud.cvm.v20170312 import cvm_client, models
from .. import Services
from ..tencentcloud import TencentCloudQueryServiceMixIn

from .base import RegionService, ZoneService
from ...models import Region


@Services.register
class TencentCloudRegionService(TencentCloudQueryServiceMixIn, RegionService):
    mapping = {'provider': 'get_provider', 'name': 'Region', 'display': 'RegionName'}
    request_class = models.DescribeRegionsRequest

    @property
    def client(self):
        return cvm_client.CvmClient(self.credential, '')

    def get_provider(self):
        return self.account.provider


@Services.register
class TencentCloudZoneService(TencentCloudQueryServiceMixIn, ZoneService):
    mapping = {'region': 'get_region', 'name': 'Zone', 'display': 'ZoneName'}
    request_class = models.DescribeZonesRequest

    @property
    def client(self):
        return cvm_client.CvmClient(self.credential, self.region)

    def get_region(self):
        return Region.objects.get(provider=self.account.provider, name=self.region)
