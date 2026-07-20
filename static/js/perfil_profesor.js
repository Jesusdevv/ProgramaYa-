document.addEventListener('DOMContentLoaded', () => {
    const userId = sessionStorage.getItem('user_id');
    if (!userId) {
        window.location.href = '/inicio-sesion';
        return;
    }

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
        window.location.href = '/ver-cursos?propios=1';
    });

    document.getElementById('btn-logout').addEventListener('click', () => {
        sessionStorage.clear();
        window.location.href = '/';
    });

    const inputUsername = document.getElementById('input-username');
    const inputEmail = document.getElementById('input-email');
    const displayRole = document.getElementById('display-role');
    const btnSave = document.getElementById('btn-save');
    const btnCancel = document.getElementById('btn-cancel');
    const profileActions = document.getElementById('profile-actions');
    const alertProfile = document.getElementById('alert-profile');
    const loadingPerfil = document.getElementById('loading-perfil');
    const perfilContent = document.getElementById('perfil-content');

    let datosOriginales = {};

    async function cargarPerfil() {
        try {
            const res = await fetch(`/perfil?user_id=${userId}`);
            const data = await res.json();
            if (res.ok) {
                const user = data.user;
                inputUsername.value = user.username || '';
                inputEmail.value = user.email || '';
                displayRole.textContent = user.role || 'Maestro';
                datosOriginales = { username: user.username, email: user.email };
                sessionStorage.setItem('username', user.username);
                sessionStorage.setItem('user_email', user.email || '');
            } else {
                mostrarAlerta(data.error || 'Error al cargar perfil', 'error');
            }
        } catch {
            mostrarAlerta('Error de conexión al cargar perfil', 'error');
        }
        loadingPerfil.classList.add('hidden');
        perfilContent.classList.remove('hidden');
    }

    function hayCambios() {
        return inputUsername.value !== datosOriginales.username ||
               inputEmail.value !== datosOriginales.email;
    }

    function mostrarAlerta(mensaje, tipo) {
        alertProfile.textContent = mensaje;
        alertProfile.className = 'mt-4 p-3 text-sm rounded-xl font-medium';
        if (tipo === 'success') {
            alertProfile.classList.add('bg-tertiary-container', 'text-on-tertiary-container');
        } else {
            alertProfile.classList.add('bg-error-container', 'text-on-error-container');
        }
        alertProfile.classList.remove('hidden');
        setTimeout(() => alertProfile.classList.add('hidden'), 4000);
    }

    inputUsername.addEventListener('input', () => {
        profileActions.classList.toggle('hidden', !hayCambios());
    });

    inputEmail.addEventListener('input', () => {
        profileActions.classList.toggle('hidden', !hayCambios());
    });

    btnCancel.addEventListener('click', () => {
        inputUsername.value = datosOriginales.username || '';
        inputEmail.value = datosOriginales.email || '';
        profileActions.classList.add('hidden');
    });

    btnSave.addEventListener('click', async () => {
        const body = { user_id: parseInt(userId) };
        if (inputUsername.value !== datosOriginales.username) {
            body.username = inputUsername.value;
        }
        if (inputEmail.value !== datosOriginales.email) {
            body.email = inputEmail.value;
        }
        if (Object.keys(body).length === 1) {
            profileActions.classList.add('hidden');
            return;
        }
        btnSave.disabled = true;
        btnSave.innerHTML = '<span class="material-symbols-outlined text-lg animate-spin">progress_activity</span> Guardando...';
        try {
            const res = await fetch('/perfil', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            const data = await res.json();
            if (res.ok) {
                const user = data.user;
                datosOriginales = { username: user.username, email: user.email };
                inputUsername.value = user.username || '';
                inputEmail.value = user.email || '';
                profileActions.classList.add('hidden');
                sessionStorage.setItem('username', user.username);
                sessionStorage.setItem('user_email', user.email || '');
                mostrarAlerta('Perfil actualizado exitosamente', 'success');
            } else {
                mostrarAlerta(data.error || 'Error al guardar', 'error');
            }
        } catch {
            mostrarAlerta('Error de conexión al guardar', 'error');
        }
        btnSave.disabled = false;
        btnSave.innerHTML = '<span class="material-symbols-outlined text-lg">save</span> Guardar';
    });

    cargarPerfil();

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
