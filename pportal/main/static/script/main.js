


function init() {

    $('#pull').click(function() {
	    $.post(PULL_FORMS_URL, function(data) {
		    console.log(data);
		});
	});

}