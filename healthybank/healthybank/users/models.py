from django.contrib.auth.base_user import AbstractBaseUser
from django.core.mail import send_mail
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser,PermissionsMixin, BaseUserManager
# Create your models here.
from time import timezone
from django.utils.translation import ugettext_lazy as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, mobile, password,first_name, **extra_fields):
        """Create and save a User with the given email and password."""
        if not mobile:
            raise ValueError('The given mobile must be set')
        # mobile = self.normalize_email(email)
        user = self.model(mobile=mobile, **extra_fields)
        user.first_name = first_name
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, mobile, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, mobile, password, first_name, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(mobile, password, first_name, **extra_fields)


from commons.models import BaseModel


class User(AbstractBaseUser, BaseModel, PermissionsMixin):
    class Meta:
        #     proxy = True
        db_table = 'users'

    USER_VEFIFICATION = (('UNVERIFIED', 'UNVERIFIED'), ('VERFIED', 'VERIFIED'))
    verification_state = models.CharField(max_length=20, default='UNVERIFIED', choices=USER_VEFIFICATION)
    mobile = models.CharField(max_length=20, null=True, unique=True,default=None)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True, null=True,blank=True)
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female'), ('O', 'Other')), null=True)
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = ['first_name','last_name']
    objects = UserManager()
    landing_page = models.CharField(max_length=20, blank=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    from datetime import datetime, timedelta, timezone, tzinfo
    date_joined = models.DateTimeField(_('date joined'), default=datetime.now)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


    @property
    def name(self):
        return "%s %s" % (self.first_name, self.last_name)

    def __str__(self):
        return "%s %s -  %s" % (self.first_name, self.last_name, self.mobile)


    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

from django.contrib import admin


class UserAdmin(admin.ModelAdmin):
    search_fields = ['mobile', 'first_name','last_name']
