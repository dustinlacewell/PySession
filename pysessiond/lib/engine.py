from cStringIO import StringIO
from code import InteractiveConsole
import sys, traceback

from twisted.python.log import msg as log, err
from twisted.application.service import IService, IServiceCollection
from twisted.internet import reactor

from redent import redent

from lib.event import Signal

from django.contrib.auth.models import User, Group
from pysession.apps.irc.models import Configuration
from pysession.apps.snippits.models import Snippit
from pysession.settings import *

class IRCConsole(InteractiveConsole):
    """
    An InteractiveConsole that temporarilly redirects sys.stdout to an internal
    buffer. When an entire statement has been processed and executed the
    internal buffer is flushed. Upon flushing the buffer it's contents are
    recorded internally by datetime and made available via the webservice.

    Depending on the size of the buffer at the time of flushing, the entire or
    clipped output is also relayed to the IRC channel.
    """
    def __init__(self, engine):
        self.engine = engine
        self._stdout = sys.stdout
        self._ibuffer = [] #Parts of a statement
        self._obuffer = [] #Lines of output
        self.user_tracker = {}
        InteractiveConsole.__init__(self, {'engine': self.engine})

    def inc_tracker(self, nickname):
        self.user_tracker[nickname] = self.user_tracker.get(nickname, 0) + 1

    def inc_winner(self):
        highest = 0
        user = ''
        for u in self.user_tracker:
            if self.user_tracker[u] > highest:
                highest = self.user_tracker[u]
                user = u
        self.user_tracker = {}
        return user
        
    def write(self, data):
        "Makes this file-like. Doesn't write empty strings."
        lines = data.split('\n')
        for line in lines:
            cline = line.strip()
            if cline: 
                self._obuffer.append(line)

    def showsyntaxerror(self, filename=None):
        """Display the syntax error that just occurred.

        This doesn't display a stack trace because there isn't one.

        If a filename is given, it is stuffed in the exception instead
        of what was there before (because Python's parser always uses
        "<string>" when reading from a string).

        The output is written by self.write(), below.

        """
        type, value, sys.last_traceback = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        if filename and type is SyntaxError:
            # Work hard to stuff the correct filename in the exception
            try:
                msg, (dummy_filename, lineno, offset, line) = value
            except:
                # Not the format we expect; leave it alone
                pass
            else:
                # Stuff in the right filename
                value = SyntaxError(msg, (filename, lineno, offset, line))
                sys.last_value = value
        list = traceback.format_exception_only(type, value)
        list = list[2:]
        map(self.write, list)

    def showtraceback(self):
        """Display the exception that just occurred.

        We remove the first stack item because it is our own code.

        The output is written by self.write(), below.

        """
        try:
            type, value, tb = sys.exc_info()
            sys.last_type = type
            sys.last_value = value
            sys.last_traceback = tb
            tblist = traceback.extract_tb(tb)
            del tblist[:1]
            list = traceback.format_list(tblist)
            if list:
                list.insert(0, "Traceback (most recent call last):\n")
            list[len(list):] = traceback.format_exception_only(type, value)
        finally:
            tblist = tb = None
        list = list[2:]
        map(self.write, list)



    def flush(self):
        "Flushes internal buffer to web and irc services."
        # Timestamp
        winner = self.inc_winner()
        snippit = Snippit()
        snippit.channel = self.engine.current_channel
        snippit.nickname = winner
        snippit.code = redent(str("\n".join(self._ibuffer)))
        snippit.result = unicode("\n".join(self._obuffer))
        snippit.save()

        # Less than four lines
        if len(self._obuffer) <= 4:
            for line in self._obuffer:
                # Return result to channel
                self.engine.signals['outgoing_msg'].emit(
                    self.engine.ircconf.channel,
                    line
                )
        else:
            # Return perma-link to output
            self.engine.signals['outgoing_msg'].emit(
                self.engine.ircconf.channel,
                # TODO: Change with config.
                'Output too long : http://%s/%d' % (SITE_DOMAIN, snippit.pk)
            )
        self._ibuffer = []
        self._obuffer = []
    
    def writelines(self, lines):
        "Makes this file-like."
        for l in lines:
            cl = l.strip()
            if cl:
                self.write(l)
        
    def push(self, nickname, line):
        "Redirects stdout upon push."
        self.inc_tracker(nickname)
        sys.stdout = self
        self._ibuffer.append(line)
        if not InteractiveConsole.push(self, line):
            self.flush()
        sys.stdout = self._stdout

class EngineClass(object):
    signals = {}
    def __init__(self, application):
        # Application Setup #
        self.application = application
        # Service References #
        self._services = {}
        # Configuration persistance #
        self.ircconf = Configuration.get()
        # Event signals #
        self.signals['quit'] = Signal() # (reason)
        self.signals['admin_notice'] = Signal() # (message)
        self.signals['outgoing_msg'] = Signal() # (destination, message)
        # Interactive Console
        self.ic = IRCConsole(self)
        # Default timeout
        self.timeout = 60
        # Set channel home
        self.current_channel = IRC_CHANNEL
        
    def reset(self):
        del self.ic
        self.ic = IRCConsole(self)
        
    def _register_listeners(self, service):
        '''
        Registers all event handlers for a service.
        '''
        signalmatrix = service.get_signal_matrix()
        for signal, handler in signalmatrix.items():
            try:
                #Register the service's  handler to the event system's signal
                self.signals[signal].register(handler)
            except KeyError:
                log("couldnt find a '%s' signal for registration" % signal)
              
    def _unregister_listeners(self, service):
        '''
        Unregisters all event handlers for a service.
        '''
        signalmatrix = service.get_signal_matrix()
        for signal, handler in signalmatrix.items():
            try:
                self.signals[signal].unregister(handler)
            except KeyError:
                log("couln't find a '%s' signal to unregister" % signal)
        
    def add_service(self, svc_cls):
        name = svc_cls.service_name
        log('Starting ' + name)
        service = svc_cls(self)
        self._register_listeners(service)
        log(name + ' started.')
        service.setName(name)
        service.setServiceParent(self.application)
        
    def start_service(self, name):
        svc = self.application.getServiceName(name)
        svc.startService()
        svc._register_listeners(svc)
        
    def stop_service(self, name):
        svc = self.application.getServiceNamed(name)
        svc.stopService()
        svc._unregister_listeners(svc)
        
    def get_service(self, name):
        try:
            serv = IServiceCollection(self.application).getServiceNamed(name)
        except KeyError:
            serv = None
        return serv

    def is_svc_running(self, name):
        svc = self.get_service(name)
        if svc:
            return IService(svc).running
    
    #  Code utilities
    def code(self, nickname, code):
        "Utility function to push code segments."
        self.ic.push(nickname, code)
    
    #  User Queries #
    def admins(self):
        """ Returns a list of admin nicks """
        return [u.username for u in User.objects.filter(groups__name="Moderator")]
    
    def is_admin(self, nickname):
        """ Return whether nickname is an admin """
        return nickname in self.admins()
        
    def set_channel(self, channel):
        self.ircconf.channel = channel
        self.ircconf.save()
        print "**********", self.ircconf.channel

    def get_user(self, nickname):
        user, new = User.objects.get_or_create(username=nickname)
        if new:
            user.save()
            Group.objects.get(name="Moderator").user_set.add(user)
            user.password = "changeme"
            user.save()
        return user
            
        
    def make_admin(self, nickname):
        u = self.get_user(nickname)
        u.is_staff = True
        u.save()
        g = Group.objects.get(name="Moderator").user_set.add(u)
        
    def remove_admin(self, nickname):
        u = self.get_user(nickname)
        u.is_staff = False
        u.save()
        Group.objects.get(name="Moderator").user_set.remove(u)
        
    def temp_admin(self, nickname):        
        self.make_admin(nickname)
        reactor.callLater(self.timeout, self.remove_admin, nickname)
        
    def set_timeout(self, seconds):
        self.timeout = seconds
        
