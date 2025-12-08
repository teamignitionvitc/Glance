document.addEventListener('DOMContentLoaded', () => {
    // Mobile navigation toggle
    const menuToggle = document.getElementById('menu-toggle');
    const sidebar = document.getElementById('sidebar');
    const content = document.querySelector('.content');
    const menuIcon = menuToggle.querySelector('.icon-menu');
    const closeIcon = menuToggle.querySelector('.icon-close');

    menuToggle.addEventListener('click', (e) => {
        e.stopPropagation(); // Prevent this click from immediately closing the menu
        const isOpen = sidebar.classList.toggle('open');
        document.body.classList.toggle('sidebar-is-open', isOpen);

        menuIcon.style.display = isOpen ? 'none' : 'block';
        closeIcon.style.display = isOpen ? 'block' : 'none';
    });

    // Function to close the sidebar
    const closeSidebar = () => {
        if (sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            document.body.classList.remove('sidebar-is-open');
            menuIcon.style.display = 'block';
            closeIcon.style.display = 'none';
        }
    };

    // Close sidebar when clicking on the dimmed content area or any other body element
    document.body.addEventListener('click', (e) => {
        if (document.body.classList.contains('sidebar-is-open')) {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                closeSidebar();
            }
        }
    });

    // Copy-to-clipboard for code blocks with improved feedback
    document.querySelectorAll('.copy-btn').forEach(button => {
        const originalContent = button.innerHTML;
        const copiedContent = `<svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg><span>Copied!</span>`;

        button.addEventListener('click', () => {
            const pre = button.closest('.code-block-wrapper').querySelector('pre');
            if (pre) {
                const code = pre.querySelector('code').innerText;
                navigator.clipboard.writeText(code).then(() => {
                    button.innerHTML = copiedContent;
                    button.classList.add('copied');
                    setTimeout(() => {
                        button.innerHTML = originalContent;
                        button.classList.remove('copied');
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                });
            }
        });
    });


    // Active nav item on scroll
    const sections = document.querySelectorAll('main section[id]');
    const navItems = document.querySelectorAll('.nav-item');
    const observer = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                navItems.forEach(item => {
                    item.classList.toggle('active', item.getAttribute('href') === `#${id}`);
                });
            }
        });
    }, { rootMargin: '-30% 0px -70% 0px' });

    sections.forEach(section => observer.observe(section));

    // --- ENHANCED SEARCH FUNCTIONALITY WITH HIGHLIGHTING ---
    const searchInput = document.getElementById('search-input');
    const searchClearBtn = document.getElementById('search-clear-btn');
    const navLinks = document.querySelectorAll('.nav-item');
    const navSections = document.querySelectorAll('.nav-section');
    const mainContent = document.querySelector('main');
    const mainHeader = document.querySelector('.main-header');

    const searchableSectionsData = Array.from(document.querySelectorAll('main > section[id]')).map(section => {
        const title = section.querySelector('h2');
        return {
            id: section.id,
            element: section,
            title: title ? title.textContent.toLowerCase() : '',
            originalHTML: section.innerHTML // Store original HTML to remove highlights
        };
    });

    let noResultsMessage = document.createElement('div');
    noResultsMessage.id = 'no-results';
    noResultsMessage.style.display = 'none';
    noResultsMessage.style.textAlign = 'center';
    noResultsMessage.style.padding = '4rem 0';
    mainContent.appendChild(noResultsMessage);

    function escapeRegex(string) {
        return string.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&');
    }

    function highlightText(searchTerm) {
        if (!searchTerm) return;
        const regex = new RegExp(`(${escapeRegex(searchTerm)})`, 'gi');
        searchableSectionsData.forEach(sec => {
            if (sec.element.style.display !== 'none') {
                sec.element.innerHTML = sec.originalHTML.replace(regex, `<mark>$1</mark>`);
            }
        });
    }

    function removeHighlights() {
        searchableSectionsData.forEach(sec => {
            sec.element.innerHTML = sec.originalHTML;
        });
    }

    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        searchClearBtn.style.display = searchTerm ? 'block' : 'none';

        removeHighlights(); // Always remove old highlights first

        if (searchTerm === '') {
            mainHeader.style.display = 'block';
            searchableSectionsData.forEach(sec => sec.element.style.display = 'block');
            navLinks.forEach(link => link.style.display = 'flex');
            navSections.forEach(section => section.style.display = 'block');
            noResultsMessage.style.display = 'none';
            return;
        }

        const matchedIds = new Set();

        searchableSectionsData.forEach(sec => {
            const content = sec.title + ' ' + sec.element.textContent.toLowerCase();
            const isMatch = content.includes(searchTerm);
            sec.element.style.display = isMatch ? 'block' : 'none';
            if (isMatch) {
                matchedIds.add(sec.id);
            }
        });

        highlightText(searchTerm);

        navLinks.forEach(link => {
            const linkId = link.getAttribute('href')?.substring(1);
            link.style.display = (linkId && matchedIds.has(linkId)) ? 'flex' : 'none';
        });

        navSections.forEach(section => {
            const visibleLinks = section.querySelectorAll('.nav-item[style*="display: flex"]');
            section.style.display = visibleLinks.length > 0 ? 'block' : 'none';
        });

        if (matchedIds.size === 0) {
            mainHeader.style.display = 'none';
            noResultsMessage.innerHTML = `<h3>No results found for "${searchInput.value}"</h3><p>Try searching for a different term or check your spelling.</p>`;
            noResultsMessage.style.display = 'block';
        } else {
            mainHeader.style.display = 'block';
            noResultsMessage.style.display = 'none';
        }
    }

    // Smart scroll for sidebar links when search is active
    navLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            const searchTerm = searchInput.value.trim();
            if (searchTerm) {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetSection = document.getElementById(targetId);

                if (targetSection) {
                    const firstHighlight = targetSection.querySelector('mark');
                    if (firstHighlight) {
                        firstHighlight.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    } else {
                        targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }
                }
            }
            // Close sidebar on mobile after click
            if (window.innerWidth <= 1024) {
                closeSidebar();
            }
        });
    });


    searchInput.addEventListener('input', performSearch);

    searchClearBtn.addEventListener('click', () => {
        searchInput.value = '';
        searchInput.focus();
        performSearch();
    });


    // --- Fetch GitHub Contributors ---
    const listElement = document.getElementById('contributor-list');

    function displayContributors(contributors) {
        listElement.innerHTML = ''; // Clear loading message

        const maxVisible = 4; // Show max 4 avatars
        const topContributors = contributors.filter(c => c.type !== 'Bot');

        const visibleContributors = topContributors.slice(0, maxVisible);

        visibleContributors.forEach(contributor => {
            const listItem = document.createElement('li');
            listItem.className = 'contributor-item';
            listItem.title = contributor.login;

            listItem.innerHTML = `
                        <a href="${contributor.html_url}" target="_blank" rel="noopener noreferrer">
                            <img src="${contributor.avatar_url}" alt="Avatar for ${contributor.login}" loading="lazy">
                        </a>
                    `;
            listElement.appendChild(listItem);
        });

        if (topContributors.length > maxVisible) {
            const remainingCount = topContributors.length - maxVisible;
            const overflowItem = document.createElement('li');
            overflowItem.className = 'contributor-overflow';
            overflowItem.title = `${remainingCount} more contributors`;
            overflowItem.textContent = `+${remainingCount}`;
            listElement.appendChild(overflowItem);
        }
    }

    async function fetchContributors() {
        const owner = 'teamignitionvitc';
        const repo = 'Glance';
        const apiUrl = `https://api.github.com/repos/${owner}/${repo}/contributors`;
        const cacheKey = 'githubContributors';
        const cacheDuration = 24 * 60 * 60 * 1000; // 24 hours

        const cachedData = localStorage.getItem(cacheKey);

        if (cachedData) {
            const { timestamp, data } = JSON.parse(cachedData);
            if (Date.now() - timestamp < cacheDuration) {
                displayContributors(data);
                return;
            }
        }

        try {
            const response = await fetch(apiUrl);
            if (!response.ok) {
                throw new Error(`GitHub API error: ${response.status}`);
            }
            const contributors = await response.json();

            const cachePayload = {
                timestamp: Date.now(),
                data: contributors
            };
            localStorage.setItem(cacheKey, JSON.stringify(cachePayload));
            displayContributors(contributors);

        } catch (error) {
            if (cachedData) {
                console.log('GitHub API request failed, serving stale data from cache.', error.message);
                const { data } = JSON.parse(cachedData);
                displayContributors(data);
            } else {
                console.error('Failed to fetch contributors and no cache is available:', error);
                listElement.innerHTML = '<li class="contributor-list-loading">Could not load contributors.</li>';
            }
        }
    }

    fetchContributors();

    // Animate workflow on scroll
    const workflowObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, { threshold: 0.5 });

    document.querySelectorAll('.workflow-step').forEach(step => {
        workflowObserver.observe(step);
    });
});

// --- EASTER EGGS ---

// 1. Console Greeting
console.log(
    '%c🚀 Ready for liftoff? %c\nChecked out the source content? You are a curious one! \n\n✨ KONAMI CODE: ↑ ↑ ↓ ↓ ← → ← → b a\n\nJoin us at Team Ignition: https://teamignition.space',
    'font-size: 20px; font-weight: bold; color: #0a84ff;',
    'font-size: 14px; color: #a0a0a5;'
);

// 2. Logo Spin (5 Clicks)
const mainLogo = document.querySelector('.main-header .main-logo');
if (mainLogo) {
    let logoClicks = 0;
    mainLogo.addEventListener('click', () => {
        logoClicks++;
        if (logoClicks === 5) {
            mainLogo.classList.add('spin-wildly');
            setTimeout(() => mainLogo.classList.remove('spin-wildly'), 2000);
            logoClicks = 0;
        }
    });
}

// 3. Konami Code (Rocket Launch)
const konamiCode = [
    'ArrowUp', 'ArrowUp',
    'ArrowDown', 'ArrowDown',
    'ArrowLeft', 'ArrowRight',
    'ArrowLeft', 'ArrowRight',
    'b', 'a'
];
let konamiIndex = 0;

document.addEventListener('keydown', (e) => {
    if (e.key === konamiCode[konamiIndex]) {
        konamiIndex++;
        if (konamiIndex === konamiCode.length) {
            launchRocket();
            konamiIndex = 0;
        }
    } else {
        konamiIndex = 0;
    }
});

function launchRocket() {
    // block multiple launches
    if (document.querySelector('.easter-egg-rocket')) return;

    const rocket = document.createElement('div');
    rocket.className = 'easter-egg-rocket';

    // Build Rocket DOM
    rocket.innerHTML = `
                    <div class="rocket-fuselage">
                        <div class="rocket-window"></div>
                    </div>
                    <div class="rocket-fin fin-left"></div>
                    <div class="rocket-fin fin-right"></div>
                    <div class="rocket-exhaust-flame"></div>
                `;

    document.body.appendChild(rocket);

    // Shake the CONTAINER, not body (to preserve fixed positioning context of rocket)
    const container = document.querySelector('.container');
    if (container) container.classList.add('shake-screen');

    // Launch Animation - Use setTimeout to ensure DOM render & transition
    setTimeout(() => {
        rocket.style.bottom = '120vh'; // Fly off screen
    }, 50);

    // Smoke Particle System
    let smokeInterval = setInterval(() => {
        createSmoke(rocket);
    }, 50);

    // Cleanup
    setTimeout(() => {
        clearInterval(smokeInterval);
        rocket.remove();
        if (container) container.classList.remove('shake-screen');
    }, 3000);
}

function createSmoke(rocket) {
    const rect = rocket.getBoundingClientRect();
    const smoke = document.createElement('div');
    smoke.className = 'rocket-smoke';

    // Randomize smoke size and position slightly
    const size = Math.random() * 20 + 10;
    smoke.style.width = `${size}px`;
    smoke.style.height = `${size}px`;
    smoke.style.left = `${rect.left + rect.width / 2 - size / 2 + (Math.random() * 10 - 5)}px`;
    smoke.style.bottom = `${window.innerHeight - rect.bottom - 10}px`;

    document.body.appendChild(smoke);

    // Remove smoke particle after animation
    setTimeout(() => {
        smoke.remove();
    }, 1500);
}
