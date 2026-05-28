# DVDcoin Exams Module

Sistema de exámenes y oposiciones para dvta.ch

## 🚀 Inicio Rápido

### Instalación

```bash
cd modules/exams
pip install -r requirements.txt
```

### Configuración

1. **Email**: Copiar `config/email.json.example` a `config/email.json` y configurar
2. **Admins**: Editar `config/admins.json` para añadir/quitar administradores

### Ejecutar

```bash
python app_exams.py
```

El servidor se iniciará en `http://localhost:8001`

## 📁 Estructura

```
exams/
├── app_exams.py          # Servidor principal
├── data/                 # Bases de datos
│   ├── users_exams.db    # Usuarios del módulo
│   ├── exams.db          # Exámenes generales
│   └── opo.db            # Oposiciones
├── static/               # Archivos estáticos
│   ├── index.html        # Página principal
│   ├── css/
│   └── js/
├── opo/                  # Módulo de oposiciones
│   ├── list.html         # Lista de oposiciones
│   ├── admin.html        # Panel admin
│   ├── exam-types.html   # Tipos de examen
│   └── exam.html         # Ejecución del examen
└── config/               # Configuración
    ├── email.json        # Config de email
    └── admins.json       # Lista de admins
```

## 🔐 Autenticación

### Registro
- Email + contraseña
- Verificación por email obligatoria
- Roles: `free`, `premium`, `admin`

### Admins
- Usuarios en `config/admins.json`
- Acceso gratis a todo el contenido
- Pueden gestionar preguntas y exámenes

## 💳 Sistema de Pagos

### Planes
- **Free**: Acceso limitado
- **Premium Mensual**: 9.99€/mes
- **Premium Anual**: 99€/año

### Integración Stripe
Configurar en variables de entorno:
```bash
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxxxx
```

## 📧 Sistema de Email

### Proveedores soportados
- SMTP (desarrollo)
- SendGrid (producción recomendado)
- Mailgun (alternativa)

### Emails automáticos
- Verificación de cuenta
- Recuperación de contraseña
- Confirmación de pago
- Recordatorios

## 🎯 Oposiciones (OPO)

### Categorías actuales
- Técnico Superior en Imagen para el Diagnóstico y Medicina Nuclear

### Tipos de examen
- **Test rápido**: 20 preguntas, 15 minutos
- **Simulacro**: 50 preguntas, 60 minutos
- **Examen completo**: 100 preguntas, 120 minutos

### Panel Admin
Acceso: `/opo/admin` (solo admins)

Funciones:
- Añadir/editar preguntas
- Gestionar categorías
- Ver estadísticas
- Exportar/importar preguntas

## 🔌 API Endpoints

### Autenticación
- `POST /api/auth/register` - Registro
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/verify-email` - Verificar email
- `POST /api/auth/reset-password` - Solicitar reset
- `POST /api/auth/new-password` - Establecer nueva contraseña

### Exámenes
- `GET /api/exams` - Lista de exámenes
- `GET /api/exams/:id` - Detalle de examen
- `POST /api/exams/:id/start` - Iniciar examen
- `POST /api/exams/:id/submit` - Enviar respuestas

### OPO
- `GET /api/opo/categories` - Categorías
- `GET /api/opo/questions` - Preguntas (admin)
- `POST /api/opo/questions` - Crear pregunta (admin)
- `PUT /api/opo/questions/:id` - Editar pregunta (admin)
- `DELETE /api/opo/questions/:id` - Eliminar pregunta (admin)

## 🎨 Estilo

Colores principales:
- Azul oscuro: `#2A4A78`
- Azul principal: `#4A7AB8`
- Azul claro: `#6B9BD4`
- Azul pálido: `#8BB3E8`

Fondo menos oscuro que bank para mejor legibilidad.

## 🚀 Despliegue

### Cloudflare Tunnel
```yaml
tunnel: dvta-tunnel
ingress:
  - hostname: dvta.ch
    service: http://localhost:8001
```

### Systemd Service
```ini
[Unit]
Description=DVDcoin Exams
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/modules/exams
ExecStart=/usr/bin/python3 app_exams.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📝 TODO

- [ ] Implementar sistema de pagos Stripe
- [ ] Añadir más categorías de oposiciones
- [ ] Sistema de estadísticas avanzadas
- [ ] Modo offline (PWA)
- [ ] App móvil (React Native)
- [ ] Gamificación (badges, rankings)
- [ ] Foro de estudiantes
- [ ] Clases en vivo

## 🐛 Troubleshooting

### Email no se envía
- Verificar configuración en `config/email.json`
- Comprobar logs del servidor
- Para desarrollo, usar MailHog: `docker run -p 1025:1025 -p 8025:8025 mailhog/mailhog`

### Base de datos bloqueada
- SQLite usa WAL mode para mejor concurrencia
- Si persiste, reiniciar el servidor

### Token JWT inválido
- Verificar que `config/jwt_secret_exams.txt` existe
- No compartir el secret entre módulos

## 📄 Licencia

© 2026 DVDcoin Platform. Todos los derechos reservados.
