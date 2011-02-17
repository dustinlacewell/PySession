from django import template
register = template.Library()

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from pygments.styles import get_style_by_name

# Python Markdown (dropped in my project directory)
#from codebase.markdown import markdown

# BeautifulSoup: http://www.crummy.com/software/BeautifulSoup/
#from codebase.BeautifulSoup import BeautifulSoup

@register.filter
def render(content, safe="unsafe"):
    """Render this content for display."""
    style = get_style_by_name("emacs")
    lexer = PythonLexer(stripnl=True, tabsize=4, encoding='UTF-8')
    formatter = HtmlFormatter(cssclass='syntax', style=style)
    return highlight(str(content), lexer, formatter)
