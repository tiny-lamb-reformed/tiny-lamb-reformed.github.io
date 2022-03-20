function selectCategory(category) {
  $('#page-title').text(category);
  highlighSidebarItem(category);
  hideCategoriesExcept(category);
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
