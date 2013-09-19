jQuery(function($) {
    console.log('hi there');
    console.log($('#tablename').val());
    tables = tables.replace(/&quot;/g, '"')
    tables = $.parseJSON(tables)

    var get_columns = function(tablename) {
        $("#fields option").remove();
        $.each(tables[tablename], function(i, column) {
            $("#fields").append("<option value='"+column+"'>"+column+"</option>");
        });
    }

    get_columns($('#tablename').val());

    $('#tablename').change( function() {
        var tablename = $('#tablename').val()
        console.log(tablename);
        get_columns(tablename)
    });

    $('#dataformat-selector button').click(function(e) {
        $('button').each(function(i, button) {
            $(button).removeClass('btn-success')
        });
        var format = $(e.target).data('format')
        $(e.target).addClass('btn-success')
        console.log(format);
        $('#dataformat').val(format);
    });

});
