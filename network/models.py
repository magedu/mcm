import ipaddress
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from common.models import BaseModel, ProviderAccount, Region, Task, Zone, SaveTaskMeta, SaveTaskMixin


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_version__eq=0)


# Create your models here.
class VPC(SaveTaskMixin, BaseModel):
    # objects = SoftDeleteManager()
    # soft_delete_objects = SoftDeleteManager()

    account = models.ForeignKey(ProviderAccount, on_delete=models.RESTRICT, null=False)
    region = models.ForeignKey(Region, on_delete=models.RESTRICT, null=False)
    name = models.CharField(max_length=64, null=False)
    cidr = models.CharField(max_length=64, null=False)
    identity = models.CharField(max_length=64, null=True)
    # deleted = models.BooleanField(default=False)
    deleted_version = models.IntegerField(default=0)

    class Meta:
        unique_together = [
            ['account', 'identity', 'deleted_version'],
            ['name', 'deleted_version'],
            ['cidr', 'deleted_version']
        ]

    _task_meta = SaveTaskMeta('network.svc.base.VPCService')

    def delete(self, using=None, keep_parents=False):
        # return super().delete(using, keep_parents)
        self.deleted_version += 1
        self.save()

    @property
    def network(self):
        return ipaddress.ip_network(self.cidr)

    def clean_cidr(self):
        try:
            ipaddress.ip_network(self.cidr)
        except Exception as e:
            raise ValidationError(f'{self.cidr} is not cidr')

        # my = ipaddress.ip_network(self.cidr)
        # for instance in self.__class__.objects.all():
        #     net = instance.network
        #     if my.overlaps(net):
        #         raise ValidationError(f'{self.cidr} overlaps {instance}')

    def clean_region(self):
        if not self.region.available:
            raise ValidationError(f'{self.region} unavailable')
        if self.region.provider.id != self.account.provider.id:
            raise ValidationError(f'{self.region} ')

    def clean(self):
        super(VPC, self).clean()
        self.clean_cidr()
        self.clean_region()


class Subnet(SaveTaskMixin, BaseModel):
    vpc = models.ForeignKey(VPC, on_delete=models.CASCADE, null=True)
    zone = models.ForeignKey(Zone, on_delete=models.RESTRICT, null=True)
    name = models.CharField(unique=True, null=True, max_length=64, default='')
    cidr = models.CharField(unique=True, null=True, max_length=64, default='')
    identity = models.CharField(null=True, max_length=64)

    class Meta:
        unique_together = ['vpc', 'identity']

    _task_meta = SaveTaskMeta('network.svc.base.SubnetService')

    def clean_cidr(self):
        try:
            ipaddress.ip_network(self.cidr)
        except Exception as e:
            raise ValidationError(f'{self.cidr} is not cidr')
        my: ipaddress.IPv4Network = ipaddress.ip_network(self.cidr)
        print(self.cidr)
        print(self.vpc.cidr)
        if not my.subnet_of(ipaddress.ip_network(self.vpc.cidr)):
            raise ValidationError(f'{self.cidr} is not subnet of {self.vpc.cidr}')

    def clean_fields(self, exclude=None):
        super(Subnet, self).clean_fields(exclude)
        self.clean_cidr()


# @receiver(post_save, sender=Subnet)
# def save_task_by_subnet(sender, instance, created, *args, **kwargs):
#     if instance.create_task:
#         task = Task()
#         task.model = f'{sender.__module__}.{sender.__name__}'
#         task.service = 'network.svc.base.SubnetService'
#         task.identity = instance.id
#         task.save()

class Instance(BaseModel):
    pass


class DataDisk(BaseModel):
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, null=False)


@receiver(post_save, sender=DataDisk)
def post_data_disk_save(sender, instance, created, *args, **kwargs):
    pass