from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User

# username: admin
# pass: superuser
# email: admin@gmail.com

class Collection(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField('Date created')

    def was_created_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return self.name

# Create a foreign key to form a relationship between User and Image objects
# e.g. each Image is related to a single User (if not initially at some point once 'liked')
class Image(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    alt = models.CharField(max_length=200)
    src = models.CharField(max_length=200)
    created_at = models.DateTimeField('image created')
    votes = models.IntegerField(default=0)

    def was_created_recently(self):
        return self.created_at >= timezone.now() - datetime.timedelta(days=1)

    def __str__(self):
        return "{t} <User: {u}> <Collection: {c}>".format(t=self.title, u=self.user.username, c=self.collection.name)
