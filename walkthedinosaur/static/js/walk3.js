function checkDiff(fromValue, toValue) {
    var fromDate = new Date(fromValue+" PST");
    var toDate = new Date(toValue+" PST");
    var diff = toDate.getTime() - fromDate.getTime();
    var diffDays = Math.ceil(diff / (1000 * 3600 * 24));
    console.log("diffDays = "+diffDays);
    return (diffDays <= 1096) && (diffDays > 0); //365*3 = 1095, so 1096 accounting for a leap year in between.
}

window.onload=function() {
    $('#CSV').click();

    jQuery.validator.addMethod("RealDate", function(value, element) {
	if (value != '') {
	    var strings = value.split('-');
	    var rawmonth = strings[1];
            var rawday   = strings[2];
            var rawyear  = strings[0];
            var checkdate = new Date(value+" PST");
	    return ((rawmonth == checkdate.getMonth()+1) &&
		    (rawday == checkdate.getDate()) &&
		    (rawyear == checkdate.getFullYear()) && 
		    (rawyear >= '1980'));
	}
	return true;
    }, "Incorrect Format");

    jQuery.validator.addMethod("RelevantDate", function(value, element) {
	if (value != '') {
	    var strings = value.split('-');
	    var rawyear  = strings[0];
            var checkdate = new Date(value+" PST");
	    return (rawyear >= 1980);
	}
	return true;
    }, "Year cannot be before 1980");

    jQuery.validator.addMethod("FileThreeYearGap", function() {
	if (($("#pri-date-file-from").val() != "") && ($("#pri-date-file-to").val() != "")) {
    	    var fromValue = $("#pri-date-file-from").val();
    	    var toValue = $("#pri-date-file-to").val();
	    return checkDiff(fromValue,toValue); 
	}
	return true;
    }, "Dates can only be 3 years apart")
    
    jQuery.validator.addMethod("GrantThreeYearGap", function() {
	if (($("#pri-date-grant-from").val() != "") && ($("#pri-date-grant-to").val() != ""))  {
    	    var fromValue = $("#pri-date-grant-from").val();
    	    var toValue = $("#pri-date-grant-to").val();
    	    return checkDiff(fromValue,toValue);
	}
	return true;
    }, "Dates can only be 3 years apart")
    

    $('#pri-date-grant-from').tooltip();
    $('#pri-date-grant-to').tooltip();
    $('#pri-date-file-from').tooltip();
    $('#pri-date-file-to').tooltip();
    $('#cit-date-from').tooltip();
    $('#cit-date-to').tooltip();

    $('#search-form').validate({
	rules: {
        email: {email: true, required: true},
	    pri_date_file_from : {RealDate: true, RelevantDate: true, dateISO: true, FileThreeYearGap: true},
	    pri_date_file_to : {RealDate: true, RelevantDate: true, dateISO: true, FileThreeYearGap: true},
	    pri_date_grant_from : {RealDate: true, RelevantDate: true, dateISO: true, GrantThreeYearGap: true},
	    pri_date_grant_to : {RealDate: true, RelevantDate: true, dateISO: true, GrantThreeYearGap: true},
	    cit_date_from : {RealDate: true, RelevantDate: true, dateISO: true},
	    cit_date_to : {RealDate: true, RelevantDate: true, dateISO: true}
	},
	highlight: function(element) {
            $(element).closest('.form-group').addClass('has-error');
	},
	unhighlight: function(element) {
            $(element).closest('.form-group').removeClass('has-error');
	},
	errorElement: 'span',
	errorClass: 'help-block',
	errorPlacement: function(error, element) {
            if(element.parent('.input-group').length) {
		error.insertAfter(element.parent());
            } else {
		error.insertAfter(element);
            }
	}
    });
}