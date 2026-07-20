document.addEventListener('DOMContentLoaded', () => {
    // =============================================
    // MENU HAMBURGUESA (siempre funcional)
    // =============================================
    const menuBtn = document.getElementById('menu-btn');
    const dropdown = document.getElementById('menu-dropdown');

    if (menuBtn && dropdown) {
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('hidden');
        });
        dropdown.addEventListener('click', (e) => e.stopPropagation());
        document.addEventListener('click', () => {
            dropdown.classList.add('hidden');
        });

        document.getElementById('btn-inicio').addEventListener('click', () => {
            window.location.href = '/pagina-inicio-sesion-prof';
        });
        document.getElementById('btn-crear-curso').addEventListener('click', () => {
            window.location.href = '/crear-curso';
        });
        document.getElementById('btn-crear-capitulo').addEventListener('click', () => {
            window.location.href = '/crear-capitulo';
        });
        document.getElementById('btn-cursos').addEventListener('click', () => {
            window.location.href = '/ver-cursos';
        });
        document.getElementById('btn-perfil').addEventListener('click', () => {
            window.location.href = '/perfil-profesor';
        });
        document.getElementById('btn-logout').addEventListener('click', () => {
            sessionStorage.clear();
            window.location.href = '/';
        });
    }

    // =============================================
    // LOGICA DEL FORMULARIO
    // =============================================
    const form = document.getElementById('form-capitulo');
    const btn = document.getElementById('btn-submit');
    const alertContainer = document.getElementById('alert-container');
    const cursoSelect = document.getElementById('curso-select');

    const userRole = sessionStorage.getItem('user_role');
    const userId = sessionStorage.getItem('user_id');

    if (!userId || userRole !== 'Maestro') {
        alertContainer.textContent = 'Acceso denegado. Solo los Maestros pueden crear capítulos.';
        alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
        alertContainer.classList.remove('hidden');
        btn.disabled = true;
        return;
    }

    // Cargar cursos del maestro
    async function cargarCursos() {
        try {
            const res = await fetch(`/cursos?propios=1&id_user=${userId}&limit=100`);
            if (!res.ok) throw new Error('Error al cargar cursos');
            const data = await res.json();
            const cursos = data.cursos || [];

            if (cursos.length === 0) {
                cursoSelect.innerHTML = '<option value="">No tienes cursos creados</option>';
                btn.disabled = true;
                return;
            }

            cursoSelect.innerHTML = '<option value="">Selecciona un curso...</option>';
            cursos.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id_course;
                opt.textContent = `${c.title} (${c.language || ''})`;
                cursoSelect.appendChild(opt);
            });
        } catch (e) {
            alertContainer.textContent = 'Error al cargar cursos: ' + e.message;
            alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
            alertContainer.classList.remove('hidden');
        }
    }

    cargarCursos();

const btnAddEjercicio = document.getElementById('btn-add-ejercicio');
    const ejerciciosContainer = document.getElementById('ejercicios-container');
    let ejercicioCount = 0;

    btnAddEjercicio.addEventListener('click', () => {
        ejercicioCount++;
        const idx = ejercicioCount;
        const div = document.createElement('div');
        div.className = 'ejercicio-item p-sm border border-outline-variant rounded-xl bg-surface-container-low';
        div.dataset.index = idx;
        div.innerHTML = `
            <div class="flex items-center justify-between mb-xs">
                <span class="text-xs font-semibold text-secondary">Ejercicio ${idx}</span>
                <button type="button" class="btn-remove-ejercicio text-error hover:text-error/80 transition-colors">
                    <span class="material-symbols-outlined text-base">remove_circle</span>
                </button>
            </div>
            <div class="space-y-xs">
                <input class="ej-q w-full h-10 px-sm rounded-lg border border-outline focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none text-sm" placeholder="Pregunta / enunciado" type="text"/>
                <input class="ej-sol w-full h-10 px-sm rounded-lg border border-outline focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none text-sm" placeholder="Solución esperada" type="text"/>
            </div>
        `;
        div.querySelector('.btn-remove-ejercicio').addEventListener('click', () => div.remove());
        ejerciciosContainer.appendChild(div);
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const cursoId = cursoSelect.value;
        const chapter_title = document.getElementById('titulo').value.trim();
        const chapter_order = parseInt(document.getElementById('orden').value, 10);
        const chapter_content = document.getElementById('contenido').value.trim();

        if (!cursoId) {
            alertContainer.textContent = 'Selecciona un curso.';
            alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
            alertContainer.classList.remove('hidden');
            return;
        }
        if (!chapter_title || !chapter_order || !chapter_content) {
            alertContainer.textContent = 'Completa todos los campos obligatorios.';
            alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
            alertContainer.classList.remove('hidden');
            return;
        }

        const exercises = [];
        document.querySelectorAll('.ejercicio-item').forEach(item => {
            const q = item.querySelector('.ej-q').value.trim();
            const sol = item.querySelector('.ej-sol').value.trim();
            if (q && sol) {
                exercises.push({ question: q, expected_solution: sol });
            }
        });

        btn.disabled = true;
        btn.innerHTML = '<span class="material-symbols-outlined animate-spin">sync</span> Guardando...';

        try {
            const res = await fetch(`/cursos/${cursoId}/capitulo/nuevo`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_user: userId, chapter_title, chapter_content, chapter_order, exercises })
            });
            const data = await res.json();

            if (res.ok) {
                alertContainer.textContent = '¡Capítulo creado exitosamente!';
                alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-green-100 text-green-700 font-medium';
                alertContainer.classList.remove('hidden');
                form.reset();
                ejerciciosContainer.innerHTML = '';
                ejercicioCount = 0;
                cargarCursos();
            } else {
                alertContainer.textContent = data.error || 'Error al crear el capítulo.';
                alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
                alertContainer.classList.remove('hidden');
            }
        } catch (error) {
            alertContainer.textContent = 'Error de conexión con el servidor.';
            alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
            alertContainer.classList.remove('hidden');
        }

        btn.disabled = false;
        btn.innerHTML = '<span class="material-symbols-outlined">save</span> Guardar Capítulo';
    });
});
