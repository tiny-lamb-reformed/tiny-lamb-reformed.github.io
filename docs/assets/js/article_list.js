var valueNames = [
  'listjs-title',
  'archive__item-excerpt',
  { data: ['category'] }
];

var detailedList = new List('main', {
  valueNames: valueNames,
  listClass: 'entries-list'
});

var simpleList = new List('main', {
  valueNames: valueNames
});

window.onhashchange = refreshList;

var windowWidth = window.innerWidth
  || document.documentElement.clientWidth
  || document.body.clientWidth;
if (windowWidth < 600) {
  hideDetails();
}
else {
  showDetails();
}

setupSearchBar();


function setupSearchBar() {
  var searchBar = document.getElementById('quick-search');
  var inputtingSearchTerms = false;
  var fired = false;

  function search(keyword) {
    detailedList.search(keyword);
    simpleList.search(keyword);
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
    detailedList.filter(categorySelected);
    simpleList.filter(categorySelected);
  }
  else {
    detailedList.filter();
    simpleList.filter();
  }
  updateBreadCrumb(selectedCategoryText);
  highlightMenuItem(selectedMenuItem);
}

function showDetails() {
  document.getElementById('detailed-list').style.display = '';
  document.getElementById('simple-list').style.display = 'none';
}

function hideDetails() {
  document.getElementById('detailed-list').style.display = 'none';
  document.getElementById('simple-list').style.display = '';
}
