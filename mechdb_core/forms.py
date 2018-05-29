from django import forms

from .models import Container

class ContainerForm(forms.ModelForm):

    class Meta:
        model = Container
        fields = ('title', 'descripton', 'descripton', 'is_repair_organization', 'in_container_id')
