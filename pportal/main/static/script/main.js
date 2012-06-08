

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
		$.post(PULL_FORMS_URL + viewModel.id(), onresult);
	    }, function(data) {
		console.log(data.study_data);
		viewModel.load_metadata(data.study_data);
		$.each(data.errors, function(i, err) {
			console.log(err);
			alert(err);
		    });
	    });
    }
};



function CRFModel(data) {
    this.id = ko.observable(data.id);
    this.oid = ko.observable(data.oid);
    this.name = ko.observable(data.name);
    this.as_of = ko.observable(data.as_of);
}

function StudyEventModel(data) {
    this.name = ko.observable(data.name);
    this.oid = ko.observable(data.oid);
    this.crfs = ko.observableArray($.map(data.crfs, function(crf) {
		return new CRFModel(crf);
	    }));
}

function StudyModel(data) {
    this.id = ko.observable(data.id);
    this.oid = ko.observable(data.oid);
    this.tag = ko.observable(data.tag);
    this.name = ko.observable(data.name);
    this.events = ko.observableArray();

    this.load_metadata = function(events) {
	this.events($.map(events, function(event) {
		    return new StudyEventModel(event);
		}));
    }
    this.load_metadata(data.events);
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

function clearstudy(data) {
    $.post('/debug/clearstudy/' + data.id(), function(data) {
	    window.location.reload();
	});
    return false;
}