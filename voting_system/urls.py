from django.urls import path
from .views import *

urlpatterns = [
    path('post-votes/', PostVote.as_view(), name="post-votes"),
    path('get-votes/<votes_id>/', GetVotes.as_view(), name="get-votes"),

]
