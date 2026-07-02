document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("login-form");
    const userInput = document.getElementById("user");
    const passInput = document.getElementById("pass");
    const togglePasswordBtn = document.getElementById("toggle-password");
    const alertContainer = document.getElementById("alert-container");
    const btnSubmit = document.getElementById("btn-submit");

    // 1. Micro-interacciones estéticas para los iconos (Cambio a color Primary al hacer Foco)
    const setupFocusEvent = (inputElement, iconId) => {
        const icon = document.getElementById(iconId);
        if (!inputElement || !icon) return;

        inputElement.addEventListener("focus", () => {
            icon.classList.add("text-primary");
            icon.style.fontVariationSettings = "'FILL' 1";
        });
        inputElement.addEventListener("blur", () => {
            icon.classList.remove("text-primary");
            icon.style.fontVariationSettings = "'FILL' 0";
        });
    };

    setupFocusEvent(userInput, "icon-user");
    setupFocusEvent(passInput, "icon-pass");

    // 2. Interacción para Mostrar/Ocultar el texto de la contraseña
    if (togglePasswordBtn && passInput) {
        togglePasswordBtn.addEventListener("click", () => {
            const isPassword = passInput.getAttribute("type") === "password";
            passInput.setAttribute("type", isPassword ? "text" : "password");
            
            const iconSpan = togglePasswordBtn.querySelector(".material-symbols-outlined");
            if (iconSpan) {
                iconSpan.textContent = isPassword ? "visibility_off" : "visibility";
            }
        });
    }

    // 3. Conexión por Red (Fetch API) con tu endpoint de Flask /login
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault(); // Evita que la página se recargue por defecto

            // Limpiamos alertas previas y deshabilitamos el botón para evitar doble envío
            alertContainer.classList.add("hidden");
            btnSubmit.disabled = true;
            btnSubmit.textContent = "Verificando...";

            // Capturamos los datos ingresados por el usuario
            const email = userInput.value.trim();
            const password = passInput.value;

            try {
                // Petición POST asíncrona hacia Flask
                const response = await fetch("/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json();

                if (response.ok) {
                    // ¡Login Exitoso! Guardamos los datos clave en el localStorage del navegador
                    console.log("Acceso concedido exitosamente:", data);
                    
                    localStorage.setItem("user_role", data.user.role);
                    localStorage.setItem("user_id", data.user.id_user);
                    localStorage.setItem("username", data.user.username);

                    // Redirección dinámica según las reglas de negocio de los Roles
                    if (data.user.role === "Administrador") {
                        window.location.href = "/admin/dashboard";
                    } else if (data.user.role === "Maestro") {
                        window.location.href = "/perfil_profesor"; // O a su respectivo home de profesor
                    } else {
                        window.location.href = "/index_estudiante"; // Home del estudiante base
                    }
                } else {
                    // El backend rechazó las credenciales (Error 400 o 401)
                    alertContainer.textContent = data.error || "Credenciales incorrectas o usuario no registrado.";
                    alertContainer.className = "mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium";
                    alertContainer.classList.remove("hidden");
                    
                    btnSubmit.disabled = false;
                    btnSubmit.textContent = "Iniciar sesión";
                }

            } catch (error) {
                // Captura si el servidor Flask está apagado o hay caída de red
                console.error("Error en la petición Fetch de login:", error);
                alertContainer.textContent = "Error de red: No se pudo establecer conexión con el servidor.";
                alertContainer.className = "mb-4 p-4 text-sm rounded-xl bg-red-100 text-red-700 font-medium";
                alertContainer.classList.remove("hidden");
                
                btnSubmit.disabled = false;
                btnSubmit.textContent = "Iniciar sesión";
            }
        });
    }
});