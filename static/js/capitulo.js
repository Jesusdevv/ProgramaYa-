document.addEventListener('DOMContentLoaded', () => {
    // Menu hamburguesa
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
            window.location.href = '/pagina-inicio-sesion-est';
        });
        document.getElementById('btn-perfil').addEventListener('click', () => {
            window.location.href = '/perfil-estudiante';
        });
        document.getElementById('btn-cursos').addEventListener('click', () => {
            window.location.href = '/ver-cursos';
        });
        document.getElementById('btn-logout').addEventListener('click', () => {
            localStorage.clear();
            window.location.href = '/';
        });
    }

    // Obtener curso_id de la URL
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

    let capitulos = [];
    let currentIndex = 0;

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

        loading.classList.add('hidden');
        chapterView.classList.remove('hidden');
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

    cargarCapitulos();
});
