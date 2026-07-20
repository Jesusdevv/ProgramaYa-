function mostrarAlerta(mensaje, tipo) {
    const container = document.getElementById('alert-container');
    container.textContent = mensaje;
    container.className = 'p-4 rounded-xl font-medium text-sm transition-all duration-200';
    if (tipo === 'success') {
        container.classList.add('bg-tertiary-container', 'text-on-tertiary-container');
    } else {
        container.classList.add('bg-error-container', 'text-on-error-container');
    }
    container.classList.remove('hidden');
    setTimeout(() => container.classList.add('hidden'), 5000);
}

async function cargarSolicitudes() {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '<tr id="row-loading"><td colspan="4" class="px-6 py-8 text-center"><div class="flex items-center justify-center gap-3"><span class="material-symbols-outlined text-2xl text-primary animate-spin">progress_activity</span><span class="text-on-surface-variant">Cargando peticiones...</span></div></td></tr>';
    try {
        const res = await fetch('/solicitudes-pendientes');
        if (!res.ok) throw new Error('Error al obtener solicitudes');
        const data = await res.json();
        document.getElementById('count-pending').textContent = data.length;
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-on-surface-variant">No hay solicitudes pendientes.</td></tr>';
            return;
        }
        tbody.innerHTML = '';
        data.forEach(s => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-outline-variant hover:bg-surface-variant active:bg-surface-container-high transition-colors duration-150';
            tr.innerHTML = `
                <td class="px-6 py-4 font-medium text-on-surface">#${s.id_request}</td>
                <td class="px-6 py-4 text-on-surface">${s.id_user}</td>
                <td class="px-6 py-4"><span class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">${s.status}</span></td>
                <td class="px-6 py-4 text-right space-x-2">
                    <button onclick="procesarSolicitud(${s.id_request}, 'APROBAR')" class="px-3 py-1.5 text-xs font-bold rounded-lg bg-primary text-white hover:bg-primary-fixed-variant active:scale-[0.95] transition-all duration-150">Aprobar</button>
                    <button onclick="procesarSolicitud(${s.id_request}, 'RECHAZAR')" class="px-3 py-1.5 text-xs font-bold rounded-lg bg-error text-white hover:bg-error-fixed-variant active:scale-[0.95] transition-all duration-150">Rechazar</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-red-600">Error al cargar solicitudes.</td></tr>';
        mostrarAlerta('Error al cargar solicitudes: ' + e.message, 'error');
    }
}

async function procesarSolicitud(idSolicitud, accion) {
    try {
        const res = await fetch('/procesar-maestro', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id_request: idSolicitud,
                id_admin: parseInt(sessionStorage.getItem('user_id')),
                accion: accion
            })
        });
        const data = await res.json();
        if (res.ok) {
            mostrarAlerta(data.mensaje, 'success');
            cargarSolicitudes();
            cargarNotificaciones();
        } else {
            mostrarAlerta(data.error || 'Error al procesar', 'error');
        }
    } catch (e) {
        mostrarAlerta('Error de conexión: ' + e.message, 'error');
    }
}

async function cargarAprobadas() {
    try {
        const res = await fetch('/solicitudes-aprobadas');
        if (!res.ok) throw new Error('Error al obtener aprobadas');
        const data = await res.json();
        document.getElementById('count-approved').textContent = data.length;
    } catch (e) {
        document.getElementById('count-approved').textContent = '0';
    }
}

async function cargarPendientesValidacion() {
    const tbody = document.getElementById('validation-table-body');
    tbody.innerHTML = '<tr id="validation-row-loading"><td colspan="5" class="px-6 py-8 text-center"><div class="flex items-center justify-center gap-3"><span class="material-symbols-outlined text-2xl text-primary animate-spin">progress_activity</span><span class="text-on-surface-variant">Cargando usuarios pendientes...</span></div></td></tr>';
    try {
        const res = await fetch('/usuarios-pendientes');
        if (!res.ok) throw new Error('Error al obtener usuarios pendientes');
        const data = await res.json();
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-on-surface-variant">No hay usuarios pendientes de validación.</td></tr>';
            return;
        }
        tbody.innerHTML = '';
        data.forEach(u => {
            const tr = document.createElement('tr');
            tr.className = 'border-b border-outline-variant hover:bg-surface-variant active:bg-surface-container-high transition-colors duration-150';
            tr.innerHTML = `
                <td class="px-6 py-4 font-medium text-on-surface">${u.id_user}</td>
                <td class="px-6 py-4 text-on-surface">${u.username}</td>
                <td class="px-6 py-4 text-on-surface-variant">${u.email}</td>
                <td class="px-6 py-4"><span class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">${u.role}</span></td>
                <td class="px-6 py-4 text-right">
                    <button onclick="validarUsuario(${u.id_user})" class="px-3 py-1.5 text-xs font-bold rounded-lg bg-primary text-white hover:bg-primary-fixed-variant active:scale-[0.95] transition-all duration-150">Activar cuenta</button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5" class="px-6 py-8 text-center text-red-600">Error al cargar usuarios pendientes.</td></tr>';
        mostrarAlerta('Error al cargar usuarios pendientes: ' + e.message, 'error');
    }
}

async function validarUsuario(idUser) {
    try {
        const res = await fetch('/validar-usuario', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id_user: idUser,
                id_admin: sessionStorage.getItem('user_id')
            })
        });
        const data = await res.json();
        if (res.ok) {
            mostrarAlerta(data.mensaje, 'success');
            cargarPendientesValidacion();
        } else {
            mostrarAlerta(data.error || 'Error al activar cuenta', 'error');
        }
    } catch (e) {
        mostrarAlerta('Error de conexión: ' + e.message, 'error');
    }
}

// --- Notificaciones ---
const notifDropdown = document.getElementById('notif-dropdown');
const notifList = document.getElementById('notif-list');
const notifBadge = document.getElementById('notif-badge');
const btnNotif = document.getElementById('btn-notificaciones');

async function cargarNotificaciones() {
    try {
        const res = await fetch('/notificaciones');
        if (!res.ok) return;
        const data = await res.json();
        const count = data.length;

        if (count > 0) {
            notifBadge.textContent = count > 99 ? '99+' : count;
            notifBadge.classList.remove('hidden');
        } else {
            notifBadge.classList.add('hidden');
        }

        if (!notifDropdown.classList.contains('hidden')) {
            renderNotificaciones(data);
        }
    } catch (e) {
        console.error('Error al cargar notificaciones:', e);
    }
}

function renderNotificaciones(notifs) {
    if (notifs.length === 0) {
        notifList.innerHTML = '<div class="p-4 text-center text-sm text-on-surface-variant">No hay notificaciones.</div>';
        return;
    }
    notifList.innerHTML = '';
    notifs.forEach(n => {
        const div = document.createElement('div');
        div.className = 'p-3 hover:bg-surface-variant transition-colors duration-150';
        div.innerHTML = `
            <div class="flex items-start gap-3">
                <span class="material-symbols-outlined text-primary mt-0.5">${n.type === 'role_request' ? 'person_add' : 'notifications'}</span>
                <div class="flex-1 min-w-0">
                    <p class="text-sm text-on-surface">${n.message}</p>
                    <p class="text-xs text-on-surface-variant mt-1">${new Date(n.created_at).toLocaleString()}</p>
                </div>
                <button onclick="marcarLeida(${n.id_notification})" class="text-on-surface-variant hover:text-primary transition-colors" title="Marcar como leída">
                    <span class="material-symbols-outlined text-lg">check_circle</span>
                </button>
            </div>
        `;
        notifList.appendChild(div);
    });
}

async function marcarLeida(idNotif) {
    try {
        const res = await fetch(`/notificaciones/${idNotif}/leer`, { method: 'PUT' });
        if (res.ok) {
            cargarNotificaciones();
        }
    } catch (e) {
        console.error('Error al marcar leída:', e);
    }
}

btnNotif.addEventListener('click', (e) => {
    e.stopPropagation();
    const isHidden = notifDropdown.classList.toggle('hidden');
    if (!isHidden) {
        fetch('/notificaciones')
            .then(r => r.json())
            .then(data => renderNotificaciones(data))
            .catch(() => {});
    }
});

document.addEventListener('click', (e) => {
    if (!notifDropdown.contains(e.target) && !btnNotif.contains(e.target)) {
        notifDropdown.classList.add('hidden');
    }
});

// --- Fin Notificaciones ---

document.addEventListener('DOMContentLoaded', () => {
    // Verificar que el usuario logueado sea Administrador
    if (sessionStorage.getItem('user_role') !== 'Administrador') {
        window.location.href = '/inicio-sesion';
        return;
    }
    cargarSolicitudes();
    cargarAprobadas();
    cargarPendientesValidacion();
    cargarNotificaciones();

    // Polling cada 30 segundos
    setInterval(cargarNotificaciones, 30000);

    const adminName = document.getElementById('admin-name');
    const storedUsername = sessionStorage.getItem('username');
    adminName.textContent = storedUsername || 'Administrador';
    document.getElementById('btn-logout').addEventListener('click', () => {
        sessionStorage.removeItem('user_role');
        sessionStorage.removeItem('user_id');
        sessionStorage.removeItem('username');
        window.location.href = '/inicio-sesion';
    });
});
