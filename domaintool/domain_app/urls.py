from django.urls import path
from . import views
from .views import DomainUpdateView, MyRestrictedView

urlpatterns = [
    path("", views.index, name="index"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("signin/", views.signin, name="signin"),
    path("logout/", views.signout, name="signout"),
    path("delete_company/<int:company_id>", views.company_delete, name="company_delete"),
    path("manage_companies/add_company", views.company_list, name="companies"),
    path("manage_companies/edit_company/<int:id>/", views.company_list, name="company_update"),
    path("manage_users/", views.list_users, name="users"),
    path("manage_companies/", views.companies, name="lists"),
    path("manage_domains/", views.domain, name="domain"),
    path("manage_domains/add_domain/",views.domain_list, name="domain_update"),
    path('lookup/', views.lookup, name='lookup'),
    path("domain_status/", views.domain_status, name='domain_status'),
    path('api/domain-update/<str:domain_name>/', DomainUpdateView.as_view(), name='domain-api'),
    path("delete_domain/<int:domain_id>", views.domain_delete, name="domain_delete"),
    path('manage_users/add_user/', views.add_user, name='add_user'),
    path("manage_users/edit_user/<int:user_id>/", views.add_user, name="user_update"),
    path('inactive_account/', MyRestrictedView.as_view(), name='inactive_account'),
]
