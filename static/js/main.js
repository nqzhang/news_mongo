$(document).ready(function() {
    // sticky menu
    var menuOffset= $('#menu-wrapper').offset().top;
    var menuHeight= $('#menu-wrapper').innerHeight();
    $(window).scroll(function() {
        stickMenu(menuOffset, menuHeight);
    });
})

// stickey menu function
function stickMenu(menuOffset, menuHeight) {
    var scrollTop = $(window).scrollTop();
    if (scrollTop > menuOffset) {
        $('#menu-wrapper').addClass('sticky');
        $('#content-wrapper').css("padding-top", menuHeight + 'px') ;
    } else {
        $('#menu-wrapper').removeClass('sticky');
        $('#content-wrapper').css("padding-top", 0);
    }
}