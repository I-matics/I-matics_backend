from django.db import models

# Create your models here.


class UserDetail(models.Model):
    mob = models.BigIntegerField(null=False)
    Trip = models.BigIntegerField(null=True)


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
    C1 = models.FloatField(null=True)
    C2 = models.FloatField(null=True)
    C3 = models.FloatField(null=True)
    C4 = models.FloatField(null=True)
    C5 = models.FloatField(null=True)
    C6 = models.FloatField(null=True)
    C7 = models.FloatField(null=True)
    C8 = models.FloatField(null=True)
    C9 = models.FloatField(null=True)
    C10 = models.FloatField(null=True)
    C11 = models.FloatField(null=True)
    C12 = models.FloatField(null=True)
    C13 = models.TextField(null=True)
    C14 = models.TextField(null=True)
    C15 = models.TextField(null=True)
    resultant = models.FloatField(null=True)
    # Hard_Acc = models.IntegerField(null=True)
    # Hard_brake = models.IntegerField(null=True)
    # Hard_cornering = models.IntegerField(null=True)

class TripDetail(models.Model):
    Tripdetail_id = models.ForeignKey(UserDetail, on_delete=models.CASCADE)
    Trip_No = models.BigIntegerField(null=True)
    Risk_Instance = models.FloatField(null=True)
    Average_speed = models.FloatField(null=True) 
    Trip_time = models.FloatField(null=True)
    Distance_Travelled = models.FloatField(null=True)
    Score = models.FloatField(null=True)
    C1 = models.TextField(null=True)
    C2 = models.TextField(null=True)
    C3 = models.TextField(null=True)
    C4 = models.FloatField(null=True)
    C5 = models.FloatField(null=True)

