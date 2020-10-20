from common.svc.tencentcloud import TencentCloudQueryServiceMixIn
from common.svc import Services
from common.svc.wrappers import Filterable
from common.models import Region
from tencentcloud.vpc.v20170312 import vpc_client
from tencentcloud.vpc.v20170312 import models
from .base import VPCService
from ..models import VPC


@Services.register
class TencentCloudVPCService(TencentCloudQueryServiceMixIn, VPCService):
    request_class = models.DescribeVpcsRequest
    mapping = {'account': 'account', 'region': 'get_region', 'name': 'VpcName', 'identity': 'VpcId',
               'cidr': 'CidrBlock'}

    @property
    def client(self):
        return vpc_client.VpcClient(self.credential, self.region)

    def get_region(self):
        return Region.objects.get(provider=self.account.provider, name=self.region)

    def sync(self, model: VPC):
        service = Filterable(self).filter('cidr-block', model.cidr)
        obj = service.get(model.identity)
        print("========")
        if obj:
            print("+++++++++++")
            request = models.ModifyVpcAttributeRequest()
            request.VpcId = obj.VpcId
            request.VpcName = model.name
            print(request)
            self.client.ModifyVpcAttribute(request)
            model.identity = obj.VpcId
            model.cidr = obj.CidrBlock
        else:
            print("-------------")
            request = models.CreateVpcRequest()
            request.VpcName = model.name
            request.CidrBlock = model.cidr
            print(request)
            response: models.CreateVpcResponse = self.client.CreateVpc(request)
            model.identity = response.Vpc.VpcId
        model.create_task(False)
        model.save()
