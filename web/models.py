from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    is_token_user = models.BooleanField(default=False)
    provider = models.CharField(max_length=40, blank=True, null=True)


# Create your models here.
class OAuth2Token(models.Model):
    name = models.CharField(max_length=40)
    token_type = models.CharField(max_length=40)
    access_token = models.CharField(max_length=200)
    refresh_token = models.CharField(max_length=200)
    expires_at = models.PositiveIntegerField(blank=True, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, default=1)
    expires_in = models.DateTimeField(null=True)

    def to_token(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
            expires_in=self.expires_in,
        )