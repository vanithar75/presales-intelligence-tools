(() => {
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => [...document.querySelectorAll(sel)];

  let lastResults = [];
  let filter = "all";
  let selectedFile = null;

  async function checkHealth() {
    try {
      const r = await fetch("/health");
      const j = await r.json();
      $("#healthStatus").textContent = `API ${j.status} · ${j.sprint}`;
    } catch {
      $("#healthStatus").textContent = "API offline — start uvicorn";
    }
  }

  function setTab(name) {
    $$(".tab").forEach((t) => {
      const on = t.dataset.tab === name;
      t.classList.toggle("active", on);
      t.setAttribute("aria-selected", on ? "true" : "false");
    });
    $("#pane-upload").classList.toggle("hidden", name !== "upload");
    $("#pane-paste").classList.toggle("hidden", name !== "paste");
  }

  $$(".tab").forEach((t) => t.addEventListener("click", () => setTab(t.dataset.tab)));

  const drop = $("#dropZone");
  const pdfInput = $("#pdfInput");
  drop.addEventListener("click", () => pdfInput.click());
  drop.addEventListener("dragover", (e) => {
    e.preventDefault();
    drop.classList.add("drag");
  });
  drop.addEventListener("dragleave", () => drop.classList.remove("drag"));
  drop.addEventListener("drop", (e) => {
    e.preventDefault();
    drop.classList.remove("drag");
    if (e.dataTransfer.files?.[0]) setFile(e.dataTransfer.files[0]);
  });
  pdfInput.addEventListener("change", () => {
    if (pdfInput.files?.[0]) setFile(pdfInput.files[0]);
  });

  function setFile(file) {
    selectedFile = file;
    $("#fileName").textContent = file.name;
    $("#runPdf").disabled = false;
  }

  function renderMetrics(counts) {
    $("#summaryPanel").hidden = false;
    $("#metrics").innerHTML = `
      <div class="metric"><b>${counts.requirements}</b><span>Requirements</span></div>
      <div class="metric"><b>${counts.mapped}</b><span>Mapped</span></div>
      <div class="metric"><b>${counts.unmapped}</b><span>Unmapped</span></div>
      <div class="metric"><b>${Math.round((counts.map_rate || 0) * 100)}%</b><span>Map rate</span></div>
    `;
  }

  function renderResults() {
    const body = $("#resultsBody");
    const rows = lastResults.filter((r) => {
      if (filter === "mapped") return !r.unmapped;
      if (filter === "unmapped") return r.unmapped;
      return true;
    });
    body.innerHTML = rows
      .map((r) => {
        const m = r.matches?.[0];
        const cap = r.unmapped
          ? `<span class="cap">UNMAPPED</span>`
          : `<span class="cap">${escapeHtml(m.capability_name)}</span><span class="alias">${escapeHtml(m.capability_alias || m.capability_id)}</span>`;
        const conf = r.unmapped ? "—" : m.confidence;
        const page = r.page ? `p${r.page} · ` : "";
        return `<tr class="${r.unmapped ? "unmapped" : ""}">
          <td class="req">${page}${escapeHtml(r.requirement)}</td>
          <td>${cap}</td>
          <td class="conf">${conf}</td>
          <td><button type="button" class="linkish" data-phrase="${escapeAttr(r.requirement)}" data-cap="${escapeAttr(m?.capability_id || "")}">Feedback</button></td>
        </tr>`;
      })
      .join("");

    body.querySelectorAll("[data-phrase]").forEach((btn) => {
      btn.addEventListener("click", () => {
        $("#fbPhrase").value = btn.dataset.phrase;
        $("#fbCap").value = btn.dataset.cap || "";
        $("#fbStatus").textContent = "Ready to save feedback for this phrase.";
      });
    });

    const msiMap = new Map();
    lastResults.forEach((r) => {
      (r.msi_coverage || []).forEach((m) => {
        const key = `${m.product_id}|${m.capability_id}`;
        if (!msiMap.has(key)) msiMap.set(key, m);
      });
    });
    const msi = [...msiMap.values()];
    $("#msiBody").innerHTML = msi.length
      ? msi
          .slice(0, 40)
          .map(
            (m) => `<div class="msi-card">
              <strong>${escapeHtml(m.product_name || m.product_id)}</strong>
              <span>${escapeHtml(m.family || "")} · ${escapeHtml(m.capability_id)}</span>
              <div class="badge ${escapeAttr(m.support_level)}">${escapeHtml(m.support_level)}</div>
            </div>`
          )
          .join("")
      : `<p class="hint">No MSI coverage rows for current matches.</p>`;
  }

  function escapeHtml(s) {
    return String(s || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }
  function escapeAttr(s) {
    return escapeHtml(s).replaceAll("'", "&#39;");
  }

  function showDoc(doc) {
    lastResults = doc.results || [];
    $("#resultsSection").hidden = false;
    renderMetrics(doc.counts || {});
    renderResults();
  }

  $$(".chip").forEach((c) =>
    c.addEventListener("click", () => {
      $$(".chip").forEach((x) => x.classList.remove("active"));
      c.classList.add("active");
      filter = c.dataset.filter;
      renderResults();
    })
  );

  $("#runPdf").addEventListener("click", async () => {
    if (!selectedFile) return;
    $("#runHint").textContent = "Matching PDF…";
    const fd = new FormData();
    fd.append("file", selectedFile);
    const maxPages = $("#maxPages").value || 20;
    try {
      const r = await fetch(`/api/match/pdf?max_pages=${encodeURIComponent(maxPages)}`, {
        method: "POST",
        body: fd,
      });
      if (!r.ok) throw new Error(await r.text());
      const doc = await r.json();
      showDoc(doc);
      $("#runHint").textContent = `Done · ${doc.source_file || selectedFile.name}`;
    } catch (e) {
      $("#runHint").textContent = `Error: ${e.message || e}`;
    }
  });

  $("#runText").addEventListener("click", async () => {
    const text = $("#textInput").value.trim();
    if (text.length < 10) {
      $("#runHint").textContent = "Paste at least a short requirement.";
      return;
    }
    $("#runHint").textContent = "Matching text…";
    try {
      const r = await fetch("/api/match/text", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, top_k: 3 }),
      });
      if (!r.ok) throw new Error(await r.text());
      const doc = await r.json();
      showDoc(doc);
      $("#runHint").textContent = "Done · pasted text";
    } catch (e) {
      $("#runHint").textContent = `Error: ${e.message || e}`;
    }
  });

  $("#loadDemo").addEventListener("click", async () => {
    const r = await fetch("/api/demo/fixture");
    const j = await r.json();
    $("#textInput").value = j.text;
    setTab("paste");
    $("#runHint").textContent = "Demo fixture loaded — click Run match.";
  });

  $("#feedbackForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const action = e.submitter?.dataset?.action || "accept";
    const payload = {
      phrase: $("#fbPhrase").value.trim(),
      capability_id: $("#fbCap").value.trim(),
      note: $("#fbNote").value.trim(),
      action,
    };
    try {
      const r = await fetch("/api/feedback/synonym", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!r.ok) throw new Error(await r.text());
      $("#fbStatus").textContent = `Saved ${action} feedback.`;
      $("#fbNote").value = "";
    } catch (err) {
      $("#fbStatus").textContent = `Save failed: ${err.message || err}`;
    }
  });

  // preload capability datalist (lightweight)
  fetch("/api/capabilities?limit=200")
    .then((r) => r.json())
    .then((j) => {
      $("#capList").innerHTML = (j.capabilities || [])
        .map((c) => `<option value="${escapeAttr(c.id)}">${escapeHtml(c.alias || c.name)}</option>`)
        .join("");
    })
    .catch(() => {});

  checkHealth();
})();
