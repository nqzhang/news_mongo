//文章底部匹配
$(document).ready(function() {
            var ads_div = $("#ads-article-bottom");
            var current_width = ads_div.css('width');
            var ins = '<ins class="adsbygoogle" style="display:block;' +
                'max-width:' + current_width + '" ' +
                'data-ad-client="ca-pub-7536255340317474" ' +
                'data-ad-slot="1268860504" data-ad-format="auto" ' +
                'data-full-width-responsive="true"' +
                '></ins>' +
                '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'
            ads_div.append(ins);

             var ins_middle = '<ins class="adsbygoogle" style="display:block; text-align:center;" ' +
                 'data-ad-layout="in-article" ' +
                 'data-ad-format="fluid" ' +
                'data-ad-client="ca-pub-7536255340317474" ' +
                'data-ad-slot="4000725278"' +
                '></ins>' +
                 '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'
            var content_p_middle_index = Math.floor($('.post-content *').length /2);
            $('.post-content *').eq(content_p_middle_index).after(ins_middle)

    });



