from django.http import JsonResponse


class Response(JsonResponse):
    def __init__(self, data, *args, **kwargs):
        self.data = data
        super().__init__(data, *args, **kwargs)
