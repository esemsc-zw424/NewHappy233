from django.core.management.base import BaseCommand, CommandError
from pst.models import User, Spending, SpendingFile, Categories, Budget, RewardPoint, Reward, Post, PostImage, Reply, Like

class Command(BaseCommand):
    def handle(self, *args, **options):
        User.objects.all().delete()
        Spending.objects.all().delete()
        SpendingFile.objects.all().delete()
        Categories.objects.all().delete()
        Budget.objects.all().delete
        RewardPoint.objects.all().delete
        Reward.objects.all().delete
        Post.objects.all().delete
        PostImage.objects.all().delete
        Reply.objects.all().delete
        Like.objects.all().delete


