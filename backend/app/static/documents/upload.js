function showTab(tab) {
    document.getElementById("resultTab").style.display =
        tab === "result" ? "block" : "none";

    document.getElementById("logsContainer").style.display =
        tab === "logs" ? "block" : "none";

    if (tab === "logs") {
        document.getElementById("log_uploaded_by").value =
            document.getElementById("uploaded_by").value;

        document.getElementById("log_uploaded_by").disabled = true;
        loadLogs();
    }
}

document.getElementById("uploadForm").addEventListener("submit", async function(event) {
    event.preventDefault();

    const form = document.getElementById("uploadForm");
    const formData = new FormData(form);

    const resultTab = document.getElementById("resultTab");
    resultTab.innerHTML = "Uploading...";

    try {
        const response = await fetch("/documents/upload", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (response.ok) {
            resultTab.innerHTML =
                "<div class='success'>SUCCESS</div><br>" +
                "<pre>" + escapeHtml(JSON.stringify(data, null, 2)) + "</pre>";
        } else {
            resultTab.innerHTML =
                "<div class='error'>FAILED</div><br>" +
                "<pre>" + escapeHtml(JSON.stringify(data, null, 2)) + "</pre>";
        }

        showTab("result");
    } catch (error) {
        resultTab.innerHTML =
            "<div class='error'>FAILED</div><br>" +
            escapeHtml(String(error));
    }
});

async function loadLogs() {
    const uploadedBy = document.getElementById("log_uploaded_by").value;
    const correlationId = document.getElementById("log_correlation_id").value;
    const jobId = document.getElementById("log_job_id").value;
    const documentId = document.getElementById("log_document_id").value;
    const level = document.getElementById("log_level").value;

    const params = new URLSearchParams();

    if (uploadedBy) params.append("uploaded_by", uploadedBy);
    if (correlationId) params.append("correlation_id", correlationId);
    if (jobId) params.append("job_id", jobId);
    if (documentId) params.append("document_id", documentId);
    if (level) params.append("level", level);

    const response = await fetch("/documents/logs?" + params.toString());
    const data = await response.json();

    const logHtml = data.logs.map(line => {
        const lower = line.toLowerCase();

        if (
            lower.includes("level=error") ||
            lower.includes("failed") ||
            lower.includes("failure") ||
            lower.includes("exception") ||
            lower.includes("virus detected") ||
            lower.includes("malware")
        ) {
            return "<div style='color:red; font-weight:bold;'>" + escapeHtml(line) + "</div>";
        }

        if (lower.includes("level=warn") || lower.includes("duplicate")) {
            return "<div style='color:orange; font-weight:bold;'>" + escapeHtml(line) + "</div>";
        }

        return "<div style='color:#00ff66;'>" + escapeHtml(line) + "</div>";
    }).join("");

    document.getElementById("logsTab").innerHTML =
        "<b>Total Logs: " + data.count + "</b><br><br>" + logHtml;
}

function escapeHtml(text) {
    return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;");
}