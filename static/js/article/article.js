$(window).on("load",function () {
    var comment_id = getUrlParam('commentScrool');
    commentScrool_selector=   '[data-comment-id="' + comment_id + '"]';
    $([document.documentElement, document.body]).animate({
        scrollTop: $(commentScrool_selector).offset().top
    }, 300);

    }
)