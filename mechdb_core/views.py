from django.shortcuts import render
from .models import Container
from django.utils import timezone

# Create your views here.
def index_page(request):
    return render(request, 'mechdb_core/under_construction.html', {})
def containers_map(request):

    # todo: если в реквесте передаётся pk контейнера - создать карту только для него

#    def search_dependent(input_pk):
#        # функция поиска вложенных контейнеров
#        # вход - pk исследуемого контейнера, выход - список подчинённых контейнеров в виде словарей или False
#        containers = Container.objects.filter(owner=request.user, in_container_id=input_pk).order_by('in_container_id')
#        def_output=[]
#        if containers:
#            # если найдены вложенные контейнеры - составляем их список
#            for y in containers:
#                def_output.append({'pk':y.pk, 'title':y.title, 'dependent':search_dependent(y.pk)})
#            return def_output
#        else:
#            # если вложенные контейнеры не найнеды - записываем False для удобства вывода в шаблоне
#            return False

    containers = Container.objects.filter(owner=request.user, in_container_id__isnull=True).order_by('in_container_id')
#    containers_output = []

#    for i in containers:
#        # Начинаем с нулевого уровня (in_container_id==Null) и далее разворачиваем функцией поиска вложенных контов
#        containers_output.append({'pk':i.pk, 'title':i.title, 'dependent':search_dependent(i.pk)})

    return render(request, 'mechdb_core/containers_map.html', {'containers': containers})
