# 🏗️ PLAN DE ARQUITECTURA MODULAR - DVDcoin Platform

## 📅 Fecha: 27 Mayo 2026

## 🎯 Objetivo
Separar el proyecto monolítico actual en módulos independientes por funcionalidad, cada uno con:
- Servidor Python propio
- Base de datos separada
- Sistema de autenticación independiente
- Interfaz HTML propia con estilo diferenciado

---

## 📁 Nueva Estructura de Carpetas

```
dvdcoin/
├── modules/
│   ├── bank/              # DVDcoin Bank (migrado desde raíz)
│   │   ├── static/
│   │   ├── data/
│   │   ├── app_bank.py
│   │   └── requirements.txt
│   │
│   ├── exams/             # Sistema de Exámenes (NUEVO)
│   │   ├── static/
│   │   │   ├── css/
│   │   │   │   └── exams-style.css  # Estilo azulado
│   │   │   ├── js/
│   │   │   └── index.html           # Lista de exámenes
│   │   ├── opo/
│   │   │   ├── admin.html           # Gestión admin (dvd/tata)
│   │   │   ├── list.html            # Lista de oposiciones
│   │   │   ├── exam-types.html      # Tipos de examen
│   │   │   └── exam.html            # Ejecución del examen
│   │   ├── data/
│   │   │   ├── exams.db             # BD principal
│   │   │   ├── opo.db               # BD oposiciones
│   │   │   └── users_exams.db       # Usuarios del módulo
│   │   ├── app_exams.py             # Servidor FastAPI
│   │   ├── auth_exams.py            # Sistema auth + email
│   │   ├── payments.py              # Sistema de pagos
│   │   └── requirements.txt
│   │
│   ├── games/             # Juegos (reorganizado)
│   │   ├── static/
│   │   │   ├── cifrasletras/
│   │   │   ├── hundirlaflota/
│   │   │   ├── millonario/
│   │   │   ├── pasapalabra/
│   │   │   ├── quiensoy/
│   │   │   └── index.html           # Lista de juegos
│   │   ├── data/
│   │   │   └── games.db
│   │   ├── app_games.py
│   │   └── requirements.txt
│   │
│   ├── social/            # Sistema Social (futuro)
│   │   ├── static/
│   │   ├── data/
│   │   ├── app_social.py
│   │   └── requirements.txt
│   │
│   └── shared/            # Código compartido
│       ├── utils.py
│       ├── jwt_helper.py
│       └── email_service.py
│
├── config/                # Configuración global
│   ├── cloudflare-bank.yml
│   ├── cloudflare-exams.yml
│   └── cloudflare-games.yml
│
├── main_router.py         # Router principal (redirige a módulos)
└── requirements.txt       # Dependencias globales
```

---

## 🔐 Sistema de Autenticación por Módulo

### EXAMS (dvta.ch/exams)
- **Registro**: Email + contraseña
- **Verificación**: Link por email (obligatorio)
- **Roles**:
  - `admin`: dvd, tata (acceso total gratis)
  - `premium`: usuarios de pago (acceso completo)
  - `free`: usuarios gratuitos (acceso limitado)
- **Cambio de contraseña admin**: Archivo config editable

### BANK (dvdbank.com)
- Sistema actual (sin cambios)

### GAMES
- Login opcional
- Puntuaciones anónimas o con usuario

---

## 💳 Sistema de Pagos (EXAMS)

### Proveedores
- Stripe (principal)
- PayPal (alternativo)

### Planes
1. **Free**: Acceso a exámenes demo
2. **Premium Mensual**: 9.99€/mes
3. **Premium Anual**: 99€/año (2 meses gratis)

### Excepciones
- Admins (dvd, tata): acceso gratis siempre
- Códigos promocionales

---

## 🎨 Estilos por Módulo

### BANK
- **Colores**: Dorado oscuro (#D4A843) sobre negro (#04040A)
- **Estilo**: Art-deco noir, elegante

### EXAMS
- **Colores**: Azul (#4A7AB8, #6B9BD4, #8BB3E8) sobre gris oscuro (#1A2030)
- **Estilo**: Moderno, limpio, profesional
- **Menos oscuro** que bank

### GAMES
- **Colores**: Variados según juego
- **Estilo**: Divertido, colorido

---

## 📧 Sistema de Email (EXAMS)

### Proveedor
- SendGrid / Mailgun / SMTP

### Emails automáticos
1. **Verificación de cuenta**
   - Link de activación (válido 24h)
   - Reenvío si expira

2. **Recuperación de contraseña**
   - Link de reset (válido 1h)

3. **Confirmación de pago**
   - Recibo + activación premium

4. **Recordatorios**
   - Exámenes pendientes
   - Renovación de suscripción

---

## 🗄️ Bases de Datos

### EXAMS
```sql
-- users_exams.db
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'free',  -- admin, premium, free
    verified INTEGER DEFAULT 0,
    verification_token TEXT,
    created_at TEXT,
    verified_at TEXT
);

CREATE TABLE subscriptions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    plan TEXT,  -- monthly, annual
    status TEXT,  -- active, cancelled, expired
    started_at TEXT,
    expires_at TEXT,
    stripe_subscription_id TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- exams.db
CREATE TABLE exam_categories (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    description TEXT,
    icon TEXT,
    requires_premium INTEGER DEFAULT 1
);

CREATE TABLE exams (
    id INTEGER PRIMARY KEY,
    category_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    duration_minutes INTEGER,
    total_questions INTEGER,
    passing_score INTEGER,
    requires_premium INTEGER DEFAULT 1,
    FOREIGN KEY (category_id) REFERENCES exam_categories(id)
);

-- opo.db (migrado desde bank)
CREATE TABLE opo_questions (
    id INTEGER PRIMARY KEY,
    category TEXT,
    question TEXT,
    options_json TEXT,
    correct_answer TEXT,
    explanation TEXT
);

CREATE TABLE opo_results (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    exam_id INTEGER,
    score INTEGER,
    correct INTEGER,
    wrong INTEGER,
    duration_seconds INTEGER,
    completed_at TEXT
);
```

---

## 🚀 Rutas y Dominios

### Cloudflare Tunnels
```yaml
# dvdbank.com → bank
tunnel: dvdbank-tunnel
ingress:
  - hostname: dvdbank.com
    service: http://localhost:8000

# dvta.ch → exams
tunnel: dvta-tunnel
ingress:
  - hostname: dvta.ch
    service: http://localhost:8001
  - hostname: dvta.ch
    path: /exams/*
    service: http://localhost:8001
  - hostname: dvta.ch
    path: /opo/*
    service: http://localhost:8001

# games.dvdbank.com → games (futuro)
tunnel: games-tunnel
ingress:
  - hostname: games.dvdbank.com
    service: http://localhost:8002
```

### Puertos
- **8000**: Bank
- **8001**: Exams
- **8002**: Games
- **8003**: Social (futuro)

---

## 📝 Migración de OPO

### Pasos
1. ✅ Copiar archivos de `static/opo/` a `modules/exams/opo/`
2. ✅ Copiar `data/opo.db` y `data/oposiciones.db` a `modules/exams/data/`
3. ✅ Crear nuevos HTML separados:
   - `admin.html` - Panel admin (solo dvd/tata)
   - `list.html` - Lista de oposiciones disponibles
   - `exam-types.html` - Tipos de examen (test, simulacro, etc.)
   - `exam.html` - Ejecución del examen
4. ✅ Crear rutas en `app_exams.py`
5. ✅ Eliminar código OPO de `src/main.py`
6. ✅ Eliminar archivos OPO de `static/opo/`
7. ✅ Actualizar navegación en bank (quitar pestaña OPO)

### HTML a crear
```
modules/exams/
├── static/
│   ├── index.html              # Lista de categorías de exámenes
│   └── css/
│       └── exams-style.css     # Estilo azulado
└── opo/
    ├── admin.html              # Gestión (añadir/editar preguntas)
    ├── list.html               # Lista de oposiciones
    ├── exam-types.html         # Selección de tipo
    └── exam.html               # Ejecución
```

---

## 🔧 Tecnologías

### Backend
- **FastAPI** (todos los módulos)
- **SQLite** (bases de datos)
- **JWT** (autenticación)
- **bcrypt** (hashing contraseñas)
- **SendGrid** (emails)
- **Stripe** (pagos)

### Frontend
- **HTML5 + CSS3**
- **JavaScript vanilla** (sin frameworks)
- **Fetch API** (llamadas AJAX)

---

## ✅ Checklist de Implementación

### Fase 1: Estructura Base
- [ ] Crear carpeta `modules/`
- [ ] Crear subcarpetas por módulo
- [ ] Crear `shared/` con utilidades comunes

### Fase 2: Módulo EXAMS
- [ ] Crear `app_exams.py`
- [ ] Crear sistema de autenticación
- [ ] Crear sistema de email
- [ ] Crear sistema de pagos
- [ ] Crear bases de datos
- [ ] Crear `index.html` (lista de exámenes)
- [ ] Crear estilos azulados

### Fase 3: Migración OPO
- [ ] Copiar archivos y BD
- [ ] Crear HTML separados (admin, list, types, exam)
- [ ] Implementar rutas en `app_exams.py`
- [ ] Probar funcionalidad completa
- [ ] Eliminar de bank
- [ ] Actualizar navegación bank

### Fase 4: Módulo GAMES
- [ ] Reorganizar juegos actuales
- [ ] Crear `app_games.py`
- [ ] Crear `index.html` (lista de juegos)
- [ ] Redirigir rutas

### Fase 5: Configuración Cloudflare
- [ ] Configurar tunnel para exams (puerto 8001)
- [ ] Configurar DNS dvta.ch
- [ ] Probar acceso externo

### Fase 6: Testing
- [ ] Probar registro + verificación email
- [ ] Probar login/logout
- [ ] Probar acceso admin
- [ ] Probar sistema de pagos
- [ ] Probar exámenes OPO
- [ ] Verificar que bank sigue funcionando

---

## ⚠️ Precauciones

1. **NO romper bank**: Mantener funcionando mientras migramos
2. **Backups**: Hacer backup completo antes de cada fase
3. **Testing**: Probar cada módulo independientemente
4. **Rollback**: Tener plan de vuelta atrás si algo falla

---

## 📞 Contacto Admin

**Admins EXAMS**: dvd, tata
**Cambio de contraseña**: Editar `modules/exams/config/admins.json`

```json
{
  "admins": [
    {"username": "dvd", "password_hash": "..."},
    {"username": "tata", "password_hash": "..."}
  ]
}
```

---

**Estado**: 🟡 Planificación completa
**Próximo paso**: Crear estructura de carpetas y módulo EXAMS
