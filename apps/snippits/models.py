from django.db import models

class Snippit(models.Model):
    channel = models.CharField(max_length=32, blank=True) # TODO: validate channel hash
    nickname = models.CharField(max_length=16, blank=True)
    
    code = models.TextField()
    result = models.TextField(blank=True)

    highlight = models.BooleanField(default=True)

    timestamp = models.DateTimeField(auto_now_add=True)


    

