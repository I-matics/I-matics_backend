from rest_framework import serializers
from .models import CarDetail, UserDetail,TripDetail


class CarDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarDetail
        # fields = ['time', 'ax', 'ay', 'az', 'speed', 'trip', 'geoloacation']
        fields = '__all__'

class UserIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        fields = '__all__'

class UserdetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        # fields = ['time', 'ax', 'ay', 'az', 'speed', 'trip', 'geoloacation']
        fields = ['id','Trip']

class TripDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripDetail
        # fields = ['time', 'ax', 'ay', 'az', 'speed', 'trip', 'geoloacation']
        # fields = ['Trip_No', 'Risk_Instance', 'Average_speed', 'Trip_time', 'Distance_Travelled', 'Score']
        fields = '__all__'

class TripDetailsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripDetail
        # fields = ['time', 'ax', 'ay', 'az', 'speed', 'trip', 'geoloacation']
        fields = ['Trip_No', 'Risk_Instance', 'Average_speed', 'Trip_time', 'Distance_Travelled', 'Score']
        # fields = '__all__'

