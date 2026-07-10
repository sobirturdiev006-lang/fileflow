(function () {
    const API_BASE = window.FILEFLOW_API_BASE; // masalan "/api/jobs/"
    const STORAGE_KEY = "fileflow_job_ids";
    const POLL_INTERVAL_MS = 3000;

    const form = document.getElementById("upload-form");
    const submitBtn = document.getElementById("submit-btn");
    const errorEl = document.getElementById("form-error");
    const tbody = document.getElementById("jobs-tbody");
    const refreshBtn = document.getElementById("refresh-btn");
    const jobTypeSelect = document.getElementById("job_type");
    const dedupRow = document.getElementById("dedup-row");

    let pollTimer = null;

    // --- localStorage bilan job id'larni saqlash (auth yo'q, shu sababli) ---
    function getStoredJobIds() {
        try {
            return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
        } catch {
            return [];
        }
    }

    function addStoredJobId(id) {
        const ids = getStoredJobIds();
        if (!ids.includes(id)) {
            ids.unshift(id);
            localStorage.setItem(STORAGE_KEY, JSON.stringify(ids.slice(0, 50)));
        }
    }

    // --- UI yordamchilari ---
    function jobTypeLabel(type) {
        const map = {
            excel_clean: "Excel tozalash",
            excel_to_pdf: "Excel → PDF",
            pdf_table_extract: "PDF → Excel",
            docx_to_pdf: "Word → PDF",
            pdf_text_extract: "PDF → Word",
        };
        return map[type] || type;
    }

    function statusLabel(status) {
        const map = {
            pending: "Kutilmoqda",
            processing: "Qayta ishlanmoqda",
            done: "Tayyor",
            failed: "Xatolik",
        };
        return map[status] || status;
    }

    function formatDate(iso) {
        const d = new Date(iso);
        return d.toLocaleString("uz-UZ", { dateStyle: "short", timeStyle: "short" });
    }

    function renderJobs(jobs) {
        if (!jobs.length) {
            tbody.innerHTML = `<tr><td colspan="4" class="muted">Hozircha job yo'q. Yuqorida fayl yuklang.</td></tr>`;
            return;
        }

        tbody.innerHTML = jobs.map((job) => {
            const resultCell = job.status === "done" && job.result_file
                ? `<a class="download-link" href="${job.result_file}" target="_blank">Yuklab olish</a>`
                : job.status === "failed"
                    ? `<span class="muted" title="${escapeHtml(job.error_message || "")}">Xato tafsiloti</span>`
                    : "—";

            return `
                <tr data-job-id="${job.id}">
                    <td>${jobTypeLabel(job.job_type)}</td>
                    <td><span class="badge badge--${job.status}">${statusLabel(job.status)}</span></td>
                    <td>${formatDate(job.created_at)}</td>
                    <td>${resultCell}</td>
                </tr>
            `;
        }).join("");
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }

    // --- API chaqiruvlari ---
    async function fetchJob(id) {
        const res = await fetch(`${API_BASE}${id}/`);
        if (!res.ok) throw new Error("Job topilmadi");
        return res.json();
    }

    async function refreshJobsList() {
        const ids = getStoredJobIds();
        if (!ids.length) {
            renderJobs([]);
            return;
        }
        const jobs = await Promise.all(
            ids.map((id) => fetchJob(id).catch(() => null))
        );
        renderJobs(jobs.filter(Boolean));
    }

    function startPolling() {
        if (pollTimer) clearInterval(pollTimer);
        pollTimer = setInterval(() => {
            const ids = getStoredJobIds();
            const hasActive = ids.length > 0; // soddalashtirilgan: faqat bor-yo'qligini tekshiramiz
            if (hasActive) refreshJobsList();
        }, POLL_INTERVAL_MS);
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
        return null;
    }

    // --- dedup ustun maydonini faqat excel_clean uchun ko'rsatish ---
    function toggleDedupRow() {
        dedupRow.style.display = jobTypeSelect.value === "excel_clean" ? "" : "none";
    }
    jobTypeSelect.addEventListener("change", toggleDedupRow);
    toggleDedupRow();

    // --- forma yuborish ---
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorEl.textContent = "";
        submitBtn.disabled = true;
        submitBtn.textContent = "Yuborilmoqda...";

        try {
            const fileInput = document.getElementById("input_file");
            const dedupInput = document.getElementById("dedup_columns");

            const formData = new FormData();
            formData.append("job_type", jobTypeSelect.value);
            formData.append("input_file", fileInput.files[0]);

            if (jobTypeSelect.value === "excel_clean" && dedupInput.value.trim()) {
                const cols = dedupInput.value.split(",").map((c) => c.trim()).filter(Boolean);
                formData.append("options", JSON.stringify({ dedup_columns: cols }));
            }

            const csrftoken = getCookie("csrftoken");
            const headers = {};
            if (csrftoken) headers["X-CSRFToken"] = csrftoken;

            const res = await fetch(API_BASE, {
                method: "POST",
                body: formData,
                headers,
            });

            if (!res.ok) {
                const data = await res.json().catch(() => ({}));
                throw new Error(data.input_file?.[0] || data.detail || "Yuklashda xatolik yuz berdi.");
            }

            const job = await res.json();
            addStoredJobId(job.id);
            form.reset();
            toggleDedupRow();
            await refreshJobsList();
        } catch (err) {
            errorEl.textContent = err.message;
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = "Yuborish";
        }
    });

    refreshBtn.addEventListener("click", refreshJobsList);

    // --- ishga tushirish ---
    refreshJobsList();
    startPolling();
})();