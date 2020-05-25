jQuery(document).ready(function($) {
    $('.post-read-more a').click(function() {
        $this = $(this);
        var lang = getUrlParam('lang');
        var loading_string;
        if ( ['zh-tw','zh-hk'].includes(lang)){
             loading_string = "加載中";
             loading_fail_string = "加載失敗";
             loading_success_string = "加載更多";
        } else {
            loading_string = "加载中";
            loading_fail_string = "加载失败";
            loading_success_string = "加载更多";
        }
        jQuery("body").addClass('is-loadingApp');
        $(this).html('<i class="icon-spin4"></i> ' + loading_string + '...');
        var href = $this.attr("href");
        if (href != undefined) {
            $.ajax({
                url: href,
                type: "get",
                error: function(request) {
                    $(this).html('<i class="icon-spin4"></i> ' + loading_fail_string);
                },
                success: function(data) {
                    $('.post-read-more a').text(loading_success_string);
                    jQuery("body").removeClass('is-loadingApp');
                    var $res = $(data).find(".content");
                    $('.posts').append($res);
                    observer.observe();
                    var newhref = $(data).find(".post-read-more a").attr("href");
                    if (newhref != undefined) {
                        $(".post-read-more a").attr("href", newhref);
                    } else {
                        $(".post-read-more").hide();
                    }
                }
            });
        }
        return false;
    });
});
