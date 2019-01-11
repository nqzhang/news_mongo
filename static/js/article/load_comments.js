

$(document).ready(function(){
    window.replyTo = undefined;

    ApiCommentsGetAll();

    $('#comment-form').submit(function(e) {
        e.preventDefault();

        var comment = extractRepliedContent($('#comment-form textarea[name=comment]').val());
        var post_id = $('#comment-form input[name=post_id]').val();

        if (comment !== '') {
            $.ajax({
                url: '/api/comments/add/',
                headers: {'X-XSRFToken': token},
                data: {
                    post_id,
                    reply_to: window.replyTo ? window.replyTo : "",
                    comment_content: comment
                },
                type: "POST",
                success: function (res, textStatus, jqXHR) {
                    $("#success-info").text("留言成功");
                    $('#comment-form textarea[name=comment]').val("");
                    ApiCommentsGetAll();
                },
                error: function (jqXHR, status, err) {
                    $("#success-info").text("留言失敗，請檢查網絡或者聯繫管理員");
                },
            });
        }
    });

    $('#comment-form textarea[name=comment]').on("input", function() {
        if (!hasReplyTo($(this).val())) {
            window.replyTo = undefined;
        } 
    })
});

function ApiCommentsGetAll() {
    $.ajax({
        url: '/api/comments/get_all/',
        headers: {'X-XSRFToken': token},
        data: {post_id: post_id},
        type: "POST",
        success: function (res, textStatus, jqXHR) {
            var data = JSON.parse(res);
            if(data.length > 0) {
                $('#comment-list').text('');
                $('#comment-list').append("<ul class='top'></ul>")

                // 1. 按照时间排列数据，越晚越靠前
                data.sort(sortDataByDate);

                // 2. 先列出所有评论，无论他们是在第几层
                data.forEach(function(comment){
                    console.log(comment);
                    $('#comment-list ul.top').append(
                        "<li class='comment-item' data-comment-id='" + comment._id.$oid  + "' data-reply-to='" + comment.reply_to  + "'>" + 
                            "<div class='comment-meta'>" +
                                "<div class='comment-author user-icon'>" + comment.comment_author_name.charAt(0) + "</div>" +
                                "<div class='author-info-wrapper'>" +
                                    "<a class='author-name' href='/u/" + comment.comment_author_id.$oid + "' target='_blank'>" + comment.comment_author_name + "</a>" +
                                    "<div class='comment-time'>" +
                                        "<img src='/static/svgs/clock.svg' />" +
                                        "<div>" + "<a title=" + "'" + getDateTime(comment.comment_date.$date) + "'>"  + timeago(comment.comment_date.$date) + "</a>" + "</div>" +
                                    "</div>" +
                                "</div>" +
                                "<div class='reply-comment' data-reply-to='" + comment._id.$oid + "' data-author-name='" + comment.comment_author_name + "'>" +
                                    "<img src='/static/svgs/reply.svg' />" +
                                    "<span>回复</span>" +
                                "</div>" +
                            "</div>" + 
                            "<div class='comment-content'>" + 
                                "<div>" + comment.comment_content + "</div>" +
                            "</div>" + 
                            "<ul></ul>" +
                        "</li>"
                    )
                });

                data.forEach(function(comment){
                    // 3. 检查reply_to变量，如果不为空，则将这条评论移动至他父评论下。
                    if (comment.reply_to !== '') {
                        $("#comment-list li[data-comment-id='" + comment.reply_to + "'] > ul").append($("#comment-list li[data-comment-id='" + comment._id.$oid + "']"));

                        // 如果是第三层或者以上，则删除当前评论给回复按钮
                        if($("#comment-list li[data-comment-id='" + comment.reply_to + "']").attr('data-reply-to') !== "") {
                            $("#comment-list li[data-comment-id='" + comment._id.$oid + "'] .reply-comment").remove();
                        }
                    }

                });

                //5. 生成DOM完成以后，才能监听“回复评论”按钮
                $('.reply-comment').click(function() {
                    var author_name = $(this).attr("data-author-name");
                    var content = $('#comment-form textarea[name=comment]').val();

                    window.replyTo = $(this).attr("data-reply-to");
                    $('#comment-form textarea[name=comment]').val(addReplyToText(content, author_name));

                    //页面自动上移到评论表格
                    $('html, body').animate({
                        scrollTop: $("#comment-form-wrapper").offset().top
                    }, 200);
                })
            }
        }
    });
}

function toLocalTimestamp(utcTimestamp){
    localTimestamp = utcTimestamp + new Date().getTimezoneOffset()*60*1000;
    return localTimestamp;
}
function getDateTime(utcTimestamp) {
    var localTimestamp = toLocalTimestamp(utcTimestamp);
    var date = new Date(localTimestamp);
    var hour = date.getHours() < 10 ? "0" + date.getHours() : date.getHours();
    var minutes = date.getMinutes() < 10 ? "0" + date.getMinutes() : date.getMinutes();
    return date.toISOString().slice(0, 10) + ' ' + hour + ":" + minutes;
}

function sortDataByDate(a, b) {
    if (a.comment_date.$date < b.comment_date.$date)
        return -1;
    if (a.comment_date.$date > b.comment_date.$date)
        return 1;
        
    return 0;
}

function addReplyToText(content, author_name) {
    var _content = content;
    var content_prefix_index = content.indexOf("@");
    var content_suffix_index = content.indexOf(":");
    if(content_prefix_index !== -1 && content_suffix_index !== -1) {
        
        //逻辑应该是content_suffix_index + 1,这里的 + 2 是为了移除后面的一个空格
        _content = _content.slice(content_suffix_index + 2, _content.length);
    }

    return "@回复用戶 " + author_name + ": " + _content;
}

function hasReplyTo(content){
    var content_prefix_index = content.indexOf("@");
    var content_suffix_index = content.indexOf(":");
    if(content_prefix_index !== -1 && content_suffix_index !== -1) {
        return true;
    } else {
        return false;
    }
}

function extractRepliedContent(content){
    var content_prefix_index = content.indexOf("@");
    var content_suffix_index = content.indexOf(":");
    if(content_prefix_index !== -1 && content_suffix_index !== -1) {
        return content.slice(content_suffix_index + 2, content.length);
    } else {
        return content;
    }
}


function timeago(dateTimeStamp){   //dateTimeStamp是一个时间毫秒，注意时间戳是秒的形式，在这个毫秒的基础上除以1000，就是十位数的时间戳。13位数的都是时间毫秒。
    var minute = 1000 * 60;      //把分，时，天，周，半个月，一个月用毫秒表示
    var hour = minute * 60;
    var day = hour * 24;
    var week = day * 7;
    var halfamonth = day * 15;
    var month = day * 30;
    var now = new Date().getTime();   //获取当前时间毫秒
    var diffValue = now - toLocalTimestamp(dateTimeStamp);//时间差
    console.log(diffValue);
    if(diffValue < 0){
        return;
    }
    var minC = diffValue/minute;  //计算时间差的分，时，天，周，月
    var hourC = diffValue/hour;
    var dayC = diffValue/day;
    var weekC = diffValue/week;
    var monthC = diffValue/month;
    if(monthC >= 1 && monthC <= 3){
        result = " " + parseInt(monthC) + "月前"
    }else if(weekC >= 1 && weekC <= 3){
        result = " " + parseInt(weekC) + "周前"
    }else if(dayC >= 1 && dayC <= 6){
        result = " " + parseInt(dayC) + "天前"
    }else if(hourC >= 1 && hourC <= 23){
        result = " " + parseInt(hourC) + "小时前"
    }else if(minC >= 1 && minC <= 59){
        result =" " + parseInt(minC) + "分钟前"
    }else if(diffValue >= 0 && diffValue <= minute){
        result = "刚刚"
    }else {
        var datetime = new Date();
        datetime.setTime(dateTimeStamp);
        var Nyear = datetime.getFullYear();
        var Nmonth = datetime.getMonth() + 1 < 10 ? "0" + (datetime.getMonth() + 1) : datetime.getMonth() + 1;
        var Ndate = datetime.getDate() < 10 ? "0" + datetime.getDate() : datetime.getDate();
        var Nhour = datetime.getHours() < 10 ? "0" + datetime.getHours() : datetime.getHours();
        var Nminute = datetime.getMinutes() < 10 ? "0" + datetime.getMinutes() : datetime.getMinutes();
        var Nsecond = datetime.getSeconds() < 10 ? "0" + datetime.getSeconds() : datetime.getSeconds();
        result = Nyear + "-" + Nmonth + "-" + Ndate
    }
    return result;
}

