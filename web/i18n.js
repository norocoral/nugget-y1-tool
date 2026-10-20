/* i18n.js: English / Korean switcher (same engine as the landing site).
   Static text is swapped automatically. Messages sent by the installer
   (.dyn elements) are translated by app.js using the same list. */

const TRANSLATIONS = [
  [`File`, `파일`],
  [`Start over`, `처음부터 다시`],
  [`Quit`, `종료`],
  [`Help`, `도움말`],
  [`Nugget on GitHub`, `GitHub의 Nugget`],
  [`Get help`, `도움 받기`],

  [`Let's install Nugget on your Y1`, `Y1에 Nugget을 설치해 볼까요?`],
  [`It only takes a few minutes and we'll do the hard parts for you. All you need is your Y1 and its USB cable.`,
   `몇 분이면 끝나고, 어려운 부분은 저희가 알아서 해드려요. Y1과 USB 케이블만 준비하세요.`],
  [`Let's go`, `시작하기`],
  [`WARNING: Installing replaces the original software on your Y1. While extremely rare, it can cause the malfunction of the device. We are not responsible of the damage to your device. Only the Y1 TypeA device is supported.`,
   `주의: 설치하면 Y1의 기존 소프트웨어가 교체됩니다. 매우 드물지만 기기가 오작동할 수 있으며, 기기 손상에 대해서는 책임지지 않습니다. Y1 TypeA 기기만 지원합니다.`],

  [`Local mode`, `로컬 모드`],
  [`Local files`, `로컬 파일`],
  [`Select custom files to install instead of downloading from GitHub.`, `GitHub에서 다운로드하는 대신 설치할 커스텀 파일을 선택하세요.`],
  [`Boot image (.img) *`, `부팅 이미지 (.img) *`],
  [`Logo (.bin) [optional]`, `로고 파일 (.bin) [선택]`],
  [`Rockbox archive (.zip) *`, `Rockbox 압축 파일 (.zip) *`],
  [`Install from local files`, `로컬 파일로 설치하기`],
  [`Uploading files...`, `파일 업로드 중...`],
  [`Recovery`, `복구 모드`],
  [`Recovery mode`, `복구 모드`],
  [`Your Y1 is powered on in USB drive mode. Press the pinhole once to shut down.`, `Y1이 USB 드라이브 모드로 켜져 있어요. 핀홀을 한 번 눌러 전원을 꺼주세요.`],
  [`Repairing .rockbox (preserving your music)...`, `.rockbox 폴더를 복구하는 중이에요 (음악 파일은 안전하게 유지됩니다)...`],
  [`Recovery complete! Your .rockbox installation has been repaired.`, `복구가 끝났어요! 음악 파일은 그대로 두고 .rockbox를 복구했어요.`],

  [`Put your Y1 in Download mode`, `Y1을 다운로드 모드로 바꿔 주세요`],
  [`Turn it off`, `전원 끄기`],
  [`Make sure your Y1 is completely off and unplugged.`, `Y1이 완전히 꺼져 있고 케이블이 빠져 있는지 확인하세요.`],
  [`Press the pinhole once`, `핀홀 한 번 누르기`],
  [`Press the pinhole on the bottom of your Y1 once with a pin or paperclip. You don't need to hold it.`, `Y1 아래쪽의 핀홀을 핀이나 클립으로 한 번 누르세요. 계속 누르고 있을 필요는 없어요.`],
  [`Connect the USB cable to your computer. The installer takes it from there.`, `USB 케이블을 컴퓨터에 연결하세요. 나머지는 설치 프로그램이 알아서 해요.`],
  [`Plug it in`, `케이블 연결하기`],
  [`Please don't unplug your Y1 while it's installing.`, `설치하는 동안에는 Y1의 케이블을 뽑지 마세요.`],
  [`Y1 spotted. Connecting`, `Y1을 찾았어요. 연결하는 중이에요`],

  [`Turn your Y1 on and plug it back in`, `Y1을 켜고 다시 연결해 주세요`],
  [`Nugget is installed and your Y1 has switched itself off.`, `Nugget 설치가 끝났고 Y1은 스스로 꺼졌어요.`],
  [`Unplug the cable`, `케이블 뽑기`],
  [`Disconnect your Y1 from the computer.`, `컴퓨터에서 Y1을 분리하세요.`],
  [`Turn it on`, `전원 켜기`],
  [`Press and hold the center button on your Y1 and wait for it to start up.`, `Y1의 중앙 버튼을 길게 누른 상태에서 전원이 켜질 때까지 기다리세요.`],
  [`Plug it in again`, `다시 연결하기`],
  [`When it asks you to connect to a computer, plug the USB cable back in.`, `컴퓨터에 연결하라는 화면이 나오면 USB 케이블을 다시 꽂아 주세요.`],
  [`Not showing up? If you can see your Y1 below, pick it.`, `나타나지 않나요? 아래에 Y1이 보이면 선택하세요.`],

  [`Y1 connected. Preparing flash...`, `Y1이 연결되었어요. 플래시 준비 중...`],
  [`Connecting to Download Agent...`, `다운로드 에이전트에 연결하는 중이에요...`],
  [`DA connected. Initializing flash...`, `DA 연결 완료. 플래시 초기화 중...`],
  [`Flashing Nugget boot & logo...`, `Nugget 부팅 이미지와 로고를 설치하고 있어요...`],
  [`Flashing complete!`, `플래시 설치 완료!`],

  [`Adding the finishing touches`, `마무리하는 중이에요`],
  [`We're putting everything Nugget needs onto your Y1. This can take a few minutes.`, `Nugget에 필요한 모든 파일을 Y1에 넣고 있어요. 몇 분 걸릴 수 있어요.`],
  [`Please don't unplug your Y1 while files are copying.`, `파일을 복사하는 동안에는 Y1의 케이블을 뽑지 마세요.`],
  [`You're all set!`, `모든 준비가 끝났어요!`],
  [`Safely eject your Y1, unplug it and turn it on. Welcome to Nugget.`, `Y1을 안전하게 제거한 뒤 케이블을 뽑고 전원을 켜세요. Nugget에 오신 것을 환영해요.`],
  [`Close`, `닫기`],
  [`Something went wrong`, `문제가 생겼어요`],
  [`Try again`, `다시 시도`],

  /* Messages sent by the installer */
  [`Getting things ready`, `준비하는 중이에요`],
  [`Waiting for your Y1`, `Y1을 기다리는 중이에요`],
  [`Y1 found. Installing Nugget, please don't unplug it.`, `Y1을 찾았어요. Nugget을 설치하는 중이니 케이블을 뽑지 마세요.`],
  [`Installing Nugget`, `Nugget을 설치하는 중이에요`],
  [`Waiting for your Y1 to show up as a drive`, `Y1이 드라이브로 나타나기를 기다리는 중이에요`],
  [`Copying Nugget to your Y1`, `Y1에 Nugget을 복사하는 중이에요`],
  [`We couldn't download Nugget. Check your internet connection and try again.`, `Nugget을 다운로드하지 못했어요. 인터넷 연결을 확인하고 다시 시도해 주세요.`],
  [`Some installer files are missing. Please download the installer again.`, `설치 프로그램 파일 일부가 없어요. 설치 프로그램을 다시 다운로드해 주세요.`],
  [`The installation didn't finish. Unplug your Y1 and try again.`, `설치가 끝나지 않았어요. Y1을 분리하고 다시 시도해 주세요.`],
  [`We couldn't copy the files. Make sure your Y1 is still connected and try again.`, `파일을 복사하지 못했어요. Y1이 연결되어 있는지 확인하고 다시 시도해 주세요.`],
  [`You can close this tab now.`, `이제 이 탭을 닫아도 돼요.`],
];

const KO_META = {
  title: `Y1용 Nugget 설치 프로그램`,
  description: `몇 단계만으로 Innioasis Y1에 Nugget을 설치하세요.`,
};

/* =========================================================
   Engine. You shouldn't need to edit below this line.
   ========================================================= */

const SKIP = "script, style, pre, .titlebar, .meter-fill, .dyn";
const norm = (s) => s.replace(/\s+/g, " ").trim();
const dict = new Map(TRANSLATIONS.map(([en, ko]) => [norm(en), ko]));
const originals = new Map();
const metaDesc = document.querySelector('meta[name="description"]');
const englishMeta = { title: document.title, description: metaDesc ? metaDesc.content : "" };
const langBtn = document.getElementById("langBtn");

/* Finds the innermost elements whose full text matches an English entry. */
function findMatches(el, found) {
  if (el.matches(SKIP)) return false;
  let childMatched = false;
  for (const child of el.children) {
    if (findMatches(child, found)) childMatched = true;
  }
  if (childMatched) return true;
  const key = norm(el.textContent);
  if (dict.has(key)) { found.push([el, key]); return true; }
  return false;
}

function applyLanguage(lang) {
  document.documentElement.lang = lang;

  /* Put the English back first */
  originals.forEach((html, el) => { el.innerHTML = html; });
  originals.clear();
  document.title = englishMeta.title;
  if (metaDesc) metaDesc.content = englishMeta.description;

  if (lang === "ko") {
    const found = [];
    findMatches(document.querySelector(".page"), found);
    for (const [el, key] of found) {
      const hrefs = [...el.querySelectorAll("a")].map((a) => a.getAttribute("href"));
      originals.set(el, el.innerHTML);
      el.innerHTML = dict.get(key);
      el.querySelectorAll("a").forEach((a, i) => { if (hrefs[i]) a.setAttribute("href", hrefs[i]); });
    }
    document.title = KO_META.title;
    if (metaDesc) metaDesc.content = KO_META.description;
    if (location.search.includes("i18n=debug")) reportMissing();
  }

  if (langBtn) {
    langBtn.textContent = lang === "ko" ? "English" : "한국어";
    langBtn.lang = lang === "ko" ? "en" : "ko";
    langBtn.setAttribute("aria-label", lang === "ko" ? "Switch to English" : "한국어로 보기");
  }
  try { localStorage.setItem("lang", lang); } catch (e) {}
}

/* Debug helper: lists English text blocks that have no translation */
function reportMissing() {
  const done = [...originals.keys()];
  document.querySelectorAll(".page p, .page h1, .page h2, .page h3, .page li, .page summary, .page td, .page th, .page .btn").forEach((el) => {
    if (el.closest(SKIP)) return;
    if (done.some((t) => t === el || t.contains(el) || el.contains(t))) return;
    const text = norm(el.textContent);
    if (/[A-Za-z]{3,}/.test(text)) console.info("[i18n] missing:", text);
  });
}

function startLanguage() {
  let saved = null;
  try { saved = localStorage.getItem("lang"); } catch (e) {}
  const fallback = (navigator.language || "").toLowerCase().startsWith("ko") ? "ko" : "en";
  applyLanguage(saved || fallback);
}

if (langBtn) {
  langBtn.addEventListener("click", () => {
    applyLanguage(document.documentElement.lang === "ko" ? "en" : "ko");
  });
}
startLanguage();