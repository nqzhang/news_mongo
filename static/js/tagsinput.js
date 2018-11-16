/*
     <input id="categorys" name='categorys' type="text" data-display-name='文章分類' data-role="tagsinput" value="" placeholder="輸入文章分類">
    使用此组件， 
    1. 应该使用input标签
    2. 加入 data-role="tagsinput" 让组件检测识别
    3， data-display-name 为标签的显示名称，不会在发送post时使用，仅仅用于给用户显示
*/

$(document).ready(function(){

    // 这个变量用来检查点击新加按钮以后会不会增加新的标签输入栏，如果当前已经有一个空的标签栏，则不会添加新的
    window.hasEmptyTag = {};

    $('input[data-role=tagsinput]').each(function(index, element){
        window.hasEmptyTag[index] = false;
        init(index, element);
    });
});

// 初始化
function init(index, element) {
    // 隐藏真正的input，之后会用js操作他的数据
    $(element).css('display', 'none');

    //组合所有内容，添加到真正的input后面
    var $content = $('<div/>', {
        'class': 'tag-section'
    })
    .append(renderExistingTags())
    .append(renderAddTagButton(index, element))
    
    $(element).after($content);
}

// 加入已有的标签
function renderExistingTags() {
    return '<div class="tags"></div>';
}

//加入“添加标签”按钮
function renderAddTagButton(index, element) {
    //组合“添加标签”按钮，并且连接相应event listener
    var $addTagButton = $('<div class="add-more-tags"><img src="/static/svgs/add-more.svg" />添加新' + $(element).data('display-name') + '</div>')
        .on('click', function() {
            
            //没有空标签时候才会添加新标签
            if (!window.hasEmptyTag[index]) {
                // add new tag into DOM
                $($('.tag-section')[index]).children('.tags').append(renderNewTag(index));
                // update global variable
                window.hasEmptyTag[index] = true;
                // focus on the new tag
                $($('.tag-section')[index]).children('.tags .tag-input:last-child')[0].focus();
            }
        })

    return $addTagButton;
}

function renderNewTag(index) {
    var preVal;
    //删除按钮
    var closeButton = $('<span class="tag-close">╳</span>')
        .click(function(){
            //如果删除了空标签，设置hasEmptyTag为false， 这样就可以允许用户再继续添加标签
            if($(this).prev().val() === "") {
                window.hasEmptyTag[index] = false
            }
            $(this).parent().remove();
        });

    //标签
    var $tag = $('<input />', {
            'class': 'tag-input',
            'type': 'text',
            'max-length': '50'})
        .change(function() {
            //判定是否需要改变hasEmptyTag变量
            if($(this).val() === '' ) {
                window.hasEmptyTag[index] = true;
            } else {
                if (window.hasEmptyTag[index] === false || preVal === '') {
                    window.hasEmptyTag[index] = false;
                }
            }
        })
        .focus(function() {
            preVal = $(this).val();
        });
    
    var wrapper = $('<div class="tag-wrapper"></div>')
        .append($($tag))
        .append($(closeButton))
    return wrapper;
}


function renderDefaultTags() {

}

function renderOptions() {

}