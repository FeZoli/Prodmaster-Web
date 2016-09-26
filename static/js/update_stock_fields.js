function update_stock_fields(partner_id) {
        $('#product_select').prop('disabled', true);
        $('#unit_text').prop('disabled', true);
        $('#unit_price_recorded').prop('disabled', true);

        var prod_id = $("#product_select").val();
        var url1 = '/FoodMaster/products/get_unit_name/?product_id=' + prod_id;
        $.get(url1, function(result) {
            $('#unit_text').text(result);
        });

        var url3 = '/' + 'FoodMaster'
                    + '/products/get_last_or_recorded_price_of_product/?product_id=' + prod_id
                    + '&partner_id=' + partner_id;
        $.get(url3, function(result) {
            $('#unit_price_recorded').val(result);
        });

        var url2 = '/FoodMaster/actual_stock/get_actual_stock_of_product.xml/?product_id=' + prod_id;
        $.get(url2, function(result) {
             var row = '';
             $(result).find("item").each(function() {
                row += '<tr class="sid_row"><td>'
                       + $(this).find('serial_id').text() + '&nbsp;';
                 if ($(this).find('serial_id').text() != 'Total') {
                    row += $(this).find('quantity').text() + '</td>'
                           +'<td><input name="sid:' + $(this).find('serial_id').text() + '"/></td></tr>';
                 } else {
                     row += '<td>' + $(this).find('quantity').text() + '</td></tr>';
                 }

             });
            $('.sid_row').remove();
            $('#datatable').after(row);
            $('#product_select').prop('disabled', false);
            $('#unit_text').prop('disabled', false);
            $('#unit_price_recorded').prop('disabled', false);
        });
}


$( document ).ready(function() {
    $('#product_select').change(function() {
        update_stock_fields();
    });
});
