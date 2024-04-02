$(function () {
    var CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    $("#step_one_form").submit(function (e) {
        e.preventDefault();
        
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: new FormData($(this)[0]),
            dataType: 'json',
            contentType: false,
            processData: false,
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            beforeSend: function() {
                $("#submit_sheetname_btn").html("Saving <i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
            },
            success: function(response) {
                if (response.success) {
                    window.location.href = response.url;
                } else {
                    $("#submit_sheetname_btn").html(`Next <i class="fas fa-long-arrow-right"></i>`).attr('type', 'submit');
                    var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                    $("#step_one_form .formsms").html(fdback);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });

    $('#headerboxes_form table .form-check-input').change(function() {
        var $row = $(this).closest('tr');
        var $select = $row.find('select');
        var $input = $row.find('input[type="text"]');

        if ($(this).prop('checked')) {
            $select.prop('disabled', false);
            $input.prop('disabled', false);
        } else {
            $select.prop('disabled', true);
            $input.prop('disabled', true);
        }
    });

    $("#headerboxes_form").submit(function (e) {
        e.preventDefault();
        var data = [];

        $("#headerboxes_form table tbody tr").each(function() {
            var header_txt = $(this).find('td:first').text();
            var checkbox_val = $(this).find("input[type='checkbox']").is(':checked');
            var label_txt = $.trim($(this).find('input[type="text"]').val());
            var label_size = $(this).find('select').val();

            var row = {
                'header': header_txt,
                'enabled': checkbox_val,
                'label': label_txt,
                'size': label_size
            }
            data.push(row);
        });

        var formdata = new FormData();
        formdata.append('data', JSON.stringify(data));
        formdata.append('step', 3);
        formdata.append('sheet', $('#sheet_input_id').val());
        
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formdata,
            dataType: 'json',
            contentType: false,
            processData: false,
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            beforeSend: function() {
                $("#back_btn_1").hide();
                $("#forward_btn_2").html("Saving <i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
            },
            success: function(response) {
                if (response.success) {
                    window.location.href = response.url;
                } else {
                    $("#back_btn_1").show();
                    $("#forward_btn_2").html(`Next <i class="fas fa-long-arrow-right"></i>`).attr('type', 'submit');
                    var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                    $("#headerboxes_form .formsms").html(fdback);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });

    $('#id_check').change(function() {
        if ($(this).prop('checked')) {
            $('#id_select').prop('disabled', false);
            $('#id_label').prop('disabled', false);
        } else {
            $('#id_select').prop('disabled', true);
            $('#id_label').prop('disabled', true);
        }
    });

    $('#keys_check').change(function() {
        if ($(this).prop('checked')) {
            $('#keys_letters').prop('disabled', false);
            $('#keys_label').prop('disabled', false);
        } else {
            $('#keys_letters').prop('disabled', true);
            $('#keys_label').prop('disabled', true);
        }
    });

    $("#keys_and_students").submit(function (e) {
        e.preventDefault();

        var data = [
            {
                'id_status': $('#id_check').is(':checked'),
                'id_digits': $('#id_select').val(),
                'id_labels': $.trim($('#id_label').val()),
            },
            {
                'key_status': $('#keys_check').is(':checked'),
                'key_letters': $.trim($('#keys_letters').val()),
                'key_labels': $.trim($('#keys_label').val()),
            }
        ]

        var formdata = new FormData();
        formdata.append('data', JSON.stringify(data));
        formdata.append('step', 4);
        formdata.append('sheet', $('#sheet_input_id').val());
        
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formdata,
            dataType: 'json',
            contentType: false,
            processData: false,
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            beforeSend: function() {
                $("#back_btn_2").hide();
                $("#forward_btn_3").html("Saving <i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
            },
            success: function(response) {
                if (response.success) {
                    window.location.href = response.url;
                } else {
                    $("#back_btn_2").show();
                    $("#forward_btn_3").html(`Next <i class="fas fa-long-arrow-right"></i>`).attr('type', 'submit');
                    
                    var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                    $("#keys_and_students .formsms").html(fdback);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });

    $("#multi_choice_form").submit(function (e) {
        e.preventDefault();

        var questions = {
                'qn_type': $('#multi_type').val(),
                'qn_labels': $.trim($('#multi_labels').val()),
            }

        var formdata = new FormData();
        formdata.append('questions', JSON.stringify(questions));
        formdata.append('qns_type', $('#qn_type_multichoice').val());
        formdata.append('qn_number', $('#multi_questions').val());
        formdata.append('step', 5);
        formdata.append('sheet', $('#custom_sheet_id').val());
        
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formdata,
            dataType: 'json',
            contentType: false,
            processData: false,
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            beforeSend: function() {
                $("#cancel_multi_btn").hide();
                $("#submit_multi_btn").html("Saving <i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
            },
            success: function(response) {
                $("#cancel_multi_btn").show();
                $("#submit_multi_btn").html(`Next <i class="fas fa-long-arrow-right"></i>`).attr('type', 'submit');
                
                if (response.success) {
                    $('#multi_choice_modal').modal('hide');
                    $("#qns_table").load(location.href + " #qns_table");
                    $("#multi_choice_form")[0].reset();
                    $("#multi_choice_form .formsms").html('');
                } else {
                    var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                    $("#multi_choice_form .formsms").html(fdback);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });

    $("#verbose_label_form").submit(function (e) {
        e.preventDefault();

        var short_long_labels = [];
        $("#verbose_label_form table tbody tr").each(function() {
            var short_label = $.trim($(this).find('td .l_short').val());
            var long_label = $.trim($(this).find('td .l_long').val());
            if ((short_label.length == 1) && (long_label.length > 2)) {
                short_long_labels.push({'short': short_label, 'long': long_label});
            }
        });

        if (short_long_labels.length > 0) {
            var formdata = new FormData();
            formdata.append('questions', JSON.stringify(short_long_labels));
            formdata.append('qns_type', $('#qn_type_verboselabel').val());
            formdata.append('qn_number', $('#v_label_num_questions').val());
            formdata.append('show_labels', $('#v_show_labels').val());
            formdata.append('step', 5);
            formdata.append('sheet', $('#custom_sheet_id').val());
            
            $.ajax({
                type: 'POST',
                url: $(this).attr('action'),
                data: formdata,
                dataType: 'json',
                contentType: false,
                processData: false,
                headers: {
                    'X-CSRFToken': CSRF_TOKEN
                },
                beforeSend: function() {
                    $("#verbose_label_form").html('');
                    $("#cancel_vlabel_btn").hide();
                    $("#submit_vlabel_btn").html("Saving <i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
                },
                success: function(response) {
                    $("#cancel_vlabel_btn").show();
                    $("#submit_vlabel_btn").html(`Next <i class="fas fa-long-arrow-right"></i>`).attr('type', 'submit');

                    if (response.success) {
                        $('#verbose_label_modal').modal('hide');
                        $("#qns_table").load(location.href + " #qns_table");
                        $("#verbose_label_form")[0].reset();
                        $("#verbose_label_form .formsms").html('');
                    } else {
                        $('#verbose_label_form .modal-dialog').animate({ scrollTop: 0 }, 'fast');
                        var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                        $("#verbose_label_form .formsms").html(fdback);
                    }
                },
                error: function(xhr, status, error) {
                    console.log(error);
                }
            });
        } else {
            $('#verbose_label_form .modal-dialog').animate({ scrollTop: 0 }, 'fast');
            var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> Please enter atleast 1 verbose label. <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
            $("#verbose_label_form .formsms").html(fdback);
        }
    });

    $("#verbose_questions_form").submit(function (e) {
        e.preventDefault();

        var formdata = new FormData();
        formdata.append('questions', JSON.stringify({'chars': $('#verb_num_chars').val()}));
        formdata.append('qns_type', $('#qn_type_verboseqns').val());
        formdata.append('qn_number', $('#verb_num_questions').val());
        formdata.append('step', 5);
        formdata.append('sheet', $('#custom_sheet_id').val());
        
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formdata,
            dataType: 'json',
            contentType: false,
            processData: false,
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            beforeSend: function() {
                $("#cancel_verbqns_btn").hide();
                $("#submit_verbqns_btn").html("Saving <i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
            },
            success: function(response) {
                $("#cancel_verbqns_btn").show();
                $("#submit_verbqns_btn").html(`Next <i class="fas fa-long-arrow-right"></i>`).attr('type', 'submit');
                
                if (response.success) {
                    $('#verbose_questions_modal').modal('hide');
                    $("#qns_table").load(location.href + " #qns_table");
                    $("#verbose_questions_form")[0].reset();
                    $("#verbose_questions_form .formsms").html('');
                } else {
                    var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                    $("#verbose_questions_form .formsms").html(fdback);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });

    $("#publish_sheet_form").submit(function (e) {
        e.preventDefault();

        var formdata = new FormData();
        formdata.append('step', 6);
        formdata.append('sheet', $('#custom_sheet_id').val());
        
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formdata,
            dataType: 'json',
            contentType: false,
            processData: false,
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            beforeSend: function() {
                $("#cancel_publish_btn").hide();
                $("#publish_btn").html("Publishing <i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
            },
            success: function(response) {
                if (response.success) {
                    window.location.href = response.url;
                } else {
                    $("#cancel_publish_btn").show();
                    $("#publish_btn").html(`Publish <i class="fas fa-check-circle"></i>`).attr('type', 'submit');
                    var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                    $("#verbose_questions_form .formsms").html(fdback);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });
})