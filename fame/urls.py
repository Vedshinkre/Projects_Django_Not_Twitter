from django.urls import path

from fame.views.html import bullshitters_view, experts_view, fame_list
from fame.views.rest import ExpertiseAreasApiView, FameUsersApiView, FameListApiView
app_name = "fame"
  
urlpatterns = [
    path(
       "api/expertise_areas", ExpertiseAreasApiView.as_view(), name="expertise_areas"
    ),
    path("api/users", FameUsersApiView.as_view(), name="fame_users"),
    path("api/fame", FameListApiView.as_view(), name="fame_fulllist"),
    path("html/fame", fame_list, name="fame_list"),
    path("html/experts", experts_view, name='experts'),
    path("html/bullshitters", bullshitters_view, name='bullshitters'),
]
