from django.db import models

# Create your models here.


class UserDetail(models.Model):
    mob = models.IntegerField(null=True)


class CarDetail(models.Model):
    mob_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    Trip_no = models.IntegerField(null=True)
    Trip_time = models.CharField(null=True, max_length=50)
    ax = models.FloatField(null=True)
    ay = models.FloatField(null=True)
    az = models.FloatField(null=True)
    gx = models.FloatField(null=True)
    gy = models.FloatField(null=True)
    gz = models.FloatField(null=True)
    mx = models.FloatField(null=True)
    my = models.FloatField(null=True)
    mz = models.FloatField(null=True)
    speed = models.FloatField(null=True)
    GPS = models.TextField(null=True)
    # Hard_Acc = models.IntegerField(null=True)
    # Hard_brake = models.IntegerField(null=True)
    # Hard_cornering = models.IntegerField(null=True)
