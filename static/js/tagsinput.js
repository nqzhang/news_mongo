/*
     <input id="categorys" name='categorys' type="text" data-display-name='文章分類' data-role="tagsinput" value="" placeholder="輸入文章分類">
    使用此组件， 
    1. 应该使用input标签
    2. 加入 data-role="tagsinput" 让组件检测识别
    3， data-display-name 为标签的显示名称，不会在发送post时使用，仅仅用于给用户显示
*/

$(document).ready(function(){

    $('input[data-role=tagsinput]').each(function(index, element){
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
    .append(renderExistingTags(index, element))
    .append(renderAddTagButton(index, element))
    
    $(element).after($content);
    updateInputValue(index);
}

// 加入已有的标签
function renderExistingTags(index, element) {
    if(typeof jsonData === 'undefined' || jsonData === null) return '<div class="tags"></div>';

    var elementName = $(element).attr('name');
    var $content = $('<div class="tags"></div>');
    jsonData[elementName].forEach(function(value, i) {
        $($content).append(renderTag(index, false,i ,value.name))
    });

    return $content
}

//加入“添加标签”按钮
function renderAddTagButton(index, element) {
    //组合“添加标签”按钮，并且连接相应event listener
    var $addTagButton = $('<div class="add-more-tags"><img src="/static/svgs/add-more.svg" />添加新' + $(element).data('display-name') + '</div>')
        .on('click', function() {
            //没有空标签时候才会添加新标签
            if (!hasEmptyTag(index)) {
                // add new tag into DOM
                $($('.tag-section')[index]).children('.tags').append(renderTag(index));
                // focus on the new tag
                $($('.tag-section')[index]).find('.tags .tag-input:last').focus();
            }
        })

    return $addTagButton;
}

function renderTag(index, isNew = true, tagIndex = null, value = null) {
    var preVal;

    //删除按钮
    var closeButton = $('<span class="tag-close">╳</span>')
        .click(function(){
            $(this).parent().remove();
            updateInputValue(index);
        });

    //标签
    var $tag = $('<span />', {
            'class': 'tag-input',
            'contenteditable': true
        })
        .on('input', function() {
            //更新真正input的value
            updateInputValue(index);
        })
        .focus(function() {
            preVal = $(this).text();
        });
    
    if (!isNew) {
        $($tag).text(value);
    }

    var wrapper = $('<div class="tag-wrapper"></div>')
        .append($($tag))
        .append($(closeButton))
    return wrapper;
}

//全面检查所有tag，并且更新input的value
function updateInputValue(index) {
    var $inputElement = $('input[data-role=tagsinput]').eq(index);
    var tagsArr = [];
    $inputElement.parent().find('.tag-wrapper .tag-input').each(function(index, tagElement){
        tagsArr.push($(tagElement).text());
    });

    $($inputElement).val(tagsArr.join());
}

function hasEmptyTag(index) {
    var $inputElement = $('input[data-role=tagsinput]').eq(index);
    
    var hasEmptyTag = false
    $inputElement.parent().find('.tag-wrapper .tag-input').each(function(index, tagElement){
        if($(tagElement).text() === '') {
            hasEmptyTag = true;
        }
    });

    return hasEmptyTag;
}

function renderOptions() {

}