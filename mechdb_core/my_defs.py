from .models import Container, Equipment
from django.shortcuts import get_object_or_404
from django.utils.html import escape

def tree_parse(input_pk, tree_format, user, need_zero_level=True, tree_level=-1):
    # функция парсинга древа контейнеров в заданном формате
    # формат "li" - выводит в виде html - списка
    # формат "choice" - кортеж для ChoiceField формы
    # вход - pk исследуемого контейнера, выход - список html тегов для вставки в шаблон

    containers = Container.objects.filter(owner=user, in_container_id=input_pk).order_by('title')
    def_output=[]
    tree_level+=1

    if tree_format in ('choice','choice_objects') and need_zero_level and input_pk==0:
        def_output.append((0,"--- верхний уровень ---"))
    if containers:
        # если найдены вложенные контейнеры - составляем их список

        if tree_format=='li':
            def_output.append('<UL>')

        for y in containers:

            if tree_format=='li':
                def_output.append('<LI>')

            if tree_format=='li':
                def_output.append('<a href="/place/'+str(y.pk)+'">'+escape(y.title)+'</a>')
            elif tree_format=='choice' or tree_format=='choice_objects':
                def_output.append((str(y.pk),tree_level*'⠀⠀'+escape(y.title)))

            if tree_format=='choice_objects':
                def_output.extend(tree_parse(y, tree_format, user, False, tree_level))
            else:
                def_output.extend(tree_parse(y.pk, tree_format, user, False, tree_level))


            if tree_format=='li':
                def_output.append('</LI>')

        if tree_format=='li':
            def_output.append('</UL>')

        return def_output
    else:
        return []

def get_container_place(input_pk):
    # Функция строит цепочку контейнеров, в котором расподожен искомый. вход - pk искомого контейнера, выход - список контейнеров цепочки
    def_output=[]
    recycle_flag=True
    while recycle_flag==True:
        recycle_flag=False
        if input_pk:
            recycle_flag=True
            parrent_container=get_object_or_404(Container, pk=input_pk)
            def_output.append((parrent_container.pk,parrent_container.title))
            input_pk=parrent_container.in_container_id
    return def_output[::-1]
