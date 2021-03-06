from django.db import models
from django.conf import settings
# Create your models here.
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Avg
from django.db.models.signals import post_save

User = settings.AUTH_USER_MODEL


class RatingChoices(models.IntegerChoices):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    __empty__ = "Rate this"


class RatingQuerySet(models.QuerySet):
    def rating(self):
        return self.aggregate(average=Avg('value'))['average']


class RatingManager(models.Manager):
    def get_queryset(self):
        return RatingQuerySet(self.model, using=self._db)


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField(null=True, blank=True, choices=RatingChoices.choices)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    # def get_related_object(self):
    #     """Return the model class for this type of content."""
    #     Klass = self.content_type.model_class()
    #     return Klass.objects.get(id=self.object_id)

    objects = RatingManager()


def rating_post_save(sender, instance, created, *args, **kwargs):
    if created:
        content_type = instance.content_type
        user = instance.user
        qs = Rating.objects.filter(user=user, content_type=content_type, object_id=instance.object_id).exclude(pk=instance.pk)
        if qs.exists():
            qs.delete()


post_save.connect(rating_post_save, sender=Rating)