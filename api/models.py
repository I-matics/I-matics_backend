from django.db import models

# Create your models here.


class UserDetail(models.Model):
    mob = models.IntegerField(null=False)


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
    gPS = models.TextField(null=True)
    C1_f = models.FloatField(null=True)
    C2_f = models.FloatField(null=True)
    C3_f = models.FloatField(null=True)
    C4_f = models.FloatField(null=True)
    C5_f = models.FloatField(null=True)
    C6_f = models.CharField(null=True, max_length=100)
    C7_f = models.CharField(null=True, max_length=100)
    C8_f = models.CharField(null=True, max_length=100)
    
    # Hard_Acc = models.IntegerField(null=True)
    # Hard_brake = models.IntegerField(null=True)
    # Hard_cornering = models.IntegerField(null=True)
