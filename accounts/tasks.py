from celery import shared_task
from django.contrib.auth.models import User
import time
import random
from datetime import datetime



@shared_task
def check_system_status():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[System check] System is running normally at {now}")

    return 'Status OK!'


@shared_task
def my_first_task(name):

    print(f"شروع به کار برای:{name}")
    time.sleep(5)
    print(f"کار تمام شده برای: {name}")
    return f"Done for {name}!"

@shared_task(bind=True,max_retries=3)
def send_welcome_email(self,user_id):

    try:
        print(f'[start] در حال اماده سازی برای ارسال ایمیل  برای کاربر با id {user_id}')
        time.sleep(2)
        if random.random() < 0.7:
            raise ConnectionError('ارتباط با سرور ایمیل برقرار نشد')

        print(f'[success] ایمیل به{user_id} ارسال شد ')

        # user = User.objects.get(pk=user_id)
        # print(f"Sending welcome email to {user.username}")
        #
        # time.sleep(3)
        # print(f"Welcome email sent to {user.username}")

        return f"Welcome email sent to successfully!"
    except Exception as exc:
        print(f'[error] Error occurred: {exc}')

        delay_time= (2 ** self.request.retries)

        print(f'[retry] Retrying in {delay_time} seconds...')

        raise self.retry(exc=exc, countdown=delay_time)


