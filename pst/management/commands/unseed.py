from django.core.management.base import BaseCommand, CommandError
from pst.models import User, Spending, SpendingFile

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.filter().delete()
        Spending.objects.filter().delete()
        SpendingFile.objects.filter().delete()

