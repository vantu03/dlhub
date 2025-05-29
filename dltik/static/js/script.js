function setTheme(mode) {
    localStorage.setItem("theme", mode);
    document.body.className = "";

    // Cập nhật nút giao diện
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-outline-secondary');
        if (btn.dataset.theme === mode) {
            btn.classList.remove('btn-outline-secondary');
            btn.classList.add('btn-primary');
        }
    });

    let actualMode = mode;
    if (mode === "auto") {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        actualMode = prefersDark ? "dark" : "light";
    }

    document.body.classList.add("theme-" + actualMode);
    document.documentElement.setAttribute("data-theme", actualMode);

    // Ghi vào cookie để Django có thể đọc
    document.cookie = `theme=${actualMode}; path=/; max-age=31536000`;
}

function initTheme() {
    const currentTheme = localStorage.getItem("theme") || "auto";
    setTheme(currentTheme);

    // Nếu là auto thì lắng nghe thay đổi hệ thống
    if (currentTheme === "auto") {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener("change", () => {
            setTheme("auto");
        });
    }

    // Gán sự kiện click cho các nút
    document.querySelectorAll('.theme-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const mode = this.dataset.theme;
            setTheme(mode);
        });
    });
}

initTheme();
