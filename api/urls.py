from django.urls import path
from . import views

urlpatterns = [
    path("", views.user_detail),
    path("cardetail/", views.hello_world),
    path("random/<int:pk>/", views.generate_random),
    path("trip/<int:id_n>/", views.trip_data),
    path("trip_detailcheck/<int:id_t>/", views.get_trip_details),
    path('upload-csv/', views.upload_csv_api, name='upload_csv_api'),
    path('store-mobile-number/', views.store_mobile_number, name='store-mobile-number'),
]
