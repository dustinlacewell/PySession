
import os, sys, datetime

sys.path.append('.')

# Setup up django environment
from django.core.management import setup_environ
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "../.."))
os.chdir(os.path.join(PROJECT_ROOT, ".."))
from pysession import settings
setup_environ(settings)

from twisted.application import service
from lib import engine, irc, web

from irc.models import Configuration

application = service.Application("Session")
eng = engine.EngineClass(application)
eng.add_service(irc.IRCService )
# eng.add_service(web.WebHistoryService)
