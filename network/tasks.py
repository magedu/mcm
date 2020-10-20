from celery import shared_task


@shared_task
def sync_vpc_to_model():
    pass


@shared_task
def sync_subnet_to_model():
    pass


@shared_task
def sync_vpc_to_cloud():
    pass


@shared_task
def sync_subnet_to_cloud():
    pass
