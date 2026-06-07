(function () {
    'use strict';

    var hoverTimer = null;

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

    function closeAllSubmenus(nav) {
        var open = nav.querySelectorAll('.submenu-open');
        for (var i = 0; i < open.length; i++) {
            open[i].classList.remove('submenu-open');
        }
    }

    function initMobileMenu() {
        var hamburger = document.querySelector('.hamburger');
        var nav = document.getElementById('mainNav');
        if (!hamburger || !nav) return;

        hamburger.addEventListener('click', function () {
            var expanded = hamburger.getAttribute('aria-expanded') === 'true';
            if (expanded) {
                nav.classList.remove('nav-open');
                document.body.classList.remove('menu-open');
                hamburger.setAttribute('aria-expanded', 'false');
                closeAllSubmenus(nav);
            } else {
                nav.classList.add('nav-open');
                document.body.classList.add('menu-open');
                hamburger.setAttribute('aria-expanded', 'true');
            }
        });

        var navLinks = nav.querySelectorAll('a');
        for (var i = 0; i < navLinks.length; i++) {
            navLinks[i].addEventListener('click', function () {
                nav.classList.remove('nav-open');
                document.body.classList.remove('menu-open');
                hamburger.setAttribute('aria-expanded', 'false');
                closeAllSubmenus(nav);
            });
        }

        var toggles = nav.querySelectorAll('.submenu-toggle');
        for (var j = 0; j < toggles.length; j++) {
            toggles[j].addEventListener('click', function (e) {
                e.preventDefault();
                e.stopPropagation();
                var parent = this.parentElement;
                parent.classList.toggle('submenu-open');
            });
        }
    }

    function initDesktopHover() {
        // Only activate hover menus on devices with a fine pointer (mouse/trackpad)
        // that actually support hover — skip on touch-only devices
        if (!window.matchMedia('(hover: hover)').matches) return;
        if (!window.matchMedia('(pointer: fine)').matches) return;

        var menuItems = document.querySelectorAll('.nav-list > li.has-submenu');

        function showSubmenu(li) {
            clearTimeout(hoverTimer);
            // Close any other hover submenus
            var allOpen = document.querySelectorAll('.nav-list > li.has-submenu.hover-open');
            for (var k = 0; k < allOpen.length; k++) {
                if (allOpen[k] !== li) allOpen[k].classList.remove('hover-open');
            }
            li.classList.add('hover-open');
        }

        function hideSubmenu(li) {
            hoverTimer = setTimeout(function () {
                li.classList.remove('hover-open');
            }, 300);
        }

        for (var i = 0; i < menuItems.length; i++) {
            (function (li) {
                var submenu = li.querySelector('.submenu');

                li.addEventListener('mouseenter', function () {
                    showSubmenu(li);
                });

                li.addEventListener('mouseleave', function () {
                    hideSubmenu(li);
                });

                if (submenu) {
                    submenu.addEventListener('mouseenter', function () {
                        showSubmenu(li);
                    });

                    submenu.addEventListener('mouseleave', function () {
                        hideSubmenu(li);
                    });
                }
            })(menuItems[i]);
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        loadComponent('[data-component="header"]', '/header.html', function () {
            initMobileMenu();
            initDesktopHover();
        });
        loadComponent('[data-component="footer"]', '/footer.html');
    });
})();
