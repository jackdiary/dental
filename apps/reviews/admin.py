from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('clinic', 'source', 'original_rating', 'is_processed', 'is_duplicate', 'is_flagged', 'created_at')
    list_filter = ('source', 'is_processed', 'is_duplicate', 'is_flagged', 'created_at')
    search_fields = ('clinic__name', 'original_text', 'reviewer_hash')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'search_vector', 'reviewer_hash')
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('clinic', 'source', 'external_id')
        }),
        ('리뷰 내용', {
            'fields': ('original_text', 'processed_text')
        }),
        ('메타데이터', {
            'fields': ('original_rating', 'review_date', 'reviewer_hash')
        }),
        ('처리 상태', {
            'fields': ('is_processed', 'is_duplicate', 'is_flagged')
        }),
        ('시스템 정보', {
            'fields': ('created_at', 'updated_at', 'search_vector'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_processed', 'mark_as_flagged', 'mark_as_duplicate']
    
    def mark_as_processed(self, request, queryset):
        queryset.update(is_processed=True)
    mark_as_processed.short_description = "선택된 리뷰를 처리 완료로 표시"
    
    def mark_as_flagged(self, request, queryset):
        queryset.update(is_flagged=True)
    mark_as_flagged.short_description = "선택된 리뷰를 플래그로 표시"
    
    def mark_as_duplicate(self, request, queryset):
        queryset.update(is_duplicate=True)
    mark_as_duplicate.short_description = "선택된 리뷰를 중복으로 표시"