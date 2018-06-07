from django.shortcuts import render, get_object_or_404
from .models import Container, Equipment, Equipment_sizename, Action, Action_type, Profile
from django.utils import timezone
from django.utils.html import escape
from django.forms.models import model_to_dict
from .forms import ContainerForm, EquipmentForm, SizenameForm, ActionForm
from django.shortcuts import redirect
from .my_defs import tree_parse, get_container_place
from django.http import Http404
from .forms import SignUpForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Create your views here.

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
                                                            'error_message':error_message}
                                                            )
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
        return render(request, 'mechdb_core/under_construction.html', {'current_user':request.user})
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
        containers_output=tree_parse(0, 'li', request.user)
    return render(request, 'mechdb_core/containers_map.html', {'current_user':request.user, 'containers': containers_output})

def container_detail(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    container = get_object_or_404(Container, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==container.owner:
        raise Http404
    # конец проверки

    content=tree_parse(pk,'li equipment',request.user)
    return render(request, 'mechdb_core/container_detail.html', {
                                                                'current_user':request.user,
                                                                'container':container,
                                                                'content':content
                                                                })

def container_new(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    if request.method == "POST":
        form = ContainerForm(request.POST, user=request.user, self_pk=0)
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
        form = ContainerForm(user=request.user, self_pk=0)
    return render(request, 'mechdb_core/container_edit.html', {'current_user':request.user, 'form': form})

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
    return render(request, 'mechdb_core/container_edit.html', {'current_user':request.user, 'form': form})

def equipment_list(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    equipments = Equipment.objects.filter(owner=request.user).order_by('sizename')
    return render(request, 'mechdb_core/equipment_list.html', {'current_user':request.user, 'equipments':equipments})

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
    return render(request, 'mechdb_core/equipment_detail.html', {'current_user':request.user, 'equipment':equipment,'place':place, 'actions':actions})

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
    return render(request, 'mechdb_core/equipment_remove.html', {'current_user':request.user, 'equipment':equipment})

def equipment_new(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    if request.method == "POST":
        form = EquipmentForm(request.POST ,user=request.user, formtype="new")
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
            action.action_start_date = timezone.now()
            action.action_end_date = timezone.now()
            action.type = Action_type.objects.get(title='перемещение')
            action.used_in_equipment = equipment
            action.new_container = equipment.in_container
            action.save()

            return redirect('equipment_detail', pk=equipment.pk)
    else:
        form = EquipmentForm(user=request.user, formtype='new')
    return render(request, 'mechdb_core/equipment_edit.html', {'current_user':request.user, 'form': form})

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
            if 'in_container_id' in form.fields:
                # остатки старого кода когда equipmentform могла перемещать оборудование.
                # оставил на всякий случай. да и при создании оборудования будет создаваться action перемещения, что важно
                # создаём action перемещения
                action = Action()
                action.owner = request.user
                action.created_date = timezone.now()
                # время берём из соответствующего поля
                action.action_start_date = form.cleaned_data['action_datetime']
                action.action_end_date = form.cleaned_data['action_datetime']
                action.type = Action_type.objects.get(title='перемещение')
                action.used_in_equipment = equipment
                action.new_container = get_object_or_404(Container, pk=form.cleaned_data['in_container_id'])
                action.save()
                # после добавления action проверяем методом объекта equipment текущее местоположение и переписываем соответствующее поле объекта
                last_place = equipment.get_place_on_date(timezone.now())
                if last_place:
                    equipment.in_container = last_place
            equipment.save()
            return redirect('equipment_detail', pk=equipment.pk)
    else:

        form = EquipmentForm(user=request.user, initial=instance, formtype=formtype)
    return render(request, 'mechdb_core/equipment_edit.html', {'current_user':request.user, 'form': form, 'equipment':equipment})

def sizename_list(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    sizenames = Equipment_sizename.objects.filter(owner=request.user).order_by('title')
    return render(request, 'mechdb_core/sizename_list.html', {'current_user':request.user, 'sizenames':sizenames})

def sizename_detail(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    sizename = get_object_or_404(Equipment_sizename, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==sizename.owner:
        raise Http404
    # конец проверки

    slave_equipments = Equipment.objects.filter(owner=request.user, sizename=sizename).order_by('serial_number')
    slaves_list=[]
    for slave in slave_equipments:
        slaves_list.append((slave.pk, slave.serial_number,get_container_place(slave.in_container.pk)))
    return render(request, 'mechdb_core/sizename_detail.html', {'current_user':request.user, 'sizename':sizename, 'slaves_list':slaves_list})

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
    return render(request, 'mechdb_core/sizename_edit.html', {'current_user':request.user, 'form': form})

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
    return render(request, 'mechdb_core/sizename_edit.html', {'current_user':request.user, 'form': form})

def action_list(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    actions = Action.objects.filter(owner=request.user).order_by('-action_start_date')
    return render(request, 'mechdb_core/action_list.html', {'current_user':request.user, 'actions':actions})

def action_detail(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    action = get_object_or_404(Action, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==action.owner:
        raise Http404
    # конец проверки

    return render(request, 'mechdb_core/action_detail.html', {'current_user':request.user, 'action':action})

def action_new(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    #Проверяем что в Post передан typeform, если нет - ставим 'edit'
    # если первая прогрузка формы - formtype передаётся из ссылки
    # если вторая прогрузка формы - formtype передаётся из одноимённого поля

    # блок обработки действий над оборудованием
    if 'formtype' in request.POST and 'object_pk' in request.POST:
        # представлению должны быть переданы тип формы и оборудование над которым будет воздействие. иначе - отказ
        formtype = request.POST['formtype']
        allowable_formtypes = {
                'equipment,repair,TO':"ТО",
                'equipment,repair,TR':"ТР",
                'equipment,repair,KR':"КР",
                'equipment,repair,KTS':"КТС",
                'equipment,repair,DEFF':"ремонт",
                'equipment,INFO':"информация",
                'equipment,FAILURE':"отказ",
                'equipment,REPAIR_EXPORT':"вывоз в ремонт",
                'equipment,REPAIR_IMPORT':"завоз с ремонта",
                'equipment,MOUNT':"монтаж",
                'equipment,UNMOUNT':"демонтаж",
                'equipment,MOVE':"перемещение"
                }
        if not formtype in allowable_formtypes:
            # выдаём 404 если с формтайпом что-то не то. возможно подмена запроса злобными хацкерами
            raise Http404
        # object может быть как оборудованием, так и spare_part (второе обрабатывается в следующем блоке)
        object = get_object_or_404(Equipment, pk=request.POST['object_pk'])
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

            action.type = Action_type.objects.get(title=allowable_formtypes[formtype])

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
            object.set_current_container()

            return redirect('equipment_detail', pk=object.pk)
    else:
        form = ActionForm(user=request.user, formtype=formtype, object=object)
    return render(request, 'mechdb_core/action_edit.html', {'current_user':request.user, 'form': form})

def action_edit(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    action = get_object_or_404(Action, pk=pk)
    # Проверка что объект принадлежит юзеру
    if not request.user==action.owner:
        raise Http404
    # конец проверки

    # =====================Начало формирования formtype
    formtype=''
    if action.used_in_equipment:
        object = action.used_in_equipment

        allowable_formtypes = {
                'equipment,repair,TO':"ТО",
                'equipment,repair,TR':"ТР",
                'equipment,repair,KR':"КР",
                'equipment,repair,KTS':"КТС",
                'equipment,repair,DEFF':"ремонт",
                'equipment,INFO':"информация",
                'equipment,FAILURE':"отказ",
                'equipment,REPAIR_EXPORT':"вывоз в ремонт",
                'equipment,REPAIR_IMPORT':"завоз с ремонта",
                'equipment,MOUNT':"монтаж",
                'equipment,UNMOUNT':"демонтаж",
                'equipment,MOVE':"перемещение"
                }
        # меняем в словаре местами ключи и значения и составляем formtype на основе action_type нашего action
        allowable_formtypes_reverse = {v:k for k, v in allowable_formtypes.items()}
        if action.type.title in allowable_formtypes_reverse:
            formtype = allowable_formtypes_reverse[action.type.title]
    elif action.used_in_action:
        object = action.used_in_action
    elif action.used_in_spare_part:
        object = action.used_in_spare_part
    else:
        raise Http404
    # ==============конец формирования formtype

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
            object.set_current_container()

            return redirect('action_detail', pk=action.pk)
    else:
        form = ActionForm(initial=instance, formtype=formtype, object=object, user=request.user)
    return render(request, 'mechdb_core/action_edit.html', {'current_user':request.user, 'form': form})
