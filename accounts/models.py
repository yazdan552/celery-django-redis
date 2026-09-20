from django.db import models
from django.contrib.auth.models import User


class EmailLog(models.Model):
    """لاگ ایمیل‌های ارسالی برای جلوگیری از ارسال تکراری"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_logs')
    email_type = models.CharField(max_length=50)   # 'welcome', 'reset_password', ...
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'email_type')   # ← کلید اصلی idempotency
        ordering = ['-sent_at']

    def __str__(self):
        return f"{self.user.username} - {self.email_type} ({self.sent_at})"