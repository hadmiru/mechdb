from django.shortcuts import render, get_object_or_404
from .models import Container, Equipment, Equipment_sizename
from django.utils import timezone
from django.utils.html import escape
from .forms import ContainerForm, SizenameForm
from django.shortcuts import redirect
from .my_defs import tree_parse, get_container_place


# Create your views here.
def index_page(request):
    return render(request, 'mechdb_core/under_construction.html', {})

def containers_map(request):
    if request.POST:
        containers_output=tree_parse(0, request.POST, request.user)
    else:
        containers_output=tree_parse(0, 'li', request.user)
    return render(request, 'mechdb_core/containers_map.html', {'containers': containers_output})

def container_detail(request, pk):
    container = get_object_or_404(Container, pk=pk)
    return render(request, 'mechdb_core/container_detail.html', {'container':container})

def container_new(request):
    if request.method == "POST":
        form = ContainerForm(request.POST, user=request.user)
        if form.is_valid():
            container = form.save(commit=False)
            container.owner = request.user
            container.created_date = timezone.now()
            container.save()
            return redirect('container_detail', pk=container.pk)
    else:
        form = ContainerForm(user=request.user)
    return render(request, 'mechdb_core/container_edit.html', {'form': form})

def container_edit(request, pk):
    container = get_object_or_404(Container, pk=pk)
    if request.method == "POST":
        form = ContainerForm(request.POST, user=request.user, instance=container)
        if form.is_valid():
            container = form.save(commit=False)
            container.owner = request.user
            container.created_date = timezone.now()
            container.save()
            return redirect('container_detail', pk=container.pk)
    else:
        form = ContainerForm(instance=container, user=request.user)
    return render(request, 'mechdb_core/container_edit.html', {'form': form})

def equipment_list(request):
    equipments = Equipment.objects.filter(owner=request.user).order_by('sizename')
    return render(request, 'mechdb_core/equipment_list.html', {'equipments':equipments})

def equipment_detail(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    place=get_container_place(equipment.in_container.pk)
    return render(request, 'mechdb_core/equipment_detail.html', {'equipment':equipment,'place':place})

def sizename_list(request):
    sizenames = Equipment_sizename.objects.filter(owner=request.user).order_by('title')
    return render(request, 'mechdb_core/sizename_list.html', {'sizenames':sizenames})

def sizename_detail(request, pk):
    sizename = get_object_or_404(Equipment_sizename, pk=pk)
    slave_equipments = Equipment.objects.filter(owner=request.user, sizename=sizename).order_by('serial_number')
    slaves_list=[]
    for slave in slave_equipments:
        slaves_list.append((slave.pk, slave.serial_number,get_container_place(slave.in_container.pk)))
    return render(request, 'mechdb_core/sizename_detail.html', {'sizename':sizename, 'slaves_list':slaves_list})

def sizename_new(request):
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
    sizename = get_object_or_404(Equipment_sizename, pk=pk)
    if request.method == "POST":
        form = SizenameForm(request.POST, instance=sizename)
        if form.is_valid():
            sizename = form.save(commit=False)
            sizename.owner = request.user
            sizename.created_date = timezone.now()
            sizename.save()
            return redirect('sizename_detail', pk=sizename.pk)
    else:
        form = SizenameForm(instance=sizename)
    return render(request, 'mechdb_core/sizename_edit.html', {'form': form})
