from django.urls import path
from . import views
app_name = 'core'
urlpatterns = [
    path('', views.LandingView.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Unified dashboard for all users
    path('dashboard/', views.dashboard, name='dashboard'),

    # User management (admin only)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/add/', views.UserCreateView.as_view(), name='user_add'),
    path('users/edit/<int:pk>/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/delete/<int:pk>/', views.UserDeleteView.as_view(), name='user_delete'),
    path('roles/', views.RoleListView.as_view(), name='role_list'),
    path('roles/add/', views.RoleCreateView.as_view(), name='role_add'),
    path('roles/edit/<int:pk>/', views.RoleUpdateView.as_view(), name='role_edit'),
    path('roles/delete/<int:pk>/', views.RoleDeleteView.as_view(), name='role_delete'),
    path('permissions/', views.PermissionListView.as_view(), name='permission_list'),
    path('permissions/add/', views.PermissionCreateView.as_view(), name='permission_add'),
    path('permissions/edit/<int:pk>/', views.PermissionUpdateView.as_view(), name='permission_edit'),
    path('permissions/delete/<int:pk>/', views.PermissionDeleteView.as_view(), name='permission_delete'),

    # Audit logs (admin only)
    path('audit-logs/', views.AuditLogListView.as_view(), name='auditlog_list'),
    path('audit-reports/', views.AuditReportListView.as_view(), name='auditreport_list'),
    path('audit-reports/add/', views.AuditReportCreateView.as_view(), name='auditreport_add'),
    path('audit-reports/<int:pk>/', views.AuditReportDetailView.as_view(), name='auditreport_detail'),
]
