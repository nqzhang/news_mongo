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