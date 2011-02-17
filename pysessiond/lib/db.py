from zope.interface import Interface, implements
from axiom.upgrade import registerUpgrader
from axiom.attributes import AND, OR
from axiom import item, attributes, sequence
from epsilon.extime import Time


# Service Configuration Items
config_database = u"config.axiom"
class IRCConfig( item.Item ):
    typeName = 'IRCConfig'
    schemaVersion = 1

    network = attributes.text(default = u'irc.freenode.org')
    port = attributes.text(default = u'6667')
    
    helpchannel = attributes.text(default = u'#chipy')
    channelpass = attributes.text(default = u'mdcclxxvi')
    
    nickname = attributes.text(default = u'TheSession')
    nickpass = attributes.text(default = u'mdcclxxvi')

class WebConfig( item.Item ):
    typeName = "WebConfig"
    schemaVersion = 1
    listenport = attributes.integer(default = 8080)
    
class User( item.Item ):
    typeName = 'User'
    schemaVersion = 1
    
    nickname = attributes.text(allowNone=False)
    dob = attributes.timestamp(allowNone=False)
    admin = attributes.boolean(default=False)
    
    def __repr__(self):
        return self.nickname

class Record( item.Item ):
    typeName = 'Record'
    schemaVersion = 1

    year = attributes.integer(allowNone=False)
    month = attributes.integer(allowNone=False)
    day = attributes.integer(allowNone=False)
    hour = attributes.integer(allowNone=False)
    minute = attributes.integer(allowNone=False)
    
    inlines = attributes.text(allowNone=False)
    outlines = attributes.text(allowNone=False)
