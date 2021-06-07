from pydantic import BaseModel as PydanticModel

from django.http import QueryDict
from django.utils.translation import gettext_lazy as _

from django_rest_async.rest.exceptions import RestValidateError


def clean_params(validator_cls: PydanticModel, query_params: QueryDict) -> dict:
    schema = validator_cls.schema()
    list_fields = []
    properties = schema.get("properties") or {}
    for field in properties:
        if properties[field].get("type") == "array":
            list_fields.append(field)

    params = {}
    for k in query_params:
        v = query_params.getlist(k)
        if list_fields and k in list_fields:
            params[k] = v
        else:
            params[k] = v[0]
    return params


def clean_none_values(data: dict) -> dict:
    cleaned_data = {}
    for k, v in data.items():
        if isinstance(v, dict):
            cleaned_data[k] = clean_none_values(v)
        elif isinstance(v, (list, set, tuple)):
            # note: Nones in lists are not dropped
            cleaned_data[k] = type(v)(clean_none_values(vv) if isinstance(vv, dict) else vv for vv in v)
        elif v is not None:
            cleaned_data[k] = v
    return cleaned_data


async def clean_db_field(field, model_cls, raw_data, many=False):
    value = raw_data.get(field)
    if not value:
        return [] if many else None
    if not many:
        db_obj = await model_cls.async_objects.filter(pk=value).first()
        if not db_obj:
            raise RestValidateError({field: [_("Invalid id")]})
    else:
        db_obj = await model_cls.async_objects.filter(pk__in=value).query()
        if len(db_obj) != len(value):
            raise RestValidateError({field: [_("Invalid ids")]})
    return db_obj
