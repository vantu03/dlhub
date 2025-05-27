let fakeProgress = 0;

document.getElementById("paste-btn").addEventListener("click", function () {
    navigator.clipboard.readText().then(text => {
        const input = document.getElementById("video-url-input");
        input.value = text.trim();
        const urls = linkify.find(text.trim()).filter(item => item.type === "url");
        if (urls.length > 0) {
            input.value = urls[0].href;
        }
        document.getElementById("paste-btn").classList.toggle("d-none", !!input.value);
        document.getElementById("clear-btn").classList.toggle("d-none", !input.value);
    }).catch(err => {
    });
});

// Khi có URL → ẩn nút dán, hiện nút xoá
document.getElementById("video-url-input").addEventListener("input", function () {
    const val = this.value.trim();
    document.getElementById("paste-btn").classList.toggle("d-none", !!val);
    document.getElementById("clear-btn").classList.toggle("d-none", !val);
});

// Nút Xoá → xóa input + chuyển lại nút dán
document.getElementById("clear-btn").addEventListener("click", function () {
    const input = document.getElementById("video-url-input");
    input.value = "";
    input.dispatchEvent(new Event("input")); // Kích hoạt lại để toggle
});

function showMessage(type = "info", text = "") {
    // type: 'success', 'danger', 'warning', 'info'
    const container = document.getElementById("alert-container");

    // Xóa nội dung cũ (nếu bạn muốn giữ nhiều thì bỏ dòng này)
    container.innerHTML = "";

    // Tạo alert div
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} d-flex align-items-center shadow-sm`;
    alertDiv.role = "alert";

    // Icon (tùy vào type)
    const icon = document.createElement("i");
    icon.className = "bi me-2";

    switch (type) {
        case "success": icon.classList.add("bi-check-circle-fill"); break;
        case "danger": icon.classList.add("bi-exclamation-triangle-fill"); break;
        case "warning": icon.classList.add("bi-exclamation-circle-fill"); break;
        default: icon.classList.add("bi-info-circle-fill");
    }

    // Nội dung text
    const span = document.createElement("span");
    span.innerHTML = text;

    // Gắn vào alert
    alertDiv.appendChild(icon);
    alertDiv.appendChild(span);

    // Thêm vào container
    container.appendChild(alertDiv);
    return container;
}

document.getElementById("download-btn").addEventListener("click", function () {
    const input = document.getElementById("video-url-input");
    if (!input.value) {
        showMessage("warning", "Hãy điền hoặc dán URL vào ô nhập địa chỉ.");
    } else {
        const rawUrl = input.value;
        try {
            const parsed = new URL(rawUrl);
            const host = parsed.hostname.replace(/^www\./, ''); // Bỏ 'www.' nếu có

            switch (host) {
                case "tiktok.com":
                case "vm.tiktok.com":
                case "m.tiktok.com":
                case "vt.tiktok.com":
                    encodeDownloadInfo(rawUrl, 0)
                        .then(token => downloadVideo(token))
                        .catch(err => showMessage("danger", err.message));
                    break;

                case "youtube.com":
                case "www.youtube.com":
                case "youtu.be":
                    encodeDownloadInfo(rawUrl, 1)
                        .then(token => downloadVideo(token))
                        .catch(err => showMessage("danger", err.message));
                    break;

                case "facebook.com":
                case "www.facebook.com":
                case "fb.watch":
                    encodeDownloadInfo(rawUrl, 2)
                        .then(token => downloadVideo(token))
                        .catch(err => showMessage("danger", err.message));
                    break;
                case "douyin.com":
                case "www.douyin.com":
                case "v.douyin.com":
                    encodeDownloadInfo(rawUrl, 0)
                        .then(token => downloadVideo(token))
                        .catch(err => showMessage("danger", err.message));
                    break;


                default:
                    showMessage("warning", "Không hỗ trợ trang: " + host);
            }

        } catch (e) {
            showMessage("danger", "Liên kết không hợp lệ.");
        }
    }
});

function showBlur() {
    const input = document.getElementById('input-container');
    if (input) {
        // Làm mờ toàn trang
        input.style.filter = "blur(3px)";
        input.style.pointerEvents = "none";
        input.style.userSelect = "none";
        input.style.transition = "filter 0.3s ease";
    }
}

function hideBlur() {
    const input = document.getElementById('input-container');
    if (input) {
        // Khôi phục lại bình thường
        input.style.filter = "";
        input.style.pointerEvents = "";
        input.style.userSelect = "";
        input.style.transition = "";
    }
}

function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute("content");
}

function encodeDownloadInfo(code, type1 = 0) {
    return fetch("/gen-token/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken()  // Thêm dòng này
        },
        body: JSON.stringify({ url: code, type1 })
    })
    .then(res => res.json())
    .then(data => {
        if (data.token) return data.token;
        else throw new Error("Không lấy được token");
    });
}


function downloadVideo(encoded) {
    const preview = document.getElementById("preview-container");
    const thumbnail = document.getElementById("video-thumbnail");
    const title = document.getElementById("video-title");
    const alert = document.getElementById("alert-container");
    const buttons = document.getElementById("download-buttons");
    const photoPreview = document.getElementById("photo-preview");

    thumbnail.src = "";
    title.innerText = "";
    buttons.innerHTML = "";
    alert.innerHTML = "";

    showBlur();
    startFakeProgress();

    fetch(`/perform?token=${encoded}`)
        .then(res => {
            if (!res.ok) throw new Error("Không thể lấy video.");
            return res.json();
        })
        .then(res => {
            if (!res.success) throw new Error("Tải video thất bại.");

            document.getElementById('input-container').remove();
            const data = res.data;

            thumbnail.src = data.thumbnail;
            title.innerText = data.title || "Không có tiêu đề";
            photoPreview.innerHTML = "";

            if (data.media_type === "photo") {
                data.urls.forEach(item => {
                    const label = Object.keys(item)[0];
                    const url = item[label];

                    // Hiển thị ảnh lớn bên dưới
                    const col = document.createElement("div");
                    col.className = "col";

                    const card = document.createElement("div");
                    card.className = "card shadow-sm";

                    const img = document.createElement("img");
                    img.src = url;
                    img.alt = label;
                    img.loading = 'lazy';
                    img.className = "card-img-top rounded";
                    img.className = "card-img-top rounded";
                    img.style.height = "300px";
                    img.style.objectFit = "cover";
                    img.style.width = "100%";

                    const cardBody = document.createElement("div");
                    cardBody.className = "card-body text-center";

                    const btn = document.createElement("a");
                    btn.href = url;
                    btn.download = "";
                    btn.className = "btn btn-outline-primary w-100";
                    btn.innerHTML = `<i class="bi bi-download"></i> ${label}`;

                    cardBody.appendChild(btn);
                    card.appendChild(img);
                    card.appendChild(cardBody);
                    col.appendChild(card);
                    photoPreview.appendChild(col);
                });
                setTimeout(() => {
                    photoPreview.scrollIntoView({ behavior: "smooth" });
                }, 100);

            } else {
                data.urls.forEach(item => {
                    const label = Object.keys(item)[0];
                    const url = item[label];

                    const btn = document.createElement("a");
                    btn.href = url;
                    btn.download = "";
                    btn.className = "btn btn-primary w-100 d-flex gap-2 mb-2";
                    btn.innerHTML = `<i class="bi bi-download"></i>${label}`;
                    buttons.appendChild(btn);
                });
            }
            completeFakeProgress();
            hideBlur();
            showMessage("success", "Video sẵn sàng để tải về.");
            preview.classList.remove("d-none");
        })
        .catch(err => {
            hideBlur();
            completeFakeProgress();
            showMessage("danger", err.message);
        });
}

function startFakeProgress() {
    fakeProgress = 0;
    const bar = document.getElementById("progress-bar");
    const wrapper = document.getElementById("progress-wrapper");

    wrapper.classList.remove("d-none");
    bar.style.width = "0%";

    function increase() {
        if (fakeProgress < 95) {
            fakeProgress += 1;
            bar.style.width = `${fakeProgress}%`;

            // gọi lại với delay tăng dần
            setTimeout(increase, 60 + fakeProgress * 2);
        }
    }

    increase();
}


function completeFakeProgress() {
    fakeProgress = 100;
    const bar = document.getElementById("progress-bar");

    // Bù lên 100%
    bar.style.width = "100%";
    const wrapper = document.getElementById("progress-wrapper");

    wrapper.classList.add("d-none");
}
