// Course Create - Dynamic Formsets Handler with Bootstrap Modals
document.addEventListener('DOMContentLoaded', function() {
    let moduleCounter = 0;
    let pendingDeleteModule = null;
    let pendingDeleteLesson = null;
    
    const modulesContainer = document.getElementById('modules-container');
    const addModuleBtn = document.getElementById('add-module-btn');
    const moduleTemplate = document.getElementById('module-template');
    const lessonTemplate = document.getElementById('lesson-template');
    
    // Modales
    const deleteModuleModal = new bootstrap.Modal(document.getElementById('deleteModuleModal'));
    const deleteLessonModal = new bootstrap.Modal(document.getElementById('deleteLessonModal'));
    const validationModal = new bootstrap.Modal(document.getElementById('validationModal'));
    const confirmCreateModal = new bootstrap.Modal(document.getElementById('confirmCreateModal'));
    
    // Agregar primer módulo automáticamente
    addModuleBtn.click();
    
    // Event listener para agregar módulo
    addModuleBtn.addEventListener('click', function() {
        addModule();
    });
    
    function addModule() {
        moduleCounter++;
        
        // Clonar template
        const moduleClone = moduleTemplate.content.cloneNode(true);
        const moduleCard = moduleClone.querySelector('.module-card');
        
        // Configurar el módulo
        moduleCard.setAttribute('data-module-index', moduleCounter);
        moduleCard.querySelector('.module-number').textContent = moduleCounter;
        
        // Configurar inputs del módulo
        const titleInput = moduleCard.querySelector('input[type="text"]');
        const orderInput = moduleCard.querySelector('input[type="number"]');
        
        titleInput.setAttribute('name', `module_${moduleCounter}_title`);
        orderInput.setAttribute('name', `module_${moduleCounter}_order`);
        orderInput.value = moduleCounter;
        
        // Event listener para eliminar módulo
        const removeBtn = moduleCard.querySelector('.remove-module-btn');
        removeBtn.addEventListener('click', function() {
            pendingDeleteModule = moduleCard;
            deleteModuleModal.show();
        });
        
        // Event listener para agregar lección
        const addLessonBtn = moduleCard.querySelector('.add-lesson-btn');
        addLessonBtn.addEventListener('click', function() {
            const moduleIndex = moduleCard.getAttribute('data-module-index');
            addLesson(moduleCard, moduleIndex);
        });
        
        // Agregar al container
        modulesContainer.appendChild(moduleCard);
        
        // Agregar primera lección automáticamente
        setTimeout(() => {
            const addLessonBtn = moduleCard.querySelector('.add-lesson-btn');
            addLessonBtn.click();
        }, 100);
    }
    
    function addLesson(moduleCard, moduleIndex) {
        const lessonsContainer = moduleCard.querySelector('.lessons-list');
        const currentLessons = lessonsContainer.querySelectorAll('.lesson-card');
        const lessonIndex = currentLessons.length + 1;
        
        // Clonar template
        const lessonClone = lessonTemplate.content.cloneNode(true);
        const lessonCard = lessonClone.querySelector('.lesson-card');
        
        // Configurar la lección
        lessonCard.setAttribute('data-lesson-index', lessonIndex);
        lessonCard.querySelector('.lesson-number').textContent = lessonIndex;
        
        // Configurar inputs de la lección usando selectores específicos con clases
        const titleInput = lessonCard.querySelector('.lesson-title-input');
        const orderInput = lessonCard.querySelector('.lesson-order-input');
        const typeSelect = lessonCard.querySelector('.lesson-type-input');
        const videoInput = lessonCard.querySelector('.lesson-video-input');
        const fileInput = lessonCard.querySelector('.lesson-file-input');
        const textInput = lessonCard.querySelector('.lesson-text-input');
        
        // Asignar nombres
        titleInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_title`);
        orderInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_order`);
        orderInput.value = lessonIndex;
        typeSelect.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_content_type`);
        videoInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_video_url`);
        fileInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_file`);
        textInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_text_content`);
        
        // Event listener para mostrar/ocultar campos según tipo de contenido
        typeSelect.addEventListener('change', function() {
            handleContentTypeChange(lessonCard, this.value);
        });
        
        // Event listener para eliminar lección
        const removeBtn = lessonCard.querySelector('.remove-lesson-btn');
        removeBtn.addEventListener('click', function() {
            pendingDeleteLesson = { card: lessonCard, moduleCard: moduleCard };
            deleteLessonModal.show();
        });
        
        // Agregar al container
        lessonsContainer.appendChild(lessonCard);
    }
    
    function handleContentTypeChange(lessonCard, contentType) {
        const videoField = lessonCard.querySelector('.video-field');
        const fileField = lessonCard.querySelector('.file-field');
        const videoInput = videoField.querySelector('input');
        const fileInput = fileField.querySelector('input');
        
        // Ocultar todos los campos
        videoField.style.display = 'none';
        fileField.style.display = 'none';
        videoInput.removeAttribute('required');
        fileInput.removeAttribute('required');
        
        // Mostrar el campo correspondiente
        if (contentType === 'video') {
            videoField.style.display = 'block';
            videoInput.setAttribute('required', 'required');
        } else if (contentType === 'pdf') {
            fileField.style.display = 'block';
            fileInput.setAttribute('required', 'required');
        }
    }
    
    function updateModuleNumbers() {
        const modules = modulesContainer.querySelectorAll('.module-card');
        modules.forEach((module, index) => {
            module.querySelector('.module-number').textContent = index + 1;
            module.querySelector('input[type="number"]').value = index + 1;
        });
    }
    
    function updateLessonNumbers(moduleCard) {
        const lessons = moduleCard.querySelectorAll('.lesson-card');
        lessons.forEach((lesson, index) => {
            lesson.querySelector('.lesson-number').textContent = index + 1;
            lesson.querySelector('input[type="number"]').value = index + 1;
        });
    }
    
    function showValidationMessage(message) {
        document.getElementById('validationMessage').textContent = message;
        validationModal.show();
    }
    
    // Event listeners para los botones de confirmación de los modales
    document.getElementById('confirmDeleteModule').addEventListener('click', function() {
        if (pendingDeleteModule) {
            pendingDeleteModule.remove();
            updateModuleNumbers();
            pendingDeleteModule = null;
        }
        deleteModuleModal.hide();
    });
    
    document.getElementById('confirmDeleteLesson').addEventListener('click', function() {
        if (pendingDeleteLesson) {
            pendingDeleteLesson.card.remove();
            updateLessonNumbers(pendingDeleteLesson.moduleCard);
            pendingDeleteLesson = null;
        }
        deleteLessonModal.hide();
    });
    
    document.getElementById('confirmCreate').addEventListener('click', function() {
        confirmCreateModal.hide();
        // Submit del formulario
        document.getElementById('courseForm').submit();
    });
    
    // Validación del formulario antes de enviar
    const form = document.getElementById('courseForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const modules = modulesContainer.querySelectorAll('.module-card');
        
        if (modules.length === 0) {
            showValidationMessage('Debes agregar al menos un módulo con una lección.');
            return false;
        }
        
        let hasEmptyModule = false;
        modules.forEach(module => {
            const lessons = module.querySelectorAll('.lesson-card');
            if (lessons.length === 0) {
                hasEmptyModule = true;
            }
        });
        
        if (hasEmptyModule) {
            showValidationMessage('Cada módulo debe tener al menos una lección.');
            return false;
        }
        
        // Mostrar modal de confirmación
        confirmCreateModal.show();
    });
});
