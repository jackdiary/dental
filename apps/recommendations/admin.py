from django.contrib import admin
from .models import RecommendationLog, ClinicScore, RecommendationFeedback


@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'district', 'treatment_type', 'algorithm_version', 'response_time_ms', 'created_at')
    list_filter = ('district', 'treatment_type', 'algorithm_version', 'created_at')
    search_fields = ('user__email', 'district', 'request_ip')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('요청 정보', {
            'fields': ('user', 'district', 'treatment_type')
        }),
        ('추천 결과', {
            'fields': ('recommended_clinics', 'algorithm_version')
        }),
        ('메타데이터', {
            'fields': ('request_ip', 'user_agent', 'response_time_ms')
        }),
        ('시스템 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ClinicScore)
class ClinicScoreAdmin(admin.ModelAdmin):
    list_display = ('clinic', 'comprehensive_score', 'price_competitiveness', 'medical_skill', 'overtreatment_risk', 'last_calculated')
    list_filter = ('calculation_version', 'last_calculated')
    search_fields = ('clinic__name', 'clinic__district')
    ordering = ('-comprehensive_score',)
    readonly_fields = ('last_calculated',)
    
    fieldsets = (
        ('치과 정보', {
            'fields': ('clinic',)
        }),
        ('측면별 점수', {
            'fields': ('price_competitiveness', 'medical_skill', 'overtreatment_risk', 'patient_satisfaction')
        }),
        ('종합 점수', {
            'fields': ('comprehensive_score',)
        }),
        ('메타데이터', {
            'fields': ('calculation_version', 'last_calculated', 'total_reviews_analyzed', 'price_data_points')
        }),
    )


@admin.register(RecommendationFeedback)
class RecommendationFeedbackAdmin(admin.ModelAdmin):
    list_display = ('clinic', 'feedback_type', 'did_visit', 'visit_rating', 'created_at')
    list_filter = ('feedback_type', 'did_visit', 'created_at')
    search_fields = ('clinic__name', 'comment')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('피드백 정보', {
            'fields': ('recommendation_log', 'clinic', 'feedback_type', 'comment')
        }),
        ('방문 정보', {
            'fields': ('did_visit', 'visit_rating')
        }),
        ('시스템 정보', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )