from django.http import HttpRequest, JsonResponse


def ping(request: HttpRequest):
    return JsonResponse({'status': 'ok'})
