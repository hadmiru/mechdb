from django import forms
from .models import Container, Equipment, Equipment_sizename, Action, Action_type, Spare_part
from .my_defs import tree_parse
from django.utils import timezone
from django.contrib.admin.widgets import AdminDateWidget

class In_container_choicefield(forms.ChoiceField):
    # Класс для проверки на зацикленность поля in_container_id объектов Container
    def to_python(self, value):
        if not value:
            return []
        return int(value)

    def validate(self, value):
        super(In_container_choicefield, self).validate(value)

        saved_list=[]
        recycle_flag=True
        checked_pk=value

        if self.self_pk: #если равен нулю - не добавляем в список и новые конты проскакивают проверку
            saved_list.append(self.self_pk)

        while recycle_flag == True:

            recycle_flag = False
            if checked_pk in saved_list:
                raise forms.ValidationError("Нельзя положить контейнер сам в себя")
            saved_list.append(checked_pk)
            if checked_pk>0:
                checked_container = Container.objects.get(pk=checked_pk)
                if checked_container.in_container:
                    recycle_flag = True
                    checked_pk = checked_container.in_container.pk

class ContainerForm(forms.Form):

    title = forms.CharField(max_length=200, required=True, label='Название')
    description = forms.CharField(max_length=2000, required=False, widget=forms.Textarea, label='Описание')
    is_repair_organization = forms.BooleanField(required=False, label='Ремонтная организация?')
    in_container_id = In_container_choicefield(label='Расположение')

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        self_pk=kwargs.pop('self_pk',None)
        super(ContainerForm, self).__init__(*args, **kwargs)
        self.fields['in_container_id'].choices=tree_parse(0, 'choice', user)
        self.fields['in_container_id'].self_pk=self_pk

class EquipmentForm(forms.Form):

    formtype = forms.CharField(max_length=50, widget=forms.HiddenInput())
    form_completed = forms.BooleanField(initial=True, widget=forms.HiddenInput())

    sizename = forms.ModelChoiceField(queryset=Equipment_sizename.objects.filter(owner=0), empty_label=None, required=True, label='Модель')
    serial_number = forms.CharField(max_length=50, required=False, label='Заводской номер')
    registration_number = forms.CharField(max_length=50, required=False, label='Регистрационный номер')
    in_container_id = forms.ChoiceField(required=False, label='Расположение')
    action_datetime = forms.DateTimeField(initial=timezone.now, required=True, label='Дата перемещения')

    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        formtype=kwargs.pop('formtype',None)
        super(EquipmentForm, self).__init__(*args, **kwargs)
        # Поле in_container_id заполняем деревом, которое строит функция tree_parse
        self.fields['in_container_id'].choices=tree_parse(0, 'choice', user, False)
        # Поле sizename заполняем моделями только для текущего юзверя
        self.fields['sizename'].queryset=Equipment_sizename.objects.filter(owner=user).order_by('title')
        # в зависимости от ситуации в которой используется форма (значение formtype) удаляем ненужные поля, меняем некоторые значения полей:
        if formtype=="new":
            self.label="Создание оборудования"
            self.fields['in_container_id'].required=True
            del self.fields['action_datetime']
        if formtype=="edit":
            self.label="Редактирование оборудования"
            del self.fields['in_container_id']
            del self.fields['action_datetime']
        if formtype=='move':
            self.label="Перемещение оборудования"
            self.fields['in_container_id'].label='Новое местоположение'
            del self.fields['sizename']
            del self.fields['serial_number']
            del self.fields['registration_number']

class SizenameForm(forms.ModelForm):
    class Meta:
        model = Equipment_sizename
        fields = ('title', 'manufacturer', 'supply_provider')

class ActionForm(forms.Form):

    formtype = forms.CharField(max_length=50, widget=forms.HiddenInput())
    form_completed = forms.BooleanField(initial=True, widget=forms.HiddenInput())
    object_pk = forms.IntegerField(required=True, widget=forms.HiddenInput())

    used_in_equipment = forms.ModelChoiceField(queryset=Equipment.objects.filter(owner=0), empty_label=None, required=False, label='Родительское борудование')
    used_in_action = forms.ModelChoiceField(queryset=Action.objects.filter(owner=0), empty_label=None, required=False, label='Родительское воздействие')
    used_in_spare_part = forms.ModelChoiceField(queryset=Spare_part.objects.filter(owner=0), empty_label=None, required=False, label='Родительский ЗИП')
    quantity_delta = forms.FloatField(required=False, label='Количество')
    new_container = forms.ChoiceField(required=False, label='Новое расположение')
    description = forms.CharField(max_length=2000, required=False, widget=forms.Textarea, label='Описание')
    action_start_date = forms.DateTimeField(initial=timezone.now, required=True, label='Начало')
    action_end_date = forms.DateTimeField(required=False, label='Окончание')
    scheduled = forms.BooleanField(required=False, label='Плановое?')


    def __init__(self, *args, **kwargs):
        user=kwargs.pop('user',None)
        formtype=kwargs.pop('formtype',None)
        object=kwargs.pop('object',None)
        super(ActionForm, self).__init__(*args, **kwargs)
        # подставляем значения для конкретного юзверя
        self.fields['used_in_equipment'].queryset=Equipment.objects.filter(owner=user).order_by('created_date')
        self.fields['used_in_action'].queryset=Action.objects.filter(owner=user).order_by('action_start_date')
        self.fields['used_in_spare_part'].queryset=Spare_part.objects.filter(owner=user).order_by('created_date')
        self.fields['new_container'].choices=tree_parse(0, 'choice', user, False)

        self.fields['formtype'].initial=formtype
        self.fields['object_pk'].initial=object.pk
        # =====================
        # меняем форму в соответствии с formtype
        if 'equipment' in formtype:
            self.fields['used_in_equipment'].widget = forms.HiddenInput()
            self.fields['used_in_equipment'].initial = object
            del self.fields['used_in_action']
            del self.fields['used_in_spare_part']
            del self.fields['quantity_delta']
            if 'repair' in formtype:
                del self.fields['new_container']
                if 'TO' in formtype:
                    self.label='Добавить Техническое обслуживание'
                    self.object=object
                if 'TR' in formtype:
                    self.label='Добавить Текущий ремонт'
                    self.object=object
                if 'KR' in formtype:
                    self.label='Добавить Капитальный ремонт'
                    self.object=object
                if 'KTS' in formtype:
                    self.label='Добавить Контроль технического состояния'
                    self.object=object
                if 'DEFF' in formtype:
                    self.label="Добавить ремонт по дефектной ведомости"
                    self.object=object
            if 'INFO' in formtype:
                self.label="Добавить информацию о работе оборудования"
                self.object=object
                self.fields['action_start_date'].label="Дата"
                del self.fields['action_end_date']
                del self.fields['scheduled']
                del self.fields['new_container']
            if 'FAILURE' in formtype:
                self.label="Добавить информацию об отказе"
                self.object=object
                self.fields['action_start_date'].label="Дата отказа"
                del self.fields['action_end_date']
                del self.fields['scheduled']
                del self.fields['new_container']
            if 'REPAIR_EXPORT' in formtype:
                self.label='Добавить Вывоз в ремонт оборудования'
                self.object=object
                self.fields['action_start_date'].label="Дата вывоза в ремонт"
                del self.fields['action_end_date']
                del self.fields['scheduled']
            if 'REPAIR_IMPORT' in formtype:
                self.label='Добавить Завоз с ремонта оборудования'
                self.object=object
                self.fields['action_start_date'].label="Дата завоза с ремонта"
                del self.fields['action_end_date']
                del self.fields['scheduled']
            if formtype=='equipment,MOUNT':
                self.label="Добавить Монтаж оборудования"
                self.object=object
                self.fields['action_start_date'].label="Дата монтажа"
                del self.fields['scheduled']
            if formtype=='equipment,UNMOUNT':
                self.label="Добавить Демонтаж оборудования"
                self.object=object
                self.fields['action_start_date'].label="Дата демонтажа"
                del self.fields['scheduled']


        #if 'repair' in formtype:
