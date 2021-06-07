from asgiref.sync import sync_to_async

from django.core.exceptions import ObjectDoesNotExist

from django_rest_async.db.models import AsyncModel


@sync_to_async(thread_sensitive=True)
def get_value_from_db_instance(instance: AsyncModel, field_name: str, many: bool = False):
    try:
        value = getattr(instance, field_name)
    except AttributeError:
        value = [] if many else None
    except ObjectDoesNotExist:
        value = [] if many else None
    if many:
        return [i for i in value.all()]
    return value
