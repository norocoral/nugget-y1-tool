const $ = (s) => document.querySelector(s);
const pages = [...document.querySelectorAll(".step-page")];
const dots = [...document.querySelectorAll("#pager i")];
const tr = (s) => (document.documentElement.lang === "ko" && dict.get(norm(s))) || s;
const post = (path, body = {}) => fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });

let last = null, waitSince = 0;

function pageFor(s) {
  if (s.stage === "error") return (s.step === "copy" || s.step === "recovery") ? 4 : 2;
  // Map recovering stage to Page 4 alongside copying
  return { prep: 2, waiting: 2, flashing: 2, waiting_drive: 3, copying: 4, recovering: 4, done: 4 }[s.stage] || 1;
}

function setBar(id, pct) {
  const bar = $(id);
  if (!bar) return;
  bar.style.setProperty("--fill", pct + "%");
  bar.textContent = pct > 0 ? pct + "%" : "";
}

function render(s) {
  if (!s) return;
  last = s;
  const n = pageFor(s);
  pages.forEach((p, i) => p.classList.toggle("on", i === n - 1));
  dots.forEach((d, i) => { d.className = i === n - 1 ? "on" : i < n - 1 ? "past" : ""; });

  const err = s.stage === "error";
  $("#error").classList.toggle("hidden", !err);
  if (err) $("#errText").textContent = tr(s.error);
  const msg = err ? "" : tr(s.message);
  $("#st2").textContent = msg; $("#st3").textContent = msg; $("#st4").textContent = msg;
  setBar("#bar2", n === 2 && s.stage !== "waiting" ? s.progress : 0);
  setBar("#bar4", n === 4 ? s.progress : 0);

  const done = s.stage === "done";
  $("#copying").classList.toggle("hidden", done);
  $("#done").classList.toggle("hidden", !done);

  if (s.stage === "waiting_drive") {
    waitSince = waitSince || Date.now();
    const show = Date.now() - waitSince > 45000 && s.drives.length;
    $("#pick").classList.toggle("hidden", !show);
    $("#picks").replaceChildren(...s.drives.map((d) => {
      const b = document.createElement("button");
      b.className = "btn btn-alt"; b.textContent = d.label;
      b.onclick = () => post("/api/copy", { path: d.path });
      return b;
    }));
  } else waitSince = 0;
}

async function poll() {
  try { render(await (await fetch("/api/state")).json()); } catch (e) {}
}

// Main Flow Controls
$("#goBtn").onclick = async () => { await post("/api/start"); poll(); };
$("#retryBtn").onclick = async () => { await post("/api/retry"); poll(); };
$("#mRestart").onclick = async () => { await post("/api/reset"); location.reload(); };

// Recovery Mode Control (from File Menu)
const mRec = $("#mRecovery");
if (mRec) {
  mRec.onclick = async () => {
    document.querySelectorAll(".menu.open").forEach((x) => x.classList.remove("open"));
    await post("/api/recovery");
    poll();
  };
}

// Local Mode Controls
const localToggle = $("#localToggleBtn");
if (localToggle) {
  localToggle.onclick = (e) => {
    e.stopPropagation();
    document.querySelectorAll(".menu.open").forEach((x) => x.classList.remove("open"));
    // Ensure Page 1 is displayed and show the card
    pages.forEach((p, i) => p.classList.toggle("on", i === 0));
    const card = $("#localCard");
    card.classList.toggle("hidden");
    if (!card.classList.contains("hidden")) {
      card.scrollIntoView({ behavior: "smooth" });
    }
  };
}

async function uploadLocalFile(type, file) {
  if (!file) return;
  await fetch(`/api/upload?type=${type}&name=${encodeURIComponent(file.name)}`, {
    method: "POST",
    body: file
  });
}

const startLocal = $("#startLocalBtn");
if (startLocal) {
  startLocal.onclick = async () => {
    const bootF = $("#bootFile").files[0];
    const logoF = $("#logoFile").files[0];
    const zipF = $("#zipFile").files[0];

    if (!bootF || !zipF) {
      alert(tr("Please select both a boot image (.img) and a Rockbox zip (.zip)."));
      return;
    }

    startLocal.disabled = true;
    startLocal.textContent = tr("Uploading files...");

    await uploadLocalFile("boot", bootF);
    if (logoF) await uploadLocalFile("logo", logoF);
    await uploadLocalFile("zip", zipF);

    await post("/api/start_local");
    poll();
  };
}

const quit = async () => {
  await post("/api/quit");
  document.body.innerHTML = `<p class="lead" style="text-align:center;margin-top:30vh">${tr("You can close this tab now.")}</p>`;
};
$("#mQuit").onclick = quit;
$("#closeBtn").onclick = quit;

// Menubar Dropdown Handling
document.querySelectorAll(".menu > .menu-btn").forEach((b) =>
  b.addEventListener("click", (e) => {
    e.stopPropagation();
    const m = b.parentElement, open = m.classList.contains("open");
    document.querySelectorAll(".menu.open").forEach((x) => x.classList.remove("open"));
    if (!open) m.classList.add("open");
  }));
document.addEventListener("click", () => document.querySelectorAll(".menu.open").forEach((x) => x.classList.remove("open")));
langBtn.addEventListener("click", () => setTimeout(() => render(last), 0));

poll();
setInterval(poll, 1000);