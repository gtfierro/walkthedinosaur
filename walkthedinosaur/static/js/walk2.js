jQuery(function($) {
    console.log('hi there 2');

    $('#dataformat-selector button').click(function(e) {
	console.log('function for click called');
        $('button').each(function(i, button) {
            $(button).removeClass('btn-success')
        });
        var format = $(e.target).data('format')
        $(e.target).addClass('btn-success')
        console.log(format);
        $('#dataformat').val(format);
    });

});
