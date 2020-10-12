from django.db import models
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
    sdk = models.CharField(max_length=32, choices=SDKChoices.choices, null=False, default=SDKChoices.TENCENT_CLOUD)

    def __str__(self):
        return self.name


class ProviderAccount(BaseModel):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=64, unique=True)
    access_key = models.CharField(max_length=128, null=False)
    access_secret = models.CharField(max_length=128, null=False)
    available = models.BooleanField(null=False, default=True)

    class Meta:
        unique_together = ['provider', 'access_key']

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
