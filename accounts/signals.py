from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
	if created:
		# Use get_or_create with defaults to ensure we don't create duplicates
		UserProfile.objects.update_or_create(
			user=instance,
			defaults={}
		)
