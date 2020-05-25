function load_custom_ads(){
	currentLang = navigator.language;   //判断除IE外其他浏览器使用语言
	if(!currentLang){//判断IE浏览器使用语言
		currentLang = navigator.browserLanguage;
	}
	if (currentLang.toLowerCase() != 'zh-cn') {
		return;
		}
	var elem = document.createElement("img");
	elem.setAttribute("src", "https://www.xuehua.us/wp-content/IMG_1149_1.jpg");
	var custom_ads=document.createElement("div");
	custom_ads.setAttribute("class", "widget_text widget widget_custom_html");
	custom_ads.append(elem);
	$('.widget_wazhuti_search').after(custom_ads);
}


$('img[src^="https://pic1.xuehuaimg.com/proxy/refer/https://niuerdata.g.com.cn/"]').each(function(i,e){
	$(e).attr('referrerpolicy','no-referrer');
	e.src = e.src.replace(/^(https\:\/\/pic1\.xuehuaimg\.com\/proxy\/refer\/)/,'');
        //$(e).image(e.src,function(){});
        })

$('img[src^="https://niuerdata.g.com.cn/"]').each(function(i, e) {
	$(e).attr('referrerpolicy', 'no-referrer');
	$(e).attr("src", $(e).attr("src"));
})
   $('img[src^="https://pic.pimg.tw/"],img[src*="www.pconline.com.cn"],img[src*="zimedia.com.tw"]').each(function(i, e) {
        $(e).attr("src", $(e).attr("src").replace(/^https:\/\//i, 'http://'));
        console.log('eee');
    })

