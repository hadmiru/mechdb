from .models import Container, Equipment
from django.shortcuts import get_object_or_404
from django.utils.html import escape

def parse_objects_tree_to_dict(input_pk, params, user):
    if input_pk==0:
        daughters = Container.objects.filter(owner=user, in_container__isnull=True).order_by('title')
        equipments = Equipment.objects.filter(owner=user, in_container__isnull=True).order_by('sizename')
    else:
        daughters = Container.objects.filter(owner=user, in_container=input_pk).order_by('title')
        equipments = Equipment.objects.filter(owner=user, in_container=input_pk).order_by('sizename')

    def_response={}
    def_response['pk'] = input_pk
    if input_pk==0:
        def_response['title'] = 'Верхний уровень'
    else:
        def_response['title'] = get_object_or_404(Container, pk=input_pk).title

    def_response['equipments'] = []
    if equipments:
        for z in equipments:
            def_response['equipments'].append({
                'pk': z.pk,
                'title': z.sizename.title,
                'serial_number': z.serial_number
                })

    def_response['daughters'] = []
    if daughters:
        for y in daughters:
            def_response['daughters'].append(parse_objects_tree_to_dict(y.pk, params, user))

    return def_response






def tree_parse(input_pk, tree_format, user, need_zero_level=True, tree_level=-1):
    # функция парсинга древа контейнеров в заданном формате
    # формат "li" - выводит в виде html - списка
    # формат "li equipment" - аналогично плюс оборудование в контейнерах
    # формат "choice" - кортеж для ChoiceField формы
    # вход - pk исследуемого контейнера, выход - список html тегов для вставки в шаблон

    if input_pk==0:
        containers = Container.objects.filter(owner=user, in_container__isnull=True).order_by('title')
        equipments = Equipment.objects.filter(owner=user, in_container__isnull=True).order_by('sizename')
    else:
        containers = Container.objects.filter(owner=user, in_container=input_pk).order_by('title')
        equipments = Equipment.objects.filter(owner=user, in_container=input_pk).order_by('sizename')
    def_output=[]
    if tree_format == 'li equipment' and equipments:
        for z in equipments:
            def_output.append('<br>')
            def_output.append('<a class="equipmenthref" href="/equipment/'+str(z.pk)+'">[ '+z.sizename.title+' № '+z.serial_number+' ]</a>')
    tree_level+=1

    if tree_format in ('choice','choice_objects') and need_zero_level and input_pk==0:
        def_output.append((0,"--- верхний уровень ---"))
    if containers:
        # если найдены вложенные контейнеры - составляем их список

        if tree_format in ('li','li equipment'):
            def_output.append('<UL>')

        for y in containers:

            if tree_format == 'li':
                def_output.append('<LI>')
            elif tree_format == 'li equipment':
                def_output.append('<LI style="line-height:1;margin-top:10px">')

            if tree_format in ('li','li equipment'):
                def_output.append('<a href="/place/'+str(y.pk)+'" class="containerhref">'+escape(y.title)+'</a>')
            elif tree_format=='choice' or tree_format=='choice_objects':
                def_output.append((str(y.pk),tree_level*'⠀⠀'+escape(y.title)))

            if tree_format=='choice_objects':
                def_output.extend(tree_parse(y, tree_format, user, False, tree_level))
            else:
                def_output.extend(tree_parse(y.pk, tree_format, user, False, tree_level))

            if tree_format in ('li','li equipment'):
                def_output.append('</LI>')

        if tree_format in ('li','li equipment'):
            def_output.append('</UL>')

    return def_output

def get_container_place(input_pk):
    # Функция строит цепочку контейнеров, в котором расподожен искомый. вход - pk искомого контейнера, выход - список контейнеров цепочки
    def_output=[]
    recycle_flag=True
    while recycle_flag==True:
        recycle_flag=False
        if input_pk:
            recycle_flag=True
            parrent_container=Container.objects.get(pk=input_pk)
            def_output.append((parrent_container.pk,parrent_container.title))

            if parrent_container.in_container:
                input_pk=parrent_container.in_container.pk
            else: input_pk=0
    return def_output[::-1]
