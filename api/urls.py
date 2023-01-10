from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_detail),
    path("cardetail/", views.hello_world),
    path("random/<int:pk>/", views.generate_random),
    path("trip/<int:id_n>/", views.trip_data),
]
