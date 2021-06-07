from functools import wraps

from django.utils.translation import gettext_lazy as _

from django_rest_async.auth.helpers import async_is_user_authenticated
from django_rest_async.rest.exceptions import RestValidateError
from django_rest_async.settings import REST_ASYNC_META_FIELD


def has_authentication(function=None, check_user_active=True):
    def decorator(fn):
        fn.has_authentication = True

        @wraps(fn)
        async def wrap(request, *args, **kwargs):
            user = await async_is_user_authenticated(request)
            key = REST_ASYNC_META_FIELD

            if not user:
                raise RestValidateError(errors_dict={key: _("User is not authenticated")}, status_code=401)

            if check_user_active and not user.is_active:
                raise RestValidateError(errors_dict={key: _("User is not active")}, status_code=403)

            return await fn(request, *args, **kwargs)

        return wrap

    if function:
        return decorator(function)
    return decorator
