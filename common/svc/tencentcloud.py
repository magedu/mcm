from tencentcloud.cvm.v20170312 import cvm_client, models
from ..mixins import TencentCloudQueryServiceMixIn
from . import Services, RegionService, ZoneService
from ..models import Region


@Services.register
class TencentCloudRegionService(TencentCloudQueryServiceMixIn, RegionService):
    mapping = {'provider': 'provider', 'name': 'Region', 'display': 'RegionName'}
    request_class = models.DescribeRegionsRequest
    pageable = False

    @property
    def client(self):
        return cvm_client.CvmClient(self.credential, '')


@Services.register
class TencentCloudZoneService(TencentCloudQueryServiceMixIn, ZoneService):
    mapping = {'region': 'get_region', 'name': 'Zone', 'display': 'ZoneName'}
    request_class = models.DescribeZonesRequest
    pageable = False

    @property
    def client(self):
        return cvm_client.CvmClient(self.credential, self.region)

    def get_region(self):
        return Region.objects.get(provider=self.provider, name=self.region)
