from rest_framework import serializers
from .models import CarDetail, UserDetail


class CarDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarDetail
        # fields = ['time', 'ax', 'ay', 'az', 'speed', 'trip', 'geoloacation']
        fields = '__all__'


class UserdetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetail
        # fields = ['time', 'ax', 'ay', 'az', 'speed', 'trip', 'geoloacation']
        fields = '__all__'
