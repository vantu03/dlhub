function setTheme(mode) {
    localStorage.setItem("theme", mode);
    document.body.className = "";

    // Cập nhật giao diện nút
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-secondary');
        if (btn.dataset.theme === mode) {
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-primary');
        }
    });

    document.body.classList.add("theme-" + mode);
}

setTheme(localStorage.getItem("theme") || "auto");

// Gán sự kiện click cho các nút
document.querySelectorAll('.theme-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const mode = this.dataset.theme;
        setTheme(mode);
    });
});