// DVDcoin Exams - Main JavaScript

// Verificar si el usuario está autenticado
async function checkAuth() {
    try {
        const response = await fetch('/api/auth/me', {
            credentials: 'include'
        });
        
        if (response.ok) {
            const data = await response.json();
            return data.user;
        }
        return null;
    } catch (error) {
        console.error('Error checking auth:', error);
        return null;
    }
}

// Actualizar UI según estado de autenticación
async function updateAuthUI() {
    const user = await checkAuth();
    const loginBtn = document.getElementById('loginBtn');
    const registerBtn = document.getElementById('registerBtn');
    const startBtn = document.getElementById('startBtn');
    
    if (user) {
        if (loginBtn) {
            loginBtn.textContent = user.username;
            loginBtn.href = '/profile';
        }
        if (registerBtn) {
            registerBtn.textContent = 'Mi Panel';
            registerBtn.href = '/dashboard';
        }
        if (startBtn) {
            startBtn.href = '/opo';
        }
    } else {
        if (loginBtn) {
            loginBtn.textContent = 'Iniciar Sesión';
            loginBtn.href = '/login';
        }
        if (registerBtn) {
            registerBtn.textContent = 'Crear Cuenta Gratis';
            registerBtn.href = '/register';
        }
        if (startBtn) {
            startBtn.href = '/register';
        }
    }
}

// Mostrar notificación
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '1000';
    notification.style.minWidth = '300px';
    notification.style.animation = 'slideIn 0.3s ease';
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    updateAuthUI();
});

// Animaciones CSS
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
