import os
from django.db import models
from django.urls import reverse
from signup.models import CustomUser

from django.template.defaultfilters import slugify

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    users = models.ManyToManyField(CustomUser, through='Subscribers', blank=True)
    category_slug = models.SlugField('Category slug', null=False, blank=False, unique=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name_plural = "Categories"

class Post(models.Model):
    def image_upload_to(self, instance=None):
        if instance:
            return os.path.join("Post", slugify(self.slug), instance)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, unique=True)
    subtitle = models.CharField(max_length=100, blank=True, default='')
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='Post_Category')
    slug = models.SlugField('Post slug', null=False, blank=False, unique=True)
    image = models.ImageField(default='default/default.jpg', upload_to=image_upload_to, max_length= 255)

    def get_absolute_url(self):
        # return reverse('post_edit', kwargs={'slug': self.slug})
        return reverse('post_detail', args=[self.slug])

    def __str__(self):
        return f'{self.title}'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Post, self).save(*args, **kwargs)

    # @property
    # def slug(self):
    #     return self.post_slug

class Post_Category(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Subscribers(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class UserOneTimeCode(models.Model):
    code = models.CharField(max_length=200)
    email = models.EmailField()
    user = models.OneToOneField(CustomUser, blank=False, unique=True, on_delete=models.CASCADE)


class Comment(models.Model):
    comment_text = models.CharField(max_length=100)
    comment_date = models.DateTimeField(auto_now_add=True)

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)