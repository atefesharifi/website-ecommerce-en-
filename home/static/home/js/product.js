$('.dropdown-submenu .dropdown-toggle').on("click", function(e) {
    e.stopPropagation();
    e.preventDefault();
    $(this).next('.dropdown-menu').toggle();
});
$('.dropdown-submenu>a').unbind('click').click(function(e){
    $('.dropdown-submenu>ul').hide();
    $(this).next('ul').toggle();
    e.stopPropagation();
    e.preventDefault();
});
document.getElementById("search-form").submit()