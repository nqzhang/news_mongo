$(document).ready(function(){
    $('#comment-form').submit(function(e) {
        e.preventDefault();

        var comment = $('#comment-form textarea[name=comment]').val();
        var post_id = $('#comment-form input[name=post_id]').val();

        if (comment !== '') {
            $.ajax({
                url: '/api/comments/add/',
                headers: {'X-XSRFToken': token},
                data: {
                    post_id,
                    reply_to: '',
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
});
