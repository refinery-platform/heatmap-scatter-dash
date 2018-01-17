$('body').on('click', '.nav-tabs li a', function(e) {
    e.preventDefault();
    $(this).tab('show');
});