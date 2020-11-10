//文章底部匹配
$(document).ready(function() {
            var ad_pub,site_domain = document.domain
            var ad_slot=new Array();
            if (site_domain==="www.xuehua.tw") {
                var ad_pub = "3219336841483159"
                ad_slot[0] = "2314507966"
                ad_slot[1] = "3483281765"
                } else {
                 var  ad_pub= "7536255340317474"
                ad_slot[0] = "1268860504"
                ad_slot[1] = "4000725278"
            }


            var ads_div = $("#ads-article-bottom");
            var current_width = ads_div.css('width');
            var ins = '<ins class="adsbygoogle" style="display:block;' +
                'max-width:' + current_width + '" ' +
                'data-ad-client="ca-pub-' + ad_pub + '" ' +
                'data-ad-slot="' + ad_slot[0] + '" ' +
                'data-ad-format="auto" ' +
                'data-full-width-responsive="true"' +
                '></ins>' +
                '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'
            ads_div.append(ins);

            var ins_middle = '<ins class="adsbygoogle" style="display:inline; text-align:center;" ' +
                'data-ad-layout="in-article" ' +
                'data-ad-format="fluid" ' +
                'data-ad-client="ca-pub-' + ad_pub + '" ' +
                'data-ad-slot="' + ad_slot[1] + '" ' +
                '></ins>' +
                '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'
            var content_p_middle_index = Math.floor($('.post-content *').length / 2);
            $('.post-content *').eq(content_p_middle_index).after(ins_middle)


    });



