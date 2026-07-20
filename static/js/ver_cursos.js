document.addEventListener('DOMContentLoaded', () => {
    const menuBtn = document.getElementById('menu-btn');
    const menuDropdown = document.getElementById('menu-dropdown');
    if (menuBtn && menuDropdown) {
        menuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            menuDropdown.classList.toggle('hidden');
        });
        document.addEventListener('click', function(e) {
            if (!menuDropdown.contains(e.target) && !menuBtn.contains(e.target)) {
                menuDropdown.classList.add('hidden');
            }
        });
    }

    document.getElementById('btn-inicio')?.addEventListener('click', () => {
        const role = sessionStorage.getItem('user_role');
        window.location.href = role === 'Maestro' ? '/pagina-inicio-sesion-prof' : '/pagina-inicio-sesion-est';
    });
    document.getElementById('btn-perfil')?.addEventListener('click', () => {
        const role = sessionStorage.getItem('user_role');
        window.location.href = role === 'Maestro' ? '/perfil-profesor' : '/perfil-estudiante';
    });
    document.getElementById('btn-cursos')?.addEventListener('click', () => window.location.href = '/ver-cursos');
    document.getElementById('btn-crear-curso')?.addEventListener('click', () => window.location.href = '/crear-curso');
    document.getElementById('btn-crear-capitulo')?.addEventListener('click', () => window.location.href = '/crear-capitulo');
    document.getElementById('btn-logout')?.addEventListener('click', () => {
        sessionStorage.clear();
        window.location.href = '/pagina-inicio-sinsesion';
    });

    const grid = document.getElementById('cursos-grid');
    const empty = document.getElementById('cursos-empty');
    const loadingEl = document.getElementById('loading-cursos');
    const cargarMasContainer = document.getElementById('cargar-mas-container');
    const btnCargarMas = document.getElementById('btn-cargar-mas');
    const inputBusqueda = document.getElementById('input-busqueda');
    const selectLenguaje = document.getElementById('select-lenguaje');
    const chkPropios = document.getElementById('chk-propios');
    const labelPropios = document.getElementById('label-propios');

    const role = sessionStorage.getItem('user_role');
    const userId = sessionStorage.getItem('user_id');
    const LIMIT = 12;

    let currentPage = 1;
    let totalPages = 0;
    let isLoading = false;

    if (role === 'Maestro') {
        labelPropios.classList.remove('hidden');
        document.querySelectorAll('.teacher-only').forEach(el => el.classList.remove('hidden'));
    }

    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('propios') === '1') {
        chkPropios.checked = true;
    }

    let timeoutId = null;

    function getParams(page) {
        const params = new URLSearchParams();
        const lenguaje = selectLenguaje.value;
        const q = inputBusqueda.value.trim();
        if (lenguaje) params.set('lenguaje', lenguaje);
        if (q) params.set('q', q);
        if (chkPropios.checked && userId) {
            params.set('propios', '1');
            params.set('id_user', userId);
        }
        params.set('page', page);
        params.set('limit', LIMIT);
        return params;
    }

    function mostrarOcultarCargarMas() {
        if (currentPage < totalPages) {
            cargarMasContainer.classList.remove('hidden');
        } else {
            cargarMasContainer.classList.add('hidden');
        }
    }

    async function cargarCursos(reset = true) {
        if (isLoading) return;

        if (reset) {
            currentPage = 1;
            grid.innerHTML = '';
        }

        const params = getParams(currentPage);
        isLoading = true;
        loadingEl.classList.remove('hidden');
        btnCargarMas.disabled = true;

        try {
            const url = `/cursos?${params.toString()}`;
            const res = await fetch(url);
            if (!res.ok) throw new Error('Error al cargar cursos');
            const data = await res.json();
            const cursos = data.cursos || [];
            totalPages = data.pages || 0;
            loadingEl.classList.add('hidden');

            if (reset) {
                grid.innerHTML = '';
                empty.classList.add('hidden');
            }

            if (cursos.length === 0 && currentPage === 1) {
                empty.classList.remove('hidden');
                cargarMasContainer.classList.add('hidden');
                return;
            }

            cursos.forEach(c => {
                const card = document.createElement('div');
                const isOwner = chkPropios.checked;
                card.className = 'bg-surface-container-lowest border border-on-surface p-md course-card-hover flex flex-col gap-sm' + (isOwner ? '' : ' cursor-pointer');
                if (!isOwner) card.onclick = () => window.location.href = `/capitulo?curso_id=${c.id_course}`;

                const imgSrc = c.course_image || 'https://via.placeholder.com/400x225/e2e2e2/630ed4?text=Curso';
                const nivel = c.level || 'General';
                const desc = c.description || 'Sin descripción disponible.';

                const adminBtns = isOwner ? `
                    <div class="flex gap-2 mt-1">
                        <a href="/crear-curso?curso_id=${c.id_course}" class="flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg bg-surface-variant text-on-surface text-xs font-semibold hover:bg-outline-variant transition-colors">
                            <span class="material-symbols-outlined text-sm">edit</span> Editar
                        </a>
                        <button data-id="${c.id_course}" class="btn-delete-curso flex-1 flex items-center justify-center gap-1 py-1.5 rounded-lg bg-error-container text-on-error-container text-xs font-semibold hover:bg-error hover:text-on-error transition-colors">
                            <span class="material-symbols-outlined text-sm">delete</span> Eliminar
                        </button>
                    </div>
                ` : '';

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
                    ${adminBtns}
                `;
                grid.appendChild(card);
            });

            grid.querySelectorAll('.btn-delete-curso').forEach(btn => {
                btn.addEventListener('click', async (e) => {
                    e.stopPropagation();
                    if (!confirm('¿Eliminar este curso? Esta acción no se puede deshacer.')) return;
                    const cursoId = btn.dataset.id;
                    btn.disabled = true;
                    btn.innerHTML = '<span class="material-symbols-outlined text-sm animate-spin">progress_activity</span>';
                    try {
                        const res = await fetch(`/cursos/${cursoId}?id_user=${userId}`, { method: 'DELETE' });
                        if (res.ok) {
                            cargarCursos(true);
                        } else {
                            const data = await res.json();
                            alert(data.error || 'Error al eliminar');
                        }
                    } catch {
                        alert('Error de conexión');
                    }
                    btn.disabled = false;
                    btn.innerHTML = '<span class="material-symbols-outlined text-sm">delete</span> Eliminar';
                });
            });

            mostrarOcultarCargarMas();
        } catch (e) {
            loadingEl.classList.add('hidden');
            if (reset) {
                grid.innerHTML = '<div class="col-span-full text-center py-10 text-on-surface-variant">Error al cargar cursos.</div>';
            }
        }

        isLoading = false;
        btnCargarMas.disabled = false;
    }

    function resetYBuscar() {
        currentPage = 1;
        cargarCursos(true);
    }

    inputBusqueda.addEventListener('input', () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(resetYBuscar, 300);
    });

    selectLenguaje.addEventListener('change', resetYBuscar);
    chkPropios.addEventListener('change', resetYBuscar);

    btnCargarMas.addEventListener('click', () => {
        currentPage++;
        cargarCursos(false);
    });

    cargarCursos(true);
});
