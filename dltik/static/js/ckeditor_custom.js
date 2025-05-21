CKEDITOR.on('instanceReady', function (ev) {
    console.log("Custom JS loaded for CKEditor:", ev.editor.name);

    // Ví dụ: auto focus
    ev.editor.focus();

    // Ví dụ: đặt theme nền tối nếu CSS không đủ
    ev.editor.document.getBody().setStyle('background-color', '#1e1e2f');
    ev.editor.document.getBody().setStyle('color', '#f0f0f0');
});
