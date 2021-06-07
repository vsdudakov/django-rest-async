from django.urls import path

from django_rest_async.views import api_doc, api_doc_scheme

app_name = "django_rest_async"

urlpatterns = [
    path("api/doc/", api_doc, name="api-doc"),
    path("api/doc/scheme.json", api_doc_scheme, name="api-doc-scheme"),
]
