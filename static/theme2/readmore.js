jQuery(document).ready(function($) {
    $('.post-read-more a').click(function() {
        $this = $(this);
        jQuery("body").addClass('is-loadingApp');
        $(this).html('<i class="icon-spin4"></i> 加载中...');
        var href = $this.attr("href");
        if (href != undefined) {
            $.ajax({
                url: href,
                type: "get",
                error: function(request) {
                    $(this).html('<i class="icon-spin4"></i> 加载失败');
                },
                success: function(data) {
                    $('.post-read-more a').text('加载更多');
                    jQuery("body").removeClass('is-loadingApp');
                    var $res = $(data).find(".content");
                    $('.posts').append($res);
                    jQuery(function() {
                        $("img").lazyload({
                            effect: "fadeIn",
                            failure_limit: 10,
                            threshold: 1000,
                        });
                    });
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
