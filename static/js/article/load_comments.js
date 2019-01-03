function ApiCommentsGetAll() {
    $.ajax({
        url: '/api/comments/get_all/',
        headers: {'X-XSRFToken': token},
        data: {post_id: post_id},
        type: "POST",
        success: function (res, textStatus, jqXHR) {
            var data = JSON.parse(res);
            if(data.length > 0) {
                $('#comment-form-wrapper').after("<div id='article-comments'><div class='section-head'>所有留言</div></div>");

                data.forEach(function(comment){
                    $('#article-comments').append(
                        "<div class='comment-item'>" + 
                            "<div class='comment-content'>" +
                                "<div class='comment-author'>" + comment.comment_author_name.charAt(0) + "</div>" +
                                "<a href=''>" + comment.comment_author_name + "</a>" +
                                "<div>" + comment.comment_content + "</div>" +
                            "</div>" + 
                            "<div class='comment-meta'>" + 
                                "<img src='/static/svgs/clock.svg' />" +
                                "<div>" + comment.comment_date.$date + "</div>" +
                            "</div>" + 
                        "</div>"
                    )
                });
            }
        }
    });
}

ApiCommentsGetAll()