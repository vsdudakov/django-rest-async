from django.conf import settings

REST_ASYNC_META_FIELD = getattr(settings, "REST_ASYNC_META_FIELD", "meta")
REST_ASYNC_API_DOC_URL = getattr(settings, "REST_ASYNC_API_DOC_URL", "api/doc")
