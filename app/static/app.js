(() => {
  const $ = (sel) => document.querySelector(sel);
  const $$ = (sel) => [...document.querySelectorAll(sel)];

  let lastResults = [];
  let lastCounts = {};
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
    let rows;
    if (filter === "gaps") {
      rows = [...lastResults].sort(
        (a, b) => Number(!!b.unmapped) - Number(!!a.unmapped)
      );
    } else {
      rows = lastResults.filter((r) => {
        if (filter === "mapped") return !r.unmapped;
        if (filter === "unmapped") return r.unmapped;
        return true;
      });
    }
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
    lastCounts = doc.counts || {};
    $("#resultsSection").hidden = false;
    renderMetrics(lastCounts);
    renderResults();
    const has = lastResults.length > 0;
    $("#downloadCsv").disabled = !has;
    $("#downloadJson").disabled = !has;
  }

  function coverageRows() {
    return lastResults.map((r) => {
      const m = r.matches?.[0];
      const msi = r.msi_coverage || m?.msi_coverage || [];
      const msiStr = Array.isArray(msi)
        ? msi.map((x) => `${x.family || x.product_id || ""}:${x.support_level || ""}`).join("; ")
        : "";
      return {
        requirement: r.requirement || "",
        page: r.page ?? "",
        mapped: !r.unmapped,
        capability_id: m?.capability_id || "",
        capability_alias: m?.capability_alias || "",
        capability_name: m?.capability_name || "",
        confidence: m?.confidence ?? "",
        method: m?.method || "",
        msi_coverage: msiStr,
      };
    });
  }

  function downloadBlob(filename, text, mime) {
    const blob = new Blob([text], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }

  function toCsv(rows) {
    const fields = [
      "requirement",
      "page",
      "mapped",
      "capability_id",
      "capability_alias",
      "capability_name",
      "confidence",
      "method",
      "msi_coverage",
    ];
    const esc = (v) => `"${String(v ?? "").replaceAll('"', '""')}"`;
    const lines = [fields.join(",")];
    for (const row of rows) {
      lines.push(fields.map((f) => esc(row[f])).join(","));
    }
    return lines.join("\n");
  }

  $("#downloadCsv")?.addEventListener("click", () => {
    downloadBlob("psers-coverage.csv", toCsv(coverageRows()), "text/csv;charset=utf-8");
  });
  $("#downloadJson")?.addEventListener("click", () => {
    const payload = { counts: lastCounts, rows: coverageRows() };
    downloadBlob(
      "psers-coverage.json",
      JSON.stringify(payload, null, 2),
      "application/json"
    );
  });

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
    await loadFixture("demo");
  });

  async function loadFixture(name) {
    try {
      const r = await fetch(`/api/demo/fixture?name=${encodeURIComponent(name)}`);
      if (!r.ok) throw new Error(await r.text());
      const j = await r.json();
      $("#textInput").value = j.text;
      setTab("paste");
      $("#runHint").textContent = `${j.filename} loaded — click Run match.`;
      document.getElementById("workspace")?.scrollIntoView({ behavior: "smooth" });
    } catch (e) {
      $("#runHint").textContent = `Fixture error: ${e.message || e}`;
    }
  }

  async function loadOntologySummary() {
    const metrics = $("#ontologyMetrics");
    const meta = $("#ontologyMeta");
    const grid = $("#stackGrid");
    if (!metrics) return;
    try {
      const r = await fetch("/api/ontology/summary");
      if (!r.ok) throw new Error(await r.text());
      const j = await r.json();
      const st = j.status || {};
      metrics.innerHTML = `
        <div class="metric"><b>${st.published ?? 0}</b><span>Published</span></div>
        <div class="metric"><b>${st.draft ?? 0}</b><span>Draft</span></div>
        <div class="metric"><b>${st.stub ?? 0}</b><span>Stub</span></div>
        <div class="metric"><b>${j.total ?? 0}</b><span>Total L1</span></div>
      `;
      if (meta) {
        meta.textContent = `schema ${j.schema_version || "—"} · sprint ${j.sprint || "—"}`;
      }
      if (grid) {
        const stacks = j.by_stack || {};
        grid.innerHTML = Object.entries(stacks)
          .map(
            ([k, n]) =>
              `<div class="stack-card"><b>${escapeHtml(String(n))}</b><span>${escapeHtml(k)}</span></div>`
          )
          .join("");
      }
      const mat = $("#maturityBody");
      if (mat) {
        const rows = (j.maturity || []).slice(0, 16);
        mat.innerHTML = rows
          .map(
            (r) => `<tr>
              <td>${escapeHtml(r.vertical)}</td>
              <td>${r.published ?? 0}</td>
              <td>${r.draft ?? 0}</td>
              <td>${r.total ?? 0}</td>
            </tr>`
          )
          .join("");
      }
    } catch {
      if (meta) meta.textContent = "Ontology summary unavailable (is the API up?)";
    }
  }

  function jumpToPaste() {
    setTab("paste");
    document.getElementById("workspace")?.scrollIntoView({ behavior: "smooth" });
  }

  $("#loadIncidentDemo")?.addEventListener("click", () => loadFixture("incident"));
  $("#loadIncidentDemo2")?.addEventListener("click", () => loadFixture("incident"));
  $("#loadMcxDemo")?.addEventListener("click", () => loadFixture("mcx"));
  $("#loadMcxDemo2")?.addEventListener("click", () => loadFixture("mcx"));
  $("#loadFullstackDemo")?.addEventListener("click", () => loadFixture("fullstack"));
  $("#loadFullstackDemo2")?.addEventListener("click", () => loadFixture("fullstack"));
  $("#jumpPaste")?.addEventListener("click", jumpToPaste);

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
      const j = await r.json();
      if (action === "reject") {
        $("#fbStatus").textContent = "Saved reject (audit only — not queued for L2 publish).";
      } else {
        $("#fbStatus").textContent = `Saved ${action}; queued for L2 publish.`;
      }
      if (j.queued?.status) {
        $("#fbStatus").textContent += ` [${j.queued.status}]`;
      }
      $("#fbNote").value = "";
      loadQueue();
    } catch (err) {
      $("#fbStatus").textContent = `Save failed: ${err.message || err}`;
    }
  });

  async function loadQueue() {
    try {
      const r = await fetch("/api/review-queue");
      if (!r.ok) throw new Error(await r.text());
      const j = await r.json();
      const c = j.counts || {};
      $("#queueCounts").textContent =
        `Pending ${c.pending || 0} · Published ${c.published || 0} · Rejected ${c.rejected || 0}`;
      const items = j.items || [];
      $("#queueBody").innerHTML = items.length
        ? items
            .map(
              (it) => `<tr>
                <td><span class="queue-status ${escapeAttr(it.status || "pending")}">${escapeHtml(it.status || "pending")}</span></td>
                <td>${escapeHtml(it.action || "")}</td>
                <td class="req">${escapeHtml(it.phrase || "")}</td>
                <td><span class="alias">${escapeHtml(it.capability_alias || it.capability_id || "")}</span></td>
              </tr>`
            )
            .join("")
        : `<tr><td colspan="4" class="hint">Queue empty.</td></tr>`;
    } catch (e) {
      $("#queueCounts").textContent = `Queue load failed: ${e.message || e}`;
    }
  }

  async function runPublish(dryRun) {
    $("#queuePublishStatus").textContent = dryRun ? "Dry-run…" : "Publishing…";
    try {
      const r = await fetch(`/api/review-queue/publish?dry_run=${dryRun ? "true" : "false"}`, {
        method: "POST",
      });
      if (!r.ok) throw new Error(await r.text());
      const j = await r.json();
      const s = j.summary || {};
      $("#queuePublishStatus").textContent =
        `${dryRun ? "Dry-run" : "Published"}: added=${s.added ?? 0}, dup=${s.skipped_dup ?? 0}, ` +
        `reject=${s.skipped_reject ?? 0}, already=${s.skipped_published ?? 0}`;
      if (!dryRun) await loadQueue();
    } catch (e) {
      $("#queuePublishStatus").textContent = `Publish failed: ${e.message || e}`;
    }
  }

  $("#refreshQueue").addEventListener("click", () => loadQueue());
  $("#dryPublishQueue").addEventListener("click", () => runPublish(true));
  $("#publishQueue").addEventListener("click", () => runPublish(false));

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
  loadQueue();
  loadOntologySummary();
})();
