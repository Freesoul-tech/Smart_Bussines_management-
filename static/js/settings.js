document.addEventListener("DOMContentLoaded", function () {

    const settingsPage = document.getElementById("settingsPage");
    const themeToggle = document.getElementById("themeToggle");

    if (!settingsPage || !themeToggle) {
        return;
    }

    /* =====================================================
       CSRF TOKEN
    ===================================================== */

    function getCSRFToken() {
        const csrfInput = document.querySelector(
            "[name=csrfmiddlewaretoken]"
        );

        return csrfInput ? csrfInput.value : "";
    }


    /* =====================================================
       APPLY THEME GLOBALLY
    ===================================================== */

    function applyTheme(theme) {

        // Apply theme to the entire document
        document.documentElement.setAttribute(
            "data-theme",
            theme
        );

        document.body.setAttribute(
            "data-theme",
            theme
        );

        // Keep settings page in sync
        settingsPage.setAttribute(
            "data-theme",
            theme
        );


        // Update settings toggle
        if (theme === "dark") {

            settingsPage.classList.add("dark-mode");

            themeToggle.classList.add("dark");

            themeToggle.setAttribute(
                "aria-pressed",
                "true"
            );

        } else {

            settingsPage.classList.remove("dark-mode");

            themeToggle.classList.remove("dark");

            themeToggle.setAttribute(
                "aria-pressed",
                "false"
            );
        }
    }


    /* =====================================================
       LOAD SAVED THEME
    ===================================================== */

    const savedTheme =
        document.documentElement.getAttribute("data-theme")
        || settingsPage.dataset.theme
        || "light";

    applyTheme(savedTheme);


    /* =====================================================
       THEME TOGGLE
    ===================================================== */

    themeToggle.addEventListener("click", function () {

        const currentTheme =
            document.documentElement.getAttribute("data-theme")
            || "light";

        const newTheme =
            currentTheme === "dark"
                ? "light"
                : "dark";


        // Change the interface immediately
        applyTheme(newTheme);


        /* =================================================
           SAVE THEME TO DJANGO
        ================================================= */

        fetch("/settings/toggle-theme/", {

            method: "POST",

            headers: {
                "X-CSRFToken": getCSRFToken(),

                "Content-Type":
                    "application/x-www-form-urlencoded",

                "X-Requested-With":
                    "XMLHttpRequest"
            },

            body:
                "theme=" +
                encodeURIComponent(newTheme)

        })

        .then(function (response) {

            if (!response.ok) {
                throw new Error(
                    "Theme request failed: " +
                    response.status
                );
            }

            return response.json();
        })

        .then(function (data) {

            if (!data.success) {

                console.error(
                    "Theme could not be saved:",
                    data.message
                );

                // Restore previous theme if saving failed
                applyTheme(currentTheme);
            }

        })

        .catch(function (error) {

            console.error(
                "Theme request failed:",
                error
            );

            // Restore previous theme if request failed
            applyTheme(currentTheme);
        });

    });

});