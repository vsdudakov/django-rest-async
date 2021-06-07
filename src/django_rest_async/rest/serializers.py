from django.db.models import Model

from django_rest_async.db.helpers import get_value_from_db_instance


async def serialize_django_model(instance: Model, schema: dict, definitions: dict) -> dict:
    data = {}
    properties = schema.get("properties")
    if properties is None:
        return instance
    for field_name, field in properties.items():
        field_ref = field.get("$ref")
        field_items_ref = field.get("items", {}).get("$ref")
        field_type = field.get("type")
        if field_items_ref and field_type == "array":
            # m2m or reverse field
            field_items_ref = field_items_ref.replace("#/definitions/", "")
            child_instances = await get_value_from_db_instance(instance, field_name, many=True)
            serialized_items = []
            for child_instance in child_instances:
                item = await serialize_django_model(child_instance, definitions[field_items_ref], definitions)
                serialized_items.append(item)
            data[field_name] = serialized_items
        elif field_ref:
            # fk or o2o field
            field_ref = field_ref.replace("#/definitions/", "")
            child_instance = await get_value_from_db_instance(instance, field_name)
            if child_instance:
                data[field_name] = await serialize_django_model(child_instance, definitions[field_ref], definitions)
            else:
                data[field_name] = None
        else:
            data[field_name] = await get_value_from_db_instance(instance, field_name)

    return data
