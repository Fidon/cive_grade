$(function () {
    var CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    $("#upload_form").submit(function (e) {
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
                $("#majibu_button").html("<i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
            },
            success: function(response) {
                $("#majibu_button").html("Submit").attr('type', 'submit');
                if (response.success) {
                    $("#upload_form")[0].reset();
                    $("#upload_form").before(`<h1 class="my-5 text-ttxt1 d-block">ImageText: <pre>${response.img_text}</pre></h1>`);
                } else {
                    var fdback = `<i class='fas fa-exclamation-circle'></i> ${response.sms}</div>`;
                    $("#upload_form .formsms").html(fdback).show();
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });
})