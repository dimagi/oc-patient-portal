
function init_form_admin(data) {
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

function init_user_admin(data) {
    reg_code_popup = $('#regpopup').dialog({
	    modal: true,
	    resizable: false,
	    width: 600,
	    autoOpen: false,
	});

    var model = new StudySubjectsViewModel();
    ko.applyBindings(model);
    model.load(data);
}

function init_patient(data) {
    var model = new SubjectScheduleViewModel(data);
    ko.applyBindings(model);
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

function fmt_reg_code(code) {
    code = code || '';
    return code.substring(0, 4) + ' ' + code.substring(4, 8) + ' ' + code.substring(8, 12);
}

function SubjectModel(data) {
    this.id = ko.observable(data.id);
    this.reg_status = ko.observable(data.reg_status);
    this.reg_info = ko.observable(data.reg_info);

    this.register = function(root) {
	$('#subj_id').text(this.id());
	$('#reg_code').html('&mdash;');
	reg_code_popup.dialog('open');

	var model = this;
	$.post('/register/newcode/', {subj_id: this.id(), study: root.selected_study()}, function(data) {
		$('#reg_code').text(fmt_reg_code(data.code));
		model.reg_status('pending');
		model.reg_info(data.code);
	    });
    }
}

function SubjectEventModel(data) {
    this.study_name = ko.observable(data.study_name);
    this.event_name = ko.observable(data.event_name);
    this.event_ordinal = ko.observable(data.ordinal);
    this.form_name = ko.observable(data.form_name);
    this.form_id = ko.observable(data.form_id);
    this.due = ko.observable(data.due);
}

function StudiesViewModel() {
    this.studies = ko.observableArray();

    this.load = function(data) {
	var mapped = $.map(data, function(study) {
		return new StudyModel(study);
	    });
	this.studies(mapped);
    }
}

function StudySubjectsViewModel() {
    this.studies = ko.observableArray();

    this.selected_study = ko.observable();
    this.loading_subjects = ko.observable(false);

    this.subjects = ko.observableArray();
    this._subjects_loader = ko.computed(function() {
	    var study_name = this.selected_study();
	    if (study_name) {
		this.load_subjects_ajax(study_name);
	    } else {
		this.subjects([]);
	    }
	}, this);

    this.load_subjects_ajax = function(study_name) {
	var model = this;
	model.loading_subjects(true);
	$.get(GET_SUBJECTS_URL + study_name, function(data) {
		model.loading_subjects(false);
		model.subjects($.map(data, function(subj) {
			    return new SubjectModel(subj);
			}));
	    });
    }

    this.load = function(data) {
	var mapped = $.map(data, function(study) {
		return new StudyModel(study);
	    });
	this.studies(mapped);
    }

    /*
    this.go = function() {
	var url = PATIENT_LANDING_URL;
	url = url.replace('--subjid--', this.selected_subject());
	url = url.replace('--studyname--', this.selected_study());
	window.location.href = url;
    }
    */

    var model = this;
    this.selectStudy = function(study) {
	model.selected_study(study.tag());
    };

    this.register = function(user) {
	user.register(model);
    }
}

function SubjectScheduleViewModel(data) {
    this.subject_oid = ko.observable(data.subject_oid);
    this.upcoming = ko.observableArray();

    this.load = function(data) {
	var mapped = $.map(data, function(e) {
		return new SubjectEventModel(e);
	    });
	this.upcoming(mapped);
    }
    this.load(data.upcoming);
}

function clearstudy(data) {
    $.post('/debug/clearstudy/' + data.id(), function(data) {
	    window.location.reload();
	});
    return false;
}