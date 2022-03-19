function hideCategoriesExcept(category) {
  list = document.querySelectorAll('.archive section');
  for (i = 0; i < list.length; i++) {
    var element = list[i];
    element.style.display = (element.id == category ? 'block' : 'none');
  }
}
document.addEventListener("DOMContentLoaded", function () {
  var current = decodeURI(window.location.hash).substring(1) || '成聖之路';
  hideCategoriesExcept(current);
});
