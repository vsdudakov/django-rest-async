from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import URLPattern, URLResolver

urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [""])


# https://unpkg.com/browse/swagger-ui-dist@3.23.4/
async def api_doc(request):
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>SwaggerClient test</title>
        <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@3/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>

        <script src="https://unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js" charset="UTF-8"></script>
        <script src="https://unpkg.com/swagger-ui-dist@3.23.4/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
        <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: "/api/doc/scheme.json",
                dom_id: '#swagger-ui',
                defaultModelsExpandDepth: -1,
                docExpansion: "full",
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
            })
            window.ui = ui
            }
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)


def _get_url_patterns(urlpatterns, acc=None):
    if acc is None:
        acc = []
    if not urlpatterns:
        return
    urlpattern = urlpatterns[0]
    if isinstance(urlpattern, URLPattern):
        yield ("".join(acc + [str(urlpattern.pattern)]), urlpattern)
    elif isinstance(urlpattern, URLResolver):
        yield from _get_url_patterns(urlpattern.url_patterns, acc + [str(urlpattern.pattern)])
    yield from _get_url_patterns(urlpatterns[1:], acc)


def _get_path_param_type(converter):
    if converter.__class__.__name__ == "SlugConverter":
        return "string"
    if converter.__class__.__name__ == "StringConverter":
        return "string"
    if converter.__class__.__name__ == "UUIDConverter":
        return "string"
    if converter.__class__.__name__ == "PathConverter":
        return "string"
    if converter.__class__.__name__ == "IntConverter":
        return "integer"
    return "string"


def _get_path(url):
    url = (
        url.replace("slug:", "")
        .replace("str:", "")
        .replace("uuid:", "")
        .replace("int:", "")
        .replace("<", "{")
        .replace(">", "}")
    )
    return "/" + url


async def api_doc_scheme(request):

    paths = {}
    definitions = {}
    for url, url_pattern in _get_url_patterns(urlconf.urlpatterns):
        if hasattr(url_pattern.callback, "methods"):
            methods = {}
            content = {}
            parameters = []
            if hasattr(url_pattern.callback, "params_validator_cls"):
                schema = url_pattern.callback.params_validator_cls.schema()
                for parameter, value in schema.get("properties", {}).items():
                    parameters.append(
                        {
                            "name": parameter,
                            "in": "query",
                            "required": False,
                            "schema": value,
                        }
                    )
                definitions.update(schema.get("definitions", {}))
            for parameter, value in url_pattern.pattern.converters.items():
                parameters.append(
                    {
                        "name": parameter,
                        "in": "path",
                        "required": True,
                        "schema": {"type": _get_path_param_type(value)},
                    }
                )
            content["parameters"] = parameters
            if hasattr(url_pattern.callback, "request_validator_cls"):
                schema = url_pattern.callback.request_validator_cls.schema()
                content["requestBody"] = {
                    "content": {
                        "application/json": {
                            "schema": schema,
                        }
                    },
                }
                definitions.update(schema.get("definitions", {}))
            if hasattr(url_pattern.callback, "response_validator_cls"):
                schema = url_pattern.callback.response_validator_cls.schema()
                content["responses"] = {
                    "200": {
                        "description": "Ok",
                        "content": {
                            "application/json": {
                                "schema": schema,
                            }
                        },
                    },
                }
                definitions.update(schema.get("definitions", {}))
            else:
                content["responses"] = {"200": {"description": "Ok"}}

            content["responses"]["401"] = {"description": "Not authenticated"}
            content["responses"]["403"] = {"description": "Forbidden"}
            if getattr(url_pattern.callback, "login_required", False):
                content["security"] = {
                    "cookieAuth": [],
                }
            for method in url_pattern.callback.methods:
                methods[method.lower()] = content

            paths[_get_path(url)] = methods

    openapi = {
        "openapi": "3.0.3",
        "paths": paths,
        "definitions": definitions,
        "components": {
            "securitySchemes": {
                "cookieAuth": {
                    "type": "apiKey",
                    "in": "cookie",
                    "name": "JSESSIONID",
                },
            },
        },
        "security": {"cookieAuth": []},
    }
    print(openapi)
    return JsonResponse(openapi)
