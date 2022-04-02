function selectCategory(category) {
  if (categoryExist(category)) {
    $('#page-title').text(category);
    highlighSidebarItem(category);
    hideCategoriesExcept(category);
    showOnlyMatch();
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
  $('.archive div[data-category]').hide();
  $('.archive div[data-category="' + category + '"]').show();
}

function showOnlyMatch() {
  var keyword_list = $('#search').val().split(' ');
  var filter = '';
  for (var i = 0; i < keyword_list.length; i++) {
    var keyword = keyword_list[i];
    filter += ':contains("' + keyword + '")';
  }
  $('div.list__item').show();
  if (filter) {
    $('div.list__item:not(' + filter + ')').hide();
  }
}

document.addEventListener("DOMContentLoaded", function () {
  var category = decodeURI(window.location.hash).substring(1) || '成聖之路';
  if (category) {
    selectCategory(category);
  }

  var inputtingSearchTerms = false;
  var fired = false;
  $('#search')
    .on('compositionstart', function () { inputtingSearchTerms = true })
    .on('compositionend', function () {
      inputtingSearchTerms = false;
      showOnlyMatch();
      fired = true;
    })
    .on('input', function () {
      if (!inputtingSearchTerms && !fired) {
        showOnlyMatch();
      }
      fired = false;
    });
});
