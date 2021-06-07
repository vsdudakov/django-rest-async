from pydantic import BaseModel as PydanticModel


async def enrich_body(validator_cls: PydanticModel, method: str, raw_data: dict, context: dict) -> dict:
    if not hasattr(validator_cls, "schema"):
        return raw_data
    schema = validator_cls.schema()
    properties = schema["properties"]
    for field_name, field in properties.items():
        fn = getattr(validator_cls, f"{method}_{field_name}", None)
        if fn:
            raw_data[field_name] = await fn(raw_data, context=context)
        field_ref = field.get("$ref")
        field_items_ref = field.get("items", {}).get("$ref")
        field_type = field.get("type")
        if field_items_ref and field_type == "array":
            if raw_data[field_name]:
                sub_validator_cls = validator_cls.__fields__[field_name].type_
                new_items = []
                for item in raw_data[field_name]:
                    new_item = await enrich_body(sub_validator_cls, method, item, context)
                    new_items.append(new_item)
                raw_data[field_name] = new_items
        elif field_ref:
            if raw_data[field_name]:
                sub_validator_cls = validator_cls.__fields__[field_name].type_
                raw_data[field_name] = await enrich_body(sub_validator_cls, method, raw_data[field_name], context)
    return raw_data


def pydantic_errors_to_rest_errors(pydantic_errors: dict) -> dict:
    rest_errors = {}
    for error in pydantic_errors:
        fields = error.get("loc") or []
        message = error.get("msg")
        for field in fields:
            if field not in rest_errors:
                rest_errors[field] = []
            rest_errors[field].append(message)

    return rest_errors
