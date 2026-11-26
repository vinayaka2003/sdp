document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
        form.addEventListener("submit", function (event) {
            if (!window.confirm(form.dataset.confirm)) {
                event.preventDefault();
            }
        });
    });

    document.querySelectorAll(".flash-close").forEach(function (button) {
        button.addEventListener("click", function () {
            button.closest(".flash-message").remove();
        });
    });
});
