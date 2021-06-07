import json
from functools import wraps
from typing import Sequence, Tuple

from pydantic import BaseModel as PydanticModel
from pydantic import ValidationError as PydanticValidationError

from django.db.models import Model as DjangoModel
from django.http import HttpRequest

from django_rest_async.rest.cleaners import clean_none_values, clean_params
from django_rest_async.rest.exceptions import RestForbiddenError, RestNotFoundError, RestValidateError
from django_rest_async.rest.helpers import enrich_body, pydantic_errors_to_rest_errors
from django_rest_async.rest.response import Response
from django_rest_async.rest.serializers import serialize_django_model


def rest_view(methods: Sequence, response_cls=None):
    response_cls = response_cls or Response

    def decorator(fn):
        fn.methods = methods

        @wraps(fn)
        async def wrap(request: HttpRequest, *args, **kwargs):
            if request.method not in methods:
                return response_cls({"meta": "Method not allowed"}, status=405)
            try:
                status_code, body = await fn(request, *args, **kwargs)
                return response_cls(body or {}, status=status_code)
            except (RestValidateError, RestForbiddenError, RestNotFoundError) as e:
                return response_cls(e.errors_dict, status=e.status_code)

        return wrap

    return decorator


def clean_request_params(validator_cls: PydanticModel):
    def decorator(fn):
        fn.params_validator_cls = validator_cls

        @wraps(fn)
        async def wrap(request: HttpRequest, *args, **kwargs):
            try:
                context = {"request": request}
                params = clean_params(validator_cls, request.GET)
                params = validator_cls(**params).dict()
                context["root_raw_data"] = params
                params = await enrich_body(validator_cls, "clean", params, context)
                kwargs["params"] = clean_none_values(params)
            except PydanticValidationError as e:
                errors = pydantic_errors_to_rest_errors(e.errors())
                raise RestValidateError(errors)
            return await fn(request, *args, **kwargs)

        return wrap

    return decorator


def clean_request_body(validator_cls: PydanticModel):
    def decorator(fn):
        fn.request_validator_cls = validator_cls

        @wraps(fn)
        async def wrap(request: HttpRequest, *args, **kwargs):
            try:
                context = {"request": request}
                if request.content_type == "multipart/form-data":
                    body = {}
                else:
                    body = json.loads(request.body)
                validator = validator_cls(**body)
                body = validator.dict()
                context["root_raw_data"] = body
                body = await enrich_body(validator_cls, "clean", body, context)
                kwargs["body"] = clean_none_values(body)
            except PydanticValidationError as e:
                errors = pydantic_errors_to_rest_errors(e.errors())
                raise RestValidateError(errors)
            except json.decoder.JSONDecodeError:
                raise RestValidateError({"meta": "Invalid body json data"})
            return await fn(request, *args, **kwargs)

        return wrap

    return decorator


async def _serialize_body(validator_cls: PydanticModel, body: dict, context: dict) -> dict:
    if isinstance(body, DjangoModel):
        schema = validator_cls.schema()
        body = await serialize_django_model(body, schema, schema.get("definitions", {}))

    context["root_raw_data"] = body
    body = await enrich_body(validator_cls, "serialize", body, context)

    try:
        body = validator_cls(**body).dict()
    except PydanticValidationError as e:
        errors = pydantic_errors_to_rest_errors(e.errors())
        raise RestValidateError(errors, status_code=406)

    return body


def serialize_response(validator_cls: PydanticModel):
    def decorator(fn):
        fn.response_validator_cls = validator_cls

        @wraps(fn)
        async def wrap(request: HttpRequest, *args, **kwargs) -> Tuple[int, dict]:
            status_code, body = await fn(request, *args, **kwargs)
            body = body or {}
            context = {"request": request}
            if isinstance(body, dict) and "results" in body:
                validated_body_items = []
                for body_item in body["results"]:
                    validated_body_items.append(await _serialize_body(validator_cls, body_item, context))
                body["results"] = validated_body_items
            else:
                body = await _serialize_body(validator_cls, body, context)

            return status_code, body

        return wrap

    return decorator
