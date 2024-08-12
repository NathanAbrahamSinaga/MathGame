from rest_framework import generics
from .models import Player
from .serializers import PlayerSerializer

class PlayerListCreate(generics.ListCreateAPIView):
    queryset = Player.objects.all().order_by('-score')
    serializer_class = PlayerSerializer