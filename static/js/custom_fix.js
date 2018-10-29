$(function() {
    $('.index-middle').after($('.right_sidebar'));
    $('a[href^="http"]').not('a[href*=smwenku\\.com]').attr('target','_blank');
    $('.article-content pre.cpp').removeClass('cpp').addClass('language-cpp');
    $('.article-content .dp-cpp').parent("pre").addClass('language-cpp');
    Prism.highlightAll();
});

