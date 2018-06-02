from django import forms
from .models import Container, Equipment, Equipment_sizename, Action, Action_type
from .my_defs import tree_parse
from django.utils import timezone

class In_container_choicefield(forms.ChoiceField):
    # Класс для проверки на зацикленность поля in_container_id объектов Container
    def to_python(self, value):
        # Return an empty list if no input was given.
        if not value:
            return []
        return int(value)

    def validate(self, value):
        # Use the parent's handling of required fields, etc.
        super(In_container_choicefield, self).validate(value)

        saved_list=[]
        recycle_flag=True
        checked_pk=value

        while recycle_flag == True:
            recycle_flag = False
            if checked_pk in saved_list:
                raise forms.ValidationError("Нельзя положить контейнер сам в себя")
            saved_list.append(checked_pk)
            checked_container = Container.objects.get(pk=checked_pk)
            if checked_container.in_container_id:
                recycle_flag = True
                checked_pk = checked_container.in_container_id

class ContainerForm(forms.ModelForm):

    #in_container_id = forms.ChoiceField()
    in_container_id = In_container_choicefield()

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        super(ContainerForm, self).__init__(*args, **kwargs)
        self.fields['in_container_id'].choices=tree_parse(0, 'choice', user)

    class Meta:
        model = Container
        fields = ('title', 'description', 'in_container_id')

class EquipmentForm(forms.Form):

    sizename = forms.ModelChoiceField(queryset=Equipment_sizename.objects.filter(owner=0), empty_label=None, required=True)
    serial_number = forms.CharField(max_length=50, required=False)
    registration_number = forms.CharField(max_length=50, required=False)
    in_container_id = forms.ChoiceField(required=True)

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        super(EquipmentForm, self).__init__(*args, **kwargs)
        self.fields['in_container_id'].choices=tree_parse(0, 'choice', user, False)
        self.fields['sizename'].queryset=Equipment_sizename.objects.filter(owner=user).order_by('title')

class SizenameForm(forms.ModelForm):
    class Meta:
        model = Equipment_sizename
        fields = ('title', 'manufacturer', 'supply_provider')

class ActionForm(forms.Form):

    type = forms.ModelChoiceField(queryset=Action_type.objects.all(), empty_label=None, required=True)
    description = forms.CharField(max_length=2000, required=False, widget=forms.Textarea)
    action_start_date = forms.DateTimeField(initial=timezone.now(), required=True)
    action_end_date = forms.DateTimeField(required=False)
    scheduled = forms.BooleanField(required=False)
    used_in_equipment = forms.ModelChoiceField(queryset=Equipment.objects.filter(owner=0), empty_label=None, required=True)

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        super(ActionForm, self).__init__(*args, **kwargs)
        self.fields['used_in_equipment'].queryset=Equipment.objects.filter(owner=user).order_by('created_date')
