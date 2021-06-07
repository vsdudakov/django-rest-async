from django_rest_async.auth.sync_to_async import is_user_active, is_user_authenticated


async def async_is_user_authenticated(*args, **kwargs):
    return await is_user_authenticated(*args, **kwargs)


async def async_is_user_active(*args, **kwargs):
    return await is_user_active(*args, **kwargs)
