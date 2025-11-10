from django.contrib import admin
from .models import Clinic


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'total_reviews', 'average_rating', 'has_parking', 'created_at')
    list_filter = ('district', 'has_parking', 'night_service', 'weekend_service', 'created_at')
    search_fields = ('name', 'address', 'district')
    ordering = ('-total_reviews', 'name')
    readonly_fields = ('created_at', 'updated_at', 'search_vector')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'address', 'district', 'phone')
        }),
        ('위치 정보', {
            'fields': ('latitude', 'longitude')
        }),
        ('시설 정보', {
            'fields': ('has_parking', 'night_service', 'weekend_service')
        }),
        ('통계 정보', {
            'fields': ('total_reviews', 'average_rating')
        }),
        ('외부 플랫폼', {
            'fields': ('naver_place_id', 'google_place_id')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at', 'search_vector'),
            'classes': ('collapse',)
        }),
    )