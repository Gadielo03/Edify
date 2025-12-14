# 📚 Edify - Plataforma de Cursos en Línea

Edify es una plataforma educativa moderna desarrollada con Django que permite a los maestros crear y gestionar cursos en línea, mientras que los estudiantes pueden inscribirse, realizar seguimiento de su progreso y obtener certificados al completar los cursos.

## 🎯 Propósito del Proyecto

Edify fue diseñado para facilitar el aprendizaje en línea proporcionando:

- **Para Maestros:**
  - Crear y gestionar cursos con múltiples módulos y lecciones
  - Soporte para contenido multimedia (videos de YouTube/Vimeo, archivos PDF, videos locales)
  - Seguimiento del progreso de los estudiantes
  - Sistema de reseñas y calificaciones

- **Para Estudiantes:**
  - Explorar catálogo de cursos disponibles
  - Realizar seguimiento del progreso personal
  - Descargar certificados al completar cursos
  - Dejar reseñas y calificaciones

## 🛠️ Tecnologías Utilizadas

- **Backend:** Django 5.0+
- **Base de Datos:** PostgreSQL 15
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Containerización:** Docker & Docker Compose
- **Generación de PDFs:** ReportLab
- **Procesamiento de Imágenes:** Pillow

## 📋 Prerequisitos

Antes de comenzar, asegúrate de tener instalado:

- [Docker](https://docs.docker.com/get-docker/) (v20.10 o superior)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0 o superior)
- Git

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone https://github.com/Gadielo03/Edify.git
cd Edify
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Django Settings
SECRET_KEY=tu-clave-secreta-super-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=edify_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

**Nota:** Para generar una `SECRET_KEY` segura, puedes usar:

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 3. Construir y Levantar los Contenedores

```bash
docker compose build
docker compose up -d
```

### 4. Ejecutar Migraciones

```bash
docker compose exec web python manage.py migrate
```

### 5. Crear Superusuario (Opcional)

```bash
docker compose exec web python manage.py createsuperuser
```

### 6. Cargar Archivos Estáticos

```bash
docker compose exec web python manage.py collectstatic --noinput
```

### 7. Acceder a la Aplicación

- **Aplicación Principal:** http://localhost:8000
- **Panel de Administración:** http://localhost:8000/admin

## 📂 Estructura del Proyecto

```
Edify/
├── config/              # Configuración principal de Django
│   ├── settings.py     # Configuraciones del proyecto
│   ├── urls.py         # URLs principales
│   └── middleware.py   # Middleware personalizado
├── users/              # Aplicación de usuarios
│   ├── models.py       # Modelo de Usuario personalizado
│   ├── views.py        # Vistas de autenticación y perfil
│   ├── forms.py        # Formularios de registro y login
│   └── tests.py        # Tests unitarios (10 tests)
├── course/             # Aplicación de cursos
│   ├── models.py       # Modelos: Course, Module, Lesson, etc.
│   ├── views.py        # Vistas de CRUD de cursos
│   ├── forms.py        # Formularios de cursos
│   ├── utils.py        # Utilidades (generación de certificados)
│   └── tests.py        # Tests unitarios (17 tests)
├── templates/          # Templates HTML
├── static/             # Archivos estáticos (CSS, JS)
├── media/              # Archivos subidos por usuarios
├── docker-compose.yml  # Configuración de Docker Compose
├── Dockerfile          # Dockerfile para la aplicación
├── requirements.txt    # Dependencias de Python
└── manage.py          # CLI de Django
```

## 🧪 Ejecutar Tests

### Ejecutar todos los tests
```bash
docker compose exec web python manage.py test
```

### Ejecutar tests de un módulo específico
```bash
docker compose exec web python manage.py test users.tests
docker compose exec web python manage.py test course.tests
```

### Ejecutar una clase de tests específica
```bash
docker compose exec web python manage.py test users.tests.UserLoginTest
```

### Ejecutar un test individual
```bash
docker compose exec web python manage.py test users.tests.UserLoginTest.test_login_valid_credentials
```

## 📊 Modelos Principales

### User (users.models)
- Modelo de usuario personalizado con roles (Maestro/Estudiante)
- Campos: username, email, role, bio

### Course (course.models)
- Representa un curso completo
- Campos: title, slug, description, owner, created, updated

### Module (course.models)
- Módulos dentro de un curso
- Campos: course, title, order

### Lesson (course.models)
- Lecciones individuales con diferentes tipos de contenido
- Tipos: video, pdf, text
- Soporta videos de YouTube/Vimeo y archivos locales

### UserProgress (course.models)
- Seguimiento del progreso del estudiante
- Campos: user, lesson, is_completed

### CourseReview (course.models)
- Reseñas y calificaciones de cursos
- Campos: course, user, rating (1-5), comment

## 🔧 Comandos Útiles

### Ver logs de los contenedores
```bash
docker compose logs -f web
```

### Detener los contenedores
```bash
docker compose down
```

### Eliminar volúmenes (base de datos y media)
```bash
docker compose down -v
```

### Acceder a la shell de Django
```bash
docker compose exec web python manage.py shell
```

### Crear migraciones
```bash
docker compose exec web python manage.py makemigrations
```

### Ver estado de las migraciones
```bash
docker compose exec web python manage.py showmigrations
```

## 🔐 Roles de Usuario

### Maestro (Teacher)
- Crear, editar y eliminar cursos
- Ver progreso de estudiantes
- Gestionar módulos y lecciones

### Estudiante (Student)
- Ver catálogo de cursos
- Inscribirse en cursos
- Marcar lecciones como completadas
- Descargar certificados
- Dejar reseñas