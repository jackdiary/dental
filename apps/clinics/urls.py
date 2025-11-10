from django.urls import path
from . import views, admin_views

app_name = 'clinics'

urlpatterns = [
    # 치과 CRUD
    path('', views.ClinicListCreateView.as_view(), name='clinic_list_create'),
    path('<int:pk>/', views.ClinicDetailView.as_view(), name='clinic_detail'),
    
    # 검색 및 필터링
    path('search/', views.clinic_search, name='clinic_search'),
    path('nearby/', views.clinic_nearby, name='clinic_nearby'),
    path('by-district/', views.clinic_by_district_and_location, name='clinic_by_district_location'),
    
    # 위치 서비스
    path('geocode/', views.geocode_address, name='geocode_address'),
    path('reverse-geocode/', views.reverse_geocode, name='reverse_geocode'),
    path('nearby-districts/', views.nearby_districts, name='nearby_districts'),
    path('seoul-districts/', views.seoul_districts, name='seoul_districts'),
    
    # 유틸리티
    path('districts/', views.clinic_districts, name='clinic_districts'),
    path('stats/', views.clinic_stats, name='clinic_stats'),
    
    # 관리자 기능 - 데이터 생성
    path('admin/create-data/', admin_views.create_massive_data, name='create_massive_data'),
    path('admin/data-status/', admin_views.data_status, name='data_status'),
    path('admin/migrate/', admin_views.run_migrations, name='run_migrations'),
    path('admin/check-tables/', admin_views.check_tables, name='check_tables'),
]