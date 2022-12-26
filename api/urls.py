from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_detail),
    path("cardetail/", views.hello_world),
    path("score/<int:pk>/", views.generate_random),
]
