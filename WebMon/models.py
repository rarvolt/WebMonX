from django.db import models
from django.utils import timezone


class Watch(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField()
    xpath = models.CharField(max_length=200)
    period = models.DurationField()
    next_check = models.DateTimeField(null=True)
    notify = models.BooleanField(default=False, blank=True)
    owner = models.ForeignKey('auth.User', related_name='watches', on_delete=models.CASCADE)
    
    def save(self, *args, **kwargs):
        # Set next_check only when object is created
        if self.pk is None:
            self.next_check = timezone.now() + self.period
        super(Watch, self).save(*args, **kwargs)


class Value(models.Model):
    watch = models.ForeignKey(Watch, related_name='values', on_delete=models.CASCADE)
    created = models.DateTimeField(editable=False)
    content = models.TextField(default="")

    def save(self, *args, **kwargs):
        """ On save, update timestamp. """
        if not self.id:
            self.created = timezone.now()
        return super(Value, self).save(*args, **kwargs)
