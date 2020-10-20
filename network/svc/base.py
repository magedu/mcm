from abc import ABC

from common.svc.mixins import ServiceMixIn, SyncServiceMixIn
from ..models import VPC


class VPCService(ServiceMixIn, SyncServiceMixIn, ABC):
    service_type = 'VPC'
    model = VPC
    identities = ['cidr']

    def __init__(self, account, region, *args, **kwargs):
        self._account = account
        self.region = region
