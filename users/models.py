from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CUSTOMER = "customer"
    ROLE_MANAGER = "manager"
    ROLE_CHOICES = [(ROLE_CUSTOMER, "Customer"), (ROLE_MANAGER, "Store Manager")]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)

    def is_manager(self):
        return self.role == self.ROLE_MANAGER

