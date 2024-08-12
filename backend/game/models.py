from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    score = models.IntegerField()
    time = models.IntegerField()  # waktu dalam detik
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - Score: {self.score}"