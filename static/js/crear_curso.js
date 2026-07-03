document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('curso-form');
    const alertContainer = document.getElementById('alert-container');
    const btnSubmit = document.getElementById('btn-submit');
    const btnAddCapitulo = document.getElementById('btn-add-capitulo');
    const capitulosContainer = document.getElementById('capitulos-container');

    let capituloCount = 1;

    btnAddCapitulo.addEventListener('click', () => {
        capituloCount++;
        const div = document.createElement('div');
        div.className = 'capitulo-item bg-gray-50 p-3 rounded-xl border border-gray-200 flex items-center gap-3';
        div.innerHTML = `
            <span class="text-xs font-bold text-purple-950 bg-purple-200/60 w-6 h-6 flex items-center justify-center rounded-full index-label">${capituloCount}</span>
            <input class="w-full h-10 rounded-lg border-none bg-white shadow-sm px-3 text-sm text-gray-900 cap-input" placeholder="Nombre del capítulo" type="text" required/>
            <button type="button" class="remove-capitulo text-red-400 hover:text-red-600 transition-colors">
                <span class="material-symbols-outlined text-[18px]">close</span>
            </button>`;
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

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        alertContainer.classList.add('hidden');
        btnSubmit.disabled = true;
        btnSubmit.innerHTML = '<span class="material-symbols-outlined">hourglass_top</span> Publicando...';

        const titulo = document.getElementById('titulo').value.trim();
        const lenguaje = document.getElementById('lenguaje').value;
        const nivel = document.getElementById('nivel').value;
        const descripcion = document.getElementById('descripcion').value.trim();
        const capitulos = Array.from(document.querySelectorAll('.cap-input')).map(i => i.value.trim()).filter(Boolean);

        try {
            const response = await fetch('/cursos/manuales/nuevo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ titulo, lenguaje, nivel, descripcion, capitulos })
            });
            const data = await response.json();
            if (response.ok) {
                alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-green-100 text-green-800';
                alertContainer.textContent = 'Curso creado exitosamente.';
                alertContainer.classList.remove('hidden');
                form.reset();
                capitulosContainer.innerHTML = `
                    <div class="capitulo-item bg-gray-50 p-3 rounded-xl border border-gray-200 flex items-center gap-3">
                        <span class="text-xs font-bold text-purple-950 bg-purple-200/60 w-6 h-6 flex items-center justify-center rounded-full index-label">1</span>
                        <input class="w-full h-10 rounded-lg border-none bg-white shadow-sm px-3 text-sm text-gray-900 cap-input" placeholder="Nombre del capítulo inicial" type="text" required/>
                    </div>`;
                capituloCount = 1;
            } else {
                alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-red-100 text-red-700';
                alertContainer.textContent = data.error || 'Error al crear el curso.';
                alertContainer.classList.remove('hidden');
            }
        } catch (error) {
            alertContainer.className = 'mb-6 p-4 rounded-xl text-sm font-medium bg-red-100 text-red-700';
            alertContainer.textContent = 'Error de conexión con el servidor.';
            alertContainer.classList.remove('hidden');
        }

        btnSubmit.disabled = false;
        btnSubmit.innerHTML = '<span class="material-symbols-outlined">save</span> Publicar Curso Completo';
    });
});
