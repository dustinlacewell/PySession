import sys
sys.path.append('.')

from twisted.application import service
from lib import engine, irc, web

application = service.Application("Session")
eng = engine.EngineClass(application)
eng.add_service(irc.IRCService )
eng.add_service(web.WebHistoryService)
