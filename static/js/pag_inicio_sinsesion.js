document.addEventListener('DOMContentLoaded', () => {
    const menu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('sidebar-overlay');
    const openBtn = document.getElementById('open-sidebar');
    const closeBtn = document.getElementById('close-sidebar');

    const toggleMenu = (show) => {
        if (show) {
            menu.classList.remove('hidden', 'translate-x-full');
            overlay.classList.remove('opacity-0', 'pointer-events-none');
            document.body.classList.add('overflow-hidden');
        } else {
            menu.classList.add('translate-x-full');
            overlay.classList.add('opacity-0', 'pointer-events-none');
            setTimeout(() => menu.classList.add('hidden'), 300);
            document.body.classList.remove('overflow-hidden');
        }
    };

    if (openBtn) {
        openBtn.addEventListener('click', () => toggleMenu(true));
    }
    if (closeBtn) {
        closeBtn.addEventListener('click', () => toggleMenu(false));
    }
    if (overlay) {
        overlay.addEventListener('click', () => toggleMenu(false));
    }
});
