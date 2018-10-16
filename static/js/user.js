$("#btnPublish").click(publish);

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).on('keyup', '.bootstrap-tagsinput input', function(){
    $(this).attr('placeholder', '')
})
function publish_success(post) {
    $('#alertSuccess .title').text(post['title']);
    $('#alertSuccess').show();
    return function(data, textStatus, jqXHR) {
        $('#alertSuccess .toarticle').attr("href","/a/" + data['post_id']);
    };
}

function publish() {
    var post={};
    post['content'] = CKEDITOR.instances.editor.getData();
    post['title']= $('input#txtTitle').val();
    post['tags']= $('input#tags').val();
    post['category_person']= $('input#categorys').val();
    post['category_site']= $('#radChl option:selected').text();
    post['category'] = post['category_site'] + "," + post['category_person'];
    token = getCookie('_xsrf');
    $.ajax({
        url: '/u/postajax/',
        headers: {'X-XSRFToken' : token },
        data: post,
        //contentType: "application/json",
        //dataType: "JSON",
        type: "POST",
        success: publish_success(post),
        error: function ( data , status_text, jqXHR ) {
            alert('post fail')
        },
    });
};