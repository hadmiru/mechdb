from django.shortcuts import render, get_object_or_404
from .models import Container
from django.utils import timezone
from django.utils.html import escape
from .forms import ContainerForm
from django.shortcuts import redirect
from .my_defs import tree_parse


# Create your views here.
def index_page(request):
    return render(request, 'mechdb_core/under_construction.html', {})

def container_detail(request, pk):
    container = get_object_or_404(Container, pk=pk)
    return render(request, 'mechdb_core/container_detail.html', {'container':container})

def containers_map(request):

    if request.POST:
        containers_output=tree_parse(0, request.POST, request.user)
    else:
        containers_output=tree_parse(0, 'li', request.user)

    return render(request, 'mechdb_core/containers_map.html', {'containers': containers_output})

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
