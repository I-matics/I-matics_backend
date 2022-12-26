from django.shortcuts import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import random
#import pandas as pd

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
        # ax = float(request.data["ax"])
        # ay = float(request.data["ay"])
        # az = float(request.data["az"])
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
        r = random.randint(1,100)
        return Response(r)
