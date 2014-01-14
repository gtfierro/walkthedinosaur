window.onload=function() {

    var filterFunction = function() {
    //split the current value of searchInput
	var fullData = this.value;
	var data = this.value.split(" ");
    //create a jquery object of the rows
	var tableToFilter = "#"+$(this).attr("tableToFilter");
	var colToFilter = "#"+$(this).attr("colToFilter");
	var jo = $(tableToFilter).find("tr");
	if (this.value == "") {
            jo.show();
            return;
	}
    //hide all the rows
	jo.hide();

    //Recusively filter the jquery object to get results.
	jo.filter(function (i,v) {
            var $t = $(this).find(colToFilter);
	    var tString = $t.clone().html().toLowerCase();
            for (var d = 0; d < data.length; ++d) {
		if (tString.indexOf(data[d].toLowerCase()) <= -1) {
                    return false;
		}
            }
            return true;
	})
    //show the rows that match.
	    .show();
    };

    $("#filterQID").keyup(filterFunction);
    $("#filterQQuery").keyup(filterFunction);
    $("#filterQDate").keyup(filterFunction);
    $("#filterQFormat").keyup(filterFunction);
    $("#filterQEmail").keyup(filterFunction);
    $("#filterQStatus").keyup(filterFunction);

    $("#filterCID").keyup(filterFunction);
    $("#filterCQuery").keyup(filterFunction);
    $("#filterCDate").keyup(filterFunction);
    $("#filterCFormat").keyup(filterFunction);
    $("#filterCEmail").keyup(filterFunction);
    $("#filterCStatus").keyup(filterFunction);

    // Prevent page from going to top when clicking glyphicons.
    // The class should be noTop for the link wrapper around the glyphicon.
    $('.noTop').click(function(e) {
	e.preventDefault();
    });

}