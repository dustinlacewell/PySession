from django import forms

from snippits.models import Snippit

class PasteForm(forms.ModelForm):
    class Meta:
	model = Snippit
	fields = ('code', 'highlight')
