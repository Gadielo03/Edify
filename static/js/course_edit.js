// Course Edit - Dynamic Formsets Handler with Bootstrap Modals
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
    const confirmUpdateModal = new bootstrap.Modal(document.getElementById('confirmUpdateModal'));
    
    // Cargar datos existentes
    const existingModulesData = JSON.parse(document.getElementById('existing-modules-data').textContent);
    
    // Cargar módulos existentes
    if (existingModulesData && existingModulesData.length > 0) {
        existingModulesData.forEach(moduleData => {
            addModule(moduleData);
        });
    } else {
        // Si no hay módulos, agregar uno vacío
        addModuleBtn.click();
    }
    
    // Event listener para agregar módulo
    addModuleBtn.addEventListener('click', function() {
        addModule(null);
    });
    
    function addModule(moduleData = null) {
        moduleCounter++;
        
        // Clonar template
        const moduleClone = moduleTemplate.content.cloneNode(true);
        const moduleCard = moduleClone.querySelector('.module-card');
        
        // Configurar el módulo
        moduleCard.setAttribute('data-module-index', moduleCounter);
        moduleCard.querySelector('.module-number').textContent = moduleCounter;
        
        // Configurar inputs del módulo
        const idInput = moduleCard.querySelector('.module-id-input');
        const titleInput = moduleCard.querySelector('.module-title-input');
        const orderInput = moduleCard.querySelector('.module-order-input');
        
        idInput.setAttribute('name', `module_id_${moduleCounter}`);
        titleInput.setAttribute('name', `module_${moduleCounter}_title`);
        orderInput.setAttribute('name', `module_${moduleCounter}_order`);
        
        // Si hay datos existentes, cargarlos
        if (moduleData) {
            idInput.value = moduleData.id || '';
            titleInput.value = moduleData.title || '';
            orderInput.value = moduleData.order || moduleCounter;
        } else {
            orderInput.value = moduleCounter;
        }
        
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
            addLesson(moduleCard, moduleIndex, null);
        });
        
        // Agregar al container
        modulesContainer.appendChild(moduleCard);
        
        // Cargar lecciones existentes o agregar una vacía
        if (moduleData && moduleData.lessons && moduleData.lessons.length > 0) {
            moduleData.lessons.forEach(lessonData => {
                const moduleIndex = moduleCard.getAttribute('data-module-index');
                addLesson(moduleCard, moduleIndex, lessonData);
            });
        } else {
            setTimeout(() => {
                const addLessonBtn = moduleCard.querySelector('.add-lesson-btn');
                addLessonBtn.click();
            }, 100);
        }
    }
    
    function addLesson(moduleCard, moduleIndex, lessonData = null) {
        const lessonsContainer = moduleCard.querySelector('.lessons-list');
        const currentLessons = lessonsContainer.querySelectorAll('.lesson-card');
        const lessonIndex = currentLessons.length + 1;
        
        // Clonar template
        const lessonClone = lessonTemplate.content.cloneNode(true);
        const lessonCard = lessonClone.querySelector('.lesson-card');
        
        // Configurar la lección
        lessonCard.setAttribute('data-lesson-index', lessonIndex);
        lessonCard.querySelector('.lesson-number').textContent = lessonIndex;
        
        // Configurar inputs de la lección
        const idInput = lessonCard.querySelector('.lesson-id-input');
        const titleInput = lessonCard.querySelector('.lesson-title-input');
        const orderInput = lessonCard.querySelector('.lesson-order-input');
        const typeSelect = lessonCard.querySelector('.lesson-type-input');
        const videoInput = lessonCard.querySelector('.lesson-video-input');
        const videoFileInput = lessonCard.querySelector('.lesson-video-file-input');
        const fileInput = lessonCard.querySelector('.lesson-file-input');
        const textInput = lessonCard.querySelector('.lesson-text-input');
        
        idInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_id`);
        titleInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_title`);
        orderInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_order`);
        typeSelect.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_content_type`);
        videoInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_video_url`);
        videoFileInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_video_file`);
        fileInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_file`);
        textInput.setAttribute('name', `module_${moduleIndex}_lesson_${lessonIndex}_text_content`);
        
        // Si hay datos existentes, cargarlos
        if (lessonData) {
            idInput.value = lessonData.id || '';
            titleInput.value = lessonData.title || '';
            orderInput.value = lessonData.order || lessonIndex;
            typeSelect.value = lessonData.content_type || '';
            videoInput.value = lessonData.video_url || '';
            textInput.value = lessonData.text_content || '';
            
            // Mostrar archivo actual si existe
            if (lessonData.file_name) {
                const currentFileSpan = lessonCard.querySelector('.current-file');
                currentFileSpan.textContent = `Archivo actual: ${lessonData.file_name}`;
                currentFileSpan.innerHTML += ' <a href="' + lessonData.file_url + '" target="_blank" class="text-primary">(Ver)</a>';
            }
            
            // Mostrar video actual si existe
            if (lessonData.video_file_name) {
                const currentVideoFileSpan = lessonCard.querySelector('.current-video-file');
                currentVideoFileSpan.textContent = `Video actual: ${lessonData.video_file_name}`;
                currentVideoFileSpan.innerHTML += ' <a href="' + lessonData.video_file_url + '" target="_blank" class="text-primary">(Ver)</a>';
            }
            
            // Mostrar campos según tipo de contenido
            handleContentTypeChange(lessonCard, lessonData.content_type);
        } else {
            orderInput.value = lessonIndex;
        }
        
        // Event listener para tipo de contenido
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
        const videoFileField = lessonCard.querySelector('.video-file-field');
        const fileField = lessonCard.querySelector('.file-field');
        const videoInput = videoField.querySelector('input');
        const videoFileInput = videoFileField.querySelector('input');
        const fileInput = fileField.querySelector('input');
        
        // Ocultar todos los campos
        videoField.style.display = 'none';
        videoFileField.style.display = 'none';
        fileField.style.display = 'none';
        videoInput.removeAttribute('required');
        videoFileInput.removeAttribute('required');
        fileInput.removeAttribute('required');
        
        // Mostrar el campo correspondiente
        if (contentType === 'video') {
            videoField.style.display = 'block';
            videoFileField.style.display = 'block';
            // No hacer required porque puede ser URL O archivo, no ambos
        } else if (contentType === 'pdf') {
            fileField.style.display = 'block';
            // No hacer required en edición si ya existe un archivo
            const currentFile = fileField.querySelector('.current-file').textContent;
            if (!currentFile) {
                fileInput.setAttribute('required', 'required');
            }
        }
    }
    
    function updateModuleNumbers() {
        const modules = modulesContainer.querySelectorAll('.module-card');
        modules.forEach((module, index) => {
            module.querySelector('.module-number').textContent = index + 1;
            const orderInput = module.querySelector('.module-order-input');
            orderInput.value = index + 1;
        });
    }
    
    function updateLessonNumbers(moduleCard) {
        const lessons = moduleCard.querySelectorAll('.lesson-card');
        lessons.forEach((lesson, index) => {
            lesson.querySelector('.lesson-number').textContent = index + 1;
            const orderInput = lesson.querySelector('.lesson-order-input');
            orderInput.value = index + 1;
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
    
    document.getElementById('confirmUpdate').addEventListener('click', function() {
        confirmUpdateModal.hide();
        // Submit del formulario
        document.getElementById('courseForm').submit();
    });
    
    // Validación del formulario antes de enviar
    const form = document.getElementById('courseForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const modules = modulesContainer.querySelectorAll('.module-card');
        
        if (modules.length === 0) {
            showValidationMessage('Debes tener al menos un módulo con una lección.');
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
        confirmUpdateModal.show();
    });
});
