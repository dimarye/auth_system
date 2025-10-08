from django.db import models
from django.contrib.auth.models import User, AbstractUser
import uuid
from django.utils import timezone
from datetime import datetime, timedelta


class User(AbstractUser):
    def deactivate(self):
        self.is_active = False
        self.tokens.all().delete()
        self.save()

class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=256, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = datetime.now(timezone.utc)  + timedelta(days=7)
        super().save(*args, **kwargs)

    def is_expired(self):
        return datetime.now(timezone.utc).now() > self.expires_at

    def __str__(self):
        return f"Token for {self.user.username}"
