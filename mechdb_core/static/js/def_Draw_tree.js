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
        }
        ;
    }
    ;

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
