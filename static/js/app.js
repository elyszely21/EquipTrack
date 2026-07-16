document.addEventListener("DOMContentLoaded", function () {

    // =========================
    // DELETE CONFIRMATION
    // =========================
    document.querySelectorAll("[data-confirm-delete]").forEach(function (el) {
        el.addEventListener("click", function (e) {
            var message = el.getAttribute("data-confirm-delete") || "Are you sure you want to delete this?";
            if (!confirm(message)) {
                e.preventDefault();
            }
        });
    });

    // =========================
    // FORM SUBMIT LOADING STATE
    // =========================
    document.querySelectorAll("form[data-disable-on-submit]").forEach(function (form) {
        form.addEventListener("submit", function () {
            var btn = form.querySelector('[type="submit"]');
            if (btn) {
                btn.classList.add("btn-loading");
                btn.disabled = true;
            }
            // Disable all inputs
            form.querySelectorAll("input, select, textarea, button").forEach(function (el) {
                if (el.type !== "hidden") {
                    el.disabled = true;
                }
            });
        });
    });

    // =========================
    // TOAST NOTIFICATION SYSTEM
    // =========================
    window.EquipTrack = window.EquipTrack || {};
    window.EquipTrack.toast = function (message, type) {
        type = type || "success";
        var container = document.getElementById("toast-container");
        if (!container) {
            container = document.createElement("div");
            container.id = "toast-container";
            container.className = "toast-container";
            document.body.appendChild(container);
        }

        var icons = {
            success: "bi-check-circle-fill",
            danger: "bi-x-circle-fill",
            warning: "bi-exclamation-triangle-fill",
            info: "bi-info-circle-fill"
        };

        var toast = document.createElement("div");
        toast.className = "toast align-items-center text-bg-" + type + " border-0 show";
        toast.setAttribute("role", "alert");
        toast.innerHTML =
            '<div class="d-flex">' +
            '  <div class="toast-body"><i class="bi ' + (icons[type] || icons.info) + ' me-2"></i>' + message + "</div>" +
            '  <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>' +
            "</div>";

        container.appendChild(toast);

        setTimeout(function () {
            toast.classList.remove("show");
            setTimeout(function () {
                toast.remove();
            }, 300);
        }, 4000);
    };

    // Auto-dismiss flash messages as toasts
    document.querySelectorAll(".alert-dismissible").forEach(function (alert) {
        var text = alert.querySelector(".alert") || alert;
        var msg = text.textContent.trim();
        var type = "info";
        if (alert.classList.contains("alert-success")) type = "success";
        else if (alert.classList.contains("alert-danger")) type = "danger";
        else if (alert.classList.contains("alert-warning")) type = "warning";

        // Show as toast and dismiss alert
        window.EquipTrack.toast(msg, type);
        var closeBtn = alert.querySelector(".btn-close");
        if (closeBtn) closeBtn.click();
    });

    // =========================
    // SEARCH INPUT CLEAR ON ESC
    // =========================
    document.querySelectorAll('input[name="search"]').forEach(function (input) {
        input.addEventListener("keydown", function (e) {
            if (e.key === "Escape") {
                input.value = "";
                input.form.submit();
            }
        });
    });

});
