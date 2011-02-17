from django.contrib.admin.sites import AdminSite
from django.utils.safestring import mark_safe
from django import http, template
from django.shortcuts import render_to_response
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy, ugettext as _

class PySessionAdmin(AdminSite):
    index_template = "admin/index.html"

    def __init__(self,name=None, app_name=None):
	super(PySessionAdmin, self).__init__()        

    def index(self, request, extra_context=None):
        """
        Displays the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_dict = {}
        user = request.user
        for model, model_admin in self._registry.items():
            app_label = model._meta.app_label
            has_module_perms = user.has_module_perms(app_label)

            if has_module_perms:
                perms = model_admin.get_model_perms(request)

                # Check whether user has any perm for this module.
                # If so, add the module to the model_list.
                if True in perms.values():
                    model_dict = {
                        'name': capfirst(model._meta.verbose_name_plural),
                        'admin_url': mark_safe('%s/%s/' % (app_label, model.__name__.lower())),
                        'perms': perms,
                    }
                    if app_label in app_dict:
                        app_dict[app_label]['models'].append(model_dict)
                    else:
                        app_dict[app_label] = {
                            'name': app_label.title(),
                            'app_url': app_label + '/',
                            'has_module_perms': has_module_perms,
                            'models': [model_dict],
                        }

        # Sort the apps alphabetically.
        app_list = app_dict.values()
        app_list.sort(key=lambda x: x['name'])

        # Sort the models alphabetically within each app.
        for app in app_list:
            app['models'].sort(key=lambda x: x['name'])

        context = {
            'title': _('Select object type:'),
            'app_list': app_list,
            'root_path': self.root_path,
        }
        context.update(extra_context or {})
        context_instance = template.RequestContext(request, current_app=self.name)
        return render_to_response(self.index_template or 'admin/index.html', context,
            context_instance=context_instance
        )

site = PySessionAdmin()

# Default registers
# ------------------------------------------------------------------------------
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

site.register(User, UserAdmin)
site.register(Group, GroupAdmin)

# from irc.models import Configuration
# from irc.admin import ConfigurationAdmin
# site.register(Configuration, ConfigurationAdmin)

from snippits.models import Snippit
from snippits.admin import SnippitAdmin
site.register(Snippit, SnippitAdmin)


