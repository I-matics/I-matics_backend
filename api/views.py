from django.shortcuts import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import random
import math
import math
import pandas as pd
import datetime
import os
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.http import Http404
from .serializers import CarDetailSerializer,UserdetailSerializer, TripDetailsSerializer, TripDetailsViewSerializer, UserIdSerializer
from .models import CarDetail,UserDetail,TripDetail
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
import io
from api.Scoring.helper_functions import fir_filter, ekf_filter, calculate_exponential_score
from api.Scoring.speeding import overspeed_score
from api.Scoring.extrapolation import create_smooth_curve
import api.Scoring.timeoftravel
from api.Scoring.acceleration import capture_peaks_and_differentiate2
from api.Scoring.distance import distance_based_risk

# Create your views here.

def map_trip_data_to_model(data):
    # Define a mapping between dictionary keys and model fields
    field_mapping = {
        "Trip No":"Trip_No",
        "Tripdetail_id": "Tripdetail_id" ,
        "Total Distance": "Risk_Instance",
        "Overspeed Score": "Average_speed",
        "Acceleration Score": "Trip_time",
        "Braking Score": "Distance_Travelled",
        "Time of Travel Score": "Score",
        "Distance Score": "C1",
        "Total Averaged Score": "C2",
        "Exponential Score": "C4",
    }

    mapped_data = {}
    for key, field_name in field_mapping.items():
        if key in data:
            mapped_data[field_name] = data[key]

    return mapped_data


def process_trip_data(doc):
    
    tripdetail_id = doc['mob_id'].unique()
    trip_n = doc['Trip_no'].unique()

    # Frequency
    freq = 50

    # Calculate total distance
    total_distance = sum((doc["speed"] * (5 / 18)) / freq) / 1000

    if total_distance <= 0.5:
        return "Low Distance"
    # Take a reading from the speed list once every 50 times into  a separate list
    speed = doc["speed"]
    speed_data = [speed[i] for i in range(len(speed)) if i % freq == 0]

    # Overspeeding parameters
    original_frequency = 1
    target_frequency = 50
    target_time, smoothed_speed_data = create_smooth_curve(speed_data, original_frequency, target_frequency)
    overspeeding_weight = 0.1
    speed_limit = 40
    speed_exponent = 0.8

    # Calculate Overspeed score
    overspeed_score_value = overspeed_score(
        speed_data=speed_data,
        overspeeding_weight=overspeeding_weight,
        speed_limit=speed_limit,
        speed_exponent=speed_exponent,
    )

    # Hard acceleration/braking parameters
    acceleration_threshold = 17
    acceleration_weight = 0.3
    event_time = 1
    braking_weight = 0.4
    acc_exponent = 0.3
    brak_exponent = 0.3

    # FIR filter parameters
    filter_order = 25
    fir_cutoff = 5

    # Filter and orient the data
    oax, oay, oaz, ogx, ogy, ogz, omx, omy, omz = fir_filter(
        doc, filter_order=filter_order, sampling_freq=freq, fir_cutoff=fir_cutoff
    )

    # Orientation of the filtered data
    ax, ay, az = ekf_filter(ax=oax, ay=oay, az=oaz, gx=ogx, gy=ogy, gz=ogz, mx=omx, my=omy, mz=omz)

    # Get the acceleration score
    peak_events, acceleration_score, braking_score = capture_peaks_and_differentiate2(
        ax_data=ax,
        ay_data=ay,
        speed_data=smoothed_speed_data,
        acc_exponent=acc_exponent,
        brak_exponent=brak_exponent,
        threshold=acceleration_threshold,
        time=event_time,
        data_freq=freq,
    )

    for event in peak_events:
        if event == "Hard Acceleration":
            acceleration_score += acceleration_weight
        elif event == "Hard Braking":
            braking_score += braking_weight

    # Time-based risk parameters
    time_weights = 1
    time_exponent_indice = 2

    # Get the time of travel score
    time_of_travel_score = (
        api.Scoring.timeoftravel.time_based_risk(timedata=doc["Trip_time"], exponential_indice=time_exponent_indice)
        * time_weights
    )

    # Distance-based risk parameters
    distance_weight = 1
    distance_exponential_indice = 0.34

    # Get the distance-based score
    distance_score = (
        distance_based_risk(total_distance, exponential_indice=distance_exponential_indice)
        * distance_weight
    )

    # Total Averaged Score
    total_score = (
        overspeed_score_value
        + acceleration_score
        + braking_score
        + time_of_travel_score
        + distance_score
    ) / total_distance

    # Exponential Score Parameters
    exponent_multiplier = 0.018
    exponent_base = 2

    # Calculate the exponential score
    exponent_score = calculate_exponential_score(
        risk_score=total_score, base=exponent_base, exponent_multiplier=exponent_multiplier
    )

    # Return all data points
    return {
        "Tripdetail_id": tripdetail_id[0],
        "Trip No":trip_n[0],
        "Total Distance": total_distance,
        "Overspeed Score": overspeed_score_value,
        "Acceleration Score": acceleration_score,
        "Braking Score": braking_score,
        "Time of Travel Score": time_of_travel_score,
        "Distance Score": distance_score,
        "Total Averaged Score": total_score,
        "Exponential Score": exponent_score,
    }



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
    trip_no = car_df_raw['Trip_no'].unique().tolist()
    if 0 in trip_no: trip_no.remove(0)
    for trip_n in trip_no:
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
        trip['Tripdetail_id'] = car_df['mob_id'].unique()
        trip["Trip_No"] = trip_n
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
        trip["Distance_Travelled"] = dist_travelled1
        score = round(100*math.exp(-risk_instance*0.005),2) 
        # trip.append("score"+":"+str(score))
        trip["Score"] = score
    return trip


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

@api_view(['GET'])
def get_trip_details(request, id_t):
    try:
        trip_details = TripDetail.objects.filter(Tripdetail_id_id=id_t)
        serializer = TripDetailsViewSerializer(trip_details, many=True)
        # Modify the field names in the serialized data
        modified_data = []
        for item in serializer.data:
            modified_item = {
                'Trip No': item['Trip_No'],  # Replace with your desired field name
                # 'Tripdetail Id': item['Tripdetail_id'],
                'Total Distance': item['Risk_Instance'],
                'Overspeed Score': item['Average_speed'],  # Replace with your desired field name
                'Acceleration Score': item['Trip_time'],
                'Braking Score': item['Distance_Travelled'],
                'Time of Travel Score': item['Score'],  # Replace with your desired field name
                'Distance Score': item['C1'],
                'Total Averaged Score': item['C2'],
                'Exponential Score': item['C4'],
                # Add other fields as needed
            }
            modified_data.append(modified_item)
        print(modified_data)
        return Response(modified_data, status=status.HTTP_200_OK)
    except TripDetail.DoesNotExist:
        return Response({"error": "Trip details not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def upload_csv_api(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']

        # Check if the uploaded file is a CSV file
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'Only CSV files are allowed.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Save the file to S3 bucket
        file_path = 'csv_file_folder/' + csv_file.name
        default_storage.save(file_path, csv_file)
        
        # Process the CSV file and perform any necessary calculations
        with default_storage.open(file_path, 'rb') as file:
            file_data = file.read()

        data = pd.read_csv(io.BytesIO(file_data))

        trip_data = process_trip_data(data)
        mapped_trip_data = map_trip_data_to_model(trip_data)
        mapped_trip_data["C3"] = file_path
        # Save the processed data using your serializer
        serializer = TripDetailsSerializer(data=mapped_trip_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'Success': 'File and data sucessfully updated'},status=status.HTTP_201_CREATED)
    return Response({'error': 'No CSV file found in the request.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def store_mobile_number(request):
    mobile_number = request.data.get('mob')
    # Check data already exist in database
    try:
        user_detail = UserDetail.objects.get(mob=mobile_number)
        return Response({'id':user_detail.id},status=status.HTTP_200_OK)
    except UserDetail.DoesNotExist:
        pass # Continue to save the new record
    # Mobile Number Does not exist , create a new UserDetail record
    serializer = UserIdSerializer(data=request.data)
    if serializer.is_valid():
        instance = serializer.save()
        return Response({'id':instance.id},status = status.HTTP_201_CREATED)
    return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)


