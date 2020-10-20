import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mcm.settings')
django.setup()

from common.models import ProviderAccount, Region, Zone
from network.models import VPC, Subnet
from common.tasks import run_tasks

if __name__ == '__main__':
    account = ProviderAccount.objects.get(pk=1)
    region = Region.objects.filter(available=True).first()

    vpc = VPC()
    vpc.account = account
    vpc.region = region
    # vpc = VPC.objects.get(pk=1)

    vpc.name = 'test2'
    vpc.cidr = '172.16.0.0/16'
    # vpc.save()

    # vpc = VPC.objects.get(pk=1)
    # zone = Zone.objects.filter(region=vpc.region).first()
    # s = Subnet()
    # s.vpc = vpc
    # s.zone = zone
    # s.name = 'test3'
    # s.cidr = '172.16.3.0/24'
    # s.save()

    run_tasks.delay()
