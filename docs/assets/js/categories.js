function hideCategoriesExcept(category) {
  list = document.querySelectorAll('.archive section');
  for (i = 0; i < list.length; i++) {
    var element = list[i];
    element.style.display = (element.id == category ? 'block' : 'none');
  }
}
