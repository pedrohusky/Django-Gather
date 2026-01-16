from django.db import models
from django.contrib.auth.models import User
import uuid


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    skin = models.CharField(max_length=50, default='009')
    visited_realms = models.JSONField(default=list)

    def __str__(self):
        return f"{self.user.username}'s profile"


class Realm(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    share_id = models.UUIDField(default=uuid.uuid4, unique=True)
    map_data = models.JSONField()
    only_owner = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
