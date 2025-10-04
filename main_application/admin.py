from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from django.utils import timezone
from django.db.models import Q
from django.db import models
from .models import (
    Organization, TenderCategory, Tender, TenderDocument,
    Vendor, Bid, BidDocument, TenderAmendment, Clarification,
    Contract, Milestone, Evaluation, BidEvaluation, Notification, Review
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization_type', 'registration_number', 'city', 'country', 'is_verified', 'tender_count', 'created_at']
    list_filter = ['organization_type', 'is_verified', 'country', 'created_at']
    search_fields = ['name', 'registration_number', 'email', 'tax_id']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'slug', 'organization_type', 'logo')
        }),
        ('Registration Details', {
            'fields': ('registration_number', 'tax_id', 'is_verified')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Location', {
            'fields': ('address', 'city', 'country')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def tender_count(self, obj):
        count = obj.tenders.count()
        url = reverse('admin:tenders_tender_changelist') + f'?organization__id__exact={obj.id}'
        return format_html('<a href="{}">{} tenders</a>', url, count)
    tender_count.short_description = 'Tenders Posted'


@admin.register(TenderCategory)
class TenderCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'slug', 'tender_count', 'icon']
    list_filter = ['parent']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def tender_count(self, obj):
        count = obj.tenders.count()
        return f"{count} tenders"
    tender_count.short_description = 'Active Tenders'


class TenderDocumentInline(admin.TabularInline):
    model = TenderDocument
    extra = 1
    fields = ['document_type', 'title', 'file', 'file_size', 'is_mandatory']
    readonly_fields = ['file_size']


class TenderAmendmentInline(admin.TabularInline):
    model = TenderAmendment
    extra = 0
    fields = ['amendment_number', 'title', 'affects_submission_deadline', 'published_at']
    readonly_fields = ['published_at']


class ClarificationInline(admin.TabularInline):
    model = Clarification
    extra = 0
    fields = ['vendor', 'question', 'is_answered', 'is_public', 'asked_at']
    readonly_fields = ['asked_at']


@admin.register(Tender)
class TenderAdmin(admin.ModelAdmin):
    list_display = ['tender_number', 'title_short', 'organization', 'category', 'status', 'estimated_value_display', 'submission_deadline', 'bid_count', 'views_count', 'is_featured']
    list_filter = ['status', 'procurement_method', 'organization__organization_type', 'category', 'is_featured', 'publication_date', 'project_country']
    search_fields = ['tender_number', 'title', 'organization__name', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['id', 'views_count', 'created_at', 'updated_at', 'bid_statistics']
    date_hierarchy = 'publication_date'
    
    inlines = [TenderDocumentInline, TenderAmendmentInline, ClarificationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'tender_number', 'slug', 'title', 'organization', 'category')
        }),
        ('Description', {
            'fields': ('description', 'detailed_requirements')
        }),
        ('Procurement Details', {
            'fields': ('status', 'procurement_method', 'is_featured')
        }),
        ('Financial Information', {
            'fields': ('estimated_value', 'currency', 'bid_security_amount')
        }),
        ('Important Dates', {
            'fields': ('publication_date', 'submission_deadline', 'opening_date', 'expected_award_date', 'contract_duration_days')
        }),
        ('Project Location', {
            'fields': ('project_location', 'project_city', 'project_country')
        }),
        ('Eligibility Criteria', {
            'fields': ('eligible_countries', 'minimum_experience_years', 'minimum_turnover', 'requires_prequalification'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('contact_person', 'contact_email', 'contact_phone'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('views_count', 'created_by', 'created_at', 'updated_at', 'bid_statistics'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_published', 'mark_as_closed', 'mark_as_cancelled', 'feature_tenders']
    
    def title_short(self, obj):
        return obj.title[:50] + '...' if len(obj.title) > 50 else obj.title
    title_short.short_description = 'Title'
    
    def estimated_value_display(self, obj):
        return format_html('<strong>{} {:,.2f}</strong>', obj.currency, obj.estimated_value)
    estimated_value_display.short_description = 'Estimated Value'
    estimated_value_display.admin_order_field = 'estimated_value'
    
    def bid_count(self, obj):
        count = obj.bids.count()
        url = reverse('admin:tenders_bid_changelist') + f'?tender__id__exact={obj.id}'
        return format_html('<a href="{}">{} bids</a>', url, count)
    bid_count.short_description = 'Bids Received'
    
    def bid_statistics(self, obj):
        stats = obj.bids.aggregate(
            total=Count('id'),
            submitted=Count('id', filter=models.Q(status='submitted')),
            under_review=Count('id', filter=models.Q(status='under_review')),
            awarded=Count('id', filter=models.Q(status='awarded'))
        )
        return format_html(
            '<div style="line-height: 1.8;">'
            '<strong>Total Bids:</strong> {}<br>'
            '<strong>Submitted:</strong> {}<br>'
            '<strong>Under Review:</strong> {}<br>'
            '<strong>Awarded:</strong> {}'
            '</div>',
            stats['total'], stats['submitted'], stats['under_review'], stats['awarded']
        )
    bid_statistics.short_description = 'Bid Statistics'
    
    def mark_as_published(self, request, queryset):
        queryset.update(status='published')
    mark_as_published.short_description = 'Mark selected as Published'
    
    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
    mark_as_closed.short_description = 'Mark selected as Closed'
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = 'Mark selected as Cancelled'
    
    def feature_tenders(self, request, queryset):
        queryset.update(is_featured=True)
    feature_tenders.short_description = 'Feature selected tenders'


@admin.register(TenderDocument)
class TenderDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'tender', 'document_type', 'file_size_display', 'is_mandatory', 'uploaded_at']
    list_filter = ['document_type', 'is_mandatory', 'uploaded_at']
    search_fields = ['title', 'tender__tender_number', 'description']
    readonly_fields = ['uploaded_at']
    
    def file_size_display(self, obj):
        size_kb = obj.file_size / 1024
        if size_kb < 1024:
            return f"{size_kb:.2f} KB"
        else:
            return f"{size_kb/1024:.2f} MB"
    file_size_display.short_description = 'File Size'


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['company_name', 'registration_number', 'business_type', 'city', 'country', 'is_verified', 'is_blacklisted', 'rating', 'bid_count', 'contract_count']
    list_filter = ['business_type', 'is_verified', 'is_blacklisted', 'country', 'created_at']
    search_fields = ['company_name', 'registration_number', 'tax_id', 'email', 'user__username']
    prepopulated_fields = {'slug': ('company_name',)}
    readonly_fields = ['id', 'rating', 'total_reviews', 'created_at', 'updated_at']
    filter_horizontal = ['categories']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'company_name', 'slug', 'business_type')
        }),
        ('Registration Details', {
            'fields': ('registration_number', 'tax_id', 'verification_documents')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Address', {
            'fields': ('address', 'city', 'country', 'postal_code')
        }),
        ('Business Information', {
            'fields': ('year_established', 'number_of_employees', 'annual_turnover', 'categories', 'service_areas')
        }),
        ('Verification & Status', {
            'fields': ('is_verified', 'is_blacklisted')
        }),
        ('Ratings', {
            'fields': ('rating', 'total_reviews'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['verify_vendors', 'blacklist_vendors', 'remove_from_blacklist']
    
    def bid_count(self, obj):
        count = obj.bids.count()
        url = reverse('admin:tenders_bid_changelist') + f'?vendor__id__exact={obj.id}'
        return format_html('<a href="{}">{} bids</a>', url, count)
    bid_count.short_description = 'Total Bids'
    
    def contract_count(self, obj):
        count = obj.contracts.count()
        url = reverse('admin:tenders_contract_changelist') + f'?vendor__id__exact={obj.id}'
        return format_html('<a href="{}">{} contracts</a>', url, count)
    contract_count.short_description = 'Contracts'
    
    def verify_vendors(self, request, queryset):
        queryset.update(is_verified=True)
    verify_vendors.short_description = 'Verify selected vendors'
    
    def blacklist_vendors(self, request, queryset):
        queryset.update(is_blacklisted=True)
    blacklist_vendors.short_description = 'Blacklist selected vendors'
    
    def remove_from_blacklist(self, request, queryset):
        queryset.update(is_blacklisted=False)
    remove_from_blacklist.short_description = 'Remove from blacklist'


class BidDocumentInline(admin.TabularInline):
    model = BidDocument
    extra = 1
    fields = ['document_type', 'title', 'file', 'uploaded_at']
    readonly_fields = ['uploaded_at']


@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = ['bid_number', 'tender_link', 'vendor', 'bid_amount_display', 'status', 'total_score', 'submitted_at', 'delivery_timeline_days']
    list_filter = ['status', 'submitted_at', 'tender__category', 'vendor__country']
    search_fields = ['bid_number', 'tender__tender_number', 'vendor__company_name']
    prepopulated_fields = {'slug': ('bid_number',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'submitted_at', 'reviewed_at']
    date_hierarchy = 'submitted_at'
    
    inlines = [BidDocumentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'bid_number', 'slug', 'tender', 'vendor')
        }),
        ('Bid Details', {
            'fields': ('bid_amount', 'currency', 'delivery_timeline_days')
        }),
        ('Proposals', {
            'fields': ('technical_proposal', 'financial_proposal')
        }),
        ('Bid Security', {
            'fields': ('bid_security_reference', 'bid_security_amount'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Evaluation Scores', {
            'fields': ('technical_score', 'financial_score', 'total_score', 'evaluator_comments'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('submitted_at', 'reviewed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_submitted', 'mark_as_under_review', 'mark_as_shortlisted', 'mark_as_rejected']
    
    def tender_link(self, obj):
        url = reverse('admin:tenders_tender_change', args=[obj.tender.id])
        return format_html('<a href="{}">{}</a>', url, obj.tender.tender_number)
    tender_link.short_description = 'Tender'
    
    def bid_amount_display(self, obj):
        return format_html('<strong>{} {:,.2f}</strong>', obj.currency, obj.bid_amount)
    bid_amount_display.short_description = 'Bid Amount'
    bid_amount_display.admin_order_field = 'bid_amount'
    
    def mark_as_submitted(self, request, queryset):
        queryset.update(status='submitted', submitted_at=timezone.now())
    mark_as_submitted.short_description = 'Mark as Submitted'
    
    def mark_as_under_review(self, request, queryset):
        queryset.update(status='under_review')
    mark_as_under_review.short_description = 'Mark as Under Review'
    
    def mark_as_shortlisted(self, request, queryset):
        queryset.update(status='shortlisted')
    mark_as_shortlisted.short_description = 'Mark as Shortlisted'
    
    def mark_as_rejected(self, request, queryset):
        queryset.update(status='rejected')
    mark_as_rejected.short_description = 'Mark as Rejected'


@admin.register(BidDocument)
class BidDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'bid', 'document_type', 'uploaded_at']
    list_filter = ['document_type', 'uploaded_at']
    search_fields = ['title', 'bid__bid_number', 'description']
    readonly_fields = ['uploaded_at']


@admin.register(TenderAmendment)
class TenderAmendmentAdmin(admin.ModelAdmin):
    list_display = ['amendment_number', 'tender', 'title', 'affects_submission_deadline', 'affects_estimated_value', 'published_at']
    list_filter = ['affects_submission_deadline', 'affects_estimated_value', 'published_at']
    search_fields = ['amendment_number', 'title', 'tender__tender_number']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['published_at']


@admin.register(Clarification)
class ClarificationAdmin(admin.ModelAdmin):
    list_display = ['tender', 'vendor', 'is_answered', 'is_public', 'asked_at', 'answered_at']
    list_filter = ['is_answered', 'is_public', 'asked_at']
    search_fields = ['tender__tender_number', 'vendor__company_name', 'question', 'answer']
    readonly_fields = ['asked_at', 'answered_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('tender', 'vendor', 'is_public')
        }),
        ('Question', {
            'fields': ('question', 'asked_at')
        }),
        ('Answer', {
            'fields': ('answer', 'is_answered', 'answered_at')
        }),
    )


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1
    fields = ['sequence_number', 'title', 'amount', 'percentage_of_total', 'due_date', 'status']


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'tender_link', 'vendor', 'contract_value_display', 'start_date', 'end_date', 'duration_days', 'status', 'signed_status']
    list_filter = ['status', 'start_date', 'signed_by_organization', 'signed_by_vendor']
    search_fields = ['contract_number', 'tender__tender_number', 'vendor__company_name']
    prepopulated_fields = {'slug': ('contract_number',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'milestone_summary']
    date_hierarchy = 'start_date'
    
    inlines = [MilestoneInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'contract_number', 'slug', 'tender', 'winning_bid', 'vendor')
        }),
        ('Contract Value & Duration', {
            'fields': ('contract_value', 'currency', 'start_date', 'end_date', 'duration_days')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Terms & Conditions', {
            'fields': ('terms_and_conditions', 'performance_bond_amount', 'retention_percentage')
        }),
        ('Signatures', {
            'fields': ('signed_contract', 'signed_by_organization', 'signed_by_vendor'),
            'classes': ('collapse',)
        }),
        ('Milestones', {
            'fields': ('milestone_summary',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_active', 'mark_as_completed', 'mark_as_terminated']
    
    def tender_link(self, obj):
        url = reverse('admin:tenders_tender_change', args=[obj.tender.id])
        return format_html('<a href="{}">{}</a>', url, obj.tender.tender_number)
    tender_link.short_description = 'Tender'
    
    def contract_value_display(self, obj):
        return format_html('<strong>{} {:,.2f}</strong>', obj.currency, obj.contract_value)
    contract_value_display.short_description = 'Contract Value'
    contract_value_display.admin_order_field = 'contract_value'
    
    def signed_status(self, obj):
        org = '✓' if obj.signed_by_organization else '✗'
        vendor = '✓' if obj.signed_by_vendor else '✗'
        return format_html('Org: {} | Vendor: {}', org, vendor)
    signed_status.short_description = 'Signatures'
    
    def milestone_summary(self, obj):
        milestones = obj.milestones.all()
        total = milestones.count()
        completed = milestones.filter(status='paid').count()
        total_amount = milestones.aggregate(Sum('amount'))['amount__sum'] or 0
        return format_html(
            '<div style="line-height: 1.8;">'
            '<strong>Total Milestones:</strong> {}<br>'
            '<strong>Completed:</strong> {}<br>'
            '<strong>Total Amount:</strong> {} {:,.2f}'
            '</div>',
            total, completed, obj.currency, total_amount
        )
    milestone_summary.short_description = 'Milestone Summary'
    
    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
    mark_as_active.short_description = 'Mark as Active'
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = 'Mark as Completed'
    
    def mark_as_terminated(self, request, queryset):
        queryset.update(status='terminated')
    mark_as_terminated.short_description = 'Mark as Terminated'


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['contract', 'sequence_number', 'title', 'amount', 'percentage_of_total', 'due_date', 'status', 'completion_date']
    list_filter = ['status', 'due_date', 'completion_date']
    search_fields = ['title', 'contract__contract_number', 'description']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['mark_as_completed', 'mark_as_verified', 'mark_as_paid']
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed', completion_date=timezone.now().date())
    mark_as_completed.short_description = 'Mark as Completed'
    
    def mark_as_verified(self, request, queryset):
        queryset.update(status='verified')
    mark_as_verified.short_description = 'Mark as Verified'
    
    def mark_as_paid(self, request, queryset):
        queryset.update(status='paid', payment_date=timezone.now().date())
    mark_as_paid.short_description = 'Mark as Paid'


class BidEvaluationInline(admin.TabularInline):
    model = BidEvaluation
    extra = 0
    fields = ['bid', 'financial_score', 'total_score', 'recommendation']
    readonly_fields = ['evaluated_at']


@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ['tender', 'evaluator', 'evaluation_date', 'is_completed', 'evaluated_bids_count']
    list_filter = ['is_completed', 'evaluation_date']
    search_fields = ['tender__tender_number', 'evaluator__username']
    readonly_fields = ['evaluation_date']
    
    inlines = [BidEvaluationInline]
    
    def evaluated_bids_count(self, obj):
        return obj.bid_evaluations.count()
    evaluated_bids_count.short_description = 'Bids Evaluated'


@admin.register(BidEvaluation)
class BidEvaluationAdmin(admin.ModelAdmin):
    list_display = ['bid', 'evaluation', 'financial_score', 'total_score', 'recommendation', 'evaluated_at']
    list_filter = ['recommendation', 'evaluated_at']
    search_fields = ['bid__bid_number', 'remarks']
    readonly_fields = ['evaluated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'is_read', 'created_at', 'read_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['recipient__username', 'title', 'message']
    readonly_fields = ['created_at', 'read_at']
    
    actions = ['mark_as_read']
    
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True, read_at=timezone.now())
    mark_as_read.short_description = 'Mark as Read'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['contract', 'reviewer', 'overall_rating', 'quality_rating', 'timeliness_rating', 'professionalism_rating', 'would_work_again', 'created_at']
    list_filter = ['overall_rating', 'would_work_again', 'created_at']
    search_fields = ['contract__contract_number', 'reviewer__username', 'comment']
    readonly_fields = ['created_at']


# Custom Admin Site Configuration
admin.site.site_header = "Tender Management System Administration"
admin.site.site_title = "TMS Admin"
admin.site.index_title = "Welcome to Tender Management System Administration"