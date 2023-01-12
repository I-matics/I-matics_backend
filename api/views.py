from django.shortcuts import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import random
import math
import math
import pandas as pd
import datetime
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.http import Http404
from .serializers import CarDetailSerializer, UserdetailSerializer
from .models import CarDetail,UserDetail

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


def calculations(car_df):      
    car_df_raw = pd.DataFrame(car_df)
    trip_no = car_df_raw['Trip_no'].unique()
    Trip_Data = []
    for trip_n in trip_no:
        print(trip_n)
        car_df = car_df_raw[car_df_raw['Trip_no'] == trip_n]
        car_df = car_df.reset_index()
        trip={}
        for i in range(1, len(car_df)):
            if car_df.loc[i, 'resultant'] > 1.3:
                if int(car_df.loc[i, 'resultant']) - int(car_df.loc[i-1, 'resultant']) < 0.2:
                    car_df.loc[i, 'count'] = 0
                else:
                    car_df.loc[i, 'count'] =1
            else:
                car_df.loc[i, 'count'] = 0 
        risk_instance = car_df['count'].sum()
        # trip.append("Risk_Instance"+":"+str(risk_instance))
        trip["Trip No"] = trip_n
        trip["Risk_Instance"] = risk_instance
        avg_speed = round(car_df['speed'].mean(),2)
        # trip.append("Average_speed"+":"+str(avg_speed))
        trip["Average_speed"] = avg_speed
        car_df['Trip_time'] = pd.to_datetime(car_df['Trip_time'])
        dist_travelled = car_df.loc[len(car_df['Trip_time'])-1, 'Trip_time'] - car_df.loc[0, 'Trip_time']
        total_time = round(dist_travelled.total_seconds()/3600,3)
        Trip_time = round(dist_travelled.total_seconds()/60,3)
        # trip.append("Trip_time"+":"+str(Trip_time))
        trip["Trip_time"] = Trip_time
        dist_travelled1 = round(avg_speed*total_time,2)
        # trip.append("dist_travelled"+":"+str(dist_travelled1))
        trip["Distance Travelled"] = dist_travelled1
        score = round(100*math.exp(-risk_instance*0.005),2) 
        # trip.append("score"+":"+str(score))
        trip["Score"] = score
        print(trip)
        Trip_Data.append(trip)
    return Trip_Data


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
        car_detail = CarDetail.objects.filter(mob_id_id = pk).values()   #filter data according to mobile id
        if not car_detail:
            car_detail = get_object_or_404(CarDetail, mob_id_id=pk).values()
        else:
            car_detail = CarDetail.objects.filter(mob_id_id = pk).values()
        Trip_Data = calculations(car_detail)
        return Response(Trip_Data)
  
        # filter data if result>1.3 then check (resultant-(previous resultant))>0.2 then count 1
        # Average speed, Duration of travel, distance travelled = Average speed*Duration of travel
        # Return the value
        # r = random.randint(1,100)

@api_view(['GET','PUT'])
def trip_data(request,id_n):
    if request.method == 'GET':
        id_detail = UserDetail.objects.filter(id = id_n).values()
        serializer = UserdetailSerializer(
            id_detail, many=True, context={'request': request})
        return Response(serializer.data)
    if request.method == 'PUT':
        instance = get_object_or_404(UserDetail.objects.all(), pk=id_n)
        serializer = UserdetailSerializer(instance, data=request.data)
        # validate and update
        if serializer.is_valid():
            serializer.save()
            serializer_dict = serializer.data
            serializer_dict["Trip"] = request.data['Trip']
            return Response(serializer_dict, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
                            
