from django.db import models


# Create your models here.

class User(models.Model):
    name = models.CharField(blank=False, null=False, max_length=255)
    email = models.EmailField(blank=False, null=False, max_length=255)
    password = models.CharField(blank=False, null=False, max_length=1000)

    def __str__(self):
        return str(self.name)


class Session(models.Model):
    id = models.CharField(max_length=250, blank=False, null=False, unique=True, primary_key=True)
    creation_date = models.DateTimeField(null=False, auto_now=True, blank=False)
    users = models.ManyToManyField(User, related_name="contributors")

    def __str__(self):
        return str(self.id)


class File(models.Model):
    name = models.CharField(blank=False, null=False, default="main", max_length=100)
    file_current = models.TextField(blank=True, null=False, default="")
    file_backup = models.TextField(blank=True, null=False, default="")
    session_id = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_link", null=False,
                                   blank=False)
    last_changed = models.DateTimeField(auto_now=True, null=False, blank=False, )
    language = models.CharField(blank=False, null=False, default='python', max_length=100)

    def __str__(self):
        return str(self.id)
