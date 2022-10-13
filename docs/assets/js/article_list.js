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

function refreshList() {
  detailedList.filter(categorySelected);
  simpleList.filter(categorySelected);
  var currentSelected = decodeURI(location.hash).substring(1).replace(/\-/g, '、');
  updateBreadCrumb(currentSelected);
}

function categorySelected(item) {
  var category = item.values()['category'].replace(/、/g, '-');
  var currentSelected = decodeURI(location.hash).substring(1);
  return currentSelected === '' ? true : category === currentSelected;
}

function showDetails() {
  document.querySelector('#detailed-list').style.display = '';
  document.querySelector('#simple-list').style.display = 'none';
}

function hideDetails() {
  document.querySelector('#detailed-list').style.display = 'none';
  document.querySelector('#simple-list').style.display = '';
}

function updateBreadCrumb(category) {
  document.querySelector('#selected-catagory').textContent = category !== '' ? ' > ' + category : '';
}