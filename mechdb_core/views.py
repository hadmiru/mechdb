from django.shortcuts import render, get_object_or_404
from .models import Container, Equipment, Equipment_sizename, Action, Action_type
from django.utils import timezone
from django.utils.html import escape
from django.forms.models import model_to_dict
from .forms import ContainerForm, EquipmentForm, SizenameForm, ActionForm
from django.shortcuts import redirect
from .my_defs import tree_parse, get_container_place
from django.http import Http404


# Create your views here.
def index_page(request):
    timezone.now
    return render(request, 'mechdb_core/under_construction.html', {})

def containers_map(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    if request.POST:
        containers_output=tree_parse(0, request.POST, request.user)
    else:
        containers_output=tree_parse(0, 'li', request.user)
    return render(request, 'mechdb_core/containers_map.html', {'containers': containers_output})

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
    return render(request, 'mechdb_core/container_edit.html', {'form': form})

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
    return render(request, 'mechdb_core/container_edit.html', {'form': form})

def equipment_list(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    equipments = Equipment.objects.filter(owner=request.user).order_by('sizename')
    return render(request, 'mechdb_core/equipment_list.html', {'equipments':equipments})

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
    return render(request, 'mechdb_core/equipment_detail.html', {'equipment':equipment,'place':place, 'actions':actions})

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
        print('Сработало удаление оборудования')
        if equipment.owner == request.user:
            equipment.delete()
        return redirect('equipment_list')
    else:
        confirmed=False

    place = get_container_place(equipment.in_container.pk)
    actions = Action.objects.filter(owner=request.user, used_in_equipment=equipment).order_by('-action_start_date')
    return render(request, 'mechdb_core/equipment_remove.html', {'equipment':equipment, 'confirmed':confirmed})

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
    return render(request, 'mechdb_core/equipment_edit.html', {'form': form})

def equipment_edit(request, pk, formtype):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    equipment = get_object_or_404(Equipment, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==equipment.owner:
        raise Http404
    # конец проверки

    instance = model_to_dict(equipment)
    instance['in_container_id']=instance['in_container']

    if request.method == "POST":
        form = EquipmentForm(request.POST ,user=request.user, initial=instance, formtype=formtype)
        if form.is_valid():
            if 'sizename' in form.fields:
                equipment.sizename = form.cleaned_data['sizename']
            if 'serial_number' in form.fields:
                equipment.serial_number = form.cleaned_data['serial_number']
            if 'registration_number' in form.fields:
                equipment.registration_number = form.cleaned_data['registration_number']
            if 'in_container_id' in form.fields:
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
    return render(request, 'mechdb_core/equipment_edit.html', {'form': form})

def sizename_list(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    sizenames = Equipment_sizename.objects.filter(owner=request.user).order_by('title')
    return render(request, 'mechdb_core/sizename_list.html', {'sizenames':sizenames})

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
    return render(request, 'mechdb_core/sizename_detail.html', {'sizename':sizename, 'slaves_list':slaves_list})

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
    return render(request, 'mechdb_core/sizename_edit.html', {'form': form})

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
    return render(request, 'mechdb_core/sizename_edit.html', {'form': form})

def action_list(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    actions = Action.objects.filter(owner=request.user).order_by('-action_start_date')
    return render(request, 'mechdb_core/action_list.html', {'actions':actions})

def action_detail(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    action = get_object_or_404(Action, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==action.owner:
        raise Http404
    # конец проверки

    return render(request, 'mechdb_core/action_detail.html', {'action':action})

def action_new(request):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    if request.method == "POST":
        form = ActionForm(request.POST, user=request.user)
        if form.is_valid():
            action = Action()
            action.owner = request.user
            action.created_date = timezone.now()
            action.type = form.cleaned_data['type']
            action.action_start_date = form.cleaned_data['action_start_date']
            if form.cleaned_data['action_end_date']:
                action.action_end_date = form.cleaned_data['action_end_date']
            else:
                action.action_end_date = form.cleaned_data['action_start_date']
            action.scheduled = form.cleaned_data['scheduled']
            action.description = form.cleaned_data['description']
            action.used_in_equipment = form.cleaned_data['used_in_equipment']
            action.save()
            return redirect('action_detail', pk=action.pk)
    else:
        form = ActionForm(user=request.user)
    return render(request, 'mechdb_core/action_edit.html', {'form': form})

def action_edit(request, pk):
    timezone.now
    if not request.user.is_authenticated:
        return redirect('index_page')

    action = get_object_or_404(Action, pk=pk)

    # Проверка что объект принадлежит юзеру
    if not request.user==action.owner:
        raise Http404
    # конец проверки

    instance=model_to_dict(action)
    if request.method == "POST":
        form = ActionForm(request.POST, initial=instance, user=request.user)
        if form.is_valid():
            action.owner = request.user
            action.created_date = timezone.now()
            action.type = form.cleaned_data['type']
            if form.cleaned_data['action_end_date']:
                action.action_end_date = form.cleaned_data['action_end_date']
            else:
                action.action_end_date = form.cleaned_data['action_start_date']
            action.scheduled = form.cleaned_data['scheduled']
            action.description = form.cleaned_data['description']
            action.used_in_equipment = form.cleaned_data['used_in_equipment']
            action.save()
            return redirect('action_detail', pk=action.pk)
    else:
        form = ActionForm(initial=instance, user=request.user)
    return render(request, 'mechdb_core/action_edit.html', {'form': form})
