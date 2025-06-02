<script>
document.addEventListener('DOMContentLoaded', function () {
    const popoverId = 'join-fb-group-popover';
    const storageKey = 'fb_group_popover_last_shown';
    const cooldownHours = 24; // 1 ngày

    function shouldShowPopover() {
        const lastShown = parseInt(localStorage.getItem(storageKey), 10);
        if (!lastShown) return true;
        const hoursPassed = (Date.now() - lastShown) / (1000 * 60 * 60);
        return hoursPassed >= cooldownHours;
    }

    function showPopover() {
        if (document.getElementById(popoverId)) return;

        const div = document.createElement('div');
        div.id = popoverId;
        div.className = 'position-fixed bottom-0 end-0 bg-white border shadow rounded p-3 m-4';
        div.style.zIndex = 9999;
        div.style.maxWidth = '320px';

        div.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="me-2">
                    <i class="bi bi-people-fill text-primary fs-4"></i>
                </div>
                <div class="flex-grow-1">
                    <strong>Tham gia nhóm DLHub Community!</strong>
                    <p class="mb-2 small text-muted">Giao lưu, hỏi đáp và chia sẻ kinh nghiệm tải video TikTok và công cụ tiện ích.</p>
                    <a href="https://www.facebook.com/groups/1255118046232813" target="_blank" class="btn btn-sm btn-primary">Tham gia nhóm</a>
                </div>
                <button class="btn-close ms-2 mt-1" onclick="document.getElementById('${popoverId}')?.remove()"></button>
            </div>
        `;

        document.body.appendChild(div);
        localStorage.setItem(storageKey, Date.now().toString());
    }

    // Chờ 10 giây rồi hiển thị nếu đủ điều kiện
    if (shouldShowPopover()) {
        setTimeout(showPopover, 10000);
    }
});
</script>
