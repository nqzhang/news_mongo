$(document).ready(function(){

    $('#forgot-password-form').submit(function(e) {
        e.preventDefault();
        showError("");
        var email = $('#forgot-password-form input[name=email]').val();
        if (email === '') {
            showError('請輸入註冊時的郵箱');
            return;
        } 
        
        if(!validateEmail(email)) {
            showError('郵件格式錯誤');
            return;
        }

        $('#forgot-password-form')[0].submit();
    });
    $('#forgot-password-form input[name=email]').focus(function() {
            showError('');
    });
});

function showError(errorMsg) {
    $('.err-info').html(errorMsg);
}
