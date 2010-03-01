from code import InteractiveConsole
import sys

from axiom.store import Store
from axiom.attributes import AND, OR
from twisted.python.log import msg as log, err
from twisted.application.service import IService, IServiceCollection
from twisted.internet import reactor
from epsilon.extime import Time

from lib import db
from lib.event import Signal

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
        InteractiveConsole.__init__(self, {'engine': self.engine})
        
    def write(self, data):
        "Makes this file-like. Doesn't write empty strings."
        lines = data.split('\n')
        for line in lines:
            if line != '\n':
                self._obuffer.append(line)

    def flush(self):
        "Flushes internal buffer to web and irc services."
        # Timestamp
        dob = Time().asStructTime()[:5]
        newrec = db.Record(store=self.engine.database,
                year = dob[0],
                month = dob[1],
                day = dob[2],
                hour = dob[3],
                minute = dob[4],
                inlines = unicode("\n".join(self._ibuffer)),
                outlines = unicode("\n".join(self._obuffer))
                )
        # Less than four lines
        if len(self._obuffer) <= 4:
            for line in self._obuffer:
                # Return result to channel
                self.engine.signals['outgoing_msg'].emit(
                    self.engine.ircconf.helpchannel,
                    line
                )
        else:
            # Return perma-link to output
            self.engine.signals['outgoing_msg'].emit(
                self.engine.ircconf.helpchannel,
                # TODO: Change with config.
                'Output too long : http://ldlework.com:8080/#%s' % newrec.storeID
            )
        self._ibuffer = []
        self._obuffer = []
    
    def writelines(self, lines):
        "Makes this file-like."
        for l in lines:
            if cl != '\n':
                self.write(cl)
        
    def push(self, line):
        "Redirects stdout upon push."
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
        self.database = Store(db.config_database)
        self.ircconf = self.database.findOrCreate(db.IRCConfig)
        self.webconf = self.database.findOrCreate(db.WebConfig)
        # Event signals #
        self.signals['quit'] = Signal() # (reason)
        self.signals['admin_notice'] = Signal() # (message)
        self.signals['outgoing_msg'] = Signal() # (destination, message)
        # Interactive Console
        self.ic = IRCConsole(self)
        
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
    def code(self, code):
        "Utility function to push code segments."
        self.ic.push(code)
    
    #  User Queries #
    def admins(self):
        """ Returns a list of admin nicks """
        q = self.database.query(db.User,
                db.User.admin == True
            )
        return list(q)
    
    def is_admin(self, nickname):
        """ Return whether nickname is an admin """
        q = self.database.query(db.User,
                AND (
                    db.User.nickname == nickname,
                    db.User.admin == True
                )
            )
        return bool(list(q))
        
    def set_channel(self, channel):
        self.ircconf.helpchannel = channel
        
    def get_user(self, nickname):
        q = list(self.database.query(db.User,
            db.User.nickname == nickname))
        if len(q) == 0:
            user = db.User(store=self.database,
                nickname = nickname,
                dob = Time())
        else:
            user = q[0]
            
        return user
            
        
    def make_admin(self, nickname):
        u = self.get_user(nickname)
        u.admin = True
        
    def remove_admin(self, nickname):
        u = self.get_user(nickname)
        u.admin = False
        
    def temp_admin(self, nickname):        
        self.make_admin(nickname)
        reactor.callLater(self.timeout, self.remove_admin, nickname)
        
    def set_timeout(self, seconds):
        self.timeout = seconds
        
