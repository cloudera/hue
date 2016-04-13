from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    AbstractUser,
    UserManager,
    PermissionsMixin,
    Group,
    Permission,
)


# The custom User uses email as the unique identifier, and requires
# that every user provide a date of birth. This lets us test
# changes in username datatype, and non-text required fields.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, date_of_birth, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, date_of_birth):
        u = self.create_user(email, password=password, date_of_birth=date_of_birth)
        u.is_admin = True
        u.save(using=self._db)
        return u


class CustomUser(AbstractBaseUser):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    date_of_birth = models.DateField()

    custom_objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth']

    class Meta:
        app_label = 'auth'

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __unicode__(self):
        return self.email

    # Maybe required?
    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return set()

    def has_perm(self, perm, obj=None):
        return True

    def has_perms(self, perm_list, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    # Admin required fields
    @property
    def is_staff(self):
        return self.is_admin


# At this point, temporarily remove the groups and user_permissions M2M
# fields from the AbstractUser class, so they don't clash with the related_name
# that sets.

old_au_local_m2m = AbstractUser._meta.local_many_to_many
old_pm_local_m2m = PermissionsMixin._meta.local_many_to_many
groups = models.ManyToManyField(Group, blank=True)
groups.contribute_to_class(PermissionsMixin, "groups")
user_permissions = models.ManyToManyField(Permission, blank=True)
user_permissions.contribute_to_class(PermissionsMixin, "user_permissions")
PermissionsMixin._meta.local_many_to_many = [groups, user_permissions]
AbstractUser._meta.local_many_to_many = [groups, user_permissions]


# The extension user is a simple extension of the built-in user class,
# adding a required date_of_birth field. This allows us to check for
# any hard references to the name "User" in forms/handlers etc.

class ExtensionUser(AbstractUser):
    date_of_birth = models.DateField()

    custom_objects = UserManager()

    REQUIRED_FIELDS = AbstractUser.REQUIRED_FIELDS + ['date_of_birth']

    class Meta:
        app_label = 'auth'


# The CustomPermissionsUser users email as the identifier, but uses the normal
# Django permissions model. This allows us to check that the PermissionsMixin
# includes everything that is needed to interact with the ModelBackend.

class CustomPermissionsUserManager(CustomUserManager):
    def create_superuser(self, email, password, date_of_birth):
        u = self.create_user(email, password=password, date_of_birth=date_of_birth)
        u.is_superuser = True
        u.save(using=self._db)
        return u


class CustomPermissionsUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='email address', max_length=255, unique=True)
    date_of_birth = models.DateField()

    custom_objects = CustomPermissionsUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth']

    class Meta:
        app_label = 'auth'

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __unicode__(self):
        return self.email


class IsActiveTestUser1(AbstractBaseUser):
    """
    This test user class and derivatives test the default is_active behavior
    """
    username = models.CharField(max_length=30, unique=True)

    custom_objects = BaseUserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        app_label = 'auth'

    # the is_active attr is provided by AbstractBaseUser


class CustomUserNonUniqueUsername(AbstractBaseUser):
    "A user with a non-unique username"
    username = models.CharField(max_length=30)

    USERNAME_FIELD = 'username'

    class Meta:
        app_label = 'auth'


class CustomUserNonListRequiredFields(AbstractBaseUser):
    "A user with a non-list REQUIRED_FIELDS"
    username = models.CharField(max_length=30, unique=True)
    date_of_birth = models.DateField()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = 'date_of_birth'

    class Meta:
        app_label = 'auth'


class CustomUserBadRequiredFields(AbstractBaseUser):
    "A user with a non-unique username"
    username = models.CharField(max_length=30, unique=True)
    date_of_birth = models.DateField()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['username', 'date_of_birth']

    class Meta:
        app_label = 'auth'

# Undo swap hack
AbstractUser._meta.local_many_to_many = old_au_local_m2m
PermissionsMixin._meta.local_many_to_many = old_pm_local_m2m
