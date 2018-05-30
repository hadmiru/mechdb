from django import forms
from .models import Container
from .my_defs import tree_parse

class ContainerForm(forms.ModelForm):

    in_container_id = forms.ChoiceField()
    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        super(ContainerForm, self).__init__(*args, **kwargs)
        self.fields['in_container_id'].choices=tree_parse(0, 'choice', user)

    class Meta:
        model = Container
        fields = ('title', 'description', 'in_container_id')
