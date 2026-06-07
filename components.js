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

    function typesetMath() {
        if (window.MathJax && window.MathJax.typesetPromise) {
            MathJax.typesetPromise();
        }
    }

    function loadMathJax() {
        // Set config BEFORE loading MathJax
        window.MathJax = {
            tex: {
                inlineMath: [['$', '$'], ['\\(', '\\)']],
                displayMath: [['$$', '$$'], ['\\[', '\\]']]
            },
            options: {
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }
        };

        var script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js';
        script.async = true;
        script.onload = function () {
            typesetMath();
        };
        script.onerror = function () {
            console.warn('MathJax failed to load');
        };
        document.head.appendChild(script);
    }

    document.addEventListener('DOMContentLoaded', function () {
        loadComponent('[data-component="header"]', '/header.html', function () {
            initMobileMenu();
            typesetMath();
        });
        loadComponent('[data-component="footer"]', '/footer.html', function () {
            typesetMath();
        });
        loadMathJax();
    });
})();
