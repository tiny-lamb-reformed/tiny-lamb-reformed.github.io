var hash = decodeURI(window.location.hash).substring(1);
var HashNav = {
  data() {
    return {
      nav_list: Object.keys(nav_collections),
      nav: nav_collections[hash]
    }
  },
  methods: {
    isSelected: function (child) {
      return child.url.split('#')[0] === window.location.pathname;
    }
  }
};
var vm = Vue.createApp(HashNav).mount('#hash-nav');
