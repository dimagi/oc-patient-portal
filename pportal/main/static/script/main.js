


function init(xforms) {

    $('#pull').click(function() {
	    $.post(PULL_FORMS_URL, function(data) {
		    console.log(data);
		    xform_list(data);
		});
	});

    xform_list(xforms);

}

function xform_list(xforms) {
    $list = $('#xforms').find('tbody');
    $list.empty();
    $.each(xforms, function(i, xf) {
	    var $row = $('<tr />');

	    var $name = $('<td />');
	    $name.text(xf.name);

	    var $timestamp = $('<td />');
	    $timestamp.text(xf.as_of);

	    var $go = $('<td><a>fill out</a></td>');
	    $go.find('a').attr('href', '/formplay/' + xf.id);

	    $row.append($name);
	    $row.append($timestamp);
	    $row.append($go);
	    $list.append($row);
	});
}