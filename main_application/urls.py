
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Main URLs
urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('register/vendor/', views.vendor_registration, name='vendor_registration'),
    path('register/organization/', views.organization_registration, name='organization_registration'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Tenders namespace
    path('tender/', views.tender_list, name='tender_list'),
    path('tender/categories/', views.tender_categories, name='tender_categories'),
    path('tender/category/<slug:slug>/', views.tender_by_category, name='tender_category'),
    path('tender/<slug:slug>/', views.tender_detail, name='tender_detail'),
    path('tender/<slug:slug>/clarify/', views.ask_clarification, name='tender_ask_clarification'),
   
    # Organizations namespace
    path('organization/', views.organization_list, name='organization_list'),
    path('organization/<slug:slug>/', views.organization_detail, name='organization_detail'),
   
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/profile/', views.profile, name='profile'),
    path('dashboard/notifications/', views.notifications, name='notifications'),
        
    # Vendor specific
    path('bids/', views.my_bids, name='my_bids'),
    path('bids/submit/<slug:tender_slug>/', views.submit_bid, name='submit_bid'),
    path('contracts/', views.my_contracts, name='my_contracts'),
    path('contracts/<str:contract_number>/', views.contract_detail, name='contract_detail'),   
    # Organization specific
    path('tenders/', views.my_tenders, name='my_tenders'),
    path('received-bids/', views.received_bids, name='received_bids'),
  
]
