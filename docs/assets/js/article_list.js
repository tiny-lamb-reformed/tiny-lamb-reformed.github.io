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


window.onhashchange = filteritems;

function filteritems() {
  detailedList.filter(categorySelected);
  simpleList.filter(categorySelected);
}

function categorySelected(item) {
  if (location.hash === '') {
    return true;
  }
  else {
    var category = item.values()['category'].replace(/、/g, '-');
    return category === decodeURI(location.hash).substring(1);
  }
}
