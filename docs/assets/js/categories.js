function selectCategory(category) {
  if (categoryExist(category)) {
    $('#page-title').text(category);
    highlighSidebarItem(category);
    hideCategoriesExcept(category);
  }
  $('#search').focus();
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function categoryExist(category) {
  return $('.nav__items li a[data-category="' + category + '"]').length > 0;
}

function highlighSidebarItem(category) {
  $('.nav__items li a').removeClass('active');
  $('.nav__items li a[data-category="' + category + '"]').addClass('active');
}

function hideCategoriesExcept(category) {
  $('.archive section').hide();
  $('.archive section[data-category="' + category + '"]').show();
}

function showOnlyMatch() {
  var keyword_list = $('#search').val().split(' ');
  var filter = '';
  for (var i = 0; i < keyword_list.length; i++) {
    var keyword = keyword_list[i];
    filter += 'a:contains("' + keyword + '")';
  }
  $('div.list__item').show();
  if (filter) {
    $('div.list__item:not(:has(' + filter + '))').hide();
  }
}

$(document).ready(function () {
  var category = decodeURI(window.location.hash).substring(1);
  if (category) {
    selectCategory(category);
  }
});
