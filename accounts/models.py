from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Use email as the username field
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # keep username but not for login

    def __str__(self):
        return self.email

class Profile(models.Model):
    class Role(models.TextChoices):
        PROSUMER = "prosumer", "Prosumer"
        CONSUMER = "consumer", "Consumer"
        PRODUCER = "producer", "Producer"
        ADMIN = "admin", "Admin"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=32, blank=True)
    timezone = models.CharField(max_length=64, default="Africa/Nairobi")
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.CONSUMER)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile({self.user.email})"
