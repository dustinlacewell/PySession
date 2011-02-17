from cStringIO import StringIO

from django.views.generic.simple import redirect_to
from django.template import RequestContext
from django.shortcuts import render_to_response

from redent import redent

from snippits.models import Snippit
from snippits.forms import PasteForm

def snippit(request, pk):
    try:
	snip = Snippit.objects.get(pk=pk)
    except:
	return redirect_to(request, "/", False, False)
    
    return render_to_response('snippit.html', {
	    'snippit': snip}, context_instance=RequestContext(request))

def paste(request):
    if request.method == 'POST':
	form = PasteForm(request.POST)
	if form.is_valid():
	    snippit = form.save()
            reindent = request.POST.get('reindent', False)
            print "***", reindent
            if reindent:
                snippit.code = redent(snippit.code)
                snippit.save()
	    pk = snippit.pk
	    return redirect_to(request, "/%d" % pk, False, False)
	else:
	    return render_to_response('paste.html', {
		    'form': form}, context_instance=RequestContext(request))
    else:
	form = PasteForm()
	return render_to_response('paste.html', {
		'form': form}, context_instance=RequestContext(request))
