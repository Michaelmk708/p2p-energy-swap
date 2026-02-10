# backend/core/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    """
    Custom Authentication Backend to allow login via Email OR Username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if the "username" provided matches either the username OR the email
            user = UserModel.objects.get(Q(username=username) | Q(email=username))
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            return UserModel.objects.filter(email=username).order_by('id').first()

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None