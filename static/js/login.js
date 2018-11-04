$(document).ready(function(){
    $('.login, #login-layer-wrapper.overlay, .login-layer-close-button').click(function(){
        toggleLoginLayer();
    });

    $('.login-layer').click(function(e){
        e.stopPropagation();
    });
});

function toggleLoginLayer() {
    var overlay = $('#login-layer-wrapper.overlay')
    if(overlay.hasClass('active')){
        overlay.removeClass('active');
    } else {
        overlay.addClass('active');
    }
}


$(function() {
    $('.auto-login').click(function(){
            if ( !$('input[name=login_remember]',this).is(':checked') ) {
                            $('#login_radio',this).addClass("radio-icon-sel");
                      $('input[name="login_remember"]',this).prop('checked',true);
            }
            else {
                            $('#login_radio',this).removeClass("radio-icon-sel");
                            $('input[name="login_remember"]',this).prop('checked',false);
                            
            }
    });
  });
  
  $(function() {
    $('#login_sidebar').click(function(e){
            e.stopPropagation();
                  $('.body-shade').show();
                  $('.login-pop').show();
    });
  });
  
  $(function() {
    $('.close-pop').click(function(){
          $('.body-shade').hide();
          $('.login-pop').hide();
    });
  });
  
  $(function() {
          $("body").click(function() {
             if ($(".body-shade").is(":visible")) {
                 $(".body-shade").hide();
                 $('.login-pop').hide();
             }
          });
  });
  
  $(function() {
              $(".login-pop").click(function(e){
                 e.stopPropagation();
              });
  });
  
  (function () {
          login_base_action = document.getElementById('login_form').action;
          login_action = login_base_action + '?src=' + window.location.href;
    document.getElementById('login_form').action = login_action;
  })();
  
  
  $(document).ready(function(){
          // 访问该页面时，在url末尾添加?picid=8
  
          if ( getUrlParam('login') == 1 ) {
                  $('#login_sidebar').click();
          }
  });
  
  function getUrlParam(name){
          // 构造一个含有目标参数的正则表达式对象
          var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
          // 匹配目标参数
          var r = window.location.search.substr(1).match(reg);
          // 返回参数值
          if (r!=null) return unescape(r[2]);
          return null;
  }
  
  