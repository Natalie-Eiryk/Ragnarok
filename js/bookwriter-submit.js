(function () {
    "use strict";

    const INTAKE_LABELS = "bookwriter,writing-submission,triage";
    const STORAGE_KEY = "ragnarok.bookwriter.submissions.v1";
    const MAX_URL_BODY_CHARS = 5200;
    const MAX_SAVED = 20;

    const form = document.getElementById("submission-form");
    const packetOutput = document.getElementById("packet-output");
    const statusLine = document.getElementById("status-line");
    const copyButton = document.getElementById("copy-packet");
    const downloadButton = document.getElementById("download-packet");
    const clearButton = document.getElementById("clear-local");
    const savedList = document.getElementById("saved-list");
    const issueTitleInput = document.getElementById("issue-title");
    const issueBodyInput = document.getElementById("issue-body");
    const issueLabelsInput = document.getElementById("issue-labels");

    let currentPacket = "";
    let currentFilename = "bookwriter-submission.md";

    function normalize(value) {
        return String(value || "").trim();
    }

    function splitTags(value) {
        return normalize(value)
            .split(",")
            .map((tag) => tag.trim())
            .filter(Boolean);
    }

    function makeSubmissionId() {
        const stamp = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14);
        const random = Math.random().toString(36).slice(2, 7).toUpperCase();
        return `BW-${stamp}-${random}`;
    }

    function safeFilename(value) {
        const base = normalize(value)
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-+|-+$/g, "")
            .slice(0, 48);
        return base || "untitled";
    }

    function collectSubmission() {
        const data = new FormData(form);
        const title = normalize(data.get("writingTitle")) || "Untitled transmission";
        const author = normalize(data.get("author")) || "Anonymous";
        const kind = normalize(data.get("kind")) || "draft";
        const tags = splitTags(data.get("tags"));
        const notes = normalize(data.get("notes"));
        const writing = normalize(data.get("writing"));
        const createdAt = new Date().toISOString();
        const submissionId = makeSubmissionId();

        return { submissionId, title, author, kind, tags, notes, writing, createdAt };
    }

    function buildPacket(submission) {
        const tagText = submission.tags.length ? submission.tags.join(", ") : "none";
        return [
            "---",
            `submission_id: ${submission.submissionId}`,
            "source_app: ragnarok-gitpages-bookwriter",
            "system_flag: writing_submission",
            "labels: bookwriter, writing-submission, triage",
            `created_at: ${submission.createdAt}`,
            `kind: ${submission.kind}`,
            `title: ${submission.title}`,
            `author: ${submission.author}`,
            `tags: ${tagText}`,
            "---",
            "",
            "## Notes",
            "",
            submission.notes || "None",
            "",
            "## Writing",
            "",
            submission.writing,
            "",
        ].join("\n");
    }

    function loadSaved() {
        try {
            const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
            return Array.isArray(parsed) ? parsed : [];
        } catch {
            return [];
        }
    }

    function saveSubmission(submission, packet) {
        const saved = loadSaved();
        saved.unshift({
            id: submission.submissionId,
            title: submission.title,
            kind: submission.kind,
            createdAt: submission.createdAt,
            packet,
        });
        localStorage.setItem(STORAGE_KEY, JSON.stringify(saved.slice(0, MAX_SAVED)));
        renderSaved();
    }

    function renderSaved() {
        savedList.textContent = "";
        const saved = loadSaved();
        if (saved.length === 0) {
            const item = document.createElement("li");
            item.textContent = "No local packets";
            savedList.appendChild(item);
            return;
        }

        for (const submission of saved) {
            const item = document.createElement("li");
            const button = document.createElement("button");
            button.type = "button";
            button.textContent = `${submission.title} / ${submission.kind} / ${submission.id}`;
            button.addEventListener("click", () => {
                currentPacket = submission.packet;
                currentFilename = `${safeFilename(submission.title)}-${submission.id}.md`;
                packetOutput.value = currentPacket;
                copyButton.disabled = false;
                downloadButton.disabled = false;
                setStatus("Loaded local packet.");
            });
            item.appendChild(button);
            savedList.appendChild(item);
        }
    }

    function setStatus(message) {
        statusLine.textContent = message;
    }

    async function copyPacket() {
        if (!currentPacket) {
            return false;
        }
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(currentPacket);
            return true;
        }
        packetOutput.focus();
        packetOutput.select();
        return document.execCommand("copy");
    }

    function downloadPacket() {
        if (!currentPacket) {
            return;
        }
        const blob = new Blob([currentPacket], { type: "text/markdown" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = currentFilename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
    }

    function issueBodyForPacket(submission, packet) {
        if (packet.length <= MAX_URL_BODY_CHARS) {
            return packet;
        }

        return [
            "## BookWriter Submission",
            "",
            `Submission ID: ${submission.submissionId}`,
            `Title: ${submission.title}`,
            `Kind: ${submission.kind}`,
            `Author: ${submission.author}`,
            "",
            "The full packet was copied from the Ragnarok BookWriter page. Paste it below before submitting.",
            "",
        ].join("\n");
    }

    form.addEventListener("submit", (event) => {
        const submission = collectSubmission();
        if (!submission.writing) {
            event.preventDefault();
            setStatus("Writing is required.");
            return;
        }

        currentPacket = buildPacket(submission);
        currentFilename = `${safeFilename(submission.title)}-${submission.submissionId}.md`;
        packetOutput.value = currentPacket;
        copyButton.disabled = false;
        downloadButton.disabled = false;
        saveSubmission(submission, currentPacket);
        issueTitleInput.value = `[BOOKWRITER] ${submission.kind}: ${submission.title}`;
        issueBodyInput.value = issueBodyForPacket(submission, currentPacket);
        issueLabelsInput.value = INTAKE_LABELS;
        copyPacket().catch(() => {});
        setStatus("Packet saved locally. Opening system intake.");
    });

    copyButton.addEventListener("click", async () => {
        try {
            await copyPacket();
            setStatus("Packet copied.");
        } catch {
            setStatus("Copy failed. Select the packet and copy manually.");
        }
    });

    downloadButton.addEventListener("click", () => {
        downloadPacket();
        setStatus("Packet downloaded.");
    });

    clearButton.addEventListener("click", () => {
        localStorage.removeItem(STORAGE_KEY);
        renderSaved();
        setStatus("Local queue cleared.");
    });

    renderSaved();
})();
