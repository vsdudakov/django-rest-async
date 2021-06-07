from django.db import models

from django_rest_async.db.models import AsyncModel


class BaseAsyncModel(AsyncModel):
    class Meta:
        app_label = "tests"
        abstract = True


class BasicModel(BaseAsyncModel):
    field = models.CharField(
        max_length=255,
    )


class ManyToManyModel(BaseAsyncModel):
    field = models.ManyToManyField(BasicModel)


class ManyToOneModel(BaseAsyncModel):
    field = models.ForeignKey(BasicModel, on_delete=models.CASCADE)


class OneToOneModel(BaseAsyncModel):
    field = models.ForeignKey(BasicModel, on_delete=models.CASCADE)
