$(function() {
    var inputUserNameObj = $("input[name='email']");
    $("input[name='email']").blur(function() { //当该控件失去焦点时发生
        var text = inputUserNameObj.val(); //获得用户输入的邮箱
        $.post("/account/is_email_exist/" + text, null, function(response) { // 以POST方式跳转到action里面的方法中进行处理，并返回处理结果response
            if (response == "郵箱已經註冊") { //根据返回值进行处理
                $("input[name='email']").focus(); //用户名输入控件获得焦点
                document.getElementById("showResult").innerHTML = "<font color='red'>" + response + "</font>"; //在div中提示用户该用户名已经存在
            } else {
                if ($("input[name='email']").val() == "") //判断用户名是否为空
                {
                    document.getElementById("showResult").innerHTML = "<font color='red'>" + "郵箱不能為空" + "</font>"; // 在div中提示用户该用户名不能为空
                    $("input[name='email']").focus(); //用户名输入控件获得焦点
                } else {
                    document.getElementById("showResult").innerHTML = "<font color='#90ee90'>" + response + "</font>";
                }
            }
        });
    });
});