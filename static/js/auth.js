$(function () {
    var CSRF_TOKEN = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // function to validate password
    function validate_password(pass1, pass2) {
        const minLengthRegex = /.{8,}/;
        const uppercaseRegex = /[A-Z]/;
        const lowercaseRegex = /[a-z]/;
        const digitRegex = /[0-9]/;
        const specialCharRegex = /[!@#$%^&*]/;

        if (!minLengthRegex.test(pass1)) {
            return "Password must be at least 8 characters long.";
        }
        // if (!uppercaseRegex.test(pass1)) {
        //     return "Password must contain at least one uppercase letter.";
        // }
        // if (!lowercaseRegex.test(pass1)) {
        //     return "Password must contain at least one lowercase letter.";
        // }
        // if (!digitRegex.test(pass1)) {
        //     return "Password must contain at least one digit.";
        // }
        // if (!specialCharRegex.test(pass1)) {
        //     return "Password must contain at least one special character.";
        // }
        if (!(pass1 === pass2)) {
            return "Passwords must match in both fields.";
        }

        return null;
    }

    // user/teacher registraton
    $("#register_form").submit(function (e) {
        e.preventDefault();

        var password1 = $("#reg_password1").val();
        var password2 = $("#reg_password2").val();
        var check_password = validate_password(password1, password2);

        if (check_password === null) {
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
                    $("#login_url_btn").hide();
                    $("#reg_submit_button").html("<i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
                },
                success: function(response) {
                    $("#login_url_btn").show();
                    $("#reg_submit_button").text("Register").attr('type', 'submit');
                    
                    var fdback = `<div class="alert alert-${response.success ? 'success' : 'danger'} alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-${response.success ? 'check' : 'exclamation'}-circle'></i> ${response.sms} Login to contine..<button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                    
                    $('#register_form').animate({ scrollTop: 0 }, 'fast');
                    $("#register_form .formsms").html(fdback).show();
                    
                    if (response.success) {
                        $("#register_form")[0].reset();
                    }
                },
                error: function(xhr, status, error) {
                    console.log(error);
                }
            });
        } else {
            var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${check_password} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
            $('#register_form').animate({ scrollTop: 0 }, 'fast');
            $("#register_form .formsms").html(fdback).show();
        }
    });

    // user/teacher login
    $("#login_auth_form").submit(function (e) {
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
                $("#signup_url_btn").hide();
                $("#auth_submit_button").html("<i class='fas fa-spinner fa-pulse'></i>").attr('type', 'button');
            },
            success: function(response) {
                if(response.success) {
                    window.location.href = response.url;
                } else {
                    $("#signup_url_btn").show();
                    $("#auth_submit_button").html("Sign In").attr('type', 'submit');
                    var fdback = `<div class="alert alert-danger alert-dismissible fade show px-2 m-0 d-block w-100"><i class='fas fa-exclamation-circle'></i> ${response.sms} <button type="button" class="btn-close d-inline-block" data-bs-dismiss="alert"></button></div>`;
                    $("#login_auth_form .formsms").html(fdback).show();
                }
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });
})