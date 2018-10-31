// hidemenu breakpoint: 960

$(document).ready(function() {

    // sticky menu
    setMenuOffset();
    $(window).scroll(function() {
        if($(window).width() > 960) {
            toggleStickyMenu(window.menuOffsetTop, window.menuOffsetLeft);
        }
    });

    $(window).resize(function(){
        refreshMenuOffsetTop();
    });
    // sticky menu end

    // toggle mobile menu
    $("#menu-icon").click(function() {
        toggleMobileMenu();
    })

    $(".mobile-menu-background").click(function(){
        toggleMobileMenu();
    })

    $(".mobile-menu-close").click(function(){
        toggleMobileMenu();
    })
    // toggle mobile menu end
})

function setMenuOffset() {
    window.menuOffsetTop = $('.content').offset().top;
    window.menuOffsetLeft = $('.content').offset().left;
}

// stickey menu main function
function toggleStickyMenu() {
    var scrollTop = $(window).scrollTop();
    if (scrollTop >= window.menuOffsetTop) {
        stickMenu()
    } else {
        unstickMenu();
    }
}

function stickMenu() {
    var menuWidth= $('#menu-wrapper').width();
    if(!$('#menu-wrapper').hasClass('sticky')) {
        $('#menu-wrapper').addClass('sticky');
        $('#menu-wrapper').css("left", window.menuOffsetLeft + 'px') ;
        $('.main-content').css("margin-left", menuWidth + 'px');
    } else {
        $('#menu-wrapper').css("left", window.menuOffsetLeft + 'px') ;
    }
}

function unstickMenu() {
    if($('#menu-wrapper').hasClass('sticky')) {
        $('#menu-wrapper').removeClass('sticky');
        $('.main-content').css("margin-left", 0 + 'px') ;
    }
}

// sticky menu: 屏幕resize的时候更新window.menuOffsetTop， 因为他的offsetTop可能根据屏幕尺寸变化而变化
function refreshMenuOffsetTop() {
    setMenuOffset();
    if ($(window).width() > 960) {
        if ($('#menu-wrapper').hasClass('sticky')){
            stickMenu();
        } else {
            unstickMenu();
        }
    } else {
        if ($('#menu-wrapper').hasClass('sticky')){
            unstickMenu();
        }
    }
}

function toggleMobileMenu() {
    if($('.mobile-menu-background').hasClass("active")) {
        $('.mobile-menu-background').removeClass("active");
        $('.mobile-menu').removeClass("active");
        $('body').removeClass("noscroll");
    } else {
        $('.mobile-menu-background').addClass("active");
        $('.mobile-menu').addClass("active");
        $('body').addClass("noscroll");
    }
}
