function hideCategoriesExcept(category) {
  var list = document.querySelectorAll('.archive section');
  for (i = 0; i < list.length; i++) {
    var element = list[i];
    element.style.display = (element.id == category ? 'block' : 'none');
  }
}

function showOnlyMatch() {
  var keyword_list = $('#search').val();
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

document.addEventListener("DOMContentLoaded", function () {
  var current = decodeURI(window.location.hash).substring(1) || '成聖之路';
  hideCategoriesExcept(current);
});
