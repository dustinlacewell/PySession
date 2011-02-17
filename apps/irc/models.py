from django.db import models
from django.core.exceptions import ValidationError

from pysession.settings import IRC_CHANNEL

def freenode_validator(value):
    if value != "irc.freenode.net":
        raise ValidationError(u"Only 'irc.freenode.net' is supported.")

class Configuration(models.Model):
#    network = models.CharField(max_length=128, default='irc.freenode.net', help_text="only 'irc.freenode.net' is supported for now", validators=[freenode_validator])
#    port = models.PositiveIntegerField(default=6667)

    channel = models.CharField(max_length=32, default=IRC_CHANNEL) # TODO: validate channel hash

#    nickname = models.CharField(max_length=16, help_text="Must be registered with NickServ")
#    password = models.CharField(max_length=32, help_text="NickServ password")

    def save(self):
        self.id=1
        super(Configuration, self).save()

    def delete(self):
        pass
    
    @classmethod
    def get(cls):
        return Configuration.objects.get(pk=1)

