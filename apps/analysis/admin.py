from django.contrib import admin
from .models import SentimentAnalysis, PriceData, RegionalPriceStats


@admin.register(SentimentAnalysis)
class SentimentAnalysisAdmin(admin.ModelAdmin):
    list_display = ('review', 'price_score', 'skill_score', 'overtreatment_score', 'confidence_score', 'analyzed_at')
    list_filter = ('model_version', 'analyzed_at')
    search_fields = ('review__clinic__name', 'review__original_text')
    ordering = ('-analyzed_at',)
    readonly_fields = ('analyzed_at',)
    
    fieldsets = (
        ('리뷰 정보', {
            'fields': ('review',)
        }),
        ('감성 점수', {
            'fields': ('price_score', 'skill_score', 'kindness_score', 'waiting_time_score', 'facility_score', 'overtreatment_score')
        }),
        ('분석 메타데이터', {
            'fields': ('model_version', 'confidence_score', 'analyzed_at')
        }),
    )


@admin.register(PriceData)
class PriceDataAdmin(admin.ModelAdmin):
    list_display = ('clinic', 'treatment_type', 'price', 'extraction_method', 'is_verified', 'is_outlier', 'created_at')
    list_filter = ('treatment_type', 'extraction_method', 'is_verified', 'is_outlier', 'created_at')
    search_fields = ('clinic__name', 'clinic__district')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('clinic', 'review', 'treatment_type', 'price', 'currency')
        }),
        ('추출 정보', {
            'fields': ('extraction_confidence', 'extraction_method')
        }),
        ('검증 상태', {
            'fields': ('is_verified', 'is_outlier')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_verified', 'mark_as_outlier']
    
    def mark_as_verified(self, request, queryset):
        queryset.update(is_verified=True)
    mark_as_verified.short_description = "선택된 가격을 검증됨으로 표시"
    
    def mark_as_outlier(self, request, queryset):
        queryset.update(is_outlier=True)
    mark_as_outlier.short_description = "선택된 가격을 이상치로 표시"


@admin.register(RegionalPriceStats)
class RegionalPriceStatsAdmin(admin.ModelAdmin):
    list_display = ('district', 'treatment_type', 'avg_price', 'min_price', 'max_price', 'sample_count', 'last_updated')
    list_filter = ('district', 'treatment_type', 'last_updated')
    search_fields = ('district', 'treatment_type')
    ordering = ('district', 'treatment_type')
    readonly_fields = ('last_updated',)
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('district', 'treatment_type')
        }),
        ('가격 통계', {
            'fields': ('min_price', 'max_price', 'avg_price', 'median_price')
        }),
        ('메타데이터', {
            'fields': ('sample_count', 'last_updated')
        }),
    )