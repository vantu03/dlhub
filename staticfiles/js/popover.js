document.addEventListener('DOMContentLoaded', function () {
    const popoverId = 'dlhub-popover-message';
    const storageKey = 'dlhub_popover_lastShown';
    const cooldownMinutes = 5;

    function showPopover() {
        // Xóa nếu đã có
        document.getElementById(popoverId)?.remove();

        const popover = document.createElement('div');
        popover.id = popoverId;
        popover.className = 'position-fixed bottom-0 end-0 bg-white shadow border rounded p-3 m-4';
        popover.style.zIndex = 9999;
        popover.style.maxWidth = '300px';

        popover.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="me-2">
                    <i class="bi bi-check-circle-fill text-success fs-4"></i>
                </div>
                <div class="flex-grow-1">
                    <strong>Đã tải video thành công!</strong>
                    <p class="mb-1 small text-muted">
                        Dán liên kết khác để tiếp tục hoặc khám phá các công cụ tiện ích.
                    </p>
                    <a href="/articles/" class="btn btn-sm btn-outline-primary">Khám phá tiện ích</a>
                </div>
                <button class="btn-close ms-2 mt-1" onclick="document.getElementById('${popoverId}')?.remove()"></button>
            </div>
        `;

        document.body.appendChild(popover);

        // Lưu thời điểm hiện tại vào localStorage
        localStorage.setItem(storageKey, Date.now().toString());
    }

    function shouldShowPopover() {
        const lastShown = parseInt(localStorage.getItem(storageKey), 10);
        if (!lastShown) return true;
        const minutesPassed = (Date.now() - lastShown) / 1000 / 60;
        return minutesPassed >= cooldownMinutes;
    }

    const btn = document.getElementById('download-btn');
    if (btn) {
        btn.addEventListener('click', function () {
            if (shouldShowPopover()) {
                setTimeout(showPopover, 2000); // popover hiện sau 2 giây
            }
        });
    }
});
