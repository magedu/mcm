from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


# Create your models here.
class Token(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=32, unique=True, null=False)
    user = models.ForeignKey(User, null=False, on_delete=models.CASCADE)


@receiver(post_save, sender=User)
def post_user_save(sender, instance, created, *args, **kwargs):
    if not instance.is_active:
        Token.objects.filter(user=instance).delete()
