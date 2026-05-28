// ============================================================================
// EXAM TYPES - DVDcoin Exams
// ============================================================================

// Obtener parámetros de URL
const urlParams = new URLSearchParams(window.location.search);
const category = urlParams.get('category') || 'imagen-diagnostico';

// Verificar autenticación
function checkAuth() {
    const token = localStorage.getItem('exams_token');
    const user = localStorage.getItem('exams_user');
    
    if (!token || !user) {
        alert('Debes iniciar sesión para acceder a los exámenes');
        window.location.href = '/exams#login';
        return false;
    }
    
    const userData = JSON.parse(user);
    
    // Verificar si el usuario está verificado
    if (!userData.verified) {
        alert('Debes verificar tu email antes de acceder a los exámenes');
        window.location.href = '/exams';
        return false;
    }
    
    // Cargar estadísticas
    loadStats();
    
    return true;
}

// Cargar estadísticas del usuario para esta categoría
async function loadStats() {
    try {
        const token = localStorage.getItem('exams_token');
        const response = await fetch(`/api/opo/stats/${category}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            const stats = await response.json();
            document.getElementById('personalStats').style.display = 'block';
            document.getElementById('statExams').textContent = stats.total_exams || 0;
            document.getElementById('statAvg').textContent = (stats.avg_score || 0) + '%';
            document.getElementById('statBest').textContent = (stats.best_score || 0) + '%';
            document.getElementById('statTime').textContent = Math.round((stats.total_time || 0) / 3600) + 'h';
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

// Iniciar examen
function startExam(type) {
    const token = localStorage.getItem('exams_token');
    
    if (!token) {
        alert('Debes iniciar sesión para realizar exámenes');
        window.location.href = '/exams#login';
        return;
    }
    
    // Guardar configuración del examen
    const examConfig = {
        category: category,
        type: type,
        timestamp: Date.now()
    };
    
    localStorage.setItem('exam_config', JSON.stringify(examConfig));
    
    // Redirigir a la página del examen
    window.location.href = `/opo/exam?category=${category}&type=${type}`;
}

// Mostrar selector de temas
function showThemeSelector() {
    alert('Selector de temas en desarrollo. Por ahora, usa el examen completo o rápido.');
    // TODO: Implementar selector de temas
}

// Inicializar
if (checkAuth()) {
    // Actualizar título según categoría
    const categoryNames = {
        'imagen-diagnostico': 'Técnico Superior en Imagen para el Diagnóstico',
        'enfermeria': 'Enfermería',
        'auxiliar-enfermeria': 'Auxiliar de Enfermería',
        'celador': 'Celador'
    };
    
    const categoryName = categoryNames[category] || 'Oposición';
    document.getElementById('pageTitle').textContent = categoryName;
    document.getElementById('categoryName').textContent = categoryName.split(' ').slice(0, 2).join(' ');
}
