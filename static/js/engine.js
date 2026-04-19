// 1. MOBILE MENU TOGGLE
        document.getElementById('mobileToggle').addEventListener('click', function() {
            var menu = document.getElementById('mobileMenu');
            menu.classList.toggle('active');
            if (menu.classList.contains('active')) {
                this.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>';
            } else {
                this.innerHTML = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>';
            }
        });

        // 2. SEARCH BOX
        const searchInput = document.getElementById('desktop-search');
        const dropdown = document.getElementById('search-dropdown');
        if (searchInput && dropdown) {
            searchInput.addEventListener('input', function() {
                let query = this.value;
                if (query.length > 1) { 
                    fetch("{% url 'blog:search_suggestions' %}?q=" + query)
                    .then(response => response.json())
                    .then(data => {
                        dropdown.innerHTML = ''; 
                        if (data.results.length > 0) {
                            dropdown.style.display = 'block';
                            data.results.forEach(item => {
                                let link = document.createElement('a');
                                link.href = item.url;
                                link.textContent = item.title;
                                link.style.display = 'block'; link.style.padding = '12px 15px'; link.style.textDecoration = 'none'; link.style.color = 'var(--text-main)'; link.style.fontSize = '0.7rem'; link.style.textTransform = 'uppercase'; link.style.borderBottom = '1px solid var(--accent-border)';
                                link.addEventListener('mouseover', () => link.style.backgroundColor = '#f0f0f0');
                                link.addEventListener('mouseout', () => link.style.backgroundColor = 'transparent');
                                dropdown.appendChild(link);
                            });
                        } else { dropdown.style.display = 'none'; }
                    });
                } else { dropdown.style.display = 'none'; }
            });
            document.addEventListener('click', e => { if (!e.target.closest('.search-box')) dropdown.style.display = 'none'; });
        }

        // 3. FAB DRAG PROTOCOL
        document.addEventListener("DOMContentLoaded", function() {
            const fab = document.querySelector('.floating-back-btn');
            if (!fab) return;

            let isDragging = false, hasJustDragged = false, startX, startY, initialMouseX, initialMouseY;
            const savedPos = localStorage.getItem('cipher_fab_position');
            
            // Define the No-Fly Zone (height of your navbar + a little padding)
            const SAFE_ZONE_TOP = 90; 
            
            if (savedPos) {
                const { top, left } = JSON.parse(savedPos);
                
                // Ensure saved position isn't trapped from an old session
                let safeTop = parseInt(top, 10);
                if (safeTop < SAFE_ZONE_TOP) safeTop = SAFE_ZONE_TOP;
                
                fab.style.transition = 'none'; 
                fab.style.top = safeTop + 'px'; 
                fab.style.left = left;
                fab.style.setProperty('bottom', 'auto', 'important');
                fab.style.setProperty('right', 'auto', 'important');
                setTimeout(() => fab.style.transition = '', 50); 
            }

            const dragStart = (e) => {
                if (e.type === 'touchstart') e = e.touches[0];
                initialMouseX = e.clientX; initialMouseY = e.clientY;
                const rect = fab.getBoundingClientRect();
                startX = initialMouseX - rect.left; startY = initialMouseY - rect.top;
                isDragging = false; hasJustDragged = false; fab.style.transition = 'none';
                document.addEventListener('mousemove', drag); document.addEventListener('touchmove', drag, { passive: false });
                document.addEventListener('mouseup', dragEnd); document.addEventListener('touchend', dragEnd);
            };

            const drag = (e) => {
                let clientX = e.clientX, clientY = e.clientY;
                if (e.type === 'touchmove') { clientX = e.touches[0].clientX; clientY = e.touches[0].clientY; }
                if (Math.abs(clientX - initialMouseX) > 5 || Math.abs(clientY - initialMouseY) > 5) {
                    isDragging = true; hasJustDragged = true; 
                    if (e.cancelable) e.preventDefault(); 
                }
                if (isDragging) {
                    let newLeft = clientX - startX;
                    let newTop = clientY - startY;
                    
                    // Apply boundaries: left/right limits
                    newLeft = Math.max(0, Math.min(newLeft, window.innerWidth - fab.offsetWidth));
                    // Apply boundaries: top/bottom limits (using our SAFE_ZONE_TOP instead of 0)
                    newTop = Math.max(SAFE_ZONE_TOP, Math.min(newTop, window.innerHeight - fab.offsetHeight));
                    
                    fab.style.left = newLeft + 'px'; 
                    fab.style.top = newTop + 'px';
                    fab.style.setProperty('bottom', 'auto', 'important');
                    fab.style.setProperty('right', 'auto', 'important');
                }
            };

            const dragEnd = () => {
                document.removeEventListener('mousemove', drag); document.removeEventListener('touchmove', drag);
                document.removeEventListener('mouseup', dragEnd); document.removeEventListener('touchend', dragEnd);
                fab.style.transition = '';
                if (isDragging) localStorage.setItem('cipher_fab_position', JSON.stringify({ top: fab.style.top, left: fab.style.left }));
                setTimeout(() => { hasJustDragged = false; }, 50);
                isDragging = false;
            };

            fab.addEventListener('click', (e) => { if (hasJustDragged) { e.preventDefault(); e.stopImmediatePropagation(); } });
            fab.addEventListener('dragstart', (e) => e.preventDefault());
            fab.addEventListener('mousedown', dragStart);
            fab.addEventListener('touchstart', dragStart, { passive: false });
        });

        // 5. CORE DOM ENGINE
        document.addEventListener("DOMContentLoaded", function() {
            
            // Close Modals via Background Click
            document.querySelectorAll('.auth-modal-overlay').forEach(overlay => {
                overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModals(); });
            });

            // AJAX INTERCEPTOR FOR MODAL FORMS
            async function handleAuthSubmit(e, formType) {
                e.preventDefault();
                const form = e.target;
                const btn = form.querySelector('button[type="submit"]');
                const originalText = btn.textContent;
                btn.textContent = 'AUTHENTICATING...'; btn.disabled = true;

                try {
                    const formData = new FormData(form);
                    const response = await fetch(form.action, { method: 'POST', body: formData, headers: { 'X-Requested-With': 'XMLHttpRequest' } });
                    if (!response.url.includes('/login') && !response.url.includes('/register')) { window.location.reload(); return; }

                    const html = await response.text();
                    const doc = new DOMParser().parseFromString(html, 'text/html');
                    const oldError = form.querySelector('.modal-error-box');
                    if (oldError) oldError.remove();

                    let errorHtml = '';
                    if (formType === 'login') {
                        const alertDiv = doc.querySelector('.alert');
                        errorHtml = alertDiv ? alertDiv.innerHTML : "Authentication failed. Invalid credentials.";
                    } else {
                        const errorDiv = doc.querySelector('div[style*="#d93025"]');
                        errorHtml = errorDiv ? errorDiv.innerHTML : "Registration failed. Please check the rules.";
                    }

                    const errorContainer = document.createElement('div');
                    errorContainer.className = 'modal-error-box';
                    errorContainer.style.cssText = 'background: rgba(255, 0, 0, 0.05); border-left: 3px solid #d93025; padding: 10px; margin-bottom: 15px; font-size: 0.75rem; color: #d93025; text-align: left; line-height: 1.4;';
                    errorContainer.innerHTML = errorHtml;
                    form.insertBefore(errorContainer, form.firstChild);

                } catch (error) { console.error("Auth Error:", error); } 
                finally { btn.textContent = originalText; btn.disabled = false; }
            }

            document.querySelector('#loginModal form').addEventListener('submit', (e) => handleAuthSubmit(e, 'login'));
            document.querySelector('#signupModal form').addEventListener('submit', (e) => handleAuthSubmit(e, 'register'));

            // Password Visibility Toggle
            document.querySelectorAll('.toggle-password').forEach(btn => {
                btn.addEventListener('click', function() {
                    const input = this.previousElementSibling;
                    if (input.type === 'password') {
                        input.type = 'text';
                        this.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>';
                        this.style.color = 'var(--text-main)';
                    } else {
                        input.type = 'password';
                        this.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
                        this.style.color = 'var(--text-muted)';
                    }
                });
            });

            /* 6. CINEMATIC ENGINE: REVEAL ON SCROLL */
        const contentElements = document.querySelectorAll('.main-content p, .main-content h1, .main-content h2, .main-content img:not(.no-reveal), .main-content .card');
        contentElements.forEach(el => el.classList.add('reveal-element'));

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                } else {
                    // RESTORED: Removing the class when out of view makes it animate continuously!
                    entry.target.classList.remove('is-visible');
                }
            });
        }, { threshold: 0.1, rootMargin: "0px 0px -20px 0px" });
        contentElements.forEach(el => observer.observe(el));

            /* 7. THE PREMIUM DECRYPTION LOADER */
            const letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%&*";
            const sysLogs = [
                "LOCATING_NODE...",
                "VERIFYING_HOST_IDENTITY...",
                "BYPASSING_FIREWALL...",
                "DECRYPTING_PAYLOAD...",
                "ESTABLISHING_SECURE_TUNNEL...",
                "ACCESS_GRANTED."
            ];
            const isMobile = window.matchMedia('(max-width: 768px)').matches;

            document.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', e => {
                    const href = link.getAttribute('href');
                    
                    if (!href || href.startsWith('#') || link.hasAttribute('onclick') || link.target === "_blank" || href.includes('bookmark')) return;

                    e.preventDefault(); 

                    // On mobile, skip the scramble animation — just navigate instantly
                    if (isMobile) {
                        window.location.href = href;
                        return;
                    }

                    const loader = document.getElementById('decrypt-loader');
                    const text = document.getElementById('decrypt-text');
                    const subtext = document.getElementById('decrypt-subtext');
                    
                    loader.classList.add('active'); 

                    let iterations = 0;
                    let logIndex = 0;
                    const targetText = "ESTABLISHING_LINK...";

                    const logInterval = setInterval(() => {
                        if (logIndex < sysLogs.length) {
                            subtext.innerText = sysLogs[logIndex];
                            logIndex++;
                        }
                    }, 120);

                    const interval = setInterval(() => {
                        text.innerText = targetText.split("").map((letter, index) => {
                            if(index < iterations) return targetText[index];
                            return letters[Math.floor(Math.random() * letters.length)];
                        }).join("");

                        if(iterations >= targetText.length) {
                            clearInterval(interval);
                            clearInterval(logInterval);
                            subtext.innerText = "LINK_ESTABLISHED.";
                            setTimeout(() => { window.location.href = href; }, 150); 
                        }
                        iterations += 1 / 2; 
                    }, 30);
                });
            });
        });

        // 8. SCROLL PROGRESS BAR
        window.addEventListener('scroll', () => {
            let winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            let height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            let scrolled = (winScroll / height) * 100;
            document.getElementById("scroll-progress").style.width = scrolled + "%";
        });

            document.addEventListener('DOMContentLoaded', function() {
        // Find every single link on the page that has "bookmark" in the URL
        const bookmarkLinks = document.querySelectorAll('a[href*="bookmark"]');

        bookmarkLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();  // STOPS the page reload
                e.stopPropagation(); // <-- NEW: DESTROYS the click so it doesn't bubble up to the Library Card

                // Add the ajax flag to tell the backend not to redirect
                const url = this.getAttribute('href') + '?ajax=true';
                const svg = this.querySelector('svg');
                
                // Remember if the icon was originally white (hero) or gray (grid)
                if (!this.dataset.defaultStroke) {
                    this.dataset.defaultStroke = svg.getAttribute('stroke');
                }

                // Send the background request
                fetch(url, {
                    method: 'GET',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(response => response.json())
                .then(data => {
                    // Update the UI instantly without reloading
                    if (data.is_bookmarked) {
                        // Saved: Fill with gold
                        svg.setAttribute('fill', 'var(--accent-gold)');
                        svg.setAttribute('stroke', 'var(--accent-gold)');
                        svg.setAttribute('stroke-width', '2');
                    } else {
                        // Removed: Empty it out and restore original line color
                        svg.setAttribute('fill', 'none');
                        svg.setAttribute('stroke', this.dataset.defaultStroke);
                        svg.setAttribute('stroke-width', '1.5');

                        // NEW: If we are on the Library page, smoothly fade the card out and delete it
                        const libCard = this.closest('.lib-card');
                        if (libCard) {
                            libCard.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                            libCard.style.opacity = '0';
                            libCard.style.transform = 'scale(0.95)';
                            setTimeout(() => libCard.remove(), 400); // Remove from HTML after fade finishes
                        }
                    }
                })
                .catch(error => console.error('Error syncing library:', error));
            });
        });
    });

       // BULLETPROOF MODAL ENGINE
    window.closeModals = function() {
        const login = document.getElementById('loginModal');
        const signup = document.getElementById('signupModal');
        if (login) login.classList.remove('active');
        if (signup) signup.classList.remove('active');
    };
    
    window.switchModal = function(target) {
        window.closeModals(); 
        if (target === 'signup') {
            const el = document.getElementById('signupModal');
            if (el) el.classList.add('active');
        } else if (target === 'login') {
            const el = document.getElementById('loginModal');
            if (el) el.classList.add('active');
        }
    };

    // FIX FOR BROWSER "BACK" BUTTON (BFCache Defroster)
    window.addEventListener('pageshow', function(event) {
        const loader = document.getElementById('decrypt-loader');
        if (loader && loader.classList.contains('active')) {
            // If the page was restored from cache with the loader on, turn it off
            loader.classList.remove('active');
            
            // Also reset the text so it's ready for the next click
            document.getElementById('decrypt-text').innerText = "AWAITING_PROTOCOL";
            document.getElementById('decrypt-subtext').innerText = "INITIALIZING_HANDSHAKE...";
        }
    });