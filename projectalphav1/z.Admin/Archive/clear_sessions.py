"""
Management command to clear all sessions from the database.
Useful when SECRET_KEY changes and sessions become corrupted.
"""
from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session


class Command(BaseCommand):
    help = 'Clear all sessions from the database'

    def handle(self, *args, **options):
        count = Session.objects.all().count()
        Session.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} session(s)')
        )
