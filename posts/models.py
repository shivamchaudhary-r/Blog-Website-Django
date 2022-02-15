from django.db import models
from django.urls import reverse

from accounts.models import Author



class PostView(models.Model):
    user = models.ForeignKey(Author, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Category(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class Tag(models.Model):
    title = models.CharField(max_length=20)

    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey(Author, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    post = models.ForeignKey(
        'Post', related_name='comments', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Post(models.Model):
    title = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    thumbnail = models.ImageField()
    categories = models.ManyToManyField(Category)
    tags=models.ManyToManyField(Tag)
    previous_post = models.ForeignKey(
        'self', related_name='previous', on_delete=models.SET_NULL, blank=True, null=True)
    next_post = models.ForeignKey(
        'self', related_name='next', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post-detail', kwargs={
            'pk': self.pk
        })

    def get_update_url(self):
        return reverse('post-update', kwargs={
            'pk': self.pk
        })

    def get_delete_url(self):
        return reverse('post-delete', kwargs={
            'pk': self.pk
        })

    @property
    def get_comments(self):
        return self.comments.all().order_by('-timestamp')
