// ============================================================================
// OPO LIST - DVDcoin Exams
// ============================================================================

// Verificar autenticación
function checkAuth() {
    const token = localStorage.getItem('exams_token');
    const user = localStorage.getItem('exams_user');
    
    if (token && user) {
        const userData = JSON.parse(user);
        document.getElementById('userBtn').textContent = userData.username;
        
        // Mostrar sección de admin si es admin
        if (userData.role === 'admin') {
            document.getElementById('adminSection').style.display = 'block';
        }
        
        // Cargar estadísticas del usuario
        loadUserStats();
    } else {
        document.getElementById('userBtn').textContent = 'Iniciar Sesión';
    }
}

// Cargar estadísticas del usuario
async function loadUserStats() {
    try {
        const token = localStorage.getItem('exams_token');
        const response = await fetch('/api/opo/stats', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('userStats').style.display = 'block';
            document.getElementById('totalExams').textContent = stats.total_exams || 0;
            document.getElementById('avgScore').textContent = (stats.avg_score || 0) + '%';
            document.getElementById('totalTime').textContent = Math.round((stats.total_time || 0) / 3600) + 'h';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Filtrar oposiciones
function filterOposiciones() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const difficulty = document.getElementById('difficultyFilter').value;
    
    const cards = document.querySelectorAll('#opoList .card');
    
    cards.forEach(card => {
        const title = card.querySelector('.card-title').textContent.toLowerCase();
        const cardDifficulty = card.querySelector('.card-body')?.textContent.toLowerCase() || '';
        
        const matchesSearch = title.includes(searchTerm);
        const matchesDifficulty = !difficulty || cardDifficulty.includes(difficulty);
        
        if (matchesSearch && matchesDifficulty) {
            card.style.display = 'block';
        } else {
            card.style.display = 'none';
        }
    });
}

// Event listeners
document.getElementById('searchInput').addEventListener('input', filterOposiciones);
document.getElementById('difficultyFilter').addEventListener('change', filterOposiciones);

document.getElementById('userBtn').addEventListener('click', (e) => {
    e.preventDefault();
    const token = localStorage.getItem('exams_token');
    
    if (token) {
        // Mostrar menú de usuario
        if (confirm('¿Cerrar sesión?')) {
            localStorage.removeItem('exams_token');
            localStorage.removeItem('exams_user');
            window.location.reload();
        }
    } else {
        // Redirigir a login
        window.location.href = '/exams#login';
    }
});

// Inicializar
checkAuth();
