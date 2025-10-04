"""
Views for the Tender Management System
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta

from .models import (
    Tender, Organization, Vendor, TenderCategory, 
    Bid, Contract, Milestone, TenderDocument, 
    BidDocument, Clarification, Notification, Review
)
from .forms import (
    VendorRegistrationForm, OrganizationRegistrationForm,
    TenderForm, BidForm, ClarificationForm, UserRegistrationForm
)


# ==================== PUBLIC VIEWS ====================

def home(request):
    """Homepage view"""
    featured_tenders = Tender.objects.filter(
        status='published', 
        is_featured=True
    ).order_by('-publication_date')[:6]
    
    recent_tenders = Tender.objects.filter(
        status='published'
    ).order_by('-publication_date')[:8]
    
    stats = {
        'total_tenders': Tender.objects.filter(status='published').count(),
        'active_organizations': Organization.objects.filter(is_verified=True).count(),
        'registered_vendors': Vendor.objects.filter(is_verified=True).count(),
        'awarded_contracts': Contract.objects.filter(status='active').count(),
    }
    
    categories = TenderCategory.objects.filter(parent=None)[:8]
    
    context = {
        'featured_tenders': featured_tenders,
        'recent_tenders': recent_tenders,
        'stats': stats,
        'categories': categories,
    }
    return render(request, 'home.html', context)


def about(request):
    """About page"""
    return render(request, 'about.html')


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        messages.success(request, 'Thank you for your message. We will get back to you soon!')
        return redirect('contact')
    return render(request, 'contact.html')


def terms(request):
    """Terms of service page"""
    return render(request, 'terms.html')


def privacy(request):
    """Privacy policy page"""
    return render(request, 'privacy.html')


# ==================== TENDER VIEWS ====================

def tender_list(request):
    """List all published tenders with filters"""
    tenders = Tender.objects.filter(status='published')
    
    # Filters
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    location = request.GET.get('location')
    min_value = request.GET.get('min_value')
    max_value = request.GET.get('max_value')
    
    if category_slug:
        tenders = tenders.filter(category__slug=category_slug)
    
    if search_query:
        tenders = tenders.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tender_number__icontains=search_query)
        )
    
    if location:
        tenders = tenders.filter(
            Q(project_city__icontains=location) |
            Q(project_country__icontains=location)
        )
    
    if min_value:
        tenders = tenders.filter(estimated_value__gte=min_value)
    
    if max_value:
        tenders = tenders.filter(estimated_value__lte=max_value)
    
    # Pagination
    paginator = Paginator(tenders, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = TenderCategory.objects.all()
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_slug,
    }
    return render(request, 'tenders/tender_list.html', context)


def tender_detail(request, slug):
    """Tender detail view"""
    tender = get_object_or_404(Tender, slug=slug)
    
    # Increment view count
    tender.views_count += 1
    tender.save(update_fields=['views_count'])
    
    documents = tender.documents.all()
    clarifications = tender.clarifications.filter(is_public=True, is_answered=True)
    amendments = tender.amendments.all()
    
    # Check if user has already bid
    user_bid = None
    if request.user.is_authenticated:
        try:
            vendor = request.user.vendor
            user_bid = Bid.objects.filter(tender=tender, vendor=vendor).first()
        except Vendor.DoesNotExist:
            pass
    
    context = {
        'tender': tender,
        'documents': documents,
        'clarifications': clarifications,
        'amendments': amendments,
        'user_bid': user_bid,
        'days_remaining': (tender.submission_deadline - timezone.now()).days,
    }
    return render(request, 'tenders/tender_detail.html', context)


def tender_categories(request):
    """List all tender categories"""
    categories = TenderCategory.objects.filter(parent=None).annotate(
        tender_count=Count('tenders')
    )
    
    context = {
        'categories': categories,
    }
    return render(request, 'tenders/categories.html', context)


def tender_by_category(request, slug):
    """Tenders filtered by category"""
    category = get_object_or_404(TenderCategory, slug=slug)
    tenders = Tender.objects.filter(category=category, status='published')
    
    paginator = Paginator(tenders, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'tenders/category_tenders.html', context)


# ==================== ORGANIZATION VIEWS ====================

def organization_list(request):
    """List all verified organizations"""
    organizations = Organization.objects.filter(is_verified=True).annotate(
        tender_count=Count('tenders')
    )
    
    search = request.GET.get('q')
    if search:
        organizations = organizations.filter(
            Q(name__icontains=search) |
            Q(city__icontains=search) |
            Q(organization_type__icontains=search)
        )
    
    paginator = Paginator(organizations, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search,
    }
    return render(request, 'organizations/organization_list.html', context)


def organization_detail(request, slug):
    """Organization detail with their tenders"""
    organization = get_object_or_404(Organization, slug=slug, is_verified=True)
    tenders = organization.tenders.filter(status='published').order_by('-publication_date')
    
    paginator = Paginator(tenders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'organization': organization,
        'page_obj': page_obj,
    }
    return render(request, 'organizations/organization_detail.html', context)


# ==================== AUTHENTICATION VIEWS ====================

def register(request):
    """General registration page"""
    return render(request, 'auth/register_choice.html')


def vendor_registration(request):
    """Vendor registration"""
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Your account is pending verification.')
            return redirect('dashboard_home')
    else:
        form = VendorRegistrationForm()
    
    context = {'form': form}
    return render(request, 'auth/vendor_registration.html', context)


def organization_registration(request):
    """Organization registration"""
    if request.method == 'POST':
        form = OrganizationRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Your organization is pending verification.')
            return redirect('dashboard_home')
    else:
        form = OrganizationRegistrationForm()
    
    context = {'form': form}
    return render(request, 'auth/organization_registration.html', context)


def user_login(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'dashboard:home')
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'auth/login.html')


def user_logout(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


# ==================== DASHBOARD VIEWS ====================

@login_required
def dashboard_home(request):
    """Main dashboard"""
    context = {}
    
    try:
        vendor = request.user.vendor
        context['user_type'] = 'vendor'
        context['profile'] = vendor
        context['my_bids'] = Bid.objects.filter(vendor=vendor).order_by('-submitted_at')[:5]
        context['my_contracts'] = Contract.objects.filter(vendor=vendor).order_by('-created_at')[:5]
        context['notifications'] = Notification.objects.filter(
            recipient=request.user, is_read=False
        )[:5]
    except Vendor.DoesNotExist:
        # Check if organization user
        organizations = Organization.objects.filter(created_by=request.user)
        if organizations.exists():
            context['user_type'] = 'organization'
            context['organizations'] = organizations
            context['my_tenders'] = Tender.objects.filter(
                organization__in=organizations
            ).order_by('-created_at')[:5]
            context['recent_bids'] = Bid.objects.filter(
                tender__organization__in=organizations
            ).order_by('-submitted_at')[:5]
    
    return render(request, 'dashboard/home.html', context)


@login_required
def my_bids(request):
    """Vendor's bids list"""
    try:
        vendor = request.user.vendor
        bids = Bid.objects.filter(vendor=vendor).order_by('-submitted_at')
        
        paginator = Paginator(bids, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'dashboard/my_bids.html', context)
    except Vendor.DoesNotExist:
        messages.error(request, 'You must be registered as a vendor to view this page.')
        return redirect('dashboard_home')


@login_required
def submit_bid(request, tender_slug):
    """Submit bid for a tender"""
    tender = get_object_or_404(Tender, slug=tender_slug, status='published')
    
    try:
        vendor = request.user.vendor
        
        # Check if already submitted
        if Bid.objects.filter(tender=tender, vendor=vendor).exists():
            messages.error(request, 'You have already submitted a bid for this tender.')
            return redirect('tender_detail', slug=tender_slug)
        
        # Check deadline
        if timezone.now() > tender.submission_deadline:
            messages.error(request, 'The submission deadline has passed.')
            return redirect('tender_detail', slug=tender_slug)
        
        if request.method == 'POST':
            form = BidForm(request.POST, request.FILES)
            if form.is_valid():
                bid = form.save(commit=False)
                bid.tender = tender
                bid.vendor = vendor
                bid.status = 'submitted'
                bid.submitted_at = timezone.now()
                bid.save()
                
                messages.success(request, 'Your bid has been submitted successfully!')
                return redirect('dashboard_my_bids')
        else:
            form = BidForm(initial={'currency': tender.currency})
        
        context = {
            'form': form,
            'tender': tender,
        }
        return render(request, 'dashboard/submit_bid.html', context)
        
    except Vendor.DoesNotExist:
        messages.error(request, 'You must be registered as a vendor to submit bids.')
        return redirect('vendor_registration')


@login_required
def my_contracts(request):
    """Vendor's contracts"""
    try:
        vendor = request.user.vendor
        contracts = Contract.objects.filter(vendor=vendor).order_by('-created_at')
        
        paginator = Paginator(contracts, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'dashboard/my_contracts.html', context)
    except Vendor.DoesNotExist:
        messages.error(request, 'You must be registered as a vendor.')
        return redirect('dashboard_home')


@login_required
def contract_detail(request, contract_number):
    """Contract detail with milestones"""
    contract = get_object_or_404(Contract, contract_number=contract_number)
    
    # Check permissions
    if hasattr(request.user, 'vendor') and contract.vendor == request.user.vendor:
        pass
    elif contract.tender.organization.created_by == request.user:
        pass
    else:
        messages.error(request, 'You do not have permission to view this contract.')
        return redirect('dashboard_home')
    
    milestones = contract.milestones.all().order_by('sequence_number')
    
    context = {
        'contract': contract,
        'milestones': milestones,
    }
    return render(request, 'dashboard/contract_detail.html', context)


@login_required
def notifications(request):
    """User notifications"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')
    
    # Mark as read
    notifications.filter(is_read=False).update(is_read=True, read_at=timezone.now())
    
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'dashboard/notifications.html', context)


@login_required
def profile(request):
    """User profile settings"""
    try:
        vendor = request.user.vendor
        profile_type = 'vendor'
        profile = vendor
    except Vendor.DoesNotExist:
        profile_type = 'user'
        profile = request.user
    
    context = {
        'profile_type': profile_type,
        'profile': profile,
    }
    return render(request, 'dashboard/profile.html', context)


@login_required
def ask_clarification(request, tender_slug):
    """Submit clarification question"""
    tender = get_object_or_404(Tender, slug=tender_slug)
    
    try:
        vendor = request.user.vendor
        
        if request.method == 'POST':
            form = ClarificationForm(request.POST)
            if form.is_valid():
                clarification = form.save(commit=False)
                clarification.tender = tender
                clarification.vendor = vendor
                clarification.save()
                
                messages.success(request, 'Your question has been submitted.')
                return redirect('tender_detail', slug=tender_slug)
        else:
            form = ClarificationForm()
        
        context = {
            'form': form,
            'tender': tender,
        }
        return render(request, 'tenders/ask_clarification.html', context)
        
    except Vendor.DoesNotExist:
        messages.error(request, 'You must be registered as a vendor.')
        return redirect('vendor_registration')


# ==================== ORGANIZATION DASHBOARD VIEWS ====================

@login_required
def my_tenders(request):
    """Organization's tenders"""
    organizations = Organization.objects.filter(created_by=request.user)
    
    if not organizations.exists():
        messages.error(request, 'You must be associated with an organization.')
        return redirect('dashboard:home')
    
    tenders = Tender.objects.filter(organization__in=organizations).order_by('-created_at')
    
    paginator = Paginator(tenders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'dashboard/my_tenders.html', context)


@login_required
def received_bids(request):
    """Bids received for organization's tenders"""
    organizations = Organization.objects.filter(created_by=request.user)
    
    if not organizations.exists():
        messages.error(request, 'You must be associated with an organization.')
        return redirect('dashboard:home')
    
    bids = Bid.objects.filter(
        tender__organization__in=organizations
    ).order_by('-submitted_at')
    
    paginator = Paginator(bids, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'dashboard/received_bids.html', context)