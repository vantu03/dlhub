(function () {
    document.addEventListener('DOMContentLoaded', function () {
        setTimeout(() => {
            const editors = document.querySelectorAll('.ck-editor__editable_inline');

            editors.forEach((editor) => {
                // Gắn thẻ link bootstrap
                const bootstrapLink = document.createElement('link');
                bootstrapLink.rel = 'stylesheet';
                bootstrapLink.href = 'https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css';

                // Gắn vào đầu document (toàn admin)
                document.head.appendChild(bootstrapLink);

                // Thêm class Bootstrap nếu cần
                editor.classList.add('container'); // Optional
                editor.classList.add('pt-3');

                // Chỉnh lại chiều cao
                editor.style.minHeight = '300px';
                editor.style.maxHeight = '600px';
                editor.style.overflowY = 'auto';
                editor.style.boxSizing = 'border-box';
            });
        }, 500);
    });
})();
