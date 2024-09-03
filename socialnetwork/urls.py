from django.urls import path

from socialnetwork.views.html import timeline
from socialnetwork.views.rest import PostsListApiView
from .api import experts, bullshitters, follow_user, unfollow_user

app_name = "socialnetwork"

urlpatterns = [
    path("api/posts", PostsListApiView.as_view(), name="posts_fulllist"),
    path("html/timeline", timeline, name="timeline"),
    path("api/experts",experts,name='expert'),
    path("api/bullshiters",bullshitters,name='expert'),
    path("api/follow/<int:user_id>/", follow_user, name='follow_user'),
    path("api/unfollow/<int:user_id>/", unfollow_user, name='unfollow_user'),
]

