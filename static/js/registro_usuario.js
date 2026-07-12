document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registro-form');
    const btn = document.getElementById('btn-submit');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const username = document.getElementById('username').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirm = document.getElementById('confirm-password').value;

        if (!username || !email || !password) {
            alert('Completa todos los campos obligatorios.');
            return;
        }
        if (password !== confirm) {
            alert('Las contraseñas no coinciden.');
            return;
        }
        if (password.length < 6) {
            alert('La contraseña debe tener al menos 6 caracteres.');
            return;
        }

        btn.disabled = true;
        btn.innerHTML = 'Registrando...';

        try {
            const res = await fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });
            const data = await res.json();

            if (res.ok) {
                alert('Registro exitoso. Redirigiendo al inicio de sesión...');
                window.location.href = '/inicio-sesion';
            } else {
                alert(data.error || 'Error al registrarse.');
            }
        } catch (error) {
            alert('Error de conexión con el servidor.');
        }

        btn.disabled = false;
        btn.innerHTML = 'Registrarse<span class="material-symbols-outlined text-[18px]" data-icon="arrow_forward">arrow_forward</span>';
    });
});
