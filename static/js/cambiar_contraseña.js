document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('password-form');
    const btn = document.getElementById('btn-submit');
    const alertContainer = document.getElementById('alert-container');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const current_password = document.getElementById('current_password').value;
        const new_password = document.getElementById('new_password').value;
        const confirm_password = document.getElementById('confirm_password').value;

        if (!current_password || !new_password || !confirm_password) {
            alertContainer.textContent = 'Completa todos los campos.';
            alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
            alertContainer.classList.remove('hidden');
            return;
        }

        if (new_password !== confirm_password) {
            alertContainer.textContent = 'Las contraseñas nuevas no coinciden.';
            alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
            alertContainer.classList.remove('hidden');
            return;
        }

        if (new_password.length < 6) {
            alertContainer.textContent = 'La nueva contraseña debe tener al menos 6 caracteres.';
            alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
            alertContainer.classList.remove('hidden');
            return;
        }

        const id_user = sessionStorage.getItem('user_id');
        if (!id_user) {
            alertContainer.textContent = 'No has iniciado sesión. Redirigiendo...';
            alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
            alertContainer.classList.remove('hidden');
            setTimeout(() => window.location.href = '/inicio-sesion', 2000);
            return;
        }

        btn.disabled = true;
        btn.innerHTML = 'Cambiando...';

        try {
            const res = await fetch('/cambiar-contrasena', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id_user, current_password, new_password })
            });
            const data = await res.json();

            if (res.ok) {
                alertContainer.textContent = 'Contraseña cambiada exitosamente.';
                alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-green-100 text-green-700 font-medium';
                alertContainer.classList.remove('hidden');
                form.reset();
            } else {
                alertContainer.textContent = data.error || 'Error al cambiar la contraseña.';
                alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
                alertContainer.classList.remove('hidden');
            }
        } catch (error) {
            alertContainer.textContent = 'Error de conexión con el servidor.';
            alertContainer.className = 'mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium';
            alertContainer.classList.remove('hidden');
        }

        btn.disabled = false;
        btn.innerHTML = 'Cambiar Contraseña';
    });
});
