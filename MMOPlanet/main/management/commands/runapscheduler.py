import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from main.models import Category
import datetime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone


logger = logging.getLogger(__name__)


def my_job():
    date_now = datetime.datetime.now()
    date_weekago = date_now - datetime.timedelta(days=7)
    # print(date_now, date_weekago)
    for category in Category.objects.all():
        posts = category.post_set.filter(
            published_date__lt=date_now, published_date__gt=date_weekago)
        # print(posts)
        for user in category.users.all():
            html_content = render_to_string(
                'mails/posts_message.html',
                {
                    'posts': posts,
                    'user': user,
                    'category': category.name
                }
            )
            msg = EmailMultiAlternatives(
                subject=f"""{category.name} Weekly Newsletter""",
                body=f"Hello, {user.username}! {category.name} Weekly Newsletter ",
                from_email='newspaper.main@yandex.ru',
                to=[user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        print("Done!")


def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            # trigger=CronTrigger(second='*/10'),
            id="my_job",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),

            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
