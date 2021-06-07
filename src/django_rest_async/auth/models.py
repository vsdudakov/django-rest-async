from django.contrib.auth.models import User

from django_rest_async.db.models import AsyncModel


class AuthUser(AsyncModel, User):
    pass
