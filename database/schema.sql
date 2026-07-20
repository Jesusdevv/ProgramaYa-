-- Esquema completo de la base de datos ProgramaYa!
-- Ejecutar en la consola SQL de Neon para inicializar la DB.

CREATE TABLE IF NOT EXISTS users (
    id_user SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'Estudiante',
    is_validated BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id_course SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES users(id_user) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    date_created DATE DEFAULT CURRENT_DATE,
    course_image TEXT,
    language VARCHAR(50),
    module_name VARCHAR(255),
    level VARCHAR(50),
    description TEXT
);

CREATE TABLE IF NOT EXISTS chapters (
    id_chapter SERIAL PRIMARY KEY,
    id_course INTEGER NOT NULL REFERENCES courses(id_course) ON DELETE CASCADE,
    id_user INTEGER NOT NULL REFERENCES users(id_user),
    chapter_title VARCHAR(255) NOT NULL,
    chapter_content TEXT,
    chapter_order INTEGER NOT NULL,
    solution TEXT
);

CREATE TABLE IF NOT EXISTS exercises (
    id_exercise SERIAL PRIMARY KEY,
    id_chapter INTEGER NOT NULL REFERENCES chapters(id_chapter) ON DELETE CASCADE,
    question TEXT NOT NULL,
    expected_solution TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS role_requests (
    id_request SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES users(id_user),
    status VARCHAR(50) NOT NULL DEFAULT 'Pendiente'
);

CREATE TABLE IF NOT EXISTS notifications (
    id_notification SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    related_id INTEGER,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
