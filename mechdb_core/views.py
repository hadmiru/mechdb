from django.shortcuts import render, get_object_or_404
from .models import Container
from django.utils import timezone
from django.utils.html import escape

# Create your views here.
def index_page(request):
    return render(request, 'mechdb_core/under_construction.html', {})

def container_detail(request, pk):
    container = get_object_or_404(Container, pk=pk)
    return render(request, 'mechdb_core/container_detail.html', {'container':container})

def containers_map(request):

    # todo: если в реквесте передаётся pk контейнера - создать карту только для него
    # todo: не забыть экранировать как-нибудь вывод html

    def tree_parse(input_pk):
        # функция парсинга древа контейнеров в хтмl
        # вход - pk исследуемого контейнера, выход - список html тегов для вставки в шаблон
        if input_pk==0:
            containers = Container.objects.filter(owner=request.user, in_container_id__isnull=True).order_by('in_container_id')
        else:
            containers = Container.objects.filter(owner=request.user, in_container_id=input_pk).order_by('in_container_id')

        def_output=[]
        if containers:
            # если найдены вложенные контейнеры - составляем их список
            def_output.append('<UL>')
            for y in containers:
                def_output.append('<LI>')
                def_output.append('<a href="/place/'+str(y.pk)+'">'+escape(y.title)+'</a>')
                def_output.extend(tree_parse(y.pk))
                def_output.append('</LI>')
            def_output.append('</UL>')
            return def_output
        else:
            # если вложенные контейнеры не найнеды - записываем False для удобства вывода в шаблоне
            return []


    containers_output=tree_parse(0)
    return render(request, 'mechdb_core/containers_map.html', {'containers': containers_output})

def containers_map_keybook(request):

    # todo: если в реквесте передаётся pk контейнера - создать карту только для него

    def search_dependent(input_pk):
        # функция поиска вложенных контейнеров
        # вход - pk исследуемого контейнера, выход - список подчинённых контейнеров в виде словарей или False
        if input_pk==0:
            containers = Container.objects.filter(owner=request.user, in_container_id__isnull=True).order_by('in_container_id')
        else:
            containers = Container.objects.filter(owner=request.user, in_container_id=input_pk).order_by('in_container_id')

        def_output=[]
        if containers:
            # если найдены вложенные контейнеры - составляем их список
            for y in containers:
                def_output.append({'pk':y.pk, 'title':y.title, 'dependent':search_dependent(y.pk)})
            return def_output
        else:
            # если вложенные контейнеры не найнеды - записываем False для удобства вывода в шаблоне
            return False

    containers = Container.objects.filter(owner=request.user, in_container_id__isnull=True).order_by('in_container_id')
    containers_output = []
    containers_output=search_dependent(0)

    return render(request, 'mechdb_core/containers_map.html', {'containers': containers_output})
