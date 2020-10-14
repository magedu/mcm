import time
from celery import shared_task
from .svc.impl import tencentcloud
from .svc import Services
from .svc.impl.base import RegionService, ZoneService
from .models import Provider, ProviderAccount, Region


@shared_task
def add(x, y):
    return x + y


@shared_task
def sync_region_to_model():
    for provider in Provider.objects.all():
        account = ProviderAccount.objects.filter(provider=provider, available=True).first()
        if account:
            service: RegionService = Services.get(RegionService, account)
            service.sync_to_model()


@shared_task
def sync_zone_to_model():
    for region in Region.objects.filter(available=True):
        account = ProviderAccount.objects.filter(provider=region.provider, available=True).first()
        if account:
            service: ZoneService = Services.get(ZoneService, account, region.name)
            service.sync_to_model()
