# Fase #3: Diseño

---

## 1) Planificación del desarrollo

### Diagrama de Gantt (Plan de Acción)

| Fase | Actividad | Metodología | Duración Est. | Estado |
|---|---|---|---|---|
| Fase #1 | Planificación inicial (Idea, Objetivos) | N/A | 1 semana | Completado |
| Fase #2 | Análisis de Requerimientos | N/A | 1 semana | Completado |
| Fase #3 | Diseño del sistema (Diagramas, BD, Planificación) | RAD | 1 semana | En curso |
| Fase #4 | Implementación (Prototipo funcional) | RAD | 2 semanas | Pendiente |
| Fase #5 | Pruebas y cambios finales | N/A | 1 semana | Pendiente |

Duración total estimada: **6 semanas**.

---

## 2) Metodología de desarrollo

### Metodología seleccionada: RAD (Rapid Application Development)

**¿Por qué resulta la más adecuada?**

La metodología RAD resulta la más adecuada para la realización del proyecto ProgramaYa!, ya que prioriza el desarrollo rápido del sistema web, permitiendo que el equipo de desarrollo cree prototipos funcionales de cada módulo de forma iterativa. Dado que el equipo es pequeño (4 personas) y los requerimientos están bien definidos desde la Fase #2, RAD permite:

- Obtener un prototipo funcional en semanas, no en meses.
- Recibir retroalimentación temprana del usuario final.
- Ajustar funcionalidades sobre la marcha sin procesos burocráticos.
- Entregar valor incrementalmente en cada ciclo.

**Roles del equipo dentro de la metodología RAD:**

| Miembro | Rol en RAD | Responsabilidades |
|---|---|---|
| Jesús Reyes | Coordinador / Jefe de Proyecto + DBA | Gestiona el cronograma, prioriza requerimientos, comunica avances. Diseña y administra la base de datos. |
| Richardy Segovia | Desarrollador Backend | Implementa la lógica del servidor (Flask), APIs, autenticación y conexión con la base de datos. |
| Santiago Zambrano | Desarrollador Frontend | Maqueta las interfaces (HTML, CSS, Tailwind), consume las APIs y desarrolla la interactividad del lado del cliente. |
| Alejandro Cortes | Documentación y QA | Redacta la documentación del proyecto, realiza pruebas de funcionalidad y reporta errores. |

**Organización y ejecución del trabajo según RAD:**

El proyecto se divide en los siguientes ciclos RAD:

1. **Modelado de negocios** (Fase #1 y #2): Definición de objetivos, problemas, usuarios y requerimientos.
2. **Modelado de datos** (Fase #3 - actual): Diseño del esquema de base de datos y diccionario de datos.
3. **Modelado de procesos** (Fase #3 - actual): Diagramas de flujo, casos de uso y secuencia.
4. **Generación de la aplicación** (Fase #4): Desarrollo del prototipo funcional dividido en iteraciones:
   - Iteración 1: Registro, inicio de sesión, perfil
   - Iteración 2: CRUD de cursos y capítulos
   - Iteración 3: CRUD y validación de ejercicios
   - Iteración 4: Panel de administración, notificaciones, roles
5. **Pruebas y entrega** (Fase #5): Pruebas de integración, corrección de errores y entrega final.

Cada iteración incluye reunión de planificación → desarrollo → revisión → retroalimentación.

### Historias de Usuario

Basadas en los requerimientos funcionales de la Fase #2:

**HU-01: Registro e inicio de sesión**
> Como usuario visitante, quiero registrarme con mi correo y contraseña, e iniciar sesión para acceder a la plataforma según mi rol.

**HU-02: Página de inicio informativa**
> Como visitante, quiero ver una página principal que explique qué es ProgramaYa!, su finalidad, los roles disponibles y los cursos existentes.

**HU-03: Panel de administración**
> Como administrador, quiero un panel centralizado para validar cuentas, gestionar solicitudes de rol y supervisar el contenido de la plataforma.

**HU-04: Perfil de usuario**
> Como usuario registrado, quiero editar mis datos personales y, si lo deseo, solicitar el cambio de rol de Estudiante a Maestro.

**HU-05: CRUD de manuales**
> Como maestro validado, quiero crear, leer, actualizar y eliminar cursos y capítulos mediante formularios para publicar contenido educativo.

**HU-06: Validación de ejercicios**
> Como estudiante, quiero resolver ejercicios prácticos y recibir feedback inmediato (correcto/incorrecto) para verificar mi aprendizaje.

### Herramientas de apoyo

| Herramienta | Propósito |
|---|---|
| Figma | Diseño de interfaces y prototipado visual |
| Neon (PostgreSQL) | Base de datos relacional en la nube |
| Flask (Python) | Framework backend del sistema |
| HTML, CSS, Tailwind CSS | Maquetado y estilo del frontend |
| JavaScript (vanilla) | Interactividad del lado del cliente |
| Git + GitHub | Control de versiones y repositorio del código |
| WhatsApp | Comunicación del equipo |

---

## 3) Modelado del sistema

### 3.1 Diagrama de casos de uso

```
Actores:
  - Visitante (no autenticado)
  - Estudiante
  - Maestro
  - Administrador

Casos de uso (resumen textual):

1. Visitante
   - Registrarse en la plataforma
   - Ver página de inicio
   - Iniciar sesión

2. Estudiante
   - Ver su perfil
   - Editar su perfil
   - Solicitar cambio de rol a Maestro
   - Ver cursos disponibles
   - Buscar y filtrar cursos
   - Ver capítulos de un curso
   - Resolver ejercicios
   - Validar su respuesta (feedback inmediato)

3. Maestro
   - Crear curso
   - Editar curso
   - Eliminar curso
   - Crear capítulo (con ejercicios opcionales)
   - Editar capítulo
   - Eliminar capítulo
   - Crear ejercicio
   - Editar ejercicio
   - Eliminar ejercicio

4. Administrador
   - Validar cuentas de nuevos usuarios
   - Aceptar o rechazar solicitudes de rol Maestro
   - Ver notificaciones del sistema
   - Marcar notificaciones como leídas
```

### 3.2 Diagrama de secuencia (flujo principal)

**Flujo: Registro e inicio de sesión**

```
Visitante          Frontend              Backend              BD
    |                  |                    |                   |
    |--- Registro ---->|                    |                   |
    |                  |--- POST /registro ->|                   |
    |                  |                    |--- INSERT INTO --->|
    |                  |                    |<-- usuario creado -|
    |                  |<-- 201 + msg ------|                   |
    |<-- "Pendiente ---|                    |                   |
    |   de validación" |                    |                   |
    |                  |                    |                   |
    |--- Login ------->|                    |                   |
    |                  |--- POST /login --->|                   |
    |                  |                    |--- SELECT ------->|
    |                  |                    |<-- usuario + rol -|
    |                  |<-- 200 + token ----|                   |
    |<-- Dashboard ----|                    |                   |
    |   según rol      |                    |                   |
```

**Flujo: Validación de ejercicio**

```
Estudiante         Frontend              Backend              BD
    |                  |                    |                   |
    |--- Envía ------->|                    |                   |
    |   respuesta      |--- POST /ejercicios/<id>/validar ---->|
    |                  |                    |--- SELECT ------->|
    |                  |                    |   expected_solution|
    |                  |                    |<-- expected ------|
    |                  |                    |   case-insensitive|
    |                  |                    |   comparación     |
    |                  |<-- {correcto/incorrecto} -------------|
    |<-- Feedback -----|                    |                   |
    |   inmediato      |                    |                   |
```

### 3.3 Diagrama de flujo (procesos específicos)

**Proceso: Solicitud y aprobación de rol Maestro**

```
[Inicio]
    |
    v
[Estudiante solicita rol Maestro desde su perfil]
    |
    v
[Se crea notificación en BD (id_user, tipo='solicitud_maestro')]
    |
    v
[Admin recibe notificación (pestaña de notificaciones)]
    |
    v
[Admin revisa solicitud]
    |
    +--->[Aprueba] --> [UPDATE users SET role='Maestro'] --> [Notificación marcada como leída]
    |
    +--->[Rechaza] --> [Notificación marcada como leída (sin cambios)]
    |
    v
[Fin]
```

---

## 4) Modelado de base de datos

### 4.1 Diagrama Entidad-Relación (ERD) — Descripción textual

El modelo relacional consta de las siguientes entidades y sus relaciones:

**Entidades principales:**

1. **users** (id_user PK, username, email, password_hash, role, profile_picture, is_validated)
2. **courses** (id_curso PK, titulo, descripcion, languaje, nivel, id_user FK → users, created_at)
3. **chapters** (id_capitulo PK, titulo, id_curso FK → courses, chapter_order)
4. **exercises** (id_ejercicio PK, enunciado, expected_solution, id_capitulo FK → chapters)
5. **notifications** (id_notificacion PK, type, message, id_user FK → users nullable, is_read, created_at)

**Relaciones:**

- users 1 ── N courses (un usuario puede crear muchos cursos)
- courses 1 ── N chapters (un curso tiene muchos capítulos)
- chapters 1 ── N exercises (un capítulo puede tener muchos ejercicios)
- users 1 ── N notifications (un usuario puede tener muchas notificaciones)

### 4.2 Diccionario de datos

**Tabla: users**

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id_user | SERIAL | PK, NOT NULL | Identificador único del usuario |
| username | VARCHAR(100) | NOT NULL, UNIQUE | Nombre de usuario |
| email | VARCHAR(100) | NOT NULL, UNIQUE | Correo electrónico |
| password_hash | TEXT | NOT NULL | Contraseña hasheada (werkzeug) |
| role | VARCHAR(20) | DEFAULT 'Estudiante' | Rol del usuario |
| profile_picture | TEXT | NULL | URL de la foto de perfil |
| is_validated | BOOLEAN | DEFAULT FALSE | Indica si la cuenta fue validada por un admin |

**Tabla: courses**

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id_curso | SERIAL | PK, NOT NULL | Identificador único del curso |
| titulo | VARCHAR(200) | NOT NULL | Título del curso |
| descripcion | TEXT | NULL | Descripción del curso |
| languaje | VARCHAR(50) | NOT NULL | Lenguaje de programación (Python, JavaScript) |
| nivel | VARCHAR(20) | NOT NULL | Nivel de dificultad (Básico, Intermedio, Avanzado) |
| id_user | INTEGER | FK → users.id_user, NOT NULL | Creador del curso |
| created_at | TIMESTAMP | DEFAULT NOW() | Fecha de creación |

**Tabla: chapters**

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id_capitulo | SERIAL | PK, NOT NULL | Identificador único del capítulo |
| titulo | VARCHAR(200) | NOT NULL | Título del capítulo |
| id_curso | INTEGER | FK → courses.id_curso, NOT NULL | Curso al que pertenece |
| chapter_order | INTEGER | NOT NULL | Orden secuencial dentro del curso |

**Tabla: exercises**

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id_ejercicio | SERIAL | PK, NOT NULL | Identificador único del ejercicio |
| enunciado | TEXT | NOT NULL | Enunciado del ejercicio |
| expected_solution | TEXT | NOT NULL | Solución esperada (oculta en GET) |
| id_capitulo | INTEGER | FK → chapters.id_capitulo, NOT NULL | Capítulo al que pertenece |

**Tabla: notifications**

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id_notificacion | SERIAL | PK, NOT NULL | Identificador único de la notificación |
| type | VARCHAR(50) | NOT NULL | Tipo: 'solicitud_maestro', 'curso_nuevo', etc. |
| message | TEXT | NOT NULL | Contenido del mensaje |
| id_user | INTEGER | FK → users.id_user, NULL | Usuario destino (NULL = global para admins) |
| is_read | BOOLEAN | DEFAULT FALSE | Indica si fue leída |
| created_at | TIMESTAMP | DEFAULT NOW() | Fecha de creación |

---

## 5) Viabilidad de la propuesta

### 5.1 Factibilidad técnica

El equipo dispone de los conocimientos necesarios para desarrollar el proyecto:

- **Jesús Reyes** — Manejo de PostgreSQL, diseño de bases de datos relacionales y coordinación de proyectos.
- **Richardy Segovia** — Desarrollo backend con Flask (Python), creación de APIs REST y lógica de servidor.
- **Santiago Zambrano** — Maquetación con HTML, CSS, Tailwind CSS y JavaScript vanilla.
- **Alejandro Cortes** — Redacción técnica, documentación y pruebas de calidad.

Las herramientas utilizadas (Flask, PostgreSQL, Neon, Tailwind, Git) son de acceso gratuito y cuentan con amplia documentación en línea. El equipo ya ha implementado un prototipo funcional, lo que confirma la viabilidad técnica.

**Conclusión: Técnicamente factible.**

### 5.2 Factibilidad operativa

La estructura organizacional es horizontal: el equipo de 4 miembros se comunica directamente por WhatsApp y coordina mediante Git y reuniones semanales. No se requiere personal adicional ni una estructura jerárquica compleja.

- El proyecto se desarrolla en horario extracurricular compatible con las obligaciones académicas del equipo.
- Los procesos definidos (RAD con iteraciones cortas) se adaptan al tamaño y disponibilidad del equipo.

**Conclusión: Operativamente factible.**

### 5.3 Factibilidad económica

| Concepto | Costo |
|---|---|
| Hosting Neon (PostgreSQL) | Gratuito (plan serverless) |
| Dominio | \$0 (desarrollo local / GitHub Pages) |
| Herramientas (Figma, Git, WhatsApp) | Gratuitas |
| IDE (VS Code) | Gratuito |
| Framework (Flask) | Open source |
| **Total** | **\$0.00** |

Todos los recursos son de uso gratuito o cuentan con planes sin costo que cubren las necesidades del proyecto. No existe inversión económica directa. El retorno de inversión (ROI) se mide en términos académicos y de aprendizaje del equipo.

**Conclusión: Económicamente factible. Costo total: \$0.00.**

---

## 6) Tabla de recursos

### 6.1 Recursos tecnológicos

| Recurso | Especificación | Propósito |
|---|---|---|
| VS Code | Editor de código | Desarrollo del sistema |
| Neon (PostgreSQL) | Base de datos serverless | Almacenamiento persistente |
| Git + GitHub | Control de versiones | Repositorio y colaboración |
| Figma | Diseño de interfaces | Prototipado visual |
| Flask 3.x | Framework Python | Backend del sistema |
| Tailwind CSS | Framework CSS | Estilos responsivos |
| Windows 10/11 | Sistema operativo | Entorno de desarrollo |

### 6.2 Recursos humanos

| Miembro | Rol | Responsabilidades |
|---|---|---|
| Jesús Reyes | Coordinador y DBA | Gestión del proyecto, diseño de BD |
| Richardy Segovia | Backend Developer | APIs, autenticación, lógica del servidor |
| Santiago Zambrano | Frontend Developer | Interfaces, consumo de API, UX |
| Alejandro Cortes | Documentación y QA | Documentación, pruebas, control de calidad |

### 6.3 Recursos financieros

| Tipo | Detalle | Costo |
|---|---|---|
| Software | Todo open source / gratuito | \$0.00 |
| Hosting | Neon (PostgreSQL serverless) | \$0.00 |
| Comunicación | WhatsApp, GitHub | \$0.00 |
| **Total** | | **\$0.00** |
