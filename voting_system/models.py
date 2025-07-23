from django.db import models

# Create your models here.
class Votes(models.Model):
    title = models.CharField(max_length=200)
    yes_count = models.IntegerField(default=0)
    no_count = models.IntegerField(default=0)
    # ip = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.id}-->{self.title}--{self.yes_count}:yes--{self.no_count}:no'

    class Meta:
        verbose_name = 'Vote'
        verbose_name_plural = 'Votes'

class Voters(models.Model):
    STATUS = (
        ('Yes','Yes'),
        ('No','No'),

    )
    vote = models.ForeignKey(Votes, on_delete= models.CASCADE)
    ip = models.CharField(blank=True, max_length=100, default='')
    status = models.CharField(max_length=30, choices=STATUS)

    def __str__(self):
        return self.ip

    class Meta:
        verbose_name = 'Voter'
        verbose_name_plural = 'Voters'

    