from datetime import datetime
from itertools import chain

from zope.interface import implements

from twisted.internet import defer
from twisted.application import internet, service
from twisted.python import failure, log
from twisted.cred import portal, checkers, credentials, error
from twisted.web import microdom

from nevow import inevow, guard, appserver, loaders, rend, static, url, util
from nevow import tags as T

from axiom.attributes import AND, boolean, timestamp, integer, text

from epsilon.extime import Time

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from lib import engine, db, irc


class RecordPage(rend.Page):
    '''
    RecordPage is a page class that consumes all url segments using each
    part to generate a date. All previous usage of PySession is available
    by date.
    '''
    addSlash = True

    child_css = static.File(util.resource_filename('htdocs', 'index.css'))
    child_syntaxcss = static.File(util.resource_filename('htdocs', 'syntax.css'))

    def __init__(self, eng, date=None):
        super(RecordPage, self).__init__()
        self.engine = eng
        self.date = Time().oneDay()

    def render_record(self, record):
        t = (record.year, record.month, record.day, record.hour, record.minute)
        t = Time.fromStructTime([part for part in t if part])
        t = t.asISO8601TimeAndDate().replace('T', ' ')
        t = t.replace(':00+00:00','')
    
        lexer = PythonLexer()
        formatter = HtmlFormatter(linenos=True)
        lit = highlight(record.inlines, lexer, formatter)
        parsed = microdom.parseString(lit, beExtremelyLenient=True)
        
        
        return T.div(_class='record')[
            T.pre(_class='header')[t ],
            T.xml(parsed),
            T.pre(_class='outlines')[ record.outlines ],
        ]
            
    def render_results(self, ctx, data):
        criteria = []
        if self.date[0]: criteria.append(db.Record.year == self.date[0])
        if self.date[1]: criteria.append(db.Record.month == self.date[1])
        if self.date[2]: criteria.append(db.Record.day == self.date[2])
        if self.date[3]: criteria.append(db.Record.hour == self.date[3])
        if self.date[4]: criteria.append(db.Record.minute == self.date[4])
        q = list(self.engine.database.query(
            db.Record,
            AND(*criteria)))
        q.reverse()
        ret = []
        if q:
            for record in q:
                ret.append(self.render_record(record))
            return ret
        else:
            return T.div["No entries on that date."]

    def render_menu(self, ctx, data):
        menu = []
        count = 0
        names = ['Year', 'Month', 'Day', 'Hour', 'Minute']
        for value, name in zip(self.date, names):
            if value:
                backward = self.date[:]
                backward[count] = value - 1
                backward = [str(num) for num in backward if num]
                forward = self.date[:]
                forward[count] = value + 1
                forward = [str(num) for num in forward if num]
                menu.append(T.li[T.a(href='/' + '/'.join(backward))['<<'],
                                     name,
                                     T.a(href='/' + '/'.join(forward))['>>']])
            count += 1
        return menu

    def locateChild(self, ctx, segments):
        if segments[0] == 'css':
            return (self.child_css, ())
        elif segments[0] == 'syntaxcss':
            return (self.child_syntaxcss, ())

        try:
            parts = [int(value) for value in segments if value][:5]
        except ValueError:
            parts = []

        if not parts:
            l = list(Time().oneDay().asStructTime()[:3])
            l = [str(value) for value in l]
            return url.here.click('/' + '/'.join(l)), ()
        else:
            self.date = list(chain(parts, [None]*(5-len(parts))))
        return self, ()

    docFactory = loaders.stan(
        T.html[
            T.head[
                T.title['PySession History'],
                T.link(rel='stylesheet', type='text/css', href='/css'),
                T.link(rel='stylesheet', type='text/css', href='/syntaxcss')
            ],
            T.body[
                T.div(id_='topmenu')[
                    T.ul[
                        T.li[T.a(id_='highlight', href='/')['PySession']],
                        render_menu
                    ]
                ],
                T.div(style='clear:both;'),
                render_results
            ]
        ])

class WebHistoryService(internet.TCPServer):
    service_name = "webhistory"

    def __init__(self, eng):
        listenport = eng.webconf.listenport
        root = RecordPage(eng)
        internet.TCPServer.__init__(self, listenport, appserver.NevowSite(root))

    def get_signal_matrix(self):
        return {}
