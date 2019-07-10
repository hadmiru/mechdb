import json
from django.http import HttpResponse

from django.shortcuts import render, get_object_or_404
from .models import Container, Equipment, Equipment_sizename, Action, Profile, Spare_part
from django.utils import timezone
from django.utils.html import escape
from django.forms.models import model_to_dict
from .forms import ContainerForm, EquipmentForm, SizenameForm, ActionForm
from django.shortcuts import redirect
from .my_defs import tree_parse, get_container_place, parse_objects_tree_to_dict
from django.http import Http404
from .forms import SignUpForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


# Create your views here.

def terms_of_use(request):
    page_title = 'Пользовательское соглашение'
    return render(request, 'static_pages/terms_of_use.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            })

def privacy_policy(request):
    page_title = 'Политика конфиденциальности'
    return render(request, 'static_pages/privacy_policy.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            })

def guide(request):
    page_title = 'Инструкция по использованию базы данных MechDB'
    return render(request, 'mechdb_core/guide.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            })

def signin(request):
    if request.method == 'POST':
        if 'name' in request.POST and 'password' in request.POST:
            user = authenticate(username=request.POST['name'], password=request.POST['password'])
            if not user:
                # логин или пароль не верные
                error_message = 'Введённые логин или пароль не верны<br>Попробуйте ещё раз'
                return render(request, 'mechdb_core/signin.html', {
                                                            'current_user':request.user,
                                                            'authorization_hide':True,
                                                            'error_message':error_message
                                                            })
            login(request, user)
            return redirect('containers_map')

    raise Http404

def logout_view(request):
    logout(request)
    return redirect('index_page')

def signup(request):

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.email = form.cleaned_data.get('email')
            user.save()
            my_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=my_password)
            login(request, user)
            return redirect('containers_map')
    else:
        form = SignUpForm()
    return render(request, 'mechdb_core/signup.html', {'current_user':request.user, 'authorization_hide':True ,'form': form})

def index_page(request):
    timezone.now
    if not request.user.is_authenticated:
        # Если не пользователь не авторизован - отправляем на главную страницу
        return render(request, 'mechdb_core/index_page.html', {'current_user':request.user})
    else:
        # Если пользователь авторизован - перенаправляем на containers_map
        return redirect('containers_map')

def containers_map(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    if request.POST:
        containers_output=tree_parse(0, request.POST, request.user)
    else:
        #старая функция генерации дерева:
        #containers_output=tree_parse(0, 'li equipment', request.user)

        objects_map_dict = parse_objects_tree_to_dict(0,None,request.user)

    page_title = 'Карта'
    return render(request, 'mechdb_core/containers_map.html', {'current_user':request.user, 'page_title':page_title, 'objects_map_dict':objects_map_dict})

def container_detail(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    container = get_object_or_404(Container, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==container.owner:
        raise Http404
    # конец проверки

    # старая функция получения древа:
    #content=tree_parse(pk,'li equipment',request.user)

    content = parse_objects_tree_to_dict(pk,None,request.user)

    # Получаем список действий в контейнере и в его потомках 1го уровня
    containers = []
    containers.append(container)
    child_containers = Container.objects.filter(in_container=container)
    for i in child_containers:
        containers.append(i)
    actions_list = Action.objects.filter(used_in_container__in=containers).order_by("-action_start_date")

    place = get_container_place(container.pk)
    page_title = 'Карточка контейнера '+str(container.title)
    return render(request, 'mechdb_core/container_detail.html', {
                                                                'current_user':request.user,
                                                                'page_title':page_title,
                                                                'container':container,
                                                                'content':content,
                                                                'place':place,
                                                                'actions_list':actions_list
                                                                })

def container_new(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    instance={}
    if 'in_container_id' in request.GET:
        instance['in_container_id'] = request.GET['in_container_id']

    if request.method == "POST":
        form = ContainerForm(request.POST, user=request.user, self_pk=0, initial=instance)
        if form.is_valid():
            print('form valid')
            container = Container()
            container.owner = request.user
            container.created_date = timezone.now()
            container.title = form.cleaned_data['title']
            container.description = form.cleaned_data['description']
            container.is_repair_organization = form.cleaned_data['is_repair_organization']
            if form.cleaned_data['in_container_id']:
                # если кладём не в нулевой конт - заполняем поле, если в нулевой - ставится Null
                parrent_container = Container.objects.get(pk=form.cleaned_data['in_container_id'])
                container.in_container = parrent_container
            else:
                container.in_container = None
            container.save()
            return redirect('container_detail', pk=container.pk)
    else:
        form = ContainerForm(user=request.user, self_pk=0, initial=instance)
    page_title = 'Создание контейнера'
    return render(request, 'mechdb_core/container_edit.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'form': form
                                                            })

def container_edit(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    container = get_object_or_404(Container, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==container.owner:
        raise Http404
    # конец проверки

    instance = model_to_dict(container)
    instance['in_container_id']=instance['in_container']
    if request.method == "POST":
        form = ContainerForm(request.POST, user=request.user, initial=instance, self_pk=container.pk)
        if form.is_valid():
            container.owner = request.user
            container.title = form.cleaned_data['title']
            container.description = form.cleaned_data['description']
            container.is_repair_organization = form.cleaned_data['is_repair_organization']
            if form.cleaned_data['in_container_id']:
                # если кладём не в нулевой конт - заполняем поле, если в нулевой - ставится Null
                parrent_container = Container.objects.get(pk=form.cleaned_data['in_container_id'])
                container.in_container = parrent_container
            else:
                container.in_container = None
            container.save()
            return redirect('container_detail', pk=container.pk)
    else:
        form = ContainerForm(initial=instance, user=request.user, self_pk=container.pk)
    page_title = 'Редактирование контейнера '+str(container.title)
    return render(request, 'mechdb_core/container_edit.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'form': form
                                                            })

def container_remove(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    container = get_object_or_404(Container, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==container.owner:
        raise Http404
    # конец проверки

    child_equipments = Equipment.objects.filter(in_container=container).order_by("serial_number")
    child_spare_parts = Spare_part.objects.filter(in_container=container).order_by("title")
    child_containers = Container.objects.filter(in_container=container).order_by("title")
    childs = False
    if child_equipments or child_spare_parts or child_containers:
        childs = True
    if 'confirmed' in request.POST:
        if container.owner == request.user and not childs:
            # проверяем оборудование, которое изменится в результате воздействий
            child_actions = Action.objects.filter(new_container=container)
            changed_equipments=[]
            for i in child_actions:
                if i.used_in_equipment not in changed_equipments:
                    changed_equipments.append(i.used_in_equipment)
            container.delete()
            for y in changed_equipments:
                y.set_correct_places()
        return redirect('containers_map')
    page_title = 'Удаление контейнера '+str(container.title)
    return render(request, 'mechdb_core/container_remove.html', {
                                                                'current_user':request.user,
                                                                'container':container,
                                                                'child_equipments':child_equipments,
                                                                'child_spare_parts':child_spare_parts,
                                                                'child_containers':child_containers,
                                                                'childs':childs,
                                                                'page_title':page_title,
                                                                })

def equipment_list(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    equipments = Equipment.objects.filter(owner=request.user).order_by('sizename')

    page_title = 'Список оборудования'
    return render(request, 'mechdb_core/equipment_list.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'equipments':equipments
                                                            })

def equipment_detail(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    equipment = get_object_or_404(Equipment, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==equipment.owner:
        raise Http404
    # конец проверки

    place = get_container_place(equipment.in_container.pk)
    actions = Action.objects.filter(owner=request.user, used_in_equipment=equipment).order_by('-action_start_date')
    page_title = 'Карточка оборудования '+str(equipment)
    return render(request, 'mechdb_core/equipment_detail.html', {
                                                                'current_user':request.user,
                                                                'page_title':page_title,
                                                                'equipment':equipment,
                                                                'place':place,
                                                                'actions':actions
                                                                })

def equipment_remove(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    equipment = get_object_or_404(Equipment, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==equipment.owner:
        raise Http404
    # конец проверки

    if 'confirmed' in request.POST:
        if equipment.owner == request.user:
            equipment.delete()
        return redirect('equipment_list')
    page_title = 'Удаление оборудования '+str(equipment)
    return render(request, 'mechdb_core/equipment_remove.html', {
                                                                'current_user':request.user,
                                                                'page_title':page_title,
                                                                'equipment':equipment
                                                                })

def equipment_new(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    instance={}
    if 'in_container_id' in request.GET:
        instance['in_container_id'] = request.GET['in_container_id']
    if 'sizename_id' in request.GET:
        sizename_id = escape(request.GET['sizename_id'])
        instance['sizename'] = get_object_or_404(Equipment_sizename, pk=sizename_id)

    if request.method == "POST":
        form = EquipmentForm(request.POST ,user=request.user, formtype="new", initial=instance)
        if form.is_valid():
            equipment = Equipment()
            equipment.owner = request.user
            equipment.created_date = timezone.now()
            equipment.sizename = form.cleaned_data['sizename']
            equipment.serial_number = form.cleaned_data['serial_number']
            equipment.registration_number = form.cleaned_data['registration_number']
            equipment.in_container = get_object_or_404(Container, pk=request.POST['in_container_id'])
            equipment.save()

            # создаём action "перемещение"
            action = Action()
            action.owner = request.user
            action.created_date = timezone.now()
            action.action_start_date = form.cleaned_data['action_datetime']
            action.action_end_date = form.cleaned_data['action_datetime']
            action.type = 'equipment,MOVE'
            action.used_in_equipment = equipment
            action.new_container = get_object_or_404(Container, pk=form.cleaned_data['in_container_id'])
            action.save()
            equipment.set_correct_places()

            return redirect('equipment_detail', pk=equipment.pk)
    else:
        form = EquipmentForm(user=request.user, formtype='new', initial=instance)
    page_title = 'Создание оборудования'
    return render(request, 'mechdb_core/equipment_edit.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'form': form
                                                            })

def equipment_edit(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    #Проверяем что в Post передан typeform, если нет - ставим 'edit'
    # если первая прогрузка формы - formtype передаётся из ссылки
    # если вторая прогрузка формы - formtype передаётся из одноимённого поля
    if 'formtype' in request.POST:
        formtype = request.POST['formtype']
        allowable_formtypes = ('new', 'edit')
        if not formtype in allowable_formtypes:
            raise Http404
    else:
        formtype='edit'
    equipment = get_object_or_404(Equipment, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==equipment.owner:
        raise Http404
    # конец проверки

    instance = model_to_dict(equipment)
    instance['in_container_id']=instance['in_container']
    instance['formtype']=formtype

    if 'form_completed' in request.POST:
        form = EquipmentForm(request.POST ,user=request.user, initial=instance, formtype=formtype)
        if form.is_valid():
            if 'sizename' in form.fields:
                equipment.sizename = form.cleaned_data['sizename']
            if 'serial_number' in form.fields:
                equipment.serial_number = form.cleaned_data['serial_number']
            if 'registration_number' in form.fields:
                equipment.registration_number = form.cleaned_data['registration_number']
            equipment.save()
            return redirect('equipment_detail', pk=equipment.pk)
    else:
        form = EquipmentForm(user=request.user, initial=instance, formtype=formtype)
    page_title = 'Редактирование оборудования '+str(equipment)
    return render(request, 'mechdb_core/equipment_edit.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'form': form,
                                                            'equipment':equipment
                                                            })

def sizename_list(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    sizenames = Equipment_sizename.objects.filter(owner=request.user).order_by('title')
    page_title = 'Список моделей (типоразмеров) оборудования'
    return render(request, 'mechdb_core/sizename_list.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'sizenames':sizenames})

def sizename_detail(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    sizename = get_object_or_404(Equipment_sizename, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==sizename.owner:
        raise Http404
    # конец проверки

    slaves_list = Equipment.objects.filter(owner=request.user, sizename=sizename).order_by('serial_number')
#    slaves_list=[]
#    for slave in slave_equipments:
#        slaves_list.append((slave.pk, slave.serial_number,get_container_place(slave.in_container.pk)))
    page_title = 'Карточка модели '+sizename.title
    return render(request, 'mechdb_core/sizename_detail.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'sizename':sizename,
                                                            'slaves_list':slaves_list
                                                            })

def sizename_new(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    if request.method == "POST":
        form = SizenameForm(request.POST)
        if form.is_valid():
            sizename = form.save(commit=False)
            sizename.owner = request.user
            sizename.created_date = timezone.now()
            sizename.save()
            return redirect('sizename_detail', pk=sizename.pk)
    else:
        form = SizenameForm()
    page_title = 'Создание модели (типоразмера)'
    return render(request, 'mechdb_core/sizename_edit.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'form': form
                                                            })

def sizename_edit(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    sizename = get_object_or_404(Equipment_sizename, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==sizename.owner:
        raise Http404
    # конец проверки

    if request.method == "POST":
        form = SizenameForm(request.POST, instance=sizename)
        if form.is_valid():
            sizename = form.save(commit=False)
            sizename.owner = request.user
            sizename.save()
            return redirect('sizename_detail', pk=sizename.pk)
    else:
        form = SizenameForm(instance=sizename)
    page_title = 'Редактирование модели '+sizename.title
    return render(request, 'mechdb_core/sizename_edit.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'form': form
                                                            })


def sizename_remove(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    sizename = get_object_or_404(Equipment_sizename, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==sizename.owner:
        raise Http404
    # конец проверки

    child_equipments = Equipment.objects.filter(sizename=sizename).order_by("serial_number")

    if 'confirmed' in request.POST:
        if sizename.owner == request.user and not child_equipments:
            sizename.delete()
        return redirect('sizename_list')
    page_title = 'Удаление модели '+str(sizename.title)
    return render(request, 'mechdb_core/sizename_remove.html', {
                                                                'current_user':request.user,
                                                                'sizename':sizename,
                                                                'child_equipments':child_equipments,
                                                                'page_title':page_title,
                                                                })



def action_list(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    actions = Action.objects.filter(owner=request.user).order_by('-action_start_date')
    page_title = 'Список ремонтных воздействий'
    return render(request, 'mechdb_core/action_list.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'actions':actions
                                                            })

def action_detail(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    action = get_object_or_404(Action, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==action.owner:
        raise Http404
    # конец проверки
    page_title = 'Карточка ремонтного воздействия'
    return render(request, 'mechdb_core/action_detail.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'action':action
                                                            })

def action_new(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    #Проверяем что в Post передан typeform, если нет - ставим 'edit'
    # если первая прогрузка формы - formtype передаётся из ссылки
    # если вторая прогрузка формы - formtype передаётся из одноимённого поля

    # блок обработки действий над оборудованием
    if 'formtype' in request.POST and 'object_pk_from_user' in request.POST:
        # представлению должны быть переданы тип формы и оборудование над которым будет воздействие. иначе - отказ
        object = Equipment.objects.get(pk=request.POST['object_pk_from_user'])
        formtype = request.POST['formtype']

        # составляем словарь допустимых значений
        allowable_formtypes = {}
        for i in Action.action_type_choices_equipment:
            allowable_formtypes.update({i[0]:i[1]})

        if not formtype in allowable_formtypes:
            # выдаём 404 если с формтайпом что-то не то. возможно подмена запроса злобными хацкерами
            raise Http404
        # object может быть как оборудованием, так и spare_part (второе обрабатывается в следующем блоке)
        # КОТОРОГО ТУТ ПОКА НЕТ ОЛОЛО

        # Проверка что объект принадлежит юзеру
        if not request.user==object.owner:
            raise Http404
        # конец проверки
    else:
        raise Http404

    if 'form_completed' in request.POST:
        form = ActionForm(request.POST, user=request.user, formtype=formtype, object=object)
        if form.is_valid():
            action = Action()
            action.owner = request.user
            action.created_date = timezone.now()

            action.type = formtype

            if 'action_start_date' in form.fields:
                action.action_start_date = form.cleaned_data['action_start_date']
            else:
                action.action_start_date = timezone.now()
            if 'action_end_date' in form.fields and form.cleaned_data['action_end_date']:
                action.action_end_date = form.cleaned_data['action_end_date']
            else:
                action.action_end_date = action.action_start_date
            if 'scheduled' in form.fields:
                action.scheduled = form.cleaned_data['scheduled']
            if 'description' in form.fields:
                action.description = form.cleaned_data['description']
            if 'used_in_equipment' in form.fields:
                action.used_in_equipment = object
            if 'used_in_action' in form.fields:
                action.used_in_action = object
            if 'used_in_spare_part' in form.fields:
                action.used_in_spare_part = object
            if 'quantity_delta' in form.fields:
                action.quantity_delta = form.cleaned_data['quantity_delta']
            if 'new_container' in form.fields:
                action.new_container = Container.objects.get(pk=form.cleaned_data['new_container'])
            action.save()
            object.set_correct_places()

            return redirect('equipment_detail', pk=object.pk)
    else:
        form = ActionForm(user=request.user, formtype=formtype, object=object)

    page_title = 'Добавление ремонтного воздействия'
    return render(request, 'mechdb_core/action_edit.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'form': form
                                                            })

def action_remove(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    action = get_object_or_404(Action, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==action.owner:
        raise Http404
    # конец проверки

    if 'confirmed' in request.POST:
        if action.owner == request.user:
            # проверяем оборудование, которое изменится в результате воздействий
            action.delete()
            if action.new_container:
                if action.used_in_equipment:
                    action.used_in_equipment.set_correct_places()
        return redirect('action_list')
    page_title = 'Удаление воздействия '+str(action)
    return render(request, 'mechdb_core/action_remove.html', {
                                                                'current_user':request.user,
                                                                'action':action,
                                                                'page_title':page_title,
                                                                })

def action_edit(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    action = get_object_or_404(Action, pk=pk)
    # Проверка что объект принадлежит юзеру
    if not request.user==action.owner:
        raise Http404
    # конец проверки

    formtype=action.type
    # составляем словарь допустимых значений
    allowable_formtypes = {}
    for i in Action.action_type_choices_equipment:
        allowable_formtypes.update({i[0]:i[1]})
    if not formtype in allowable_formtypes:
        # выдаём 404 если с формтайпом что-то не то. возможно подмена запроса злобными хацкерами
        raise Http404

    if action.used_in_equipment:
        object = action.used_in_equipment
    elif action.used_in_action:
        object = action.used_in_action
    elif action.used_in_spare_part:
        object = action.used_in_spare_part
    else:
        raise Http404

    instance=model_to_dict(action)
    if 'form_completed' in request.POST:
        form = ActionForm(request.POST, initial=instance, formtype=formtype, object=object, user=request.user)
        if form.is_valid():

            if 'action_start_date' in form.fields:
                action.action_start_date = form.cleaned_data['action_start_date']
            if 'action_end_date' in form.fields and form.cleaned_data['action_end_date']:
                action.action_end_date = form.cleaned_data['action_end_date']
            else:
                action.action_end_date = action.action_start_date
            if 'scheduled' in form.fields:
                action.scheduled = form.cleaned_data['scheduled']
            if 'description' in form.fields:
                action.description = form.cleaned_data['description']
            if 'used_in_equipment' in form.fields:
                action.used_in_equipment = object
            if 'used_in_action' in form.fields:
                action.used_in_action = object
            if 'used_in_spare_part' in form.fields:
                action.used_in_spare_part = object
            if 'quantity_delta' in form.fields:
                action.quantity_delta = form.cleaned_data['quantity_delta']
            if 'new_container' in form.fields:
                action.new_container = Container.objects.get(pk=form.cleaned_data['new_container'])
            action.save()
            object.set_correct_places()

            return redirect('action_detail', pk=action.pk)
    else:
        form = ActionForm(initial=instance, formtype=formtype, object=object, user=request.user)
    page_title = 'Редактирование ремонтного воздействия'
    return render(request, 'mechdb_core/action_edit.html', {
                                                            'current_user':request.user,
                                                            'page_title':page_title,
                                                            'form': form})



def testview(request):
    if not request.user.is_authenticated:
        return redirect('index_page')

    return render(request, 'mechdb_core/mechdb_app.html', {'current_user':request.user})

def get_objects_tree(request):
    timezone.now
    if not request.user.is_authenticated:
        return HttpResponse(
                json.dumps({
                    "result": "error",
                    "error_text": "Аутентификация не пройдена"
                }),
                content_type="application/json"
            )
    if 'initiate_pk' in request.POST:
        initiate_pk = int(request.POST['initiate_pk'])
    else:
        initiate_pk = 0

    objects_map_dict = parse_objects_tree_to_dict(initiate_pk, None, request.user)

    return HttpResponse(
        json.dumps({
            "result": objects_map_dict,
        }),
        content_type="application/json"
    )

def get_actions_list(request):
    timezone.now
    if not request.user.is_authenticated:
        return HttpResponse(
                json.dumps({
                    "result": "error",
                    "error_text": "Аутентификация не пройдена"
                }),
                content_type="application/json"
            )


    if 'quantity_for_page' in request.POST:
        quantity_for_page = int(request.POST['quantity_for_page'])
    else:
        quantity_for_page = 20

    # создаём словарь для таблицы с заготовкой под строки
    actions_list_dict = {
        'table_header': [
            {'title': 'Дата', 'anchor': 'start_date'},
            {'title': 'Оборудование', 'anchor': 'equipment'},
            {'title': 'Тип', 'anchor': 'type'},
            {'title': 'Вид', 'anchor': 'scheduled'},
            {'title': 'Контейнер', 'anchor': 'container'},
            {'title': 'Описание', 'anchor': 'description', 'tooltiped': True}
        ],

        'table_params': {
            'html_id': 'actions_table',
            'html_class': 'content_table'
        },

        'lines': []
    }

    # выгружаем записи согласно запрошенного количества:
    if 'page' in request.POST:
        page = int(request.POST['page'])
    else:
        page = 0
    actions_list = Action.objects.filter(owner=request.user).order_by('-action_start_date')[page*quantity_for_page:page*quantity_for_page+quantity_for_page]

    for action in actions_list:

        # заполняем уровень строки с заготовками ячеек:
        actions_list_dict['lines'].append({
            # параметры строки:
            'html_id': action.pk,
            'html_class': 'action',
            # ниже заготовки для ячеек:
            'start_date': [],
            'equipment': [],
            'type': [],
            'scheduled': [],
            'container': [],
            'description': []
        })

        # заполняем сами ячейки
        # для этого ищем последний элемент в lines и добавляем данные по соответствующим ключам
        # если в ячейке несколько элементов <p> параметры ячейки (class, id и т.п.) передаём в
        # нулевом элементе чтобы была проще структура данных

        # start_date
        actions_list_dict['lines'][-1]['start_date'].append(
            {
                'title': str(action.action_start_date),
                'html_class_td': 'action'
             })

        # equipment
        actions_list_dict['lines'][-1]['equipment'].append(
            {
                'title': action.used_in_equipment.sizename.title + ' № ' + action.used_in_equipment.serial_number,
                'html_class_td': 'equipment'
             })

        # type
        actions_list_dict['lines'][-1]['type'].append(
            {
                'title': action.get_type_display(),
                'html_class_td': 'action'
             })

        # scheduled
        cell_title = ''
        if action.scheduled == True:
            cell_title = 'плановое'
        elif action.scheduled == False:
            cell_title = 'внеплановое'
        else:
            cell_title = '-'

        actions_list_dict['lines'][-1]['scheduled'].append(
            {
                'title': cell_title,
                'html_class_td': 'action'
             })

        # container
        container1 = {}
        container2 = {}

        if action.new_container:
            container2.update({
                'title': action.new_container.title,
                'html_id_p': action.new_container.pk,
            })
            container1.update({
                'separator': '<i class="fa fa-long-arrow-right"></i>'
            })

            # на случай если вдруг это первая запись, проверяем длину used in container:
            if len(action.used_in_container.all()) == 1:
                container1.update({
                    'title': ''
                })

            # так как в action.used_in_container контейнеры не упорядочены, пришлось добавить условие, сверяющее
            # значение контейнеров с new container и выводить тот что остался:

            elif action.used_in_container.last().pk == action.new_container.pk:
                container1.update({
                    'title': action.used_in_container.first().title,
                    'html_id_p': action.used_in_container.first().pk
                })
            else:
                container1.update({
                    'title': action.used_in_container.last().title,
                    'html_id_p': action.used_in_container.last().pk
                })
        else:
            if action.used_in_container.last().in_container:
                container1.update({
                    'title': action.used_in_container.last().in_container.title,
                    'html_id_p': action.used_in_container.last().in_container.pk,
                    'separator': '<i class="fa fa-angle-left"></i>'
                })
                container2.update({
                    'title': action.used_in_container.last().title,
                    'html_id_p': action.used_in_container.last().pk,
                })

        actions_list_dict['lines'][-1]['container'].append(container1)
        actions_list_dict['lines'][-1]['container'].append(container2)

        # description
        actions_list_dict['lines'][-1]['description'].append(
            {
                'title': action.description,
                'html_class': 'action'
             })



    return HttpResponse(
        json.dumps({
            "result": actions_list_dict,
        }),
        content_type="application/json"
    )