

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
                                        "<div>" + getDateTime(comment.comment_date.$date) + "</div>" +
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

function getDateTime(dateInMillionSecond) {
    var date = new Date(dateInMillionSecond);
    return date.toISOString().slice(0, 10) + ' ' + date.getHours() + ':' + date.getMinutes();
}

function sortDataByDate(a, b) {
    if (a.comment_date.$date > b.comment_date.$date)
        return -1;
    if (a.comment_date.$date < b.comment_date.$date)
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

