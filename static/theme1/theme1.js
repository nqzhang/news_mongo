
layui.use('util', function(){
  var util = layui.util;

  //执行
  util.fixbar({
    bar1: false
    ,click: function(type){
      console.log(type);
      if(type === 'bar1'){
        alert('点击了bar1')
      }
    }
  });
});

var share = {
        url: document.URL,
        pic: $('meta[property="og:image"]').length ? $('meta[property="og:image"]').attr("content") : "",
        title: $('meta[property="og:title"]').length ? $('meta[property="og:title"]').attr("content") : "",
        desc: $('meta[name="description"]').length ? $('meta[name="description"]').attr("content") : ""
    }

$(".share-weixin").each(function() {
        $(this).find(".share-popover").length || ($(this).append('<span class="share-popover"><span class="share-popover-inner" id="weixin-qrcode"></span></span>'), $("#weixin-qrcode").qrcode({
            width: 80,
            height: 80,
            text: $(this).data("url")
        }))
    })

$('[etap="share"]').click(function(){
    var dom = $(this)
    var to = dom.data('share')
    var url = ''
        switch (to) {
        case "qq":
            url = "http://connect.qq.com/widget/shareqq/index.html?url=" + share.url + "&desc=" + share.desc + "&summary=" + share.title + "&site=zeshlife&pics=" + share.pic;
            break;
        case "weibo":
            url = "http://service.weibo.com/share/share.php?title=" + share.title + "&url=" + share.url + "&appkey=448148336&pic=" + share.pic;
            break;
        case "douban":
            url = "http://www.douban.com/share/service?image=" + share.pic + "&href=" + share.url + "&name=" + share.title + "&text=" + share.desc;
            break;
        case "qzone":
            url = "http://sns.qzone.qq.com/cgi-bin/qzshare/cgi_qzshare_onekey?url=" + share.url + "&title=" + share.title + "&desc=" + share.desc;
            break;
        case "tqq":
            url = "http://share.v.t.qq.com/index.php?c=share&a=index&url=" + share.url + "&title=" + share.title;
            break;
        case "renren":
            url = "http://widget.renren.com/dialog/share?srcUrl=" + share.pic + "&resourceUrl=" + share.url + "&title=" + share.title + "&description=" + share.desc;
            break;
        case "facebook":
            url = "https://www.facebook.com/share.php?u=" + share.url + "&t=" + share.title;
            break;
        case "twitter":
            url = "https://twitter.com/intent/tweet?text=" + share.title + share.url;
            break;
        case "linkedin":
            url = "https://www.linkedin.com/shareArticle?mini=true&ro=true&armin=armin&url=" + share.url + "&title=" + share.title + "&summary=" + share.desc
        }
        dom.attr("href") || dom.attr("target") || dom.attr("href", url).attr("target", "_blank")
});

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}