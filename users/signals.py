import string
import random

from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, ReferralCode


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        # Profile.objects.create(user=instance)
        profile = Profile(user=instance)
        profile.save()
        # Generate referral code
        letters = string.ascii_letters
        referral_code = ''.join(random.choice(letters) for i in range(10))
        referral = ReferralCode(referral_code=referral_code, generatedBy=instance) # This will generate a referral code when the user creates an account.
        referral.save()


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

