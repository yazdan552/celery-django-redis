from celery import shared_task
from django.contrib.auth.models import User
import time
import random
from datetime import datetime
from celery.exceptions import SoftTimeLimitExceeded
from django.db import IntegrityError
from .models import EmailLog


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





# ==================== Chain ====================
@shared_task
def add(x, y):
    print(f"[add] {x} + {y}")
    return x + y


@shared_task
def mul(x, y):
    print(f"[mul] {x} * {y}")
    return x * y


@shared_task
def power(x, y):
    print(f"[power] {x} ^ {y}")
    return x ** y


# ==================== Group ====================
@shared_task
def process_item(item_id):
    print(f"[process] آیتم {item_id}")
    time.sleep(1)   # شبیه‌سازی کار
    return f"processed-{item_id}"


# ==================== Chord ====================
@shared_task
def sum_all(numbers):
    print(f"[sum_all] {numbers}")
    return sum(numbers)


# ==================== صف heavy ====================
@shared_task(queue='heavy')
def process_video(video_id):
    print(f"[heavy] شروع پردازش ویدیو {video_id}")
    time.sleep(10)   # شبیه‌سازی ۱۰ ثانیه کار سنگین
    print(f"[heavy] ویدیو {video_id} تموم شد")
    return f"video-{video_id}-processed"


# ==================== صف default ====================
@shared_task
def send_email(user_id):
    print(f"[default] ارسال ایمیل به {user_id}")
    time.sleep(1)
    return f"email-sent-{user_id}"


@shared_task
def resize_image(image_id):
    print(f"[default] resize عکس {image_id}")
    time.sleep(3)
    return f"image-{image_id}-resized"





# ==================== Soft Time Limit ====================
@shared_task(soft_time_limit=5, time_limit=10)
def task_with_cleanup():
    """
    تسک با cleanup:
    - ۵ ثانیه: هشدار نرم
    - ۱۰ ثانیه: kill سخت
    """
    try:
        print("[start] تسک شروع شد")
        # شبیه‌سازی کار طولانی
        for i in range(20):
            print(f"[progress] ثانیه {i}")
            time.sleep(1)
        print("[success] تسک تموم شد")
        return "done"
    except SoftTimeLimitExceeded:
        print("[cleanup] وقت تمومه! دارم cleanup می‌کنم...")
        # مثلاً: پاک کردن فایل‌های موقت، rollback دیتابیس
        return "cleaned up"


# ==================== Hard Time Limit ====================
@shared_task(time_limit=3)
def task_with_hard_limit():
    """
    تسک با kill سخت بعد از ۳ ثانیه:
    - Soft limit نداره
    - بعد از ۳ ثانیه به زور کشته میشه
    """
    print("[start] تسک شروع شد (بدون cleanup)")
    time.sleep(60)   # ۶۰ ثانیه sleep → قطعاً kill میشه
    print("[never] این خط هیچوقت اجرا نمیشه")
    return "done"



@shared_task(bind=True, max_retries=3)
def send_welcome_email_idempotent(self, user_id):
    """
    ارسال ایمیل خوش‌آمدگویی به صورت idempotent:
    - اگه قبلاً فرستادیم، skip میشه
    - حتی اگه تسک چند بار اجرا بشه، ایمیل یه بار می‌ره
    """
    try:
        # ۱) سعی کن log بساز
        try:
            log = EmailLog.objects.create(
                user_id=user_id,
                email_type='welcome',
            )
        except IntegrityError:
            # قبلاً ساخته شده → تسک قبلاً اجرا شده
            print(f"[skip] ایمیل خوش‌آمدگویی قبلاً برای user {user_id} فرستاده شده")
            return "already sent"

        # ۲) حالا ایمیل بفرست (مطمئنیم اولین باره)
        user = User.objects.get(pk=user_id)
        print(f"[send] در حال ارسال ایمیل به {user.username}")
        time.sleep(2)   # شبیه‌سازی ارسال ایمیل

        # ۳) اگه خطا داد، log رو پاک کن تا retry بشه
        # (اختیاری - بستگی به منطق پروژه داره)

        print(f"[done] ایمیل به {user.username} فرستاده شد")
        return f"sent to {user.username}"

    except User.DoesNotExist:
        print(f"[error] user {user_id} وجود نداره")
        return f"user {user_id} not found"




@shared_task(bind=True, max_retries=3)
def send_welcome_email_crash(self, user_id):
    """
    تسک idempotent که وسط کار crash می‌کنه:
    - بار اول: log ساخته میشه، بعد crash
    - retry: log قبلاً هست → skip
    - نتیجه: ایمیل یه بار می‌ره ✅
    """
    try:
        # ۱) log بساز (idempotency)
        try:
            EmailLog.objects.create(
                user_id=user_id,
                email_type='crash_test',
            )
        except IntegrityError:
            print(f"[skip] قبلاً ساخته شده برای user {user_id}")
            return "already sent"

        # ۲) ایمیل بفرست
        print(f"[send] ارسال به user {user_id}")

        # ۳) حالا crash کن! (شبیه‌سازی قطع برق وسط کار)
        raise Exception("crash وسط کار!")

    except Exception as exc:
        delay_time = 2 ** self.request.retries
        print(f"[retry] تلاش مجدد در {delay_time}s... (retry {self.request.retries})")
        raise self.retry(exc=exc, countdown=delay_time)