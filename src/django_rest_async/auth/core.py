from django_rest_async.auth.sync_to_async import authenticate, login, logout


async def async_authenticate(*args, **kwargs):
    return await authenticate(*args, **kwargs)


async def async_login(*args, **kwargs):
    return await login(*args, **kwargs)


async def async_logout(*args, **kwargs):
    return await logout(*args, **kwargs)
