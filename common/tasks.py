import time
from celery import shared_task
from django.db.models import F
from django.utils.module_loading import import_string
from .svc.impl import tencentcloud
from .svc import Services
from .svc.impl.base import RegionService, ZoneService
from .models import Provider, ProviderAccount, Region, Task


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


@shared_task
def run_tasks():
    for task in Task.objects.filter(state__in=(Task.StateChoices.WAITING, Task.StateChoices.FAILED),
                                    retry_count__lt=F('retry_times')).order_by('-created_at'):
        model_class = import_string(task.model)
        model = model_class.objects.get(pk=task.identity)
        service_class = import_string(task.service)
        print(service_class)
        service = Services.get(service_class, model.account, model.region.name)
        try:
            task.state = Task.StateChoices.RUNNING
            task.retry_count += 1
            task.save()
            method = getattr(service, task.method)
            if method:
                method(model)
            else:
                raise AttributeError(f'no attribute {method} of {service_class}')
            # service.sync(model)  # 只能调用sync方法 开机关机等
            task.state = Task.StateChoices.SUCCEED
        except Exception as e:
            task.message = str(e)
            task.state = Task.StateChoices.FAILED
        finally:
            task.save()
