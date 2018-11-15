$("#btnPublish").click(publish);

$('a[data-pid]').click(delete_post);

function publish_success(post) {
    $('#alertSuccess .title').text(post['title']);
    $('#alertSuccess').show();
    return function(data, textStatus, jqXHR) {
        $('#alertSuccess .toarticle').attr("href","/a/" + data['post_id']);
    };
}

function delete_success(post) {
    $('span.notice').text('刪除成功');
    $('.notice-box').show().delay(1000).fadeOut();
    location.reload();
    return function(data, textStatus, jqXHR) {
        //pass
    };
}

function publish() {
    var post={};
    if (typeof jsonData === 'undefined' || jsonData === null) {
        post['post_id'] = 0;
    } else {
        post['post_id'] = jsonData['post_id'];
    }
    post['content'] = CKEDITOR.instances.editor.getData();
    post['title']= $('input#txtTitle').val();
    post['category_site']= $('#radChl option:selected').text();
    var category_site_value = $('#radChl option:selected').val();
    if(category_site_value==0){
        $('span.notice').text('請選擇博客分類');
         $('.notice-box').show().delay(3000).fadeOut();
        return;
    }
    if(post['title'].trim().length==0){
        $('span.notice').text('请输入文章标题');
         $('.notice-box').show().delay(3000).fadeOut();
        return;
    }
    if(post['content'].trim().length==0){
        $('span.notice').text('请输入文章内容');
         $('.notice-box').show().delay(3000).fadeOut();
        return;
    }
    post['tags']= $('input#tags').val();
    post['category_person']= $('input#categorys').val();
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

function delete_post() {
    var really_delete=confirm("確認刪除該文章嗎？");
    if ( really_delete==false ) {
        return;
    }
    var post={};
    post['post_id'] = $(this).attr('data-pid');
    token = getCookie('_xsrf');
    $.ajax({
        url: '/u/postdelete/',
        headers: {'X-XSRFToken' : token },
        data: post,
        //contentType: "application/json",
        //dataType: "JSON",
        type: "POST",
        success: delete_success(post),
        error: function ( data , status_text, jqXHR ) {
            alert('delete fail')
        },
    });
};

$(function() {
    if (typeof jsonData === 'undefined' || jsonData === null) {
        return;
    }
    //console.log(jsonData);
    $('input#txtTitle').val(jsonData['title']);
    $('input#txtTitle').focus();
    CKEDITOR.instances.editor.setData(jsonData['content']);
    $.each(jsonData['tags'], function(index,value) {
        console.log(index,value);
        // $('input#tags').tagsinput('add', value['name']);
        });
    $.each(jsonData['category'].slice(1), function(index,value) {
    console.log(index,value);
    // $('input#categorys').tagsinput('add', value['name']);
    });
    $("#radChl option").filter(function() {
        return this.text == jsonData['category'][0]['name'];
    }).attr('selected', true);
    }
)

