function ApiCommentsGetAll() {
    $.ajax({
        url: '/api/comments/get_all/',
        headers: {'X-XSRFToken': token},
        data: {post_id: post_id},
        type: "POST",
        success: function (data, textStatus, jqXHR) {
            console.log(data);
        }
    });
}

ApiCommentsGetAll()