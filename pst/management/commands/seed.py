# this is seed file
from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from django.contrib.auth import models
from pst.models import User, Spending, SpendingFile, Categories, Budget, RewardPoint, Reward, Post, PostImage, Reply, Like
import datetime
import random
from django.db import IntegrityError


class Command(BaseCommand):
    pass
