from twisted.application import service, internet
from twisted.words.protocols.irc import IRCClient, DccChat
from twisted.internet import reactor, protocol
from twisted.python.log import msg as log, err

import chardet

from lib import db, event, engine

from pysession.settings import *

class IRCBot(IRCClient):
    admins = set()
    ignore = ['NickServ', 'ChanServ']
    prefixes = ['>>>', '...']
    kickcounts = {}
    # Unicode IO Conversations
    def sendLine(self, line):
        IRCClient.sendLine(self, str(line))
        
    def dataReceived(self, data):
        encoding = chardet.detect(data)['encoding']
        udata = data.decode(encoding)
        IRCClient.dataReceived(self, udata)
        
    def handleCommand(self, command, prefix, params):
        print command, prefix, params, "KNO"
        IRCClient.handleCommand(self, command, prefix, params)
        
    # def irc_unknown(self, prefix, command, params):
    #     print prefix, command, params, 'UNKN'
    #     IRCClient.irc_unknown(self, prefix, command, params)
        
    # def irc_RPL_WHOISUSER(self, prefix, params):
    #     print "WHOIS INFORMATION", params
    #     nickname = params[1].strip("~")
    #     if self.engine.is_admin(nickname):
    #         print nickname, 'is authed.'
    #         self.admins.add(nickname)
    #     elif len(self.engine.admins()) == 0:
    #         self.admins.add(nickname)
    #         self.engine.make_admin(nickname)
    #         print nickname, 'is authed.'
        
    # Initialization
    def connectionMade(self):
        IRCClient.connectionMade(self)
    
    # Perform here
    def signedOn(self):
        self.factory.signed_on = True
        # Identify 
        self.msg('Chanserv', 'identify %s %s' % (self.help_channel,
                                                 self.channel_pass))
        # Join
        self.join(self.help_channel)
        
    def joined(self, channel):
        log('Joined %s' % channel)
        self.engine.set_channel(channel)
        
    def left(self, channel):
        log('Parted %s' % channel)

    def kickedFrom(self, channel, kicker, message):
        if channel in self.kickcounts:
            self.kickcounts[channel] += 1
        else:
            self.kickcounts[channel] = 1
        if self.kickcounts[channel] < self.kicklimit:
            self.join(channel)
    
    def whois(self, nick):
        print "Whoising %s" % nick
        self.sendLine('WHOIS %s' % nick)
    
    def irc_330(self, prefix, params):
        if 'is logged in as' in params:
            if self.engine.is_admin(params[1]):
                print params[1], 'is authed!'
                self.admins.add(params[1])
            elif len(self.engine.admins()) == 0:
                self.admins.add(params[1])
                self.engine.make_admin(params[1])
                print params[1], 'is authed!'
            
    def irc_320(self, prefix, params):
        return irc_330(prefix, params)
    
    #===========================================================================
    # def irc_311(self, prefix, params):
    #    print "WHOIS INFORMATION", params
    #    nickname = params[0].strip("~")
    #    if self.engine.is_admin(nickname):
    #        print nickname, 'is authed.'
    #        self.admins.add(nickname)
    #    elif len(self.engine.admins()) == 0:
    #        self.admins.add(nickname)
    #        self.engine.make_admin(nickname)
    #        print nickname, 'is authed.'
    #===========================================================================

    def userRenamed(self, oldname, newname):
        if oldname in self.admins:
            self.admins.remove(oldname)
        self.whois(newname)

    def userLeft(self, nick, channel):
        if nick in self.admins:
            self.admins.remove(nick)

    def userJoined(self, user, channel):
        user = user.split('!', 1)[0]
        if self.engine.is_admin(user):
            self.whois(user)

    def irc_RPL_NAMREPLY(self, prefix, params):
        for nick in params[3].split(' '):
            for pre in ['@', '+', '!', 'v']:
                nick = nick.replace(pre, '')
            if self.engine.is_admin(nick):
                self.whois(nick)

    def handleCommand(self, comm, prefix, params):
        IRCClient.handleCommand(self, comm, prefix, params)
    
    def privmsg(self, user, channel, message):
        """Called when I have a message from a user to me or a channel.
        """
        # Only actually private messages
        user = user.split('!', 1)[0]
        if (channel != self.help_channel
            or user in self.ignore
            or not user.strip()):
            return
        if message.startswith('.ident'):
            self.whois(user)
        # Code dispatching
        if user in self.admins:
            if message[:3] in self.prefixes: 
                self.engine.code(user, message[3:])
            # Built-In Commands
            elif message[0] == '.':
                parts = message[1:].split()
                command, args = parts[0], parts[1:]
                # Public commands
                # echo #
                if command == "echo":
                    self.msg(self.help_channel, ' '.join(args))
                # mktmp user1 [user2 ...] #
                if command == "redent":
                    self.engine.code(user, " ".join(args))
                    self.engine.code(user, "\n")
                if command == "mktmp":
                    if len(args) == 0:
                        self.msg(user, "Usage:")
                        self.msg(user, "mktmp <user1> [<user2> ...]")
                    else:
                        map(self.engine.temp_admin, args)
                # mkadmin user1 [user2 ...] #
                if command == "mkadmin":
                    if len(args) == 0:
                        self.msg(user, "Usage:")
                        self.msg(user, "mkadmin <user1> [<user2> ...]")
                    else:
                        map(self.engine.make_admin, args)
                # rmadmin user1 [user2 ...] #
                if command == "rmadmin":
                    if len(args) == 0:
                        self.msg(user, "Usage:")
                        self.msg(user, "rmadmin <user1> [<user2> ...]")
                    else:
                        map(self.engine.remove_admin, args)
                # reset #
                if command == "reset":
                    self.engine.reset()
                if command == "timeout":
                    try:
                        if len(args) == 0: raise Exception
                        timeout = int(args[0])
                        self.engine.set_timeout(timeout)
                    except:
                        self.msg(user, "Usage:")
                        self.msg(user, "timeout <seconds>")
                if command == "move":
                    if len(args) == 0:
                        self.msg(user, "Usage:")
                        self.msg(user, "move <newchannel>")
                    else:
                        self.leave(self.help_channel)
                        self.engine.set_channel(args[0])
                        self.help_channel = args[0]
                        self.join(self.help_channel)
                if command == "home":
                    self.leave(self.help_channel)
                    self.engine.set_channel(IRC_CHANNEL)
                    self.help_channel = IRC_CHANNEL
                    self.join(self.help_channel)
                if command == "admins":
                    self.msg(self.help_channel, "[%s]" % ", ".join(self.engine.admins()))
        
    def dccDoChat(self, user, channel, address, port, data):
        log('Dcc Chat Request: %s, %s, %s' % (user, address, port))
        log('Dcc Chat Request Data: %s' % data)
        
class IRCBotFactory(protocol.ReconnectingClientFactory):
    protocol = IRCBot
    p = None
    signed_on = False
    
    def __init__(self, engine, ports):
        self._engine = engine
        self.ports = ports
        
    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        p.engine = self._engine
        p.nickname = IRC_NICKNAME
        p.password = IRC_PASSWORD
        p.help_channel = IRC_CHANNEL
        p.channel_pass = IRC_CHANPASS
        self.p = p
        return self.p
        
    def stopFactory(self):
        self.signed_on = False
    
    def next_port(self):
        last = self.ports.pop(0)
        self.ports.append(last)
        return self.ports[0]
    
    def clientConnectionFailed(self, connector, reason):
        self.p = None 
        connector.port = self.next_port()
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)
        
    # ENGINE EVENT HANDLERS # 
    
    def on_quit(self, reason):
        reason = reason
        self.p.quit(message = reason)
        self.stopTrying()
    
    def on_admin_notice(self, message):
        message = message
        p = self.p
        p.msg(p.help_channel, message)
        for admin in self._engine.admins():
            p.msg(admin, message)
            
    def on_outgoing_msg(self, dest, message):
        self.p.msg(dest, message)
            

class IRCService(internet.TCPClient):
    service_name = 'irc'

    def __init__(self, eng):
        # TODO : Initialize with configuration dictionary
        network = IRC_NETWORK
        ports = list(IRC_PORTS)
        self.engine = eng
        self.factory = IRCBotFactory(eng, ports)
        internet.TCPClient.__init__(self, network, ports[0], self.factory)
    
    def get_signal_matrix(self):
        return {
            'quit' : self.factory.on_quit,
            'admin_notice' : self.factory.on_admin_notice,
            'outgoing_msg' : self.factory.on_outgoing_msg
            }
    
    def startService(self):
        self.factory.resetDelay()
        internet.TCPClient.startService(self)

    def stopService(self):
        self.factory.stopTrying()
        internet.TCPClient.stopService(self)
        
    # Informational Methods #
    def is_connected(self):
        return self.factory.signed_on 

if __name__ == '__main__':
    f = IRCBotFactory()
    reactor.connectTCP('irc.freenode.net', 8000, f)
    reactor.run()
