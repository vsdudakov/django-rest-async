from django.urls import path

from django_rest_async.settings import REST_ASYNC_API_DOC_URL
from django_rest_async.views import api_doc, api_doc_scheme

app_name = "django_rest_async"

urlpatterns = [
    path(f"{REST_ASYNC_API_DOC_URL}/", api_doc, name="api-doc"),
    path(f"{REST_ASYNC_API_DOC_URL}/scheme.json", api_doc_scheme, name="api-doc-scheme"),
]
