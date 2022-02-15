from django.contrib.auth.models import User
from django.db import models
from PIL import Image


class Author(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField()


    def __str__(self):
        return self.user.username
