(function () {
    const API_BASE = window.location.protocol === "file:" ? "https://ragnarok.natalie-eiryk.com" : window.location.origin;
    const FORM = document.getElementById("ask-form");
    const CALLSIGN = document.getElementById("sender-name");
    const QUESTION = document.getElementById("question");
    const SUBMIT = document.getElementById("submit-btn");
    const STATUS = document.getElementById("form-status");
    const QUESTION_COUNT = document.getElementById("question-count");
    const TURNSTILE_NOTE = document.getElementById("turnstile-note");
    const TURNSTILE_CONTAINER = document.getElementById("turnstile-container");

    let widgetId = null;
    let turnstileToken = "";
    let publicConfig = null;

    function setStatus(message, type) {
        STATUS.textContent = message;
        STATUS.className = `form-status ${type || ""}`.trim();
    }

    function setSubmitEnabled(enabled) {
        SUBMIT.disabled = !enabled;
    }

    function updateCounter() {
        QUESTION_COUNT.textContent = String(QUESTION.value.length);
    }

    function validateFields() {
        const question = QUESTION.value.trim();
        if (!question) {
            setStatus("Transmission empty. Try again.", "error");
            return false;
        }

        if (question.length > (publicConfig?.maxQuestionLength || 4000)) {
            setStatus("Transmission exceeds the relay limit.", "error");
            return false;
        }

        if (CALLSIGN.value.trim().length > (publicConfig?.maxCallsignLength || 60)) {
            setStatus("Callsign exceeds the relay limit.", "error");
            return false;
        }

        if (!turnstileToken) {
            setStatus("Relay checks are still waiting for proof you're human.", "warning");
            return false;
        }

        return true;
    }

    function resetTurnstileToken() {
        turnstileToken = "";
    }

    async function loadTurnstileScript() {
        if (window.turnstile) {
            return;
        }

        await new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = "https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit";
            script.async = true;
            script.defer = true;
            script.onload = resolve;
            script.onerror = reject;
            document.head.appendChild(script);
        });
    }

    async function loadPublicConfig() {
        const response = await fetch(`${API_BASE}/api/public-config`, {
            headers: { Accept: "application/json" },
        });

        if (!response.ok) {
            throw new Error(`Public config failed: ${response.status}`);
        }

        return response.json();
    }

    async function renderTurnstile(siteKey) {
        await loadTurnstileScript();

        widgetId = window.turnstile.render(TURNSTILE_CONTAINER, {
            sitekey: siteKey,
            theme: "dark",
            callback(token) {
                turnstileToken = token;
                TURNSTILE_NOTE.textContent = "Relay checks complete.";
                setSubmitEnabled(true);
            },
            "error-callback"() {
                resetTurnstileToken();
                TURNSTILE_NOTE.textContent = "Relay checks failed. Reload the page and try again.";
                setSubmitEnabled(false);
            },
            "expired-callback"() {
                resetTurnstileToken();
                TURNSTILE_NOTE.textContent = "Relay checks expired. Complete them again before sending.";
                setSubmitEnabled(false);
            },
        });
    }

    async function initialize() {
        updateCounter();
        setStatus("Loading relay...", "warning");
        setSubmitEnabled(false);

        QUESTION.addEventListener("input", updateCounter);

        try {
            publicConfig = await loadPublicConfig();
        } catch (error) {
            console.error(error);
            setStatus("The transmission relay is unavailable right now.", "error");
            TURNSTILE_NOTE.textContent = "Configuration could not be loaded.";
            return;
        }

        if (!publicConfig.turnstileSiteKey) {
            setStatus("The relay has not been configured yet.", "error");
            TURNSTILE_NOTE.textContent = "Missing Turnstile site key.";
            return;
        }

        try {
            await renderTurnstile(publicConfig.turnstileSiteKey);
            setStatus("Relay ready.", "success");
        } catch (error) {
            console.error(error);
            setStatus("The relay checks could not be loaded.", "error");
            TURNSTILE_NOTE.textContent = "Turnstile failed to initialize.";
        }
    }

    FORM.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!validateFields()) {
            return;
        }

        setSubmitEnabled(false);
        setStatus("Transmitting...", "warning");

        const payload = {
            callsign: CALLSIGN.value.trim(),
            question: QUESTION.value.trim(),
            sourcePage: window.location.pathname || "/ask-astrid.html",
            turnstileToken,
        };

        try {
            const response = await fetch(`${API_BASE}/api/ask-astrid`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Accept: "application/json",
                },
                body: JSON.stringify(payload),
            });

            const data = await response.json().catch(() => ({}));

            if (!response.ok) {
                throw new Error(data.error || "Transmission failed.");
            }

            FORM.reset();
            updateCounter();
            setStatus(`Transmission queued. Reference ${data.submissionId}.`, "success");
            resetTurnstileToken();
            if (window.turnstile && widgetId !== null) {
                window.turnstile.reset(widgetId);
            }
            TURNSTILE_NOTE.textContent = "Relay checks complete.";
        } catch (error) {
            console.error(error);
            setStatus(error.message || "Transmission failed.", "error");
            setSubmitEnabled(true);
        }
    });

    document.addEventListener("DOMContentLoaded", initialize);
})();
