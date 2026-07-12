function toggleSidebar() {
    const sidebar = document.getElementById('side-navbar');
    const overlay = document.getElementById('sidebar-overlay');
    const isHidden = sidebar.classList.contains('-translate-x-full');

    if (isHidden) {
        sidebar.classList.remove('-translate-x-full');
        overlay.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
    } else {
        sidebar.classList.add('-translate-x-full');
        overlay.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const role = localStorage.getItem('user_role');
    const label = document.getElementById('user-role-label');
    if (role === 'maestro') {
        label.textContent = '👨‍🏫 Maestro';
    } else {
        label.textContent = '👨‍🎓 Estudiante';
    }

    // Cargar cursos desde la API
    const grid = document.getElementById('cursos-grid');
    const empty = document.getElementById('cursos-empty');

    async function cargarCursos() {
        try {
            const res = await fetch('/cursos');
            if (!res.ok) throw new Error('Error al cargar cursos');
            const data = await res.json();
            const cursos = data.cursos || [];

            if (cursos.length === 0) {
                grid.innerHTML = '';
                empty.classList.remove('hidden');
                return;
            }

            empty.classList.add('hidden');
            grid.innerHTML = '';

            cursos.forEach(c => {
                const card = document.createElement('div');
                card.className = 'bg-surface-container-lowest border border-on-surface p-md course-card-hover flex flex-col gap-sm cursor-pointer';
                card.onclick = () => window.location.href = `/capitulo?curso_id=${c.id_course}`;

                const imgSrc = c.course_image || 'https://via.placeholder.com/400x225/e2e2e2/630ed4?text=Curso';
                const nivel = c.level || 'General';
                const desc = c.description || 'Sin descripción disponible.';

                card.innerHTML = `
                    <div class="aspect-video bg-surface-container-high overflow-hidden border-b border-on-surface -mx-md -mt-md mb-xs">
                        <img class="w-full h-full object-cover" src="${imgSrc}" alt="${c.title}" onerror="this.src='https://via.placeholder.com/400x225/e2e2e2/630ed4?text=Curso'"/>
                    </div>
                    <h4 class="font-headline-md text-headline-md text-primary">${c.title}</h4>
                    <p class="font-body-md text-body-md text-on-surface-variant">${desc}</p>
                    <div class="mt-auto flex justify-between items-center">
                        <span class="font-label-md text-label-md text-secondary">${c.language || ''}</span>
                        <span class="bg-primary-container text-on-primary-container px-xs py-[2px] rounded font-label-md text-label-md">${nivel}</span>
                    </div>
                `;
                grid.appendChild(card);
            });
        } catch (e) {
            grid.innerHTML = '<div class="col-span-full text-center py-10 text-on-surface-variant">Error al cargar cursos.</div>';
        }
    }

    cargarCursos();
});
