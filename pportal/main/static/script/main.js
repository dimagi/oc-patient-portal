


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

function init_admin(data) {
    var model = new StudiesViewModel();

    register_update_handler($('#get_studies'), function(onresult) {
	    $.get(GET_STUDIES_URL, onresult);
	}, function(data) {
	    console.log(data);
	    model.load(data);
	});

    $('#clear_all').click(function() {
	    $.post('/debug/clearall', function(data) {
		    window.location.reload();
		});
	    return false;
	});

    ko.applyBindings(model);
    model.load(data);
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

ko.bindingHandlers.ajaxbutton = {
    init: function(element, valueAccessor, allBindingsAccessor, viewModel) {
	register_update_handler($(element), function(onresult) {
		setTimeout(function() { onresult(viewModel.name()); }, 2000);
	    }, function(data) {
		console.log('boom on ' + data);
	    });
    }
};

function CRFModel(data) {
    this.id = ko.observable(data.id);
    this.name = ko.observable(data.name);
    this.as_of = ko.observable(data.as_of);
}

function StudyEventModel(data) {
    this.name = ko.observable(data.name);
    this.crfs = ko.observableArray($.map(data.crfs, function(crf) {
		return new CRFModel(crf);
	    }));
}

function StudyModel(data) {
    this.id = ko.observable(data.id);
    this.name = ko.observable(data.name);
    this.events = ko.observableArray($.map(data.events, function(event) {
		return new StudyEventModel(event);
	    }));

    this.load_crfs = function() {
	console.log('here i am');
    }
}

function StudiesViewModel() {
    this.studies = ko.observableArray();

    var model = this;
    this.load = function(data) {
	var mapped = $.map(data, function(study) {
		return new StudyModel(study);
	    });
	model.studies(mapped);
    }
}

function oncrfupdate(data) {
    data.load_crfs();
}