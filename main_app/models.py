from django.db import models


# Create your models here.

class Session(models.Model):
    creation_date = models.DateTimeField(null=False, auto_now=True, blank=False)

    def __str__(self):
        return str(self.id)

class File(models.Model):
    name = models.CharField(blank=False, null=False, default="main", max_length=100)
    file_current = models.TextField(blank=True, null=False, default="")
    file_backup = models.TextField(blank=True, null=False, default="")
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_link", null=False, blank=False)
    last_changed = models.DateTimeField(auto_now=True, null=False, blank=False,)

    def __str__(self):
        return str(self.id)

