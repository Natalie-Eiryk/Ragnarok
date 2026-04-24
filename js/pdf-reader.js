(function () {
    function getEmbedContainer() {
        return document.querySelector(".pdf-embed-container");
    }

    function getEmbed() {
        return document.querySelector(".pdf-embed");
    }

    function getThemeButton() {
        return document.querySelector(".dark-mode-toggle");
    }

    function applyTheme(isDark) {
        const container = getEmbedContainer();
        const button = getThemeButton();
        if (!container || !button) {
            return;
        }

        container.classList.toggle("dark-mode", isDark);
        const icon = button.querySelector(".mode-icon");
        const text = button.querySelector(".mode-text");
        if (icon) {
            icon.textContent = isDark ? "☀️" : "🌙";
        }
        if (text) {
            text.textContent = isDark ? "LIGHT" : "DARK";
        }

        localStorage.setItem("ragnarok-reader-dark", isDark ? "true" : "false");
    }

    function toggleTheme() {
        const container = getEmbedContainer();
        if (!container) {
            return;
        }
        applyTheme(!container.classList.contains("dark-mode"));
    }

    async function toggleFullscreen() {
        const container = getEmbedContainer();
        if (!container) {
            return;
        }
        if (document.fullscreenElement) {
            await document.exitFullscreen();
            return;
        }
        if (container.requestFullscreen) {
            await container.requestFullscreen();
        }
    }

    function hideLoadingState() {
        const loading = document.querySelector(".pdf-loading");
        if (loading) {
            loading.style.display = "none";
        }
    }

    document.addEventListener("DOMContentLoaded", function () {
        const savedDark = localStorage.getItem("ragnarok-reader-dark");
        applyTheme(savedDark !== "false");

        document.querySelectorAll("[data-reader-action]").forEach((button) => {
            button.addEventListener("click", function () {
                if (button.dataset.readerAction === "toggle-theme") {
                    toggleTheme();
                }
                if (button.dataset.readerAction === "toggle-fullscreen") {
                    toggleFullscreen();
                }
            });
        });

        const embed = getEmbed();
        if (embed) {
            embed.addEventListener("load", hideLoadingState);
        }
    });
})();
