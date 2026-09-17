from django.shortcuts import render
from django.http import JsonResponse
from .tasks import my_first_task, send_welcome_email


def test_celery_view(request):
    my_first_task.delay('user1')

    send_welcome_email.apply_async(
        args=[1],
        countdown=10,
    )

    return JsonResponse({
        "message": "Task has been sent!"
    })
