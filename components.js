(function () {
    'use strict';

    function loadComponent(selector, url, callback) {
        var el = document.querySelector(selector);
        if (!el) return;
        fetch(url)
            .then(function (res) { return res.text(); })
            .then(function (html) {
                el.innerHTML = html;
                if (callback) callback();
            })
            .catch(function () {
                console.warn('Failed to load component: ' + url);
            });
    }

    function initMobileMenu() {
        var hamburger = document.querySelector('.hamburger');
        var nav = document.getElementById('mainNav');
        if (!hamburger || !nav) return;

        hamburger.addEventListener('click', function () {
            var expanded = hamburger.getAttribute('aria-expanded') === 'true';
            hamburger.setAttribute('aria-expanded', !expanded);
            nav.classList.toggle('nav-open');
            document.body.classList.toggle('menu-open');
        });

        // Close menu when clicking a link (mobile)
        var navLinks = nav.querySelectorAll('a');
        for (var i = 0; i < navLinks.length; i++) {
            navLinks[i].addEventListener('click', function () {
                nav.classList.remove('nav-open');
                document.body.classList.remove('menu-open');
                hamburger.setAttribute('aria-expanded', 'false');
            });
        }

        // Submenu toggles on mobile
        var toggles = nav.querySelectorAll('.submenu-toggle, .submenu-toggle-mobile');
        for (var j = 0; j < toggles.length; j++) {
            toggles[j].addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                var parent = this.parentElement;
                parent.classList.toggle('submenu-open');
            });
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        loadComponent('[data-component="header"]', '/header.html', initMobileMenu);
        loadComponent('[data-component="footer"]', '/footer.html');
    });
})();
