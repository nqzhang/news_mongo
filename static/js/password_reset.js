$(document).ready(function(){

    $('#reset-password-form').submit(function(e) {
        e.preventDefault();
        showError("");
        var password = $('#reset-password-form input[name=password]').val();
        var data = passUrlParamsToObj();
        if (password === '') {
            showError('新密碼不能為空');
            return;
        }

        $('#reset-password-form')[0].submit();
    });
});

function showError(errorMsg) {
    $('.err-info').html(errorMsg);
}
