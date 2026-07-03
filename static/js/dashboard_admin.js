function mostrarAlerta(mensaje, tipo) {
    const container = document.getElementById('alert-container');
    container.textContent = mensaje;
    container.className = 'p-4 rounded-xl font-medium text-sm transition-all duration-200';
    if (tipo === 'success') {
        container.classList.add('bg-green-100', 'text-green-800');
    } else {
        container.classList.add('bg-red-100', 'text-red-800');
    }
    container.classList.remove('hidden');
    setTimeout(() => container.classList.add('hidden'), 5000);
}

async function cargarSolicitudes() {
    const tbody = document.getElementById('table-body');
    tbody.innerHTML = '<tr><td colspan="4" class="px-6 py-8 text-center text-on-surface-variant">Cargando peticiones...</td></tr>';
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
            tr.className = 'border-b border-gray-100 hover:bg-purple-50/30 transition-colors';
            tr.innerHTML = `
                <td class="px-6 py-4 font-medium text-purple-950">#${s.id_solicitud}</td>
                <td class="px-6 py-4">${s.id_user}</td>
                <td class="px-6 py-4"><span class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-yellow-100 text-yellow-800">${s.estado}</span></td>
                <td class="px-6 py-4 text-right space-x-2">
                    <button onclick="procesarSolicitud(${s.id_solicitud}, 'APROBAR')" class="px-3 py-1.5 text-xs font-bold rounded-lg bg-green-600 text-white hover:bg-green-700 transition-colors">Aprobar</button>
                    <button onclick="procesarSolicitud(${s.id_solicitud}, 'RECHAZAR')" class="px-3 py-1.5 text-xs font-bold rounded-lg bg-red-500 text-white hover:bg-red-600 transition-colors">Rechazar</button>
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
                id_solicitud: idSolicitud,
                id_admin: 1,
                accion: accion
            })
        });
        const data = await res.json();
        if (res.ok) {
            mostrarAlerta(data.mensaje, 'success');
            cargarSolicitudes();
        } else {
            mostrarAlerta(data.error || 'Error al procesar', 'error');
        }
    } catch (e) {
        mostrarAlerta('Error de conexión: ' + e.message, 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    cargarSolicitudes();
    const adminName = document.getElementById('admin-name');
    const stored = localStorage.getItem('user');
    if (stored) {
        try {
            const user = JSON.parse(stored);
            adminName.textContent = user.username || 'Administrador';
        } catch (_) {}
    }
    document.getElementById('btn-logout').addEventListener('click', () => {
        localStorage.removeItem('user');
        window.location.href = '/inicio-sesion';
    });
});
