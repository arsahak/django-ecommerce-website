from django.db import models

# To Create a Custom User Model and Admin

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
#To Automatically create one ot one object
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy
from django.contrib.auth.hashers import make_password



class myusermanager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):

        '''creates and saves a user with given  email and password'''

        if not email:
            raise ValueError("The Email Must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(user.self._db)
        return user


    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        return self._create_user(email, password, **extra_fields)



class user(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=False)
    is_staff = models.BooleanField(
        gettext_lazy('staff_status'),
        default=False,
        help_text = gettext_lazy('Designates whether the user can log in this site')
    )

    is_active = models.BooleanField(
        gettext_lazy('active'),
        default=True,
        help_text=gettext_lazy('Designates whether this user should be treated as active, Unselect this instead of deleting accounts')
    )

    USERNAME_FIELD = 'email'
    object = myusermanager()
    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

class profiles(models.Model):
    user = models.OneToOneField(user, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=264, blank=True)
    full_name = models.CharField(max_length=264, blank=True)
    address_1 = models.TextField(max_length=300, blank=True)
    city = models.CharField(max_length=40, blank=True)
    zipcode = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self._meta = None

    def __str__(self):
        return self.user + "'s profiles"

    def is_fully_filled(self):
        fields_names = [f.name for f in self._meta.get_fields()]

        for field_name in fields_names:
            value = getattr(self, field_name)
            if value is None or value=='':
                return False

        return True

@receiver(post_save, sender = user)
def create_profile(sender, instance, created, **kwargs):
    if created:
        profiles.objects.create(user=instance)

@receiver(post_save, sender = user)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

