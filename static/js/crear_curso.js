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

    const form = document.getElementById('curso-form');
    const alertContainer = document.getElementById('alert-container');
    const btnSubmit = document.getElementById('btn-submit');
    const btnAddCapitulo = document.getElementById('btn-add-capitulo');
    const capitulosContainer = document.getElementById('capitulos-container');
    const capitulosSection = document.getElementById('capitulos-section');
    const deleteContainer = document.getElementById('delete-container');

    const params = new URLSearchParams(window.location.search);
    const editCursoId = params.get('curso_id');
    const isEditing = !!editCursoId;

    let capituloCount = 1;

    if (isEditing) {
        document.getElementById('page-title').textContent = 'Editar Curso';
        document.getElementById('page-subtitle').textContent = 'Modifica la información general del curso.';
        btnSubmit.innerHTML = '<span class="material-symbols-outlined">save</span> Guardar Cambios';
        capitulosSection.classList.add('hidden');
        deleteContainer.classList.remove('hidden');
        cargarCurso(editCursoId);
    }

    async function cargarCurso(cursoId) {
        try {
            const userId = sessionStorage.getItem('user_id');
            const res = await fetch(`/cursos?propios=1&id_user=${userId}&limit=100`);
            const data = await res.json();
            const cursos = data.cursos || [];
            const curso = cursos.find(c => String(c.id_course) === String(cursoId));
            if (!curso) {
                alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-red-100 text-red-700';
                alertContainer.textContent = 'Curso no encontrado.';
                alertContainer.classList.remove('hidden');
                return;
            }
            document.getElementById('titulo').value = curso.title || '';
            document.getElementById('lenguaje').value = curso.language || 'python';
            document.getElementById('nivel').value = curso.level || 'Básico';
            document.getElementById('descripcion').value = curso.description || '';
            if (curso.course_image) {
                document.getElementById('imagen_url').value = curso.course_image;
                document.getElementById('preview-img').src = curso.course_image;
                document.getElementById('preview-img').classList.remove('hidden');
            }
        } catch {
            alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-red-100 text-red-700';
            alertContainer.textContent = 'Error al cargar el curso.';
            alertContainer.classList.remove('hidden');
        }
    }

    btnAddCapitulo.addEventListener('click', () => {
        capituloCount++;
        const div = document.createElement('div');
        div.className = 'capitulo-item bg-gray-50 p-3 rounded-xl border border-gray-200';
        div.innerHTML = `
            <div class="flex items-center gap-3">
                <span class="text-xs font-bold text-purple-950 bg-purple-200/60 w-6 h-6 flex items-center justify-center rounded-full index-label">${capituloCount}</span>
                <input class="flex-1 h-10 rounded-lg border-none bg-white shadow-sm px-3 text-sm text-gray-900 cap-input" placeholder="Nombre del capítulo" type="text" required/>
                <button type="button" class="remove-capitulo text-red-400 hover:text-red-600 transition-colors">
                    <span class="material-symbols-outlined text-[18px]">close</span>
                </button>
            </div>
            <div class="mt-2 ml-9">
                <input class="w-full h-9 rounded-lg border border-purple-200 bg-white/70 shadow-sm px-3 text-sm text-gray-900 mod-input" placeholder="Módulo (ej: Fundamentos Básicos)" type="text"/>
            </div>`;
        div.querySelector('.remove-capitulo').addEventListener('click', () => {
            div.remove();
            actualizarIndices();
        });
        capitulosContainer.appendChild(div);
    });

    function actualizarIndices() {
        document.querySelectorAll('.capitulo-item').forEach((item, i) => {
            item.querySelector('.index-label').textContent = i + 1;
        });
        capituloCount = document.querySelectorAll('.capitulo-item').length;
    }

    const imgInput = document.getElementById('imagen_url');
    const previewImg = document.getElementById('preview-img');
    const btnPreview = document.getElementById('btn-preview-img');

    function actualizarPreview() {
        const url = imgInput.value.trim();
        if (url) {
            previewImg.src = url;
            previewImg.classList.remove('hidden');
        } else {
            previewImg.classList.add('hidden');
        }
    }

    imgInput.addEventListener('input', actualizarPreview);
    btnPreview.addEventListener('click', actualizarPreview);

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        alertContainer.classList.add('hidden');
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="material-symbols-outlined">hourglass_top</span> Guardando...';

        const usuario_id = sessionStorage.getItem('user_id');
        const titulo = document.getElementById('titulo').value.trim();
        const lenguaje = document.getElementById('lenguaje').value;
        const nivel = document.getElementById('nivel').value;
        const descripcion = document.getElementById('descripcion').value.trim();
        const imagen_url = document.getElementById('imagen_url').value.trim();

        if (!usuario_id) {
            alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-red-100 text-red-700';
            alertContainer.textContent = 'Debes iniciar sesión como Maestro.';
            alertContainer.classList.remove('hidden');
            btnSubmit.disabled = false;
            btnSubmit.innerHTML = '<span class="material-symbols-outlined">save</span> Guardar Cambios';
            return;
        }

        try {
            let url, method, body;

            if (isEditing) {
                url = `/cursos/${editCursoId}`;
                method = 'PUT';
                body = JSON.stringify({ id_user: usuario_id, titulo, lenguaje, nivel, descripcion, imagen_url: imagen_url || null });
            } else {
                const capitulos = Array.from(document.querySelectorAll('.cap-input')).map(i => i.value.trim()).filter(Boolean);
                const modulos = Array.from(document.querySelectorAll('.mod-input')).map(i => i.value.trim());
                if (!capitulos.length) {
                    alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-red-100 text-red-700';
                    alertContainer.textContent = 'Agrega al menos un capítulo.';
                    alertContainer.classList.remove('hidden');
                    btnSubmit.disabled = false;
                    btnSubmit.innerHTML = '<span class="material-symbols-outlined">save</span> Publicar Curso Completo';
                    return;
                }
                url = '/manuales/nuevo';
                method = 'POST';
                body = JSON.stringify({ usuario_id, titulo, lenguaje, nivel, descripcion, imagen_url, capitulos, modulos });
            }

            const response = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body });
            const data = await response.json();

            if (response.ok) {
                alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-green-100 text-green-800';
                alertContainer.textContent = isEditing ? 'Curso actualizado exitosamente.' : 'Curso creado exitosamente.';
                alertContainer.classList.remove('hidden');
                if (!isEditing) {
                    form.reset();
                    capitulosContainer.innerHTML = `
                        <div class="capitulo-item bg-gray-50 p-3 rounded-xl border border-gray-200">
                            <div class="flex items-center gap-3">
                                <span class="text-xs font-bold text-purple-950 bg-purple-200/60 w-6 h-6 flex items-center justify-center rounded-full index-label">1</span>
                                <input class="flex-1 h-10 rounded-lg border-none bg-white shadow-sm px-3 text-sm text-gray-900 cap-input" placeholder="Nombre del capítulo inicial" type="text" required/>
                            </div>
                            <div class="mt-2 ml-9">
                                <input class="w-full h-9 rounded-lg border border-purple-200 bg-white/70 shadow-sm px-3 text-sm text-gray-900 mod-input" placeholder="Módulo (ej: Fundamentos Básicos)" type="text"/>
                            </div>
                        </div>`;
                    capituloCount = 1;
                }
            } else {
                alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-red-100 text-red-700';
                alertContainer.textContent = data.error || 'Error al guardar.';
                alertContainer.classList.remove('hidden');
            }
        } catch {
            alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-red-100 text-red-700';
            alertContainer.textContent = 'Error de conexión con el servidor.';
            alertContainer.classList.remove('hidden');
        }

        btnSubmit.disabled = false;
        btnSubmit.innerHTML = isEditing
            ? '<span class="material-symbols-outlined">save</span> Guardar Cambios'
            : '<span class="material-symbols-outlined">save</span> Publicar Curso Completo';
    });

    // Botón eliminar
    const btnDelete = document.getElementById('btn-delete-curso');
    if (btnDelete) {
        btnDelete.addEventListener('click', async () => {
            if (!confirm('¿Eliminar este curso? Se borrarán todos los capítulos y ejercicios. Esta acción no se puede deshacer.')) return;
            const usuario_id = sessionStorage.getItem('user_id');
            btnDelete.disabled = true;
            btnDelete.innerHTML = '<span class="material-symbols-outlined animate-spin">progress_activity</span> Eliminando...';
            try {
                const res = await fetch(`/cursos/${editCursoId}?id_user=${usuario_id}`, { method: 'DELETE' });
                if (res.ok) {
                    alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-green-100 text-green-800';
                    alertContainer.textContent = 'Curso eliminado. Redirigiendo...';
                    alertContainer.classList.remove('hidden');
                    setTimeout(() => { window.location.href = '/ver-cursos?propios=1'; }, 1500);
                } else {
                    const data = await res.json();
                    alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-red-100 text-red-700';
                    alertContainer.textContent = data.error || 'Error al eliminar.';
                    alertContainer.classList.remove('hidden');
                }
            } catch {
                alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-red-100 text-red-700';
                alertContainer.textContent = 'Error de conexión.';
                alertContainer.classList.remove('hidden');
            }
            btnDelete.disabled = false;
            btnDelete.innerHTML = '<span class="material-symbols-outlined">delete_forever</span> Eliminar Curso';
        });
    }
});