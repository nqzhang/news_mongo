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

                //按照时间排列，越晚越靠前
                data.sort(sortDataByDate);

                data.forEach(function(comment){
                    $('#comment-list ul.top').append(
                        "<li class='comment-item' data-comment-id='" + comment._id.$oid  + "'>" + 
                            "<div class='comment-meta'>" +
                                "<div class='comment-author user-icon'>" + comment.comment_author_name.charAt(0) + "</div>" +
                                "<div class='author-info-wrapper'>" +
                                    "<a class='author-name' href='/u/" + comment.comment_author_id + "' target='_blank'>" + comment.comment_author_name + "</a>" +
                                    "<div class='comment-time'>" +
                                        "<img src='/static/svgs/clock.svg' />" +
                                        "<div>" + getDateTime(comment.comment_date.$date) + "</div>" +
                                    "</div>" +
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
                    if (comment.reply_to !== '') {
                        $("#comment-list li[data-comment-id='" + comment.reply_to + "'] > ul").append($("#comment-list li[data-comment-id='" + comment._id.$oid + "']"));
                    }
                });
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

ApiCommentsGetAll()
