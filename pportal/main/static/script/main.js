


function init_patient(xforms) {

    $('#pull').click(function() {
	    $('#pull').attr('disabled', 'true');
	    $.post(PULL_FORMS_URL, function(data) {
		    $('#pull').removeAttr('disabled');
		    console.log(data);
		    xform_list(data.forms);
		    $.each(data.errors, function(i, err) {
			    console.log(err);
			    alert(err);
			});
		});
	});

    $('#clear').click(function() {
	    $.post('/debug/clearforms', function(data) {
		    window.location.reload();
		});
	    return false;
	});

    xform_list(xforms);

}

function init_admin() {
    register_update_handler($('#get_studies'), function(onresult) {
	    $.get(GET_STUDIES_URL, onresult);
	}, function(data) {
	    console.log('studies', data);
	});

    $('#clear_all').click(function() {
	    alert('implement me!');
	    return false;
	});
}

function register_update_handler(button, ajax, onresult) {
    button.click(function() {
	    button.attr('disabled', 'true');
	    ajax(function(data) {
		    button.removeAttr('disabled');
		    onresult(data);
		});
	});

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