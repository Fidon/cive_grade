$(function () {
    // tabs on driver-details page
    $("#container .exam_info ul li a").click(function (e) { 
        e.preventDefault();
        var tab_id = $(this).attr('href').replace('#','');
        $("#container .exam_info .tab_container .tab_div").each(function () {
            if (($(this).is(':visible')) && ($(this).attr('id') !== tab_id)) {
                $(this).css('display','none');
                $('#'+tab_id).fadeIn('slow');
            }
        });
    });

    var CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Create new exam
    $("#new_exam_form").submit(function (e) { 
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
                $("#exam_cancel_btn").removeClass('d-inline-block').addClass('d-none');
                $("#exam_submit_btn").html("<i class='fas fa-spinner fa-pulse'></i> Saving").attr('type', 'button');
            },
            success: function(response) {
                $("#exam_cancel_btn").removeClass('d-none').addClass('d-inline-block');
                $("#exam_submit_btn").text("Save").attr('type', 'submit');

                var fdback = `<div class="alert alert-${response.success ? 'success' : 'danger'} alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-${response.success ? 'check' : 'exclamation'}-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                
                $("#new_exams_canvas .offcanvas-body").animate({ scrollTop: 0 }, 'slow');
                $("#new_exam_form .formsms").html(fdback);
                
                if(response.update_success) {
                    $("#exam_info_div").load(location.href + " #exam_info_div");
                } else if(response.success) {
                    $("#new_exam_form")[0].reset();
                    exams_list_table.draw();
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

    function clear_dates() {
        $('#min_date').val('');
        $('#max_date').val('');
    }

    $("#exams_list_table thead tr").clone(true).attr('class','filters').appendTo('#exams_list_table thead');
    var exams_list_table = $("#exams_list_table").DataTable({
        fixedHeader: true,
        processing: true,
        serverSide: true,
        ajax: {
            url: $("#exams_list_url").val(),
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
            { data: 'regDate' },
            { data: 'examName' },
            { data: 'sheetName' },
            { data: 'questions' },
            { data: 'action' },
        ],
        order: [[1, 'desc']],
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
            targets: [2, 3],
            className: 'ellipsis text-start',
        },
        {
            targets: 5,
            className: 'align-middle text-nowrap text-center',
            createdCell: function (cell, cellData, rowData, rowIndex, colIndex) {
                var cell_content = `<a href="${rowData.info}" class="btn btn-bblue text-white btn-sm">View</a>`;
                $(cell).html(cell_content);
            }
        }],
        dom: "lBfrtip",
        buttons: [
            { // Copy button
                extend: "copy",
                text: "<i class='fas fa-clone'></i>",
                className: "btn btn-bblight text-white",
                titleAttr: "Copy",
                title: "Exams - UDOM EMS",
                exportOptions: {
                    columns: [0, 1, 2, 3, 4]
                }
            },
            { // PDF button
                extend: "pdf",
                text: "<i class='fas fa-file-pdf'></i>",
                className: "btn btn-bblight text-white",
                titleAttr: "Export to PDF",
                title: "Custom answer sheets - UDOM EMS",
                filename: 'exams_udom-ems',
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
                        doc.content[1].table.body[i][3].alignment = 'left';
                        doc.content[1].table.body[i][4].alignment = 'center';
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
                title: "Exams - UDOM EMS",
                exportOptions: {
                    columns: [0, 1, 2, 3, 4]
                }
            },
            { // Print button
                extend: "print",
                text: "<i class='fas fa-print'></i>",
                className: "btn btn-bblight text-white",
                title: "Exams - UDOM EMS",
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
                        exams_list_table.draw();
                    });
                } else if (colIdx == 0 || colIdx == 5) {
                    cell.html("");
                } else {
                    $(cell).html("<input type='text' class='text-ttxt' placeholder='Filter..'/>");
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

    $("#exams_search").keyup(function() {
        exams_list_table.search($(this).val()).draw();
    });

    $("#exams_filter_clear").click(function (e) { 
        e.preventDefault();
        $("#exams_search").val('');
        clear_dates();
        exams_list_table.search('').draw();
    });

    // Mark exam
    $("#mark_exam_form").submit(function (e) { 
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
                $("#mark_exam_btn").html("<i class='fas fa-spinner fa-pulse'></i> Marking").attr('type', 'button');
            },
            success: function(response) {
                $("#mark_exam_btn").text("Mark exam").attr('type', 'submit');

                var fdback = `<div class="alert alert-${response.success ? 'success' : 'danger'} alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-${response.success ? 'check' : 'exclamation'}-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                $("#mark_exam_form .formsms").html(fdback);
                if (response.success) {
                    $("#mark_exam_form .formsms").html('');
                    $("#mark_results_model").modal('show');
                    $("#mark_exam_form")[0].reset();
                    $("#mark_results_model .formsms").html(fdback);
                    $("#ex_regno").text(response.regnumber);
                    $("#ex_marks").text(response.marks);
                    $("#ex_correct").text(response.correct);
                    $("#ex_wrong").text(response.wrong);
                    results_table.draw();
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });

    $("#confirm_delete_btn").click(function (e) { 
        e.preventDefault();

        var formData = new FormData();
        formData.append("delete_exam", $("#get_examination_id").val());

        $.ajax({
            type: 'POST',
            url: $("#new_exam_form").attr('action'),
            data: formData,
            dataType: 'json',
            contentType: false,
            processData: false,
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            },
            beforeSend: function() {
                $("#cancel_delete_btn").removeClass('d-inline-block').addClass('d-none');
                $("#confirm_delete_btn").html("<i class='fas fa-spinner fa-pulse'></i>");
            },
            success: function(response) {
                if(response.success) {
                    window.alert('Exam deleted..!');
                    window.location.href = response.url;
                } else {
                    $("#cancel_delete_btn").removeClass('d-none').addClass('d-inline-block');
                    $("#confirm_delete_btn").html("<i class='fas fa-check-circle'></i> Yes");

                    var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;

                    $("#confirm_delete_modal .formsms").html(fdback);
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });

    $("#results_table thead tr").clone(true).attr('class','filters').appendTo('#results_table thead');
    var results_table = $("#results_table").DataTable({
        fixedHeader: true,
        processing: true,
        serverSide: true,
        ajax: {
            url: $("#results_list_url").val(),
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
            { data: 'regDate' },
            { data: 'regnumber' },
            { data: 'names' },
            { data: 'program' },
            { data: 'marks' },
        ],
        order: [[1, 'desc']],
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
            "targets": 0,
            "orderable": false,
        },
        {
            targets: 3,
            className: 'ellipsis text-start',
        }],
        dom: "lBfrtip",
        buttons: [
            { // Copy button
                extend: "copy",
                text: "<i class='fas fa-clone'></i>",
                className: "btn btn-bblight text-white",
                titleAttr: "Copy",
                title: $('#get_exam_names').val()+" results - UDOM EMS",
                exportOptions: {
                    columns: [0, 1, 2, 3, 4, 5]
                }
            },
            { // PDF button
                extend: "pdf",
                text: "<i class='fas fa-file-pdf'></i>",
                className: "btn btn-bblight text-white",
                titleAttr: "Export to PDF",
                title: $('#get_exam_names').val()+" results - UDOM EMS",
                filename: 'results-udom-ems',
                orientation: 'portrait',
                pageSize: 'A4',
                footer: true,
                exportOptions: {
                    columns: [0, 1, 2, 3, 4, 5],
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
                        doc.content[1].table.body[i][3].alignment = 'left';
                        doc.content[1].table.body[i][4].alignment = 'center';
                        doc.content[1].table.body[i][5].alignment = 'center';
                        doc.content[1].table.body[i][5].margin = [0, 0, 3, 0];

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
                title: $('#get_exam_names').val()+" results - UDOM EMS",
                exportOptions: {
                    columns: [0, 1, 2, 3, 4, 5]
                }
            },
            { // Print button
                extend: "print",
                text: "<i class='fas fa-print'></i>",
                className: "btn btn-bblight text-white",
                title: $('#get_exam_names').val()+" results - UDOM EMS",
                orientation: 'portrait',
                pageSize: 'A4',
                titleAttr: "Print",
                footer: true,
                exportOptions: {
                    columns: [0, 1, 2, 3, 4, 5],
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
                        exams_list_table.draw();
                    });
                } else if (colIdx == 0) {
                    cell.html('');
                } else {
                    $(cell).html("<input type='text' class='text-ttxt' placeholder='Filter..'/>");
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

    $("#results_search").keyup(function() {
        results_table.search($(this).val()).draw();
    });

    $("#results_filter_clear").click(function (e) { 
        e.preventDefault();
        $("#results_search").val('');
        clear_dates();
        results_table.search('').draw();
    });
});