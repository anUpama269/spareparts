from django.urls import path
from . import views
app_name = 'core'
urlpatterns = [
    path('', views.LandingView.as_view(), name='home'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Unified dashboard for all users
    path('dashboard/', views.dashboard, name='dashboard'),

    # User management (admin only)
    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/add/', views.UserCreateView.as_view(), name='user_add'),
    path('users/edit/<int:pk>/', views.UserUpdateView.as_view(), name='user_edit'),
    path('users/delete/<int:pk>/', views.UserDeleteView.as_view(), name='user_delete'),

    # Audit logs (admin only)
    path('audit-logs/', views.AuditLogListView.as_view(), name='auditlog_list'),
]
