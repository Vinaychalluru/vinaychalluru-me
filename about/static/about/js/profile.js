function scroll_to(clicked_link, nav_height) {
    var element_class = clicked_link.attr('href').replace('#', '.');
    var scroll_to = 0;
    if (element_class != '.top-content') {
        element_class += '-container';
        scroll_to = $(element_class).offset().top - nav_height;
    }
    if ($(window).scrollTop() != scroll_to) {
        $('html, body').stop().animate({scrollTop: scroll_to}, 1000);
    }
}

document.addEventListener('DOMContentLoaded', function() {

    /*
        Sidebar
    */
    document.querySelectorAll('.dismiss, .overlay').forEach(function(element) {
        element.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.remove('active');
            document.querySelector('.overlay').classList.remove('active');
        });
    });

    document.querySelectorAll('.open-menu').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector('.sidebar').classList.add('active');
            document.querySelector('.overlay').classList.add('active');
            // close opened sub-menus
            document.querySelectorAll('.collapse.show').forEach(function(subMenu) {
                subMenu.classList.remove('show'); // Simpler than toggle if the goal is just to remove 'show'
            });
            document.querySelectorAll('a[aria-expanded=true]').forEach(function(link) {
                link.setAttribute('aria-expanded', 'false');
            });
        });
    });

    /* change sidebar style */
    document.querySelectorAll('a.btn-customized-dark').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector('.sidebar').classList.remove('light');
        });
    });

    document.querySelectorAll('a.btn-customized-light').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            document.querySelector('.sidebar').classList.add('light');
        });
    });

    /* replace the default browser scrollbar in the sidebar, in case the sidebar menu has a height that is bigger than the viewport */

    /*
        Navigation (jQuery dependent scrolling, leave as is)
    */
    $('a.scroll-link').on('click', function (e) {
        e.preventDefault();
        scroll_to($(this), 0);
    });

    $('.to-top a').on('click', function (e) {
        e.preventDefault();
        if ($(window).scrollTop() != 0) {
            $('html, body').stop().animate({scrollTop: 0}, 1000);
        }
    });

});
