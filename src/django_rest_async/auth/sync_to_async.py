from asgiref.sync import sync_to_async

from django.contrib.auth import authenticate as django_authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.http import HttpRequest


@sync_to_async(thread_sensitive=True)
def authenticate(*args, **kwargs):
    return django_authenticate(*args, **kwargs)


@sync_to_async(thread_sensitive=True)
def login(*args, **kwargs):
    return django_login(*args, **kwargs)


@sync_to_async(thread_sensitive=True)
def logout(*args, **kwargs):
    return django_logout(*args, **kwargs)


@sync_to_async(thread_sensitive=True)
def is_user_authenticated(request: HttpRequest) -> any:
    user = request.user
    if user.is_authenticated:
        return user
