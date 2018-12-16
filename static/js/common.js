function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function getUrlParam(name){
     // 构造一个含有目标参数的正则表达式对象
     var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
     // 匹配目标参数
     var r = window.location.search.substr(1).match(reg);
    // 返回参数值
    if (r!=null) return unescape(r[2]);
    return null;
 }

 function validateEmail(email) {
    var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
    return re.test(String(email).toLowerCase());
}
