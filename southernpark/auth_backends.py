from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class CaseInsensitiveModelBackend(ModelBackend):
    """Authenticate with case-insensitive username lookup."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            user = UserModel.objects.get(
                **{UserModel.USERNAME_FIELD + "__iexact": username}
            )
        except UserModel.DoesNotExist:
            UserModel().set_password(password)  # mitigate timing attacks
            return None
        except UserModel.MultipleObjectsReturned:
            # Duplicate usernames differing only in case — use exact match if possible
            try:
                user = UserModel.objects.get(
                    **{UserModel.USERNAME_FIELD: username}
                )
            except (UserModel.DoesNotExist, UserModel.MultipleObjectsReturned):
                UserModel().set_password(password)
                return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
