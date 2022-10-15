var articleList = new List('main', {
  valueNames: [
    'listjs-title',
    { data: ['category'] }
  ],
  searchDelay: 500,
  pagination: true,
  page: 500
});

window.onhashchange = refreshList;
refreshList();
setupSearchBar();


function setupSearchBar() {
  var searchBar = document.getElementById('listjs-search');
  var inputtingSearchTerms = false;
  var fired = false;

  function search(keyword) {
    articleList.search(keyword, ['listjs-title']);
  }

  searchBar.addEventListener('compositionstart', function () { inputtingSearchTerms = true });
  searchBar.addEventListener('compositionend', function () {
    inputtingSearchTerms = false;
    search(searchBar.value);
    fired = true;
  });
  searchBar.addEventListener('input', function () {
    if (!inputtingSearchTerms && !fired) {
      search(searchBar.value);
    }
    fired = false;
  });
}

function refreshList() {
  var selectedCategory = decodeURI(location.hash).substring(1);
  var selectedCategoryText = selectedCategory.replace(/\-/g, '、');
  var selectedMenuItem = document.querySelector('.nav__items li a[href="#' + selectedCategory + '"]');
  var categoryExists = selectedMenuItem !== null;

  function updateBreadCrumb(categoryText) {
    var breadCrumb = document.getElementById('selected-catagory');
    breadCrumb.textContent = categoryExists ? ' > ' + categoryText : '';
    breadCrumb.scrollIntoView()
  }

  function highlightMenuItem(menuItem) {
    document.querySelectorAll('.nav__items li a').forEach(function (menuItem) {
      menuItem.classList.remove('active');
    });
    if (menuItem) {
      menuItem.classList.add('active');
    }
  }

  if (categoryExists) {
    function categorySelected(item) {
      return item.values()['category'] === selectedCategoryText;
    }
    articleList.filter(categorySelected);
  }
  else {
    articleList.filter();
  }
  updateBreadCrumb(selectedCategoryText);
  highlightMenuItem(selectedMenuItem);
}
