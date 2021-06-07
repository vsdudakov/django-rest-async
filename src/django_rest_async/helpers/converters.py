def pydantic_errors_to_rest_errors(pydantic_errors: dict) -> dict:
    rest_errors = {}
    for error in pydantic_errors:
        fields = error.get("loc") or []
        message = error.get("msg")
        for field in fields:
            if field not in rest_errors:
                rest_errors[field] = []
            rest_errors[field].append(message.capitalize())

    return rest_errors
