CKEDITOR.on('instanceReady', function (ev) {
    const editor = ev.editor;

    // Làm tối vùng soạn thảo WYSIWYG
    const body = editor.document.getBody();
    body.setStyle('background-color', '#1e1e2f');
    body.setStyle('color', '#ffffff');

    // Theo dõi khi chuyển chế độ "Source"
    editor.on('mode', function () {
        if (editor.mode === 'source') {
            setTimeout(function () {
                const textarea = editor.container.$.querySelector('.cke_source');
                if (textarea) {
                    textarea.style.backgroundColor = '#1e1e2f';
                    textarea.style.color = '#ffffff';
                    textarea.style.fontFamily = 'monospace';
                }
            }, 50); // delay nhẹ để DOM ổn định
        }
    });
});
