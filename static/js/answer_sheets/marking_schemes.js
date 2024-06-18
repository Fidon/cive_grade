$(function () {
    var CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

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

    $("#markingschemes_table thead tr").clone(true).attr('class','filters').appendTo('#markingschemes_table thead');
    var markingschemes_table = $("#markingschemes_table").DataTable({
        fixedHeader: true,
        processing: true,
        serverSide: true,
        ajax: {
            url: $("#schemes_list_url").val(),
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
            { data: 'sheetName' },
            { data: 'questions' },
            { data: 'status' },
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
            targets: [2, 2, 4],
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
                title: "Marking-schemes - UDOM EMS",
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
                filename: 'marking-schemes_udom-ems',
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
                title: "Marking-schemes - UDOM EMS",
                exportOptions: {
                    columns: [0, 1, 2, 3, 4]
                }
            },
            { // Print button
                extend: "print",
                text: "<i class='fas fa-print'></i>",
                className: "btn btn-bblight text-white",
                title: "Marking-schemes - UDOM EMS",
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
                        markingschemes_table.draw();
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

    $("#schemes_search").keyup(function() {
        markingschemes_table.search($(this).val()).draw();
    });

    $("#schemes_filter_clear").click(function (e) { 
        e.preventDefault();
        $("#sheets_search").val('');
        clear_dates();
        markingschemes_table.search('').draw();
    });

    $("#question_list_table td:nth-child(3) input").on('input', function() {
        var start = this.selectionStart;
        var end = this.selectionEnd;
        this.value = this.value.toUpperCase();
        this.setSelectionRange(start, end);
    });

    function containsDigit(str) {
        return /\d/.test(str);
    }

    $("#save_marking_scheme").submit(function (e) {
        e.preventDefault();
        var answers_array = [];
        var no_problem = true;

        $("#question_list_table tbody tr").each(function () {
            var row = $(this);
            var questOptions = row.find('td:nth-child(2)').text();
            var questAnswerInput = row.find('td:nth-child(3) input');
            var questAnswer = questAnswerInput.val().trim();
            var questId = parseInt(row.attr('id').split('_')[1]);
            var questAnswerLabel = row.find('td:nth-child(3) label');
        
            function setError(message) {
                questAnswerLabel.text(message).addClass('text-danger');
                questAnswerInput.addClass('border border-danger').focus();
                return false;
            }
        
            function clearError() {
                questAnswerLabel.removeClass('text-danger').text('Correct answer');
                questAnswerInput.removeClass('border border-danger');
            }
        
            if (containsDigit(questOptions)) {
                if (questAnswer.length >= 3) {
                    answers_array.push({
                        'quest_answer': questAnswer,
                        'quest_id': questId
                    });
                    clearError();
                } else {
                    no_problem = setError("Enter at least 3 characters!");
                    return false;
                }
            } else {
                if (questOptions.includes(questAnswer)) {
                    answers_array.push({
                        'quest_answer': questAnswer,
                        'quest_id': questId
                    });
                    clearError();
                } else {
                    no_problem = setError("Answer should be from options");
                    return false;
                }
            }
        });
        

        if (no_problem == true) {
            var formdata = new FormData();
            formdata.append('answers', JSON.stringify(answers_array));

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
                    $("#cancel_save_btn").hide();
                    $("#save_markscheme_btn").html("<i class='fas fa-spinner fa-pulse'></i> Saving").attr('type', 'button');
                },
                success: function(response) {
                    $("#cancel_save_btn").show();
                    $("#save_markscheme_btn").html(`<i class="fas fa-save"></i> Save`).attr('type', 'submit');
                    var fdback = `<div class="alert alert-${response.success ? 'success' : 'danger'} alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-${response.success ? 'check' : 'exclamation'}-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                    $("#save_marking_scheme").animate({ scrollTop: 0 }, 'slow');
                    $("#save_marking_scheme .formsms").html(fdback);
                },
                error: function(xhr, status, error) {
                    console.log(error);
                }
            });
        }
    });
});