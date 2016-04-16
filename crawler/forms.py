from django.forms import ModelForm, Textarea
from crawler.models import Source

class SourceForm(ModelForm):
    class Meta:
        model = Source
        fields = ['name', 'script']
        widgets = {
            'script': Textarea(attrs={'cols': 80, 'rows': 40}),
        }
