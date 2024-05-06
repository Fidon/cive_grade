$(function () {
    var CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    var row_count = $("#qns_table tbody tr").length;
    var remove_questions = true;
    var row_number_added = false;

    function isNumber(value) {
        return /^\d+$/.test(value);
    }

    // parse string into js object/array
    function parseInput(inputId) {
        var input = $(inputId).val().replace(/'/g, '"').replace(/True/g, 'true').replace(/False/g, 'false');
        return JSON.parse(input);
    }

    function add_row_number() {
        if (row_number_added == false) {
            row_count = $("#qns_table tbody tr").length;
            $("#qns_table tbody tr").each(function (index, element) {
                if(index <= (row_count-2)) {
                    $(this).find('td:nth-child(1)').text(index+1);
                }
            });

            var html_contents = ``;
            var header_boxes = parseInput("#header_boxes_input");
            var box_width = ((header_boxes[2].enabled) && (header_boxes[3].enabled)) ? "w-50" : "w-100";
            
            if (header_boxes[0].enabled) {
                html_contents += `<div class="sheeet_head">` +
                `<div class="title">Student ID:</div>` +
                `<div class="id_boxes">`;
                for (let i=0; i<13; i++) { html_contents += `<span></span>`; }
                html_contents += `</div></div>`;
            }
            if (header_boxes[2].enabled) {
                html_contents += `<div class="sheeet_head ${box_width}">` +
                `<div class="title">Exam:</div>` +
                `<div class="id_boxes">`;
                for (let i=0; i<5; i++) { html_contents += `<span></span>`; }
                html_contents += `</div></div>`;
            }
            if (header_boxes[3].enabled) {
                html_contents += `<div class="sheeet_head ${box_width}">` +
                `<div class="title">Class:</div>` +
                `<div class="id_boxes">`;
                for (let i=0; i<5; i++) { html_contents += `<span></span>`; }
                html_contents += `</div></div>`;
            }
            if (header_boxes[1].enabled) {
                html_contents += `<div class="sheeet_head m-0">` +
                `<div class="title">Names:</div>` +
                `<div class="box"></div></div>`;
            }
            $('#answers_div').before(html_contents);

            $("#qns_table tbody tr").each(function (index, element) {
                if(!($(this).attr('id') == "select_qns_tr")) {
                    var question_type = $(this).find('td:nth-child(1)').attr('class');
                    var question_number = $(this).find('td:nth-child(1)').text();
                    var question_labels = "";
                    html_contents = ``;
                    
                    if (question_type == "multichoice") {
                        question_labels = $(this).find('td:nth-child(3)').text();
                        html_contents += `<div class="multichoice"><span>${question_number}</span>`;
                        for (let i=0; i<question_labels.length; i++) { html_contents += `<span>${question_labels[i]}</span>` }
                        html_contents += `</div>`;
                    } else if (question_type == "verboselabel") {
                        var label_list = [];
                        question_labels = $(this).find('td:nth-child(3) li');
                        question_labels.each(function(index) { label_list.push($(this).text()); });
                        html_contents += `<div class="multilabel">` +
                        `<div><span class="circle">${question_number}</span><span class="circle">.</span><span class="text">${label_list[0]}</span></div>`;
                        for (let i=1; i<question_labels.length; i++) {
                            html_contents += `<div><span class="circle">.</span><span class="circle">.</span><span class="text">${label_list[i]}</span></div>`;
                        }
                        html_contents += `</div>`;
                    } else {
                        question_labels = parseInt($(this).find('td:nth-child(3)').text().split(": ")[1]);
                        html_contents += `<div class="verbose"><span>${question_number}</span>`;
                        for (let i=0; i<question_labels; i++) { html_contents += `<span>.</span>`; }
                        html_contents += `</div>`;
                    }
                    $('#answers_div').append(html_contents);
                }
            });
            row_number_added = true;
        }
    }
    setInterval(add_row_number, 2000);

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
        var $input = $row.find('input[type="text"]');

        if ($(this).prop('checked')) {
            $input.prop('disabled', false);
        } else {
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

            var row = {
                'header': header_txt,
                'enabled': checkbox_val,
                'label': label_txt
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

    $("#multi_choice_form").submit(function (e) {
        e.preventDefault();

        var questions = {
                'qn_type': parseInt($('#multi_type').val()),
                'qn_labels': $.trim($('#multi_labels').val()),
            }

        var formdata = new FormData();
        formdata.append('questions', JSON.stringify(questions));
        formdata.append('qns_type', $('#qn_type_multichoice').val());
        formdata.append('qn_number', $('#multi_questions').val());
        formdata.append('step', 4);
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
                    row_number_added = false;
                    window.location.reload();
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
        var short_labels_array = [];
        $("#verbose_label_form table tbody tr").each(function() {
            var short_label = $.trim($(this).find('td .l_short').val());
            var long_label = $.trim($(this).find('td .l_long').val());
            if ((short_label.length == 1) && (long_label.length > 2)) {
                short_long_labels.push({'short': short_label.toUpperCase(), 'long': long_label});
                short_labels_array.push(short_label);
            }
        });

        var duplicate_labels = (input_array) => {
            const duplicates =input_array.filter((item, index) =>input_array.indexOf(item) !== index);
            return Array.from(new Set(duplicates));
        }

        if(duplicate_labels(short_labels_array).length == 0) {
            if (short_long_labels.length > 1) {
                var formdata = new FormData();
                formdata.append('questions', JSON.stringify(short_long_labels));
                formdata.append('qns_type', $('#qn_type_verboselabel').val());
                formdata.append('qn_number', $('#v_label_num_questions').val());
                formdata.append('show_labels', $('#v_show_labels').val());
                formdata.append('step', 4);
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
                            row_number_added = false;
                            window.location.reload();
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
                var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> Please enter atleast 2 verbose labels. <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                $("#verbose_label_form .formsms").html(fdback);
            }
        } else {
            $('#verbose_label_form .modal-dialog').animate({ scrollTop: 0 }, 'fast');
            var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> Short labels should be unique in each field. <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
            $("#verbose_label_form .formsms").html(fdback);
        }
    });

    $("#verbose_questions_form").submit(function (e) {
        e.preventDefault();

        var formdata = new FormData();
        formdata.append('questions', JSON.stringify({'chars': parseInt($('#verb_num_chars').val())}));
        formdata.append('qns_type', $('#qn_type_verboseqns').val());
        formdata.append('qn_number', $('#verb_num_questions').val());
        formdata.append('step', 4);
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
                    row_number_added = false;
                    window.location.reload();
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
    
    $('#publish_sheet_form').on('click', '#remove_qns_btn', function(e) {
        e.preventDefault();
        if (remove_questions) {
            var questions_to_remove = [];
            var current_row_id = '';
            var current_row_count = 0;
            var row_index_array = [];
            $("#qns_table tbody tr").each(function (index, element) {
                if((index <= (row_count-2)) && $(this).find('td:nth-child(4) input').is(':checked')) {
                    row_index_array.push(index);
                    var tr_class = $(this).attr('class');
                    if(current_row_id == tr_class) {
                        current_row_count++;
                    } else {
                        if((current_row_count > 0) && current_row_id !== '') {
                            questions_to_remove.push({
                                'id': parseInt(current_row_id.split('_')[1]),
                                'qns': current_row_count
                            });
                        }
                        current_row_id = tr_class;
                        current_row_count = 1;
                    }
                }
            });
            if((current_row_count > 0) && current_row_id !== '') {
                questions_to_remove.push({
                    'id': parseInt(current_row_id.split('_')[1]),
                    'qns': current_row_count
                });

                
                var formdata = new FormData();
                formdata.append('questions', JSON.stringify(questions_to_remove));
                formdata.append('step', 6);
                
                $.ajax({
                    type: 'POST',
                    url: $("#publish_sheet_form").attr('action'),
                    data: formdata,
                    dataType: 'json',
                    contentType: false,
                    processData: false,
                    headers: {
                        'X-CSRFToken': CSRF_TOKEN
                    },
                    beforeSend: function() {
                        remove_questions = false;
                        $("#remove_qns_btn").html("<i class='fas fa-spinner fa-pulse'></i> Removing");
                    },
                    success: function(response) {
                        $("#remove_qns_btn").html(`<i class="fas fa-trash"></i> Remove selected`);
                        if (response.success) {
                            $("#qns_table tbody tr").each(function (index, element) {
                                if(row_index_array.includes(index)) {
                                    $(this).remove();
                                }
                            });
                            row_number_added = false;
                            window.location.reload();
                        } else {
                            var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                            $("#publish_sheet_form .formsms").html(fdback);
                        }
                        remove_questions = true
                    },
                    error: function(xhr, status, error) {
                        console.log(error);
                    }
                });
            } else {
                var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> Select atleast one question to remove. <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                $("#publish_sheet_form .formsms").html(fdback);
            }
        }
    });

    $("#publish_confirm_form").submit(function (e) {
        e.preventDefault();

        var formdata = new FormData();
        formdata.append('step', 5);
        formdata.append('sheet', $('#custom_sheet_id').val());
        
        $.ajax({
            type: 'POST',
            url: $("#publish_sheet_form").attr('action'),
            data: formdata,
            dataType: 'json',
            contentType: false,
            processData: false,
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            beforeSend: function() {
                $("#publish_cancel_btn").hide();
                $("#publish_confirm_btn").html("Publishing <i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
            },
            success: function(response) {
                if (response.success) {
                    window.location.href = response.url;
                } else {
                    $("#publish_cancel_btn").show();
                    $("#publish_confirm_btn").html(`Publish <i class="fas fa-check-circle"></i>`).attr('type', 'submit');
                    var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                    $("#publish_confirm_form .formsms").html(fdback);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });

    function get_dates(dt) {
        const mindate = $('#min_date').val();
        const maxdate = $('#max_date').val();
        let dt_start = "";
        let dt_end = "";
        if (mindate) dt_start = mindate + ' 00:00:00.000000';
        if (maxdate) dt_end = maxdate + ' 23:59:59.999999';
        return (dt === 0) ? dt_start : dt_end;
    }

    $("#customsheets_table thead tr").clone(true).attr('class','filters').appendTo('#customsheets_table thead');
    var customsheets_table = $("#customsheets_table").DataTable({
        fixedHeader: true,
        processing: true,
        serverSide: true,
        ajax: {
            url: $("#custom_sheet_url").val(),
            type: "POST",
            data: function (d) {
                d.startdate = get_dates(0);
                d.enddate = get_dates(1);
            },
            dataType: 'json',
            headers: { 'X-CSRFToken': CSRF_TOKEN },
        },
        columns: [
            { data: 'count' },
            { data: 'regdate' },
            { data: 'names' },
            { data: 'questions' },
            { data: 'status' },
            { data: 'action' },
        ],
        order: [[2, 'asc']],
        paging: true,
        lengthMenu: [[10, 20, 30, 50, -1], [10, 20, 30, 50, "All"]],
        pageLength: 10,
        lengthChange: true,
        autoWidth: true,
        searching: true,
        bInfo: true,
        bSort: true,
        orderCellsTop: true,
        columnDefs: [{
            "targets": [0, 5],
            "orderable": false,
        },
        {
            targets: [2, 4],
            className: 'text-start',
        },
        {
            targets: 5,
            className: 'align-middle text-nowrap text-center',
            createdCell: function (cell, cellData, rowData, rowIndex, colIndex) {
                var cell_content =`<button type="button" class="btn btn-bblight btn-sm text-white"><i class="fas fa-trash-alt"></i></button>`;
                $(cell).html(cell_content);
                $(cell).find('button').on('click', function(e) {
                    e.preventDefault();
                    $("#confirm_delete_modal strong").text(rowData.names);
                    $("#sheet_del_id").val(rowData.id);
                    $("#confirm_delete_modal").modal('show');
                });
            }
        }],
        dom: "lBfrtip",
        buttons: [
            { // Copy button
                extend: "copy",
                text: "<i class='fas fa-clone'></i>",
                className: "btn btn-bblight text-white",
                titleAttr: "Copy",
                title: "Custom answer sheets - CIVE Grade",
                exportOptions: {
                    columns: [0, 1, 2, 3, 4]
                }
            },
            { // PDF button
                extend: "pdf",
                text: "<i class='fas fa-file-pdf'></i>",
                className: "btn btn-bblight text-white",
                titleAttr: "Export to PDF",
                title: "Custom answer sheets - CIVE Grade",
                filename: 'custom-sheets-civegrade',
                orientation: 'portrait',
                pageSize: 'A4',
                footer: true,
                exportOptions: {
                    columns: [0, 1, 2, 3, 4],
                    search: 'applied',
                    order: 'applied'
                },
                tableHeader: {
                    alignment: "center"
                },
                customize: function(doc) {
                    doc.styles.tableHeader.alignment = "center";
                    doc.styles.tableBodyOdd.alignment = "center";
                    doc.styles.tableBodyEven.alignment = "center";
                    doc.styles.tableHeader.fontSize = 7;
                    doc.defaultStyle.fontSize = 6;
                    doc.content[1].table.widths = Array(doc.content[1].table.body[1].length + 1).join('*').split('');

                    var body = doc.content[1].table.body;
                    for (i = 1; i < body.length; i++) {
                        doc.content[1].table.body[i][0].margin = [3, 0, 0, 0];
                        doc.content[1].table.body[i][0].alignment = 'center';
                        doc.content[1].table.body[i][1].alignment = 'center';
                        doc.content[1].table.body[i][2].alignment = 'left';
                        doc.content[1].table.body[i][3].alignment = 'center';
                        doc.content[1].table.body[i][4].alignment = 'left';
                        doc.content[1].table.body[i][4].margin = [0, 0, 3, 0];

                        for (let j = 0; j < body[i].length; j++) {
                            body[i][j].style = "vertical-align: middle;";
                        }
                    }
                }
            },
            { // Export to excel button
                extend: "excel",
                text: "<i class='fas fa-file-excel'></i>",
                className: "btn btn-bblight text-white",
                titleAttr: "Export to Excel",
                title: "Custom answer sheets - CIVE Grade",
                exportOptions: {
                    columns: [0, 1, 2, 3, 4]
                }
            },
            { // Print button
                extend: "print",
                text: "<i class='fas fa-print'></i>",
                className: "btn btn-bblight text-white",
                title: "Custom answer sheets - CIVE Grade",
                orientation: 'portrait',
                pageSize: 'A4',
                titleAttr: "Print",
                footer: true,
                exportOptions: {
                    columns: [0, 1, 2, 3, 4],
                    search: 'applied',
                    order: 'applied'
                },
                tableHeader: {
                    alignment: "center"
                },
                customize: function (win) {
                    $(win.document.body).css("font-size","11pt");
                    $(win.document.body).find("table").addClass("compact").css("font-size","inherit");
                }
            }
        ],
        initComplete: function() {
            var api = this.api();
            api.columns([0, 1, 2, 3, 4, 5]).eq(0).each(function (colIdx) {
                var cell = $(".filters th").eq($(api.column(colIdx).header()).index());
                if (colIdx == 1) {
                    var calendar =`<button type="button" class="btn btn-sm btn-bblight text-white" data-bs-toggle="modal" data-bs-target="#date_filter_modal"><i class="fas fa-calendar-alt"></i></button>`;
                    cell.html(calendar);
                    $("#date_clear").on("click", function() {
                        $("#min_date").val("");
                        $("#max_date").val("");
                    });
                    $("#date_filter_btn").on("click", function() {
                        customsheets_table.draw();
                    });
                } else if (colIdx == 0 || colIdx == 5) {
                    cell.html("");
                } else {
                    if (colIdx == 2 || colIdx == 4) {
                        $(cell).html("<input type='text' class='text-ttxt float-start w-auto' placeholder='Filter..'/>");
                    } else {
                        $(cell).html("<input type='text' class='text-ttxt' placeholder='Filter..'/>");
                    }
                    $("input", $(".filters th").eq($(api.column(colIdx).header()).index()))
                    .off("keyup change").on("keyup change", function(e) {
                        e.stopPropagation();
                        $(this).attr('title', $(this).val());
                        var regexr = "{search}";
                        var cursorPosition = this.selectionStart;
                        api.column(colIdx).search(
                            this.value != '' ? regexr.replace('{search}', this.value) : '',
                            this.value != '',
                            this.value == ''
                            ).draw();
                        $(this).focus()[0].setSelectionRange(cursorPosition, cursorPosition);
                    });
                }
            });
        }
    });

    $("#sheets_search").keyup(function() {
        customsheets_table.search($(this).val()).draw();
    });

    $("#sheets_filter_clear").click(function (e) { 
        e.preventDefault();
        $("#sheets_search").val('');
        customsheets_table.search('').draw();
    });

    $("#confirm_del_btn").click(function (e) { 
        e.preventDefault();
        
        var formdata = new FormData();
        formdata.append('delete_sheet', parseInt($('#sheet_del_id').val()));
        
        $.ajax({
            type: 'POST',
            url: $("#custom_sheet_url").val(),
            data: formdata,
            dataType: 'json',
            contentType: false,
            processData: false,
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            beforeSend: function() {
                $("#cancel_del_btn").hide();
                $("#confirm_del_btn").html("Deleting <i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
            },
            success: function(response) {
                $("#cancel_del_btn").show();
                $("#confirm_del_btn").html(`<i class="fas fa-check-circle"></i> Yes`).attr('type', 'submit');
                
                if (response.success) {
                    $('#confirm_delete_modal').modal('hide');
                    customsheets_table.draw();
                } else {
                    var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                    $("#confirm_delete_modal .formsms").html(fdback);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });
});