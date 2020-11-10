new Vue({
  el: '#related_article_end',
  data : {
      articles: null
    },
  mounted :function() {
    let url = '/api/article/relatedes?post_id=' + post_id
    let lang = getUrlParam('lang');
    if (lang) {
       url = url + '&lang=' + lang
    }
    axios
      .get(url)
      .then(response => (this.articles = response.data))
  }
})

    $(document).ready(function () {
        var bodyw = $(window).width();
        if (bodyw < 800) {
            m_hot_posts_1 = $('.hot_posts_1').clone()
            m_hot_posts_1.css('width', 'auto');
            m_hot_posts_1.find("ul").html($("#template_hot_posts_1").html());
            $('.wrap').append(m_hot_posts_1);
            m_hot_posts_7 = $('.hot_posts_7').clone()
            m_hot_posts_7.css('width', 'auto');
            m_hot_posts_7.find("ul").html($("#template_hot_posts_7").html());
            $('.wrap').append(m_hot_posts_7);
        }
    });