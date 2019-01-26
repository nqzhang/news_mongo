function get_post_offset() {
    return document.querySelector("#content-list section:last-child a").getAttribute('data-post-id');
}
(function() {
    is_scroll = true;
    // 加载中状态锁
    var fetching = false;
    let scroll_end = false;
    //用于加载时发送请求参数，表示第几屏内容，初始为2，以后每请求一次，递增1
    // pageYOffset设置或返回当前页面相对于窗口显示区左上角的Y位置。
    var lastScrollY = window.pageYOffset;
    var scrollY = window.pageYOffset;
    // 浏览器窗口的视口（viewport）高度
    var innerHeight;

        function fetchContent () {
            // 设置加载状态锁
            if (fetching) {
                return;
            }
            else {
                fetching = true;
            }
            var post_offset = get_post_offset();
            $.ajax({
                url: '/api/list/?path=index&postoffset=' + post_offset,
                timeout: 30000,
                //dataType: 'json',
                dataType: 'html',
                type: "GET",
                 beforeSend:function(XMLHttpRequest){
                    $(".loading").show();
                 }

            }).then(function (data) {
                $(".loading").hide();
                var ulContainer = document.getElementById('content-list');
                ulContainer.insertAdjacentHTML( 'beforeend', data );
                // 已经拉去完毕，设置标识为true
                fetching = false;
                // 强制触发
                let el = $($.parseHTML(data));
                let data_len = el.filter('section.list-item').length;
                if (data_len>=articles_per_page){
                } else {
                    scroll_end = true;
                      $(".loading").text('沒有更多內容啦');
                      $(".loading").show();
                }
            }, function (xhr, type) {
                 $(".loading").text('加載錯誤!请刷新页面');
                console.log('Refresh:Ajax Error!');
            });
        }

    function handleScroll (e, force) {
        // 如果时间间隔内，没有发生滚动，且并未强制触发加载，则do nothing，再次间隔100毫秒之后查询
        if (!force && lastScrollY === window.scrollY) {
            window.setTimeout(handleScroll, 100);
            return;
        }
        else {
            // 更新文档滚动位置
            lastScrollY = window.scrollY;
        }
        scrollY = window.scrollY;
        // 浏览器窗口的视口（viewport）高度赋值
        innerHeight = window.innerHeight;
        // 判断是否需要加载
        // document.body.offsetHeight;返回当前网页高度
        if (window.scrollY + innerHeight + 200 > document.body.offsetHeight) {
            if (!scroll_end) {
                fetchContent();
            }
        }
        window.setTimeout(handleScroll, 100);
    }

    window.setTimeout(handleScroll, 100);
}());




