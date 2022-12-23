from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.template.loader import render_to_string

from .models import Comment, Category, Post_Category

from django.core.mail import EmailMultiAlternatives

@receiver(post_save, sender=Comment)
def notify_post_comment(sender, instance, created, **kwargs):
    if created:
        comment = instance
        post = instance.post
        email_to = post.user.email

        msg = EmailMultiAlternatives(
            subject=f"""Your post was commented""",
            body=f"""Hello, {post.user.username}! Your post "{post.title}" was commented by \
fuser "{comment.user.username}"\nTo see it - 127.0.0.1:8000/posts/{post.slug}""",
            from_email='newspaper.main@yandex.ru',
            to=[email_to]
        )
        msg.send()


@receiver(m2m_changed, sender=Post_Category)
def send_email_new_post(sender, instance, action, **kwargs):
    if action == 'post_add':
        post = instance
        for pk in kwargs['pk_set']:
            category = Category.objects.get(pk=pk)
            category_users = category.users.all()
            for user in category_users:
                html_content = render_to_string(
                    'mails/post_message.html',
                    {
                        'post': post,
                        'user': user.username
                    }
                 )
                msg = EmailMultiAlternatives(
                    subject=f"""New "{category.name}" post here - {post.title}""",
                    body=f"Hello, {user.username}! New post in your favorite section! {post.title} | {post.subtitle}",
                    from_email='newspaper.main@yandex.ru',
                    to=[user.email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
