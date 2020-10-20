from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _


# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)

    class Meta:
        abstract = True
        ordering = ['created_at']


class Provider(BaseModel):
    class SDKChoices(models.TextChoices):
        TENCENT_CLOUD = 'TencentCloud', _('Tencent Cloud')
        ALIYUN = 'Aliyun', _('Alibaba Cloud')

    name = models.CharField(max_length=64, unique=True)
    sdk = models.CharField(max_length=32, choices=SDKChoices.choices,
                           null=False,
                           default=SDKChoices.TENCENT_CLOUD,
                           unique=True)

    def __str__(self):
        return self.name


class ProviderAccount(BaseModel):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=64, unique=True)
    access_key = models.CharField(max_length=128, null=False)
    access_secret = models.CharField(max_length=128, null=False)
    available = models.BooleanField(null=False, default=True)

    class Meta:
        unique_together = ['provider', 'access_key']  # unique 约束

    def __str__(self):
        return self.name


class Region(BaseModel):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=128, null=False)
    display = models.CharField(max_length=512, null=False)
    available = models.BooleanField(null=False, default=False)

    def __str__(self):
        return f'{self.display}'

    class Meta:
        unique_together = ['provider', 'name']


class Zone(BaseModel):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=128, null=False)
    display = models.CharField(max_length=512, null=False)
    available = models.BooleanField(null=False, default=True)

    class Meta:
        unique_together = ['region', 'name']

    def __str__(self):
        return self.display


class Task(BaseModel):
    class StateChoices(models.TextChoices):
        WAITING = 'WAITING', _('WAITING')
        RUNNING = 'RUNNING', _('RUNNING')
        SUCCEED = 'SUCCEED', _('SUCCEED')
        FAILED = 'FAILED', _('FAILED')

    model = models.CharField(max_length=128, null=False)
    service = models.CharField(max_length=128, null=False)
    identity = models.IntegerField(null=False)
    state = models.CharField(max_length=32, choices=StateChoices.choices, null=False, default=StateChoices.WAITING)
    retry_times = models.IntegerField(default=10)
    retry_count = models.IntegerField(default=0)
    method = models.CharField(max_length=128, null=False, default='sync')
    message = models.TextField(null=True)


class SaveTaskMeta:
    def __init__(self, service):
        self._create_task = True
        self._service = service

    @property
    def create_task(self):
        return self._create_task

    @create_task.setter
    def create_task(self, value):
        self._create_task = value

    @property
    def service(self):
        return self._service

    @service.setter
    def service(self, value):
        self._service = value

    @property
    def can_create_task(self):
        return getattr(self, 'create_task', False) and getattr(self, 'service', None)


class SaveTaskMixin:
    def create_task(self, value):
        if hasattr(self, '_task_meta'):
            self._task_meta.create_task = value

    @property
    def service(self):
        if hasattr(self, '_task_meta'):
            return self._task_meta.service

    @property
    def can_create_task(self):
        if hasattr(self, '_task_meta'):
            return self._task_meta.can_create_task


@receiver(post_save)
def save_task(sender, instance, *args, **kwargs):
    if getattr(instance, 'can_create_task', False):
        task = Task()
        task.model = f'{sender.__module__}.{sender.__name__}'
        task.service = instance.service
        task.identity = instance.id
        if getattr(instance, 'deleted_version', 0) > 0:
            task.method = 'delete'
        else:
            task.method = 'sync'
        task.save()
