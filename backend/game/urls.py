from django.urls import path
from .views import PlayerListCreate

urlpatterns = [
    path('players/', PlayerListCreate.as_view(), name='player-list-create'),
]