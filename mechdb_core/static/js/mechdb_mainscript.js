var loadingAnimation = '<img id="loadingAnimation" src="/static/img/loading-gears.gif">';
var csrftoken;

// функция возвращает карту объектов в виде строки с html кодом


function draw_tree(input_container) {
    var function_response = '';
    function_response += '<UL class="mdb_tree_element">';

    if (input_container.equipments) {
        for (var i = 0; i < input_container.equipments.length; i++) {
            function_response += '<a class="mdb_equipment mdb_tree_element" href = "/equipment/' + input_container.equipments[i].pk + '">';
            function_response += input_container.equipments[i].title + ' № ' + input_container.equipments[i].serial_number;
            function_response += '</a>';
            function_response += '<BR>';
        };
    };

    if (input_container.daughters) {
        for (var z = 0; z < input_container.daughters.length; z++) {
            function_response += '<LI class="mdb_tree_element">';
            function_response += '<a class="mdb_container mdb_tree_element" href = "/place/' + input_container.daughters[z].pk + '">';
            function_response += input_container.daughters[z].title;
            function_response += '</a>';
            function_response += draw_tree(input_container.daughters[z]);
            function_response += '</LI>';
        };
    };

    function_response += '</UL>';
    return function_response;
};

// функция генерирует таблицы на основе данных с сервера
// html_class и html_id могут быть переданы в трёх местах
// в header (нулевой элемент) - для самой таблицы
// как параметр для каждого TR
// как параметр для каждого TD
function make_table (table) {
    var function_response = '';
    var anchor = '';

    // Генерация шапки таблицы
    function_response += '<TABLE>';
    function_response += '<TR class = "table_header">';
    for (var i = 0; i < table.table_header.length; i++) {
        function_response += '<TD>';
            function_response += '<p>' + table.table_header[i].title + '</p>';
        function_response += '</TD>';
    }
    function_response += '</TR>';

    // Генерация контента таблицы
    // y - цикл по строкам
    for (var y = 0; y < table.lines.length; y++) {
        function_response += '<TR class ="' + table.lines[y].html_class + '" id="' + table.lines[y].html_id + '">';

        // x -цикл по столбцам
        for (var x = 0; x < table.table_header.length; x++) {
            function_response += '<TD>';
            anchor = table.table_header[x].anchor;

            // z - цикл по <p>, если их больше одного то в конце будут разделены separator
            for (var z = 0; z < table.lines[y][anchor].length; z++) {
                function_response += '<p>' + table.lines[y][anchor][z].title + '</p>';
                if (table.lines[y][anchor][z].separator) {
                    function_response += '<p>' + table.lines[y][anchor][z].separator + '</p>';
                };
            } // end for z

            function_response += '</TD>';
        }; // end for x

        function_response += '</TR>';

    } // end for y -->



    function_response += '</TABLE>';

    return function_response;
}

//функция создаёт html-наполнение для content_container
function generate_content (data) {
    var function_response = '';
        pageTitles = {
            'main': 'Домашняя страница: карта объектов',
            'actions_list': 'Список воздействий',
            'equipment_list': 'Список оборудования',
            'sparepart_list': 'Список запасных частей',
            'operating_time': 'Наработка',
            'files_list': 'Файлы',
            'photos_list': 'Фотографии',
            'recyclebin': 'Корзина'
    };

    function_response += '<h2>' + pageTitles[data.pagetype] + '</h2>';

    var a = 2 + 2;

    switch (data.pagetype) {
        case 'main':
            function_response += draw_tree(data.server_response);
            break;

        case 'actions_list':
            function_response += make_table(data.server_response);
            break;

        case 'equipment_list':
            function_response += 'Здесь будет информация';
            break;

        case 'sparepart_list':
            function_response += 'Здесь будет информация';
            break;

        case 'operating_time':
            function_response += 'Здесь будет информация';
            break;

        case 'files_list':
            function_response += 'Здесь будет информация';
            break;

        case 'photos_list':
            function_response += 'Здесь будет информация';
            break;

        case 'recyclebin':
            function_response += 'Здесь будет информация';
            break;

        default:
            function_response += '<p>Извините, что-то пошло не так :(</p>';
    }

    return function_response
}

// функция оформляет перезагрузку главных страниц и отправляет ajax запросы на сервер
// для генерации контента используется функция generate_content
// принимает параметры:
// pagetype: тип страницы main - главная страница

function load_page(data) {

    var $content_container = $('#content');
    var $ajax_indicator = $('#ajax_response_waiting');
    var content = '';

    ajaxParams = {
            'main': {
                'url': '/get_objects_tree/',
                'data': {
                    'initiate_pk': 0,
                    'equipment': true,
                    'spare_parts': true
                }},

            'actions_list': {
                'url': '/get_actions_list/',
                'data': {
                    'quantity_for_page': 30,
                    'page': 0
                }
            },

            'equipment_list': {
                'url': '',
                'data': {

                }},

            'sparepart_list': {
                'url': '',
                'data': {

                }},

            'operating_time': {
                'url': '',
                'data': {

                }},

            'files_list': {
                'url': '',
                'data': {

                }},

            'photos_list': {
                'url': '',
                'data': {

                }},

            'recyclebin': {
                'url': '',
                'data': {

                }}
    };

    $ajax_indicator.fadeIn();
    $.ajax({
        url: ajaxParams[data.pagetype].url,
        type: 'POST',
        headers: {"X-CSRFToken": csrftoken},
        data: ajaxParams[data.pagetype].data,
        success: function (json) {
            $ajax_indicator.fadeOut();
            $content_container.fadeOut(500, function () {
                $content_container.html('');

                content = generate_content({
                    'pagetype': data.pagetype,
                    'server_response': json.result
                });

                $content_container.append(content); // generate_content end
                $content_container.fadeIn(500);
            }); //end fadeout
        }, //end success
        error: function () {
            $ajax_indicator.hide();
             $content_container.html('<p>Извините, что-то пошло не так :(</p>');

        } // end error
    }); // end ajax
};

$(document).ready(function() {
    // начало работы сайта
    csrftoken = $("[name=csrfmiddlewaretoken]").val();
    load_page({
                'pagetype': 'main'
            });

    // ОБРАБОТЧИКИ СОБЫТИЙ
    // #mainMenu отслеживает клики на свои кнопки
    $('#mainMenu').on('click', '.mainMenu_element:not(.choiced)', function () {

        load_page({
            'pagetype': $(this).attr('id')
        }); // end load_page

        $('#mainMenu .choiced').removeClass('choiced');
        $(this).addClass('choiced');
    }); // окончание функции on
}); // end ready
