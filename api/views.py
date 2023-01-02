from django.shortcuts import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import random
import math
import pandas as pd
import datetime
from datetime import timedelta
from django.shortcuts import get_object_or_404

from .serializers import CarDetailSerializer, UserdetailSerializer
from .models import CarDetail

# Create your views here.


def Trip_Abs_Scoring(x, y, z, p):
    Hard_Acc = 0
    Hard_brake = 0
    Hard_cornering = 0
    if x > 4 & p > 5:
        Hard_Acc = x
    if x < -4 & p > 5:
        Hard_brake = x
    if y > 4 & p > 5:
        Hard_cornering = y
    if y < -4 & p > 5:
        Hard_cornering = y
    a = {"Hard_Acc": str(Hard_Acc), "Hard_brake": str(Hard_brake),
         "Hard_cornering": str(Hard_cornering)}
    return a


def Merge(dict1, dict2):
    return(dict2.update(dict1))


@api_view(['POST'])
def hello_world(request):
    if request.method == 'GET':
        queryset = CarDetail.objects.all()
        serializer = CarDetailSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        # Trip_no = int(request.data["Trip_no"])
        # Trip_time = request.data["Trip_time"]
        ax = float(request.data["ax"])
        ay = float(request.data["ay"])
        az = float(request.data["az"])
        # gx = float(request.data["gx"])
        # gy = float(request.data["gy"])
        # gz = float(request.data["gz"])
        # mx = float(request.data["mx"])
        # my = float(request.data["my"])
        # mz = float(request.data["mz"])
        # speed = float(request.data["speed"])
        # GPS = request.data["gps"]
        # detail = Trip_Abs_Scoring(ax, ay, az, speed)
        # Merge(request.data, detail)
        # print(detail)
        #get ax,ay,az  then calculate result(sqrt(x2+y2+z2))
        # net = math.sqrt((ax*ax)+(ay*ay)+(az*az))
        # if net > 1.3:
        #
            
        # store the resultant value
        serializer = CarDetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def user_detail(request):
    if request.method == 'POST':
        serializer = UserdetailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def generate_random(request,pk):
    if request.method == 'GET':
        # Get data from database using pk --CarDetail.objects.filter()
        car_detail = CarDetail.objects.filter(mob_id_id = pk).values()
        # car_detail = get_object_or_404(CarDetail, mob_id_id=pk).values()
        car_df = pd.DataFrame(car_detail)
        # datetime1 = datetime.datetime.now()
        # for i in range(0, len(car_df)):
        #     start_date = datetime.datetime.now()
        #     end_date = datetime1 + timedelta(days=2)
        #     random_date = start_date + (end_date - start_date) * random.random()
        #     car_df.loc[i, 'Trip_time'] = random_date 
        #     car_df.loc[i, 'Trip_time'] = random_date
        # for i in range(0, len(car_df)):
        #     car_df.loc[i, 'resultant']= random.uniform(0.5, 15.5)
        for i in range(1, len(car_df)):
            if car_df.loc[i, 'resultant'] > 1.3:
                 if car_df.loc[i, 'resultant'] - car_df.loc[i-1, 'resultant'] > 0.2:
                     car_df.loc[i, 'count'] = 1
                 else:car_df.loc[i, 'count'] = 0
            else:
                car_df.loc[i, 'count'] = 0 
        risk_instance = car_df['count'].sum()
        avg_speed = car_df['speed'].mean()
        dist_travelled = avg_speed *(car_df.loc[len(car_df['Trip_time'])-1, 'Trip_time'] - car_df.loc[0, 'Trip_time'])
        dist_travelled1 = dist_travelled.total_seconds()/60       
        # filter data if result>1.3 then check (resultant-(previous resultant))>0.2 then count 1
        # Average speed, Duration of travel, distance travelled = Average speed*Duration of travel
        # Return the value
        # r = random.randint(1,100)
        return Response({"Risk Instance":risk_instance,"Average_speed":avg_speed,"Distance Travelled":dist_travelled1})

