//文章底部匹配
$(document).ready(function() {
            var ads_div = $("#ads-article-bottom-match");
            var current_width = ads_div.css('width');
            var ins = '<ins class="adsbygoogle" style="display:block;' +
                'max-width:' + current_width + '"' +
                'data-ad-client="ca-pub-2073744953016040" ' +
                'data-ad-slot="3534050590" data-ad-format="autorelaxed"></ins>'
            ads_div.append(ins);
            (adsbygoogle = window.adsbygoogle || []).push({});
    });
