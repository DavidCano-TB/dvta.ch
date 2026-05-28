// ============================================================================
// EXAM - DVDcoin Exams
// ============================================================================

// Variables globales
let questions = [];
let currentQuestion = 0;
let answers = {};
let startTime = Date.now();
let timerInterval = null;
let examDuration = 3600; // 60 minutos por defecto
let timeRemaining = examDuration;

// Obtener parámetros de URL
const urlParams = new URLSearchParams(window.location.search);
const category = urlParams.get('category') || 'imagen-diagnostico';
const examType = urlParams.get('type') || 'completo';

// Configuración según tipo de examen
const examConfigs = {
    'completo': { questions: 50, duration: 3600 },
    'rapido': { questions: 20, duration: 1200 },
    'entrenamiento': { questions: 30, duration: 0 },
    'temas': { questions: 30, duration: 1800 }
};

// Inicializar examen
async function initExam() {
    // Verificar autenticación
    const token = localStorage.getItem('exams_token');
    if (!token) {
        alert('Debes iniciar sesión');
        window.location.href = '/exams';
        return;
    }
    
    // Configurar examen
    const config = examConfigs[examType] || examConfigs['completo'];
    examDuration = config.duration;
    timeRemaining = examDuration;
    
    // Actualizar título
    const examTitles = {
        'completo': 'Examen Completo',
        'rapido': 'Examen Rápido',
        'entrenamiento': 'Modo Entrenamiento',
        'temas': 'Examen por Temas'
    };
    document.getElementById('examTitle').textContent = examTitles[examType] || 'Examen';
    
    // Cargar preguntas
    await loadQuestions(config.questions);
    
    // Iniciar timer si no es modo entrenamiento
    if (examType !== 'entrenamiento') {
        startTimer();
    } else {
        document.getElementById('timer').style.display = 'none';
    }
    
    // Mostrar primera pregunta
    showQuestion(0);
    
    // Crear mapa de preguntas
    createQuestionMap();
}

// Cargar preguntas
async function loadQuestions(numQuestions) {
    try {
        const token = localStorage.getItem('exams_token');
        const response = await fetch(`/api/opo/questions/${category}?count=${numQuestions}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            questions = await response.json();
        } else {
            // Fallback: usar preguntas de ejemplo
            questions = generateSampleQuestions(numQuestions);
        }
    } catch (error) {
        console.error('Error loading questions:', error);
        questions = generateSampleQuestions(numQuestions);
    }
}

// Generar preguntas de ejemplo (fallback)
function generateSampleQuestions(count) {
    const sampleQuestions = [];
    for (let i = 0; i < count; i++) {
        sampleQuestions.push({
            id: i + 1,
            question: `Pregunta de ejemplo ${i + 1} sobre imagen diagnóstica. ¿Cuál es la respuesta correcta?`,
            options: {
                a: 'Opción A - Primera respuesta posible',
                b: 'Opción B - Segunda respuesta posible',
                c: 'Opción C - Tercera respuesta posible',
                d: 'Opción D - Cuarta respuesta posible'
            },
            correct: ['a', 'b', 'c', 'd'][Math.floor(Math.random() * 4)],
            explanation: 'Esta es una explicación de ejemplo de por qué esta respuesta es correcta.'
        });
    }
    return sampleQuestions;
}

// Mostrar pregunta
function showQuestion(index) {
    if (index < 0 || index >= questions.length) return;
    
    currentQuestion = index;
    const question = questions[index];
    
    const container = document.getElementById('questionContainer');
    container.innerHTML = `
        <div class="question-card">
            <div class="question-number">Pregunta ${index + 1} de ${questions.length}</div>
            <div class="question-text">${question.question}</div>
            <div class="options">
                ${Object.entries(question.options).map(([key, value]) => `
                    <div class="option ${answers[index] === key ? 'selected' : ''}" 
                         onclick="selectAnswer(${index}, '${key}')">
                        <div class="option-letter">${key.toUpperCase()})</div>
                        <div>${value}</div>
                    </div>
                `).join('')}
            </div>
            ${examType === 'entrenamiento' && answers[index] ? `
                <div class="explanation show">
                    <strong>Explicación:</strong> ${question.explanation || 'No disponible'}
                </div>
            ` : ''}
        </div>
    `;
    
    // Actualizar botones
    document.getElementById('prevBtn').disabled = index === 0;
    document.getElementById('nextBtn').style.display = index === questions.length - 1 ? 'none' : 'block';
    document.getElementById('finishBtn').style.display = index === questions.length - 1 ? 'block' : 'none';
    
    // Actualizar progreso
    updateProgress();
}

// Seleccionar respuesta
function selectAnswer(questionIndex, answer) {
    answers[questionIndex] = answer;
    showQuestion(questionIndex);
    updateQuestionMap();
    
    // En modo entrenamiento, mostrar explicación inmediatamente
    if (examType === 'entrenamiento') {
        const question = questions[questionIndex];
        const options = document.querySelectorAll('.option');
        options.forEach(opt => {
            const letter = opt.querySelector('.option-letter').textContent.toLowerCase().replace(')', '');
            if (letter === question.correct) {
                opt.classList.add('correct');
            } else if (letter === answer) {
                opt.classList.add('incorrect');
            }
        });
    }
}

// Navegación
function nextQuestion() {
    if (currentQuestion < questions.length - 1) {
        showQuestion(currentQuestion + 1);
    }
}

function previousQuestion() {
    if (currentQuestion > 0) {
        showQuestion(currentQuestion - 1);
    }
}

// Crear mapa de preguntas
function createQuestionMap() {
    const map = document.getElementById('questionMap');
    map.innerHTML = questions.map((q, i) => `
        <button class="btn btn-sm ${answers[i] ? 'btn-primary' : 'btn-secondary'}" 
                onclick="showQuestion(${i})"
                style="width: 40px; height: 40px; padding: 0;">
            ${i + 1}
        </button>
    `).join('');
}

// Actualizar mapa de preguntas
function updateQuestionMap() {
    createQuestionMap();
}

// Actualizar progreso
function updateProgress() {
    const answered = Object.keys(answers).length;
    const progress = (answered / questions.length) * 100;
    document.getElementById('progressFill').style.width = progress + '%';
}

// Timer
function startTimer() {
    timerInterval = setInterval(() => {
        timeRemaining--;
        
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;
        document.getElementById('timerDisplay').textContent = 
            `${minutes}:${seconds.toString().padStart(2, '0')}`;
        
        // Cambiar color cuando queda poco tiempo
        if (timeRemaining <= 300) { // 5 minutos
            document.getElementById('timer').style.color = 'var(--error)';
        }
        
        // Finalizar automáticamente cuando se acaba el tiempo
        if (timeRemaining <= 0) {
            clearInterval(timerInterval);
            finishExam();
        }
    }, 1000);
}

// Finalizar examen
async function finishExam() {
    if (Object.keys(answers).length < questions.length) {
        if (!confirm('No has respondido todas las preguntas. ¿Deseas finalizar el examen?')) {
            return;
        }
    }
    
    clearInterval(timerInterval);
    
    // Calcular resultados
    let correct = 0;
    let wrong = 0;
    
    questions.forEach((q, i) => {
        if (answers[i] === q.correct) {
            correct++;
        } else if (answers[i]) {
            wrong++;
        }
    });
    
    const score = Math.round((correct / questions.length) * 100);
    const timeTaken = examDuration - timeRemaining;
    
    // Guardar resultados
    await saveResults(score, correct, wrong, timeTaken);
    
    // Mostrar resultados
    showResults(score, correct, wrong, timeTaken);
}

// Guardar resultados
async function saveResults(score, correct, wrong, duration) {
    try {
        const token = localStorage.getItem('exams_token');
        await fetch('/api/opo/results', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                category: category,
                exam_type: examType,
                score: score,
                correct: correct,
                wrong: wrong,
                duration: duration
            })
        });
    } catch (error) {
        console.error('Error saving results:', error);
    }
}

// Mostrar resultados
function showResults(score, correct, wrong, duration) {
    const modal = document.getElementById('resultsModal');
    modal.style.display = 'flex';
    
    // Emoji según puntuación
    let emoji = '🎉';
    let message = '¡Excelente trabajo!';
    if (score < 50) {
        emoji = '📚';
        message = 'Sigue practicando';
    } else if (score < 70) {
        emoji = '👍';
        message = '¡Buen trabajo!';
    } else if (score < 90) {
        emoji = '🌟';
        message = '¡Muy bien!';
    }
    
    document.getElementById('resultEmoji').textContent = emoji;
    document.getElementById('resultScore').textContent = score + '%';
    document.getElementById('resultMessage').textContent = message;
    document.getElementById('resultCorrect').textContent = correct;
    document.getElementById('resultWrong').textContent = wrong;
    
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    document.getElementById('resultTime').textContent = 
        `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// Revisar examen
function reviewExam() {
    document.getElementById('resultsModal').style.display = 'none';
    
    // Mostrar todas las respuestas correctas
    questions.forEach((q, i) => {
        const options = document.querySelectorAll(`#questionContainer .option`);
        // TODO: Implementar revisión completa
    });
    
    showQuestion(0);
}

// Volver a tipos de examen
function goToExamTypes() {
    window.location.href = `/opo/exam-types?category=${category}`;
}

// Prevenir salida accidental
window.addEventListener('beforeunload', (e) => {
    if (Object.keys(answers).length > 0 && timerInterval) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// Inicializar
initExam();
