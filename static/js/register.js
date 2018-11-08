$(document).ready(function(){
    var isEmailValid = false;

    $('#register-form').submit(function(e) {
        e.preventDefault();

        var email = $('#register-form input[name=email]').val();
        var passwd = $('#register-form input[name=passwd]').val();
        if (email === '' || passwd === '') {
            showError('請輸入電子郵件和密碼');
        } else {
            if (isEmailValid){
                $('#register-form')[0].submit();
            } else {
                showError('郵件錯誤');                
            }
        }
    });

    var emailField = $('#register-form input[name=email]')
    // 检查邮件blur event
    emailField.blur(function() {

        //检查邮件是否为空
        if (emailField.val() === '') {
            showError('');
            isEmailValid = false;
            return;
        }

        // 检查格式是否正确
        if(!validateEmail(emailField.val())) {
            isEmailValid = false;
            showError('郵件格式錯誤');
            return 
        }

        //检查是否邮件为空
        $.post("/account/is_email_exist/" + emailField.val(), null, function(response) {
            if (response == "郵箱已經註冊") { 
                //特别处理
                isEmailValid = false;
                showError(response);
            } else {
                isEmailValid = true;
                showError(response, false);            
            }
        });
    });
});

function showError(errorMsg, red = true) {
    if (red) {
        $('.err-info').css('color', '#fd484d');
    } else {
        $('.err-info').css('color', '#3d3d3d');        
    }
    $('.err-info').html(errorMsg);
}

function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}