from django.urls import path
from . import views

urlpatterns = [
    path('launches/', views.LaunchListView.as_view(), name='launch-list'),
    path('launches/<str:launch_id>/', views.LaunchDetailView.as_view(), name='launch-detail'),
    path('statistics/', views.LaunchStatisticsView.as_view(), name='launch-statistics'),
    path('filter/', views.LaunchFilterView.as_view(), name='launch-filter'),
    path('upcoming/', views.UpcomingLaunchesView.as_view(), name='upcoming-launches'),
    path('search/', views.SearchLaunchesView.as_view(), name='search-launches'),
]
