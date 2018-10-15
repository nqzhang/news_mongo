/*!
Intelligent auto-scrolling to hide the mobile device address bar
Optic Swerve, opticswerve.com
Documented at http://menacingcloud.com/?c=iPhoneAddressBar
*/
var bodyTag;
var executionTime = new Date().getTime();
var aMenuClicked = false;
documentReady(function() {
    var readyTime = new Date().getTime()
    if ((readyTime - executionTime) < 3000) ;
    $(".container").hide();
    $(".toggle").click(function() {
        $(this).toggleClass("active").next().slideToggle(350);
        return false;
    });
    $("#submenu-1").hide();

        $('#a-menu').bind('click', function(event) {
            if (aMenuClicked) {
                $('#menu-wrapper').removeClass('');
                $('#box').removeClass('moved');
                aMenuClicked = false;
            } else {
                $('#menu-wrapper').addClass('');
                $('#box').addClass('moved');
                aMenuClicked = true;
            }
        });
        $('#a-submenu-1').bind('click', function(event) {
            $('#submenu-1').toggle(250);
        });
   
});

function documentReady(readyFunction) {
    document.addEventListener('DOMContentLoaded', function() {
        document.removeEventListener('DOMContentLoaded', arguments.callee, false);
        readyFunction();
    }, false);
}

function hideAddressBar(bPad) {
    if (screen.width > 980 || screen.height > 980) return;
    if (window.navigator.standalone === true) return;
    if (window.innerWidth !== document.documentElement.clientWidth) {
        if ((window.innerWidth - 1) !== document.documentElement.clientWidth) return;
    }
    if (bPad === true && (document.documentElement.scrollHeight <= document.documentElement.clientHeight)) {
        bodyTag = document.getElementsByTagName('body')[0];
        bodyTag.style.height = document.documentElement.clientWidth / screen.width * screen.height + 'px';
    }
    setTimeout(function() {
        if (window.pageYOffset !== 0) return;
        window.scrollTo(0, 1);
        if (bodyTag !== undefined) bodyTag.style.height = window.innerHeight + 'px';
        window.scrollTo(0, 0);
    }, 1000);
}

function quickHideAddressBar() {
    setTimeout(function() {
        if (window.pageYOffset !== 0) return;
        window.scrollTo(0, window.pageYOffset + 1);
    }, 1000);
}