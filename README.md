<p align="right">
  <a href="README.md"><img src="https://img.shields.io/badge/EN-English-0078D4?style=for-the-badge" alt="English"></a>
  &nbsp;
  <a href="README.ru.md"><img src="https://img.shields.io/badge/RU-Русский-CC0000?style=for-the-badge" alt="Русский"></a>
</p>

<p align="center">
  <img src="assets/logo.png" width="140" alt="Job Hunter AI Logo">
</p>

<h1 align="center">Job Hunter AI</h1>

<p align="center">
  <strong>Your personal AI recruiter — one hotkey, any browser, zero extensions</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3670A0?style=flat&logo=python&logoColor=ffdd54" alt="Python">
  <img src="https://img.shields.io/badge/Release-v3.1.1-00B981?style=flat" alt="Release">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-0078D4?style=flat&logo=linux&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-Non--Commercial-EF4444?style=flat" alt="License">
</p>

---

<p align="center">
<details>
<summary><b>▶️ Watch the demo</b></summary>
<br>

https://github.com/user-attachments/assets/ab707ab6-42a2-4939-bdd4-e7700fc2d999

</details>
</p>

---

**Job Hunter AI** is a standalone desktop app that analyzes job postings, ruthlessly filters out garbage (scams, MLM, 60 h/week slavery), and writes targeted cover letters — all triggered by a single global hotkey, in any browser, with zero additional software required.

**v3.0.0 dropped the Chrome extension entirely.** Press one key. The rest is automatic.

<br>

<table width="100%">
  <tr>
    <td width="60%" valign="top">
      <h3>⚡ Why this changes your routine</h3>
      <ul>
        <li>💰 <b>100% Free</b> — runs on your own API keys, including the free Gemini tier</li>
        <li>🔑 <b>One hotkey — any browser</b> — Chrome, Firefox, Edge, Brave, any site</li>
        <li>🛡️ <b>Hard filter up to 60%</b> — scam, MLM, toxic conditions, info-business don't get through</li>
        <li>✍️ <b>Cover letter in seconds</b> — personalized to the real pain points of the employer</li>
        <li>🌐 <b>Cloud or your PC</b> — Gemini, GPT-5, Claude 4, DeepSeek, OpenRouter <i>or</i> Ollama / LM Studio (offline)</li>
        <li>🔒 <b>Full privacy</b> — with local AI, nothing leaves your machine</li>
        <li>🌍 <b>EN / RU</b> — interface language = letter language and PDF resume parsing</li>
      </ul>
    </td>
    <td width="40%" align="center" valign="middle">
      <img src="assets/1.png" width="290" alt="Job Hunter AI Interface">
    </td>
  </tr>
</table>

<br>
<hr>

## ⚙️ Quick Start

> No Chrome extension. No Flask server. No port conflicts. Just run the app.

**1.** Download the latest release and launch **Job Hunter AI.exe** (Windows) or `job-hunter-ai` (Linux).

**2.** Open Settings → enter your AI provider API key.

**3.** Open any job posting in any browser.

**4.** Press **Ctrl+Shift+J** — the app selects all, copies the text, and submits it to the AI pipeline automatically.

**5.** A toast notification appears in ~15 seconds: accepted with a cover letter, or rejected with the reason.

The app lives in the **system tray** and runs silently in the background.

[![Installation Guide](https://img.shields.io/badge/⚙️_Setup-Full_installation_guide-00B981?style=for-the-badge&logo=readme)](install/INSTALL.md)

<hr>

<details>
<summary><b>✨ Full feature breakdown</b></summary>

<br>

<table width="100%">
  <tr>
    <td width="60%" valign="top">
      <b>🤖 BrowserCaptureEngine — works with any browser</b><br>
      A global hotkey listener (pynput) runs as a daemon thread. When triggered, it simulates Ctrl+A → Ctrl+C in the currently active browser window, reads the clipboard via pyperclip, and submits the text to the processing queue. Hardware Virtual Key codes (layout-independent) ensure the hotkey fires correctly on any keyboard layout — Cyrillic, QWERTY, Dvorak.
      <br><br>
      <b>🔲 System Tray — always on, never in the way</b><br>
      pystray hosts the app in the notification area. Right-click opens a context menu: show window, toggle active, exit. The main window can be hidden while the capture engine continues running.
    </td>
    <td width="40%" align="center" valign="middle">
      <img src="assets/2.png" width="320" alt="System Tray">
    </td>
  </tr>

  <tr>
    <td width="60%" valign="top">
      <b>🧠 Multi-engine AI cascade with Failover</b><br>
      Automatic switching between Gemini, GPT-5, Claude 4, DeepSeek, OpenRouter, and local models. If the primary provider is unavailable — the next one takes over without losing the task.
      <br><br>
      <b>🏠 Local AI — no internet, no API keys</b><br>
      Native HTTP integration with Ollama and LM Studio. A background probe monitors server availability and reflects status in the UI. <code>LOCAL_SAFE_PARAMS</code> compensate for artifacts in quantized 4-bit models.
    </td>
    <td width="40%" align="center" valign="middle">
      <img src="assets/3.png" width="227" alt="AI Cascade">
    </td>
  </tr>

  <tr>
    <td width="60%" valign="top">
      <b>🛡️ Two-stage AI analysis</b><br>
      <b>Stage 1 — Filter:</b> Detects scam, MLM, toxic work conditions (>45 h/week, uncompensated overtime, info-business, mass hiring). Plus geographic compliance — filters offers that prohibit remote work from your country.<br>
      <b>Stage 2 — Cover letter:</b> Only for approved listings. A targeted response addressing the employer's real requirements — no filler, no templates.
      <br><br>
      <b>📐 Scoring pipeline</b><br>
      <code>extract_relevant_context()</code> scores each paragraph by keyword density and length, greedily selects the most relevant content within a char budget, then restores document order (Narrative Rule) so the LLM reads chronological text, not a relevance-sorted shuffle.
    </td>
    <td width="40%" align="center" valign="middle">
      <img src="assets/4.png" width="267" alt="Analysis">
    </td>
  </tr>

  <tr>
    <td width="60%" valign="top">
      <b>📄 Resume history and PDF import</b><br>
      Save multiple resume versions and switch between them in one click. Direct PDF import with AI text extraction is supported.
      <br><br>
      <b>🔔 Thread-safe Telegram-style toasts</b><br>
      Animated notifications slide from the bottom of the screen, respect the taskbar height, and never block the interface. A new notification instantly replaces the old one without race conditions (<code>_notification_lock</code> + instance-bound fade closure). Audio plays in a dedicated daemon thread.
    </td>
    <td width="40%" align="center" valign="middle">
      <img src="assets/5.png" width="265" alt="Notifications">
    </td>
  </tr>
</table>

</details>

---

<details>
<summary>🗺️ Architecture diagram</summary>

```
 ┌──────────────────────────────────────────────────────────────────┐
 │           ANY JOB POSTING  ·  ANY BROWSER  ·  Ctrl+Shift+J      │
 └──────────────────────────────────┬───────────────────────────────┘
                                    │
                  ┌─────────────────▼─────────────────┐
                  │       BrowserCaptureEngine         │  jh_automation.py
                  │                                    │
                  │  pynput.keyboard.GlobalHotKeys      │  daemon thread
                  │  ① focus browser window            │
                  │  ② Ctrl+A  — select all            │  VK codes (layout-
                  │  ③ Ctrl+C  — copy to clipboard     │  independent):
                  │  ④ pyperclip.paste()               │  Win32 / X11 / macOS
                  │  ⑤ MD5 hash → dedup check          │
                  │  ⑥ queue.put(text, url)            │  Wayland guard:
                  │                                    │  PlatformSecurity-
                  │  AUTOMATION_AVAILABLE fallback      │  Exception +
                  │  for missing pynput/pyperclip       │  graceful degradation
                  └─────────────────┬─────────────────┘
                                    │ thread-safe queue
                  ┌─────────────────▼─────────────────┐
                  │           AI ENGINE                │  jh_ai_engine.py
                  │                                    │
                  │  extract_relevant_context()        │
                  │  ├─ normalize whitespace           │  Scoring:
                  │  ├─ drop nav-noise lines           │  keyword hits
                  │  ├─ score by _VACANCY_KW_RE        │  + len / 600 bonus
                  │  ├─ greedy budget select           │
                  │  ├─ Narrative Rule (doc order)     │  pack_paragraphs_
                  │  └─ pack_paragraphs_to_budget()    │  to_budget(): strict
                  │                                    │  delimiter-aware
                  │  Stage 1  12 000 chars  → Filter   │  budget invariant
                  │  Stage 2   8 000 chars  → Letter   │
                  │                                    │
                  │  Gemini → GPT-5 → Claude 4 →       │  Failover Chain
                  │  DeepSeek → OpenRouter →           │  Exp. Backoff
                  │  Ollama → LM Studio                │
                  │  5-level JSON repair pipeline      │
                  └──────────┬─────────────┬──────────┘
                    REJECTED │             │ APPROVED
                             │             ▼
                             │   ┌─────────────────────┐
                             │   │  Cover letter ready  │
                             │   └─────────┬───────────┘
                             │             │
                  ┌──────────▼─────────────▼──────────┐
                  │         STORAGE MANAGER            │  jh_storage_manager.py
                  │                                    │
                  │  _write_json_atomic()              │  Write-Copy-Replace:
                  │  mkstemp → dump → flush →          │  temp file on same
                  │  fsync → os.replace()              │  partition → atomic
                  │                                    │  at OS level
                  │  _file_lock  — disk I/O only       │
                  │  _url_lock   — set mutations only  │  O(1) dedup:
                  │  always-live _approved_urls /      │  no disk read
                  │  _rejected_urls (populated at      │  on hot path
                  │  startup)                          │
                  └─────────────────┬─────────────────┘
                                    │
                  ┌─────────────────▼─────────────────┐
                  │   DESKTOP UI  +  SYSTEM TRAY       │
                  │                                    │
                  │  CustomTkinter  ·  pystray          │
                  │  Toast: _notification_lock +        │
                  │  _fade_out_instance (instance-      │
                  │  bound closure, race-safe)          │
                  │  HiDPI · Dark Win32 title bar       │
                  │  EN / RU  (jh_i18n.py)             │
                  └────────────────────────────────────┘
```

</details>

---

<details>
<summary><b>🛠️ Tech Stack</b></summary>
<br>

| Layer | Tools |
|---|---|
| **GUI & Tray** | `customtkinter` · `pystray` · `Pillow` · `ctypes` Win32 API (dark title bar, `WM_SETICON`, DPI Awareness) |
| **Hotkey Capture** | `pynput.keyboard.GlobalHotKeys` · hardware VK codes (layout-independent) · `pyperclip` clipboard |
| **Platform Guard** | `PlatformSecurityException` · Wayland zero-trust guard · graceful degradation on unsupported sessions |
| **Localization** | `jh_i18n.py` — declarative EN/RU with `tr(key, **kwargs)` named variable substitution |
| **AI Cascade** | **Gemini 2.5** · **GPT-5 / o3** · **Claude 4** · **DeepSeek** (chat / reasoner) · **OpenRouter** (multi-vendor) · **Ollama** · **LM Studio** |
| **Scoring Pipeline** | `extract_relevant_context()` · `_VACANCY_KW_RE` keyword scoring · Narrative Rule · `pack_paragraphs_to_budget()` |
| **Resilience** | Failover Chain · Exponential Backoff · 5-level JSON repair · `AINetworkError` / `AITimeoutError` / `AIAuthError` / `AIRateLimitError` hierarchy |
| **Storage** | `_write_json_atomic()` Write-Copy-Replace + `fsync` · `_file_lock` + `_url_lock` · O(1) dedup · always-live URL sets |
| **Notifications** | `_notification_lock` + instance-bound `_fade_out_instance` · slide / fade animation · `winsound` in daemon thread |
| **Build** | `PyInstaller` · `build_exe.py` (Windows + Inno Setup) · `build_linux.py` (Linux X11) · `jh_version.py` (single version source) |

</details>

---

## 🚀 Changelog

<details open>
<summary><b>🟢 v3.1.1 — Hotfixes: tray restore, copy button, company extraction (Current)</b></summary>

<br>

> **Three targeted bug fixes on top of v3.1.**

* **[Fix]** Clicking a notification now reliably restores the window from the tray. `icon.stop()` inside `_bring_to_front` was unguarded — if pystray raised, the follow-up restore call never ran and the window stayed hidden. It is now wrapped, and `_restore_from_tray` forces the window to the foreground (`state("normal")` + a brief topmost toggle) so it surfaces above the browser on Windows instead of restoring behind it.
* **[Fix]** The "Copy letter" button no longer loses its label when clicked. The confirmation state drew `COLOR_TEXT_LIGHT` text on a `COLOR_CYAN_HOVER` fill — under the Cyber-Owl theme that is light-on-light (`#C8D4E0` on `#7DC8D4`), so "Copied! ✓" was invisible. The copied state now uses dark text for readable contrast in every theme.
* **[Fix]** Fewer spurious "company not specified" results. Field extraction now strips and normalizes the model output (empty / `null` / missing key are all handled), falls back to a language-appropriate label instead of a hardcoded Russian one, and the Stage-1 prompt now instructs the model to find the employer anywhere in the posting (page title, "About us", repeated brand names, email domains) rather than giving up when it is not in an obvious header.

</details>

<details>
<summary><b>🟢 v3.1 — OpenRouter provider + reliability hardening</b></summary>

<br>

> **Adds OpenRouter as a sixth AI provider and fixes a batch of reliability and privacy issues surfaced by a full code audit.**

**New provider**

* **[AI]** New `OpenRouterProvider` (`jh_ai_engine.py`) — cloud aggregator exposing many vendors (OpenAI, Anthropic, Google, DeepSeek, …) through a single OpenAI-compatible endpoint (`https://openrouter.ai/api/v1/chat/completions`). Models are addressed as `vendor/model` (e.g. `openai/gpt-5-mini`, `anthropic/claude-4-sonnet`). Requires an API key; runs through the same Failover Chain as every other cloud provider. Registered in `get_provider()`, `PROVIDER_ORDER`, `ALL_PROVIDERS_MODELS`, and the config defaults (`api_keys` / `active_models`) — existing configs auto-migrate the new keys on load.

**Reliability fixes**

* **[Fix]** **Rejected-vacancy dedup set desynced from disk.** `save_rejected_vacancy()` caps the on-disk log at 50 records but was adding every URL to the in-memory `_rejected_urls` set without ever removing evicted ones. The set grew unbounded and kept reporting evicted vacancies as "already rejected", so they could never be re-evaluated. The set is now rebuilt from the capped list on every write.
* **[Fix]** **Empty context sent to the LLM on single-block pages.** `extract_relevant_context()` split only on blank lines, so a `Ctrl+A` capture with single-`\n` separators collapsed into one oversized block that was skipped whole, returning `""`. Added a single-newline fallback split and a hard-truncation guarantee so a non-empty page always yields non-empty content within the char budget.
* **[Fix]** **Duplicate detection and queue feedback were dead code.** The capture engine wrote straight to the raw queue, bypassing `enqueue_vacancy()` — so pre-queue dedup, `_batch_id` tracking, and the "added to queue" status never ran, and duplicates were only discarded after the full request-delay countdown. The engine now routes through an `_EnqueueAdapter`, restoring O(1) pre-queue dedup and correct batch-completion notifications.
* **[Perf]** Stopped re-reading and re-parsing `config.json` from disk on **every** processed vacancy (`process_incoming_vacancy`); the in-memory config is already kept current by the settings window.
* **[Perf]** PDF import no longer calls `page.extract_text()` twice per page.

**Security & correctness**

* **[Security]** Gemini API key moved from the URL query string to the `x-goog-api-key` header (query strings leak into logs and exception traces).
* **[Fix]** JSON repair no longer corrupts apostrophes: the mixed-quote level only converts single quotes acting as JSON string delimiters, leaving `don't`-style values intact.
* **[Fix]** Geo matching (`_geo_match`, now module-level and unit-tested) uses whole-word token sets instead of loose substrings — `"India"` no longer matches `"Indiana"`.
* **[Cleanup]** Explicit `is_error` flag on `send_notification()` (no more brittle substring guessing), `hashlib.md5(..., usedforsecurity=False)` for the dedup-only hash, and a startup sweep of stale `*.tmp` files orphaned by hard exit.
* **[Tests]** Added `tests/test_bugfixes.py` (rejected-set sync, geo matching, JSON repair) and extended `tests/test_scoring_pipeline.py` for the new extraction contract.

</details>

<details>
<summary><b>🟢 v3.0.0 — Standalone. No extension required.</b></summary>

<br>

> **This release drops the Chrome extension permanently.**
> The extension was useful scaffolding in early versions but created real friction: manual installation, permission prompts, Manifest V3 compatibility headaches, and a hard dependency on Chrome. v3.0.0 replaces the entire input pipeline with a global hotkey that works in any browser, any OS, with nothing extra to install.

**Architecture & Features**

* **[Architecture]** Removed the Chrome extension and the local Flask webhook server. The new input path: `pynput.GlobalHotKeys` → `Ctrl+A / Ctrl+C` simulation → `pyperclip.paste()` → `queue.put()`. Zero open ports, zero browser-specific code.
* **[Automation]** New `BrowserCaptureEngine` (`jh_automation.py`): global hotkey listener in a daemon thread, configurable hotkey string, graceful `AUTOMATION_AVAILABLE` fallback when pynput/pyperclip are not installed.
* **[Automation]** Layout-independent VK keycodes: Windows uses Win32 Virtual Key codes (VK_A = 65, VK_C = 67, VK_L = 76), Linux/X11 uses hardware keycodes (A = 38, C = 54, L = 46), macOS uses kVK constants. Hotkeys fire correctly regardless of active keyboard layout.
* **[Platform]** Official Linux support (X11). `build_linux.py` added with Linux-specific PyInstaller hidden imports for pynput X11 backends (`pynput._util.xorg`, `pynput.keyboard._xorg`) and pystray GTK backend.
* **[Platform]** Wayland zero-trust guard: `enforce_linux_subsystem_guard()` checks `XDG_SESSION_TYPE` and `WAYLAND_DISPLAY`. Raises `PlatformSecurityException`; caught in `BrowserCaptureEngine.start()` — app continues without the macro feature and prints a clear remediation message (switch to GNOME on Xorg).
* **[Tray]** System tray icon via `pystray` — app runs silently in the notification area; right-click menu: show window / toggle active / exit.
* **[AI]** New scoring pipeline: `extract_relevant_context()` replaces `preprocess_vacancy_text()`. Seven steps: normalize whitespace → drop nav-noise lines (≤2 words AND ≤25 chars, no keyword match) → split on `"\n\n"` → score by `_VACANCY_KW_RE` hits + `min(len / 600, 2.0)` → greedy budget selection (score-descending) → Narrative Rule (restore document order) → `pack_paragraphs_to_budget()`. Stage 1 (12 000 chars) and Stage 2 (8 000 chars) each call the pipeline independently — no context drift between stages.
* **[AI]** `pack_paragraphs_to_budget()`: strict delimiter-aware packer. The hard invariant `len(result) ≤ max_chars` is enforced at every step, including accounting for `len(delimiter)` only from the second paragraph onward. Oversized paragraphs are skipped; the loop continues to collect smaller ones.
* **[Storage]** `_write_json_atomic()`: Write-Copy-Replace with `fsync`. `tempfile.mkstemp(dir=same_partition)` → `json.dump` → `f.flush()` → `os.fsync()` → `os.replace()`. The live file is never opened with `O_TRUNC`. All three write paths (`_save_file`, `_modify_file`, `_migrate_strip_description`) now delegate to this function.
* **[Notifications]** Thread-safe toast: `_notification_lock` guards `_toast_ref` mutations. `_fade_out_instance` captures `toast` directly (not the global ref) — concurrent notifications can't corrupt each other's fade animation. Nullifies the global ref only if `_toast_ref[0] is toast` (identity check, not equality).
* **[Build]** `build_exe.py`: fixed `logo.png` path from project root to `assets/logo.png`. `installer.iss`: removed all extension-related blocks (`[Files]`, `[Icons]`, `[Run]`, `[CustomMessages]`). `build_linux.py`: new, mirrors `build_exe.py` with Linux-specific hidden imports, `--noconsole`, `os.chmod(0o755)`, and system dependency banner.

**Bug fixes (UI freeze)**

* **[Fix]** Results/History window could freeze the entire app ("Not Responding") after roughly 10 processed vacancies. Root cause: `jh_results_ui.py` called `storage_manager.get_all_approved()` / `get_all_rejected()` (and the delete / clear-all mutations) directly on the Tk **main thread** — on window open, on every tab switch, and on every delete/clear click. All of those block on the same process-wide `_file_lock` that the background queue worker holds while persisting each processed vacancy, including the `fsync()` + `os.replace()` in `_write_json_atomic()`. On a slow, antivirus-scanned, or cloud-synced disk that lock hold can stretch from tens of ms to multiple seconds — and since it happened on the main thread, the entire Tk message loop stalled for the duration, which Windows reports as "Not Responding". More queued vacancies meant more frequent worker writes, so the odds of an unlucky UI click landing on the lock grew with volume — explaining why it surfaced "after about 10 vacancies" rather than immediately.
* **[Fix]** Added a `_run_async()` helper in `jh_results_ui.py` and routed every storage read/write triggered from a UI event (initial load, tab switch, delete, clear-all, periodic refresh) through it: the I/O now runs on a background daemon thread and results are applied via `window.after(0, ...)`, mirroring the pattern `auto_refresh_loop()` already used correctly. `refresh_list()` now refuses to run without pre-fetched data instead of silently blocking.
* **[Fix]** The `<Configure>` handler on each vacancy card's info label called `.configure(wraplength=...)` unconditionally on every resize event, which could re-trigger its own `<Configure>` and add extra reflow passes scaling with card count inside the `CTkScrollableFrame`. Now caches the last applied wraplength and skips the call when it hasn't changed.

**Bug fixes carried over from 2.0.2**

* **[Fix]** Notification theme not applied at startup: `jh_notifications.apply_theme()` was called before the module was imported — a silent `NameError` swallowed by `except Exception` meant toast colors were always stuck at hardcoded defaults, ignoring the selected theme entirely.
* **[Fix]** Gemini model config silently corrupted: the startup migration mapped `"gemini-3.0-pro"` → `"gemini-3.1-pro"`, but `"gemini-3.1-pro"` does not exist in `ALL_PROVIDERS_MODELS`. Any user with that model saved would silently lose it from the dropdown. The bogus migration clause was removed — `"gemini-3.0-pro"` is a valid model and needs no migration.
* **[Fix]** Slow-model warning showed no threshold: `tr("warn_text", min_tps=12)` passed a named kwarg that had no `{min_tps}` placeholder in either EN or RU string. The value was silently discarded by the `except (KeyError, ValueError): pass` guard in `tr()`. Added `{min_tps}` to both locale strings.
* **[Fix]** Icon and logo not found in dev mode: `_resolve_asset()` in `main_app.py` and hardcoded paths in `jh_results_ui.py` only searched the `src/` directory. `icon.ico` is at the project root and `logo.png` is under `assets/`. Both now search `src/` → project root → `assets/` → exe dir → `_MEIPASS`.
* **[Cleanup]** Removed unused `ImageTk` import from `main_app.py` (`from PIL import Image, ImageTk` → `from PIL import Image`).

</details>

<details>
<summary><b>📦 v2.0.2 — Concurrency & Reliability Fix</b></summary>

* **[Storage]** Complete rewrite of the concurrency model. Two independent, never-nested locks: `_file_lock` (disk I/O only) and `_url_lock` (in-memory set mutations only). Always-live `_approved_urls` / `_rejected_urls` sets populated at startup — O(1) dedup, zero disk reads per check.
* **[Storage]** Removed `description` field (raw `document.body.innerText`, up to several MB) from approved records. The bloated file held `_file_lock` for 8+ seconds, timing out all concurrent webhook requests.
* **[Storage]** `_migrate_strip_description()`: one-time startup migration strips the legacy `description` field from all existing records before the server starts.
* **[Enqueue]** Removed `_enqueue_lock` and `_in_flight_urls`. Replaced triple-check dedup (serializing all 24 Flask threads) with a single O(1) storage check + unconditional `queue.put()`. Worker-side safety dedup as backstop.
* **[Startup]** Fixed Flask startup race via `threading.Event` (`_flask_ready`): button shows "STARTING…" until port 5000 is bound.
* **[Extension]** Removed `tab.status === 'loading'` guard — SPAs never reach `'complete'`. Text truncated to 50 000 chars — prevents GIL contention under 24 concurrent workers.

</details>

<details>
<summary><b>📦 v2.0.1 — Full Overhaul</b></summary>

* **[Architecture]** Global `jh_` prefix refactor, unified `jh_version.py`, Self-Healing build in `build_exe.py`.
* **[i18n]** Full interface localization (EN / RU) via `jh_i18n.py` with dynamic switching.
* **[Engine]** Custom exception hierarchy, 5-level cascading JSON repair, Ollama / LM Studio integration with `LOCAL_SAFE_PARAMS`.
* **[Engine]** Toxic work condition detection and geographic compliance filter.
* **[UI]** Resume history with PDF import and AI text extraction. HiDPI centering, dark Win32 title bar, card signature caching.
* **[Notifications]** Custom Toast: slide/fade animation, color coding, audio in a dedicated thread.

</details>

<details>
<summary><b>📦 v1.2.0 — Multi-Provider Engine</b></summary>

* `BaseProvider` architecture with Failover Chain and cascading JSON parser.
* Dark CustomTkinter interface, full HiDPI support.
* Queue timeout manager (15 s) with status bar.

</details>

<details>
<summary><b>📦 v1.1.0 — UI & Keyboard Layout</b></summary>

* Quick-apply buttons in vacancy cards.
* Fixed `Ctrl+V`, `Ctrl+C`, `Ctrl+A` on Russian keyboard layout.
* Smooth scrolling, auto-reset scroll on filter switch.

</details>

---

## 🗺️ Roadmap

<details>
<summary><b>🟢 v1.1.0 — UI & Keyboard Layout (Done)</b></summary>

- [x] Hotkeys on Russian layout, smooth scroll, auto-reset on filter switch.

</details>

<details>
<summary><b>🟢 v1.2.0 — Multi-Provider (Done)</b></summary>

- [x] Modular engine, Failover Chain, JSON repair, AI control panel.

</details>

<details>
<summary><b>🟢 v2.0.1 — Full Overhaul (Done)</b></summary>

- [x] Local AI (Ollama / LM Studio), EN/RU localization, resume history, PDF import, HiDPI centering, toast notifications, toxic + geo filters.

</details>

<details>
<summary><b>🟢 v2.0.2 — Concurrency Fix (Done)</b></summary>

- [x] O(1) dedup, always-live URL sets, fixed startup race, removed `_in_flight_urls` serialization bottleneck.

</details>

<details>
<summary><b>🟢 v3.0.0 — Standalone App, No Extension (Done)</b></summary>

- [x] Chrome extension dropped — global hotkey replaces the entire Flask webhook pipeline.
- [x] `BrowserCaptureEngine`: pynput + pyperclip, layout-independent VK keycodes.
- [x] System tray via pystray — app runs silently in the background.
- [x] Official Linux (X11) support + `build_linux.py`.
- [x] Wayland zero-trust guard with graceful degradation.
- [x] `extract_relevant_context()`: keyword scoring, Narrative Rule, `pack_paragraphs_to_budget()`.
- [x] `_write_json_atomic()`: Write-Copy-Replace + fsync — crash-safe storage across all write paths.
- [x] Thread-safe toasts: `_notification_lock` + instance-bound fade closure.
- [x] Fixed notification theme not applied at startup (silent `NameError` in `jh_notifications`).
- [x] Fixed Gemini config migration mapping `"gemini-3.0-pro"` to a non-existent model.
- [x] Fixed slow-model warning not showing the tokens/sec threshold (`{min_tps}` placeholder missing).
- [x] Fixed icon and logo not found outside a packaged build (asset search now covers project root and `assets/`).
- [x] Fixed Results window freezing the entire app ("Not Responding") after ~10 vacancies — UI-thread calls into `storage_manager` (window open, tab switch, delete, clear-all) now run on a background thread via a new `_run_async()` helper, instead of blocking on `_file_lock` while the queue worker writes.

</details>

<details>
<summary><b>🔵 v3.2 — macOS (Planned)</b></summary>

- [ ] macOS support — kVK keycodes already implemented in `jh_automation.py`, needs end-to-end testing.
- [ ] `build_mac.py` with `.app` bundle and `.dmg` packaging.

</details>

<details>
<summary><b>🔵 v3.x — Quality of Life (Planned)</b></summary>

- [ ] Configurable hotkey via Settings UI (no config.json editing).
- [ ] Vacancy export to CSV / PDF report.
- [ ] Statistics dashboard: acceptance rate, top rejection reasons, response timeline.
- [ ] Telegram bot mode — send a vacancy URL via Telegram, receive the analysis in the chat.

</details>

---

## 🤝 Support the project

If the app helped you land a job — leave a star. It's free, and that's how good tools find the people who need them.

If something breaks — open an Issue. Critical bugs will be fixed.

<p align="center">
  <a href="https://github.com/eric-esoteric/job-hunter-ai">
    <img src="https://img.shields.io/badge/⭐_Star_on-GitHub-181717?style=for-the-badge&logo=github" alt="Star on GitHub">
  </a>
</p>

---

<p align="center">
  <sub>Made for people who value their time · Non-Commercial · v3.1.1</sub>
</p>
