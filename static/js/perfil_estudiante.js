document.addEventListener('DOMContentLoaded', () => {
    // Menú hamburguesa dropdown
    const menuBtn = document.getElementById('menu-btn');
    const dropdown = document.getElementById('menu-dropdown');

    if (menuBtn && dropdown) {
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            dropdown.classList.toggle('hidden');
        });
        dropdown.addEventListener('click', (e) => e.stopPropagation());
        document.addEventListener('click', () => dropdown.classList.add('hidden'));
    }

    document.getElementById('btn-inicio')?.addEventListener('click', () => {
        window.location.href = '/pagina-inicio-sesion-est';
    });

    document.getElementById('btn-perfil')?.addEventListener('click', () => {
        window.location.href = '/perfil-estudiante';
    });

    document.getElementById('btn-ver-cursos')?.addEventListener('click', () => {
        window.location.href = '/ver-cursos';
    });

    document.getElementById('btn-logout')?.addEventListener('click', () => {
        localStorage.clear();
        window.location.href = '/';
    });

    // Animación de barra de progreso (mantenida del original)
    const courseCard = document.querySelector('.glass-card .bg-primary')?.closest('.glass-card');
    const progressBar = courseCard ? courseCard.querySelector('.bg-primary') : null;

    if (courseCard && progressBar) {
        courseCard.addEventListener('mouseenter', () => {
            progressBar.style.width = '10%';
            progressBar.style.transition = 'width 1s cubic-bezier(0.4, 0, 0.2, 1)';
        });
        courseCard.addEventListener('mouseleave', () => {
            progressBar.style.width = '0%';
        });
    }

    // Cargar nombre de usuario desde localStorage
    const username = localStorage.getItem('username');
    const userInput = document.querySelector('input[placeholder="Nombre de usuario"]');
    if (username && userInput) {
        userInput.value = username;
    }

    // Cargar email desde localStorage (si se guardó) o mostrar placeholder
    const emailInput = document.querySelector('input[type="email"]');
    if (emailInput) {
        const storedEmail = localStorage.getItem('user_email');
        if (storedEmail) {
            emailInput.value = storedEmail;
        }
    }

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
