$('body').on('click', '.nav-tabs a', function(e) {
    e.preventDefault();
    $(this).tab('show');
});