var hash = decodeURI(window.location.hash).substring(1);
var HashNav = {
  data() {
    return {
      nav: nav_collections[hash],
      currentUrl: ''
    }
  },
  methods: {
    isSelected: function (child) {
      return child.url === this.currentUrl;
    }
  }
};
var vm = Vue.createApp(HashNav).mount('#hash-nav');
