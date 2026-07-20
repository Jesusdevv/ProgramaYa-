document.addEventListener('DOMContentLoaded', () => {
    const menuBtn = document.getElementById('menu-btn');
    const dropdown = document.getElementById('menu-dropdown');

    if (menuBtn && dropdown) {
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('hidden');
        });
        dropdown.addEventListener('click', (e) => e.stopPropagation());
        document.addEventListener('click', () => dropdown.classList.add('hidden'));

        document.getElementById('btn-inicio').addEventListener('click', () => {
            window.location.href = role === 'Maestro' ? '/pagina-inicio-sesion-prof' : '/pagina-inicio-sesion-est';
        });
        document.getElementById('btn-perfil').addEventListener('click', () => {
            window.location.href = role === 'Maestro' ? '/perfil-profesor' : '/perfil-estudiante';
        });
        document.getElementById('btn-cursos').addEventListener('click', () => {
            window.location.href = '/ver-cursos';
        });
        document.getElementById('btn-logout').addEventListener('click', () => {
            sessionStorage.clear();
            window.location.href = '/';
        });
    }

    const params = new URLSearchParams(window.location.search);
    const cursoId = params.get('curso_id');

    if (!cursoId) {
        document.getElementById('loading').textContent = 'No se especificó un curso.';
        return;
    }

    const loading = document.getElementById('loading');
    const chapterView = document.getElementById('chapter-view');
    const moduloLabel = document.getElementById('modulo-label');
    const chapterTitle = document.getElementById('chapter-title');
    const chapterCounter = document.getElementById('chapter-counter');
    const chapterContent = document.getElementById('chapter-content');
    const chapterIndicator = document.getElementById('chapter-indicator');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const linkVolver = document.getElementById('link-volver');
    const chapterActions = document.getElementById('chapter-actions');
    const btnEdit = document.getElementById('btn-edit-chapter');
    const btnDelete = document.getElementById('btn-delete-chapter');
    const exercisesSection = document.getElementById('exercises-section');
    const exercisesList = document.getElementById('exercises-list');

    const modalEditar = document.getElementById('modal-editar');
    const editTitle = document.getElementById('edit-title');
    const editContent = document.getElementById('edit-content');
    const btnGuardarModal = document.getElementById('btn-guardar-modal');
    const btnCancelarModal = document.getElementById('btn-cancelar-modal');
    const btnCerrarModal = document.getElementById('btn-cerrar-modal');

    let capitulos = [];
    let currentIndex = 0;
    const userId = parseInt(sessionStorage.getItem('user_id'));
    const role = sessionStorage.getItem('user_role');
    let editing = false;

    function esPropietario(capitulo) {
        return role === 'Maestro' && capitulo.id_user === userId;
    }

    function mostrarCapitulo(index) {
        if (!capitulos.length || index < 0 || index >= capitulos.length) return;

        currentIndex = index;
        const cap = capitulos[index];

        moduloLabel.textContent = 'Módulo';
        chapterTitle.textContent = cap.chapter_title || 'Sin título';
        chapterCounter.textContent = `Capítulo ${cap.chapter_order}`;
        chapterContent.textContent = cap.chapter_content || 'Contenido no disponible.';
        chapterIndicator.textContent = `${index + 1} / ${capitulos.length}`;

        btnPrev.disabled = index === 0;
        btnNext.disabled = index === capitulos.length - 1;

        chapterActions.classList.toggle('hidden', !esPropietario(cap));

        loading.classList.add('hidden');
        chapterView.classList.remove('hidden');

        cargarEjercicios(cap.id_chapter);
    }

    let ejerciciosGlobales = [];

    async function cargarEjercicios(chapterId) {
        try {
            const res = await fetch(`/capitulos/${chapterId}/ejercicios`);
            const data = await res.json();
            ejerciciosGlobales = data.ejercicios || [];
            exercisesList.innerHTML = '';
            if (ejerciciosGlobales.length === 0) {
                exercisesSection.classList.add('hidden');
                return;
            }
            exercisesSection.classList.remove('hidden');
            ejerciciosGlobales.forEach((ex, i) => {
                const div = document.createElement('div');
                div.className = 'p-4 rounded-xl border border-outline-variant bg-surface-container-low space-y-2';
                div.innerHTML = `
                    <p class="font-semibold text-sm text-on-surface">${i + 1}. ${ex.question}</p>
                    <div class="flex gap-2">
                        <input id="ej-input-${ex.id_exercise}" type="text" placeholder="Tu respuesta..." class="flex-1 h-10 px-3 rounded-lg border border-outline focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none text-sm"/>
                        <button id="ej-btn-${ex.id_exercise}" class="px-4 h-10 bg-primary text-on-primary rounded-lg text-sm font-semibold hover:bg-primary-fixed-variant active:scale-[0.97] transition-all">Validar</button>
                    </div>
                    <p id="ej-msg-${ex.id_exercise}" class="text-sm font-medium hidden"></p>
                `;
                exercisesList.appendChild(div);

                const input = div.querySelector(`#ej-input-${ex.id_exercise}`);
                const btn = div.querySelector(`#ej-btn-${ex.id_exercise}`);
                const msg = div.querySelector(`#ej-msg-${ex.id_exercise}`);

                async function validar() {
                    const user_solution = input.value.trim();
                    if (!user_solution) return;
                    btn.disabled = true;
                    btn.textContent = '...';
                    try {
                        const r = await fetch(`/ejercicios/${ex.id_exercise}/validar`, {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ user_solution })
                        });
                        const d = await r.json();
                        msg.classList.remove('hidden', 'text-green-600', 'text-red-600');
                        msg.classList.add(d.correct ? 'text-green-600' : 'text-red-600');
                        msg.textContent = d.message;
                    } catch {
                        msg.classList.remove('hidden', 'text-green-600', 'text-red-600');
                        msg.classList.add('text-red-600');
                        msg.textContent = 'Error de conexión';
                    }
                    btn.disabled = false;
                    btn.textContent = 'Validar';
                }

                btn.addEventListener('click', validar);
                input.addEventListener('keydown', (e) => { if (e.key === 'Enter') validar(); });
            });
        } catch {
            exercisesSection.classList.add('hidden');
        }
    }

    async function cargarCapitulos() {
        try {
            const res = await fetch(`/cursos/${cursoId}/capitulos`);
            if (!res.ok) throw new Error('Error al cargar capítulos');
            const data = await res.json();
            capitulos = data.capitulos || [];

            if (capitulos.length === 0) {
                loading.textContent = 'Este curso no tiene capítulos aún.';
                return;
            }

            mostrarCapitulo(0);
        } catch (e) {
            loading.textContent = 'Error al cargar el capítulo: ' + e.message;
        }
    }

    btnPrev.addEventListener('click', () => {
        if (currentIndex > 0) mostrarCapitulo(currentIndex - 1);
    });

    btnNext.addEventListener('click', () => {
        if (currentIndex < capitulos.length - 1) mostrarCapitulo(currentIndex + 1);
    });

    btnEdit.addEventListener('click', () => {
        const cap = capitulos[currentIndex];
        editTitle.value = cap.chapter_title || '';
        editContent.value = cap.chapter_content || '';
        modalEditar.classList.remove('hidden');
        editing = true;
    });

    function cerrarModal() {
        modalEditar.classList.add('hidden');
        editing = false;
    }

    btnCerrarModal.addEventListener('click', cerrarModal);
    btnCancelarModal.addEventListener('click', cerrarModal);
    modalEditar.addEventListener('click', (e) => {
        if (e.target === modalEditar) cerrarModal();
    });

    btnGuardarModal.addEventListener('click', async () => {
        const cap = capitulos[currentIndex];
        const newTitle = editTitle.value.trim();
        const newContent = editContent.value.trim();
        if (!newTitle && !newContent) return;

        btnGuardarModal.disabled = true;
        btnGuardarModal.innerHTML = '<span class="material-symbols-outlined text-lg animate-spin">progress_activity</span> Guardando...';

        try {
            const res = await fetch(`/cursos/${cursoId}/capitulo/${cap.id_chapter}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    id_user: userId,
                    chapter_title: newTitle || undefined,
                    chapter_content: newContent !== (cap.chapter_content || '') ? newContent : undefined
                })
            });
            const data = await res.json();
            if (res.ok) {
                cap.chapter_title = data.capitulo.chapter_title;
                cap.chapter_content = data.capitulo.chapter_content;
                chapterTitle.textContent = cap.chapter_title;
                chapterContent.textContent = cap.chapter_content || 'Contenido no disponible.';
                cerrarModal();
            } else {
                alert(data.error || 'Error al guardar');
            }
        } catch {
            alert('Error de conexión al guardar');
        }
        btnGuardarModal.disabled = false;
        btnGuardarModal.innerHTML = '<span class="material-symbols-outlined text-lg">save</span> Guardar';
    });

    btnDelete.addEventListener('click', async () => {
        if (!confirm('¿Eliminar este capítulo? Esta acción no se puede deshacer.')) return;

        const cap = capitulos[currentIndex];
        btnDelete.disabled = true;
        btnDelete.innerHTML = '<span class="material-symbols-outlined text-base animate-spin">progress_activity</span>';

        try {
            const res = await fetch(`/cursos/${cursoId}/capitulo/${cap.id_chapter}?id_user=${userId}`, {
                method: 'DELETE'
            });
            if (res.ok) {
                capitulos.splice(currentIndex, 1);
                if (capitulos.length === 0) {
                    chapterView.classList.add('hidden');
                    loading.textContent = 'Curso sin capítulos.';
                    loading.classList.remove('hidden');
                } else {
                    mostrarCapitulo(Math.min(currentIndex, capitulos.length - 1));
                }
            } else {
                const data = await res.json();
                alert(data.error || 'Error al eliminar');
            }
        } catch {
            alert('Error de conexión al eliminar');
        }
        btnDelete.disabled = false;
        btnDelete.innerHTML = '<span class="material-symbols-outlined text-base">delete</span> Eliminar';
    });

    cargarCapitulos();
});