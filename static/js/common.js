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

/**
 * return the url query back in the form of an Object
 */
function passUrlParamsToObj() {
	var itemStr = location.search.substr(1);
	var items;

	// extract the url into array, or into string if there is only one parameter
	if (!itemStr) {
		return undefined;
	} else {
		// if there is more than one parameter
		// the index of '&' should be at least 3 (a=b&...)
		// otherwise there is only one paramater or the format is wrong.
		if (itemStr.indexOf('&') >= 3) {
			items = itemStr.split('&');
		} else {
			items = itemStr;
		}
	}

	// map the array or string into object
	var temp;
	var result = {};
	if (Array.isArray(items)) {
		for (let index = 0; index < items.length; index++) {
			if (items[index].indexOf('=') !== -1 && items[index].length >= 3) {
				temp = items[index].split('=');
				result[temp[0]] = decodeURIComponent(temp[1]);
			}
		}
	} else {
		if (itemStr.indexOf('=') !== -1 && itemStr.length >= 3) {
			result = {};
			temp = items.split('=');
			result[temp[0]] = decodeURIComponent(temp[1]);
		} else {
			return undefined;
		}
	}

	return result;
}