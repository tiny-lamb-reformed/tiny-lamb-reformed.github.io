var PixnetComments = {
  data() {
    return {
      articleId: 0,
      currentPage: 1,
      totalPages: [],
      comments: [],
      total: 0,
      commentClosed: true
    }
  },
  methods: {
    init(articleId) {
      this.articleId = articleId;
      this.getComments(1);
    },
    getComments(page) {
      this.currentPage = page;

      var vm = this;
      var xhr = new XMLHttpRequest();
      var PRE_PAGE = 20;
      var url = 'https://emma.pixnet.cc/blog/articles/' + this.articleId + '/comments'
        + '?user=mickey1124&page=' + this.currentPage + '&per_page=' + PRE_PAGE;
      xhr.open('GET', url);
      xhr.onload = function () {
        if (xhr.status === 200) {
          var resp = JSON.parse(xhr.responseText);
          console.log(resp.message);
          vm.totalPages = [];
          for (var i = 1; i <= Math.ceil(resp.total / PRE_PAGE); i++) {
            vm.totalPages.push(i);
          }
          vm.comments = resp.comments;
          vm.total = resp.total;
          vm.commentClosed = resp.article.comment_perm === "0";
        }
      }
      // TODO: add error handling
      xhr.send();
    },
    prevComments() { if (this.currentPage > 1) this.getComments(this.currentPage - 1); },
    nextComments() { if (this.currentPage < this.totalPages.length) this.getComments(this.currentPage + 1); },
    htmlDecode(input) {
      var doc = new DOMParser().parseFromString(input, "text/html");
      return doc.documentElement.textContent;
    }
  }
};
var vm = Vue.createApp(PixnetComments).mount('#pixnet-comments');