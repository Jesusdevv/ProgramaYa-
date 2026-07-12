document.addEventListener('DOMContentLoaded', () => {
    const menuBtn = document.getElementById('menu-btn');
    const dropdown = document.getElementById('menu-dropdown');

    menuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('hidden');
    });

    dropdown.addEventListener('click', (e) => e.stopPropagation());
    document.addEventListener('click', () => dropdown.classList.add('hidden'));

    document.getElementById('btn-inicio').addEventListener('click', () => {
        window.location.href = '/pagina-inicio-sesion-prof';
    });

    document.getElementById('btn-perfil').addEventListener('click', () => {
        window.location.href = '/perfil-profesor';
    });

    document.getElementById('btn-crear-curso').addEventListener('click', () => {
        window.location.href = '/crear-curso';
    });

    document.getElementById('btn-crear-capitulo').addEventListener('click', () => {
        window.location.href = '/crear-capitulo';
    });

    document.getElementById('btn-mis-cursos').addEventListener('click', () => {
        window.location.href = '/ver-cursos';
    });

    document.getElementById('btn-logout').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = '/';
    });

    // Foto de perfil
    const fileInput = document.getElementById('profile-pic-input');
    const img = document.getElementById('profile-pic');
    const placeholder = document.getElementById('profile-pic-placeholder');
    const btnRemove = document.getElementById('btn-remove-pic');

    const savedPic = localStorage.getItem('profile_picture');
    if (savedPic) {
        img.src = savedPic;
        img.classList.remove('hidden');
        placeholder.classList.add('hidden');
    }

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (ev) => {
            const dataUrl = ev.target.result;
            img.src = dataUrl;
            img.classList.remove('hidden');
            placeholder.classList.add('hidden');
            localStorage.setItem('profile_picture', dataUrl);
        };
        reader.readAsDataURL(file);
    });

    btnRemove.addEventListener('click', () => {
        localStorage.removeItem('profile_picture');
        img.classList.add('hidden');
        img.src = '#';
        placeholder.classList.remove('hidden');
    });
});
