$(document).ready(function(){
    // initialize login form
    var form = $('#login-form');
    var login_base_action = form.attr('action');
    var login_action = login_base_action + '?src=' + encodeURI(window.location.href);
    form.attr('action',login_action);

    // handle login layer toggling
    $('.login, #login-layer-wrapper.overlay, .login-layer-close-button').click(function(){
        toggleLoginLayer();
    });

    $('.login-layer').click(function(e){
        e.stopPropagation();
    });

    form.submit(function(e) {
        e.preventDefault();

        var email = $('#login-form input[name=email]').val();
        var passwd = $('#login-form input[name=passwd]').val();
        if (email === '' || passwd === '') {
            $('.err-info').css('display', 'block')
        } else {
            form[0].submit();
        }
    });

    // 访问该页面时，在url末尾添加?picid=8
    // if ( getUrlParam('login') == 1 ) {
    //     $('#login_sidebar').click();
    // }
});

function toggleLoginLayer() {
    var overlay = $('#login-layer-wrapper.overlay')
    if(overlay.hasClass('active')){
        overlay.removeClass('active');
    } else {
        overlay.addClass('active');
    }
}
  
// function getUrlParam(name){
//     // 构造一个含有目标参数的正则表达式对象
//     var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
//     // 匹配目标参数
//     var r = window.location.search.substr(1).match(reg);
//     // 返回参数值
//     if (r!=null) return unescape(r[2]);
//     return null;
// }


var _href = $("a#logout").attr("href");
$("a#logout").attr("href", _href + '?next=' + document.URL);
  
  