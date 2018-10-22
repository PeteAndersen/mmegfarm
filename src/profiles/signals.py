from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from .models import Profile, Account


@receiver(post_save, sender=User)
def add_default_profile_to_new_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Account.objects.create(owner=instance, name='Default')
