from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=None, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        user = self.create_user(email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    #username = models.CharField(max_length=30, blank=True, null=True, unique=False)
    username = models.CharField(max_length=30, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Your custom fields
    is_admin = models.BooleanField('Is admin', default=False)
    is_user = models.BooleanField('Is user', default=False)

    # Add any other custom fields specific to your application

    # Use the custom manager for managing users
    objects = CustomUserManager()

    # Set the email field as the unique identifier for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email

class Company(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name
    
class Domain(models.Model):
    name = models.CharField(max_length=200)
    registration_date = models.DateTimeField(verbose_name="Date registered", null=True, blank=True)
    expiry_date = models.DateTimeField(verbose_name="Date of expiry", null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
class DomainInfo(models.Model):
    apiresponse = models.TextField()
    timestamp = models.DateTimeField()
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    
class Report(models.Model):
    title = models.CharField(max_length=200)
    report_date = models.DateField()
    report_generation_date = models.DateTimeField()
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.TextField()
    
    def __str__(self):
        return self.title
    
    