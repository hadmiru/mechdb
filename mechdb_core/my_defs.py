from .models import Container, Equipment
from django.utils.html import escape

def tree_parse(input_pk, tree_format, user, tree_level=-1):
    # функция парсинга древа контейнеров в заданном формате
    # формат "li" - выводит в виде html - списка
    # формат "choice" - кортеж для ChoiceField формы
    # вход - pk исследуемого контейнера, выход - список html тегов для вставки в шаблон

    containers = Container.objects.filter(owner=user, in_container_id=input_pk).order_by('title')
    def_output=[]
    tree_level+=1

    if tree_format=='choice' and input_pk==0:
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
            elif tree_format=='choice':
                def_output.append((str(y.pk),tree_level*'⠀⠀'+escape(y.title)))

            def_output.extend(tree_parse(y.pk, tree_format, user, tree_level))

            if tree_format=='li':
                def_output.append('</LI>')

        if tree_format=='li':
            def_output.append('</UL>')

        return def_output
    else:
        return []

def get_container_place(input_pk):
    def_output=[]
    recycle_flag=True
    while recycle_flag==True:
        recycle_flag=False
        if input_pk:
            recycle_flag=True
            parrent_container=Container.objects.get(pk=input_pk)
            def_output.append((parrent_container.pk,parrent_container.title))
            input_pk=parrent_container.in_container_id
    return def_output[::-1]
