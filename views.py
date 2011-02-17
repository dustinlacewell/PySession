from django.views.generic.simple import redirect_to
from django.template import RequestContext
from django.shortcuts import render_to_response

from pysession.settings import *
from irc.models import Configuration
from snippits.models import Snippit

def index(request):
    conf = Configuration.get()
    snippits = list(Snippit.objects.all().order_by('-timestamp'))[:10]
    return render_to_response('index.html', {
            'IRC_NETWORK': IRC_NETWORK,
            'IRC_CHANNEL': conf.channel,
            'IRC_NICKNAME': IRC_NICKNAME,
            'snippits': snippits,
            }, context_instance=RequestContext(request))
