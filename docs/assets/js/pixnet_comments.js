var PixnetComments = {
  data() {
    return {
      articleId: 0,
      currentPage: 1,
      totalPages: [],
      comments: []
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
        }
      }
      // TODO: add error handling
      xhr.send();
    },
    prevComments() { this.getComments(this.currentPage - 1); },
    nextComments() { this.getComments(this.currentPage + 1); },
    htmlDecode(input) {
      var doc = new DOMParser().parseFromString(input, "text/html");
      return doc.documentElement.textContent;
    }
  }
};
var vm = Vue.createApp(PixnetComments).mount('#pixnet-comments');
