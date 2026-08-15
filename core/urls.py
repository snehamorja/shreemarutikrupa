from django.urls import path
from core import views

urlpatterns = [
    # Public Website URLs
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('gallery/', views.gallery, name='gallery'),
    path('faqs/', views.faqs, name='faqs'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard Portal Core URLs
    path('dashboard/', views.overview, name='overview'),
    
    # Scaife Registry CRUD
    path('dashboard/scaife/', views.scaife_list, name='scaife_list'),
    path('dashboard/scaife/history/', views.scaife_history, name='scaife_history'),
    path('dashboard/scaife/create/', views.scaife_create, name='scaife_create'),
    path('dashboard/scaife/<int:pk>/edit/', views.scaife_edit, name='scaife_edit'),
    path('dashboard/scaife/<int:pk>/delete/', views.scaife_delete, name='scaife_delete'),
    
    # Office Management CRUD
    path('dashboard/offices/', views.office_list, name='office_list'),
    path('dashboard/offices/create/', views.office_create, name='office_create'),
    path('dashboard/offices/<int:pk>/edit/', views.office_edit, name='office_edit'),
    path('dashboard/offices/<int:pk>/delete/', views.office_delete, name='office_delete'),
    
    # Pricing Config Settings
    path('dashboard/pricing/', views.pricing_edit, name='pricing_edit'),
    
    # User Management CRUD
    path('dashboard/users/', views.user_list, name='user_list'),
    path('dashboard/users/create/', views.user_create, name='user_create'),
    path('dashboard/users/<int:pk>/edit/', views.user_edit, name='user_edit'),
    path('dashboard/users/<int:pk>/delete/', views.user_delete, name='user_delete'),

    # Worker Payroll & Ledger
    path('dashboard/workers/', views.worker_list, name='worker_list'),
    path('dashboard/workers/create/', views.worker_create, name='worker_create'),
    path('dashboard/workers/<int:pk>/', views.worker_detail, name='worker_detail'),
    path('dashboard/workers/<int:pk>/edit/', views.worker_edit, name='worker_edit'),
    path('dashboard/workers/<int:pk>/entry/add/', views.worker_entry_add, name='worker_entry_add'),
    path('dashboard/workers/entry/<int:pk>/delete/', views.worker_entry_delete, name='worker_entry_delete'),


    # User Profile Configuration
    path('dashboard/profile/', views.profile_edit, name='profile_edit'),
    
    # Branding Settings & Backups Overview
    path('dashboard/settings/', views.settings_edit, name='settings_edit'),
    
    # Operation Audit Logs
    path('dashboard/logs/', views.activity_logs, name='activity_logs'),
    
    # Report Exporting Downloads
    path('dashboard/reports/excel/', views.export_excel, name='export_excel'),
    path('dashboard/reports/pdf/', views.export_pdf, name='export_pdf'),
    
    # Database Backups Management URLs
    path('dashboard/backup/create/', views.backup_create, name='backup_create'),
    path('dashboard/backup/restore/', views.backup_restore, name='backup_restore'),
    path('dashboard/backup/download/<str:filename>/', views.backup_download, name='backup_download'),
    
    # Master Security PIN Verification & PWA Mobile App URLs
    path('dashboard/verify-pin/', views.verify_security_pin, name='verify_security_pin'),
    path('manifest.json', views.pwa_manifest, name='pwa_manifest'),
    path('sw.js', views.pwa_serviceworker, name='pwa_serviceworker'),
]
