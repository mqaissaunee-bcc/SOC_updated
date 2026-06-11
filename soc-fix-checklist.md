# Simulated SOC — Punch List

Ordered high → low priority. Check items off as we complete them.

## High priority

- [x] **1. Gate the instructor answer keys.** ✅ DONE — entire instructor edition encrypted (AES-256-GCM, PBKDF2 310k iterations). File is now an unlock shell; passphrase: `CyberSOC-Instructor-2026` (change with `lock-instructor-edition.py`). Unlock persists per browser session via sessionStorage.
- [x] **2. Accessibility + CSP pass (all 9 files).** ✅ DONE — zero inline handlers remain (251 converted to a CSP-safe delegated dispatcher, verified with Node syntax checks + 7/7 parser tests); interactive divs got `role="button"` + `tabindex` + Enter/Space support; accordions wired with `aria-expanded`/`aria-controls` kept in sync by patched toggle functions; lesson feedback + score are `aria-live` regions; display-info overlays are proper dialogs (`aria-modal`, focus moved in, restored on close, Tab trapped); skip links + `role="main"` on the four document pages; `prefers-reduced-motion` honored in all 9 files; visible `:focus-visible` outlines added and two `outline: none` suppressions fixed; multi-screen toggles now use native checkboxes and iframes have titles. *Deferred refinement: clickable divs kept as `role="button"` rather than converted to `<button>` tags (tag conversion across 107 multi-line elements risks CSS regressions — WCAG-conformant as is).*
- [x] **3. Timer & visibility management.** ✅ DONE — every dashboard's intervals (16 across the four screens) now route through a `SimTimers` manager that pauses on `visibilitychange` when the tab is hidden and on `postMessage` pause commands from the parent viewer (resume reverses both; parent-pause and tab-hidden states tracked independently — 10/10 state machine tests pass). The quad viewer sends pause to toggled-off panels and resume on re-show, and pauses its own clock when hidden. Screen 3's notes array capped at 50 (all other feeds were already capped).
- [x] **4. Fix the broken lazy-load in the multi-screen viewer.** ✅ DONE — hardcoded iframe `src` attributes removed; `updateGrid()` now assigns `src` on first show only (with per-load 6s loader failsafe), and load listeners are bound *before* the initial `updateGrid()` so fast loads can't slip past them. Default all-four view still loads everything; presets/toggles now genuinely defer loading.

## Medium priority

- [x] **5. Persistence via localStorage.** ✅ DONE — lesson saves section position, every quiz and triage-sim answer (replayed faithfully on reload, rebuilding the score), and completion state under `soc-lesson-v1`; completion screen now shows a deterministic completion code (`SOC-<pct>-<hash>`, FNV-1a — same score always yields the same code, so instructors can verify by recomputing) plus a Reset Progress button. Both exercise editions persist expanded exercises and revealed answer keys under their own keys. All storage calls try/catch-wrapped per the module skill.
- [x] **6. Dynamic dates.** ✅ DONE — Screen 3's incident counter and default case ID now derive from the current year (`INC-2026…` today, `INC-2027…` next year, automatically). Exercise scenario text keeps readable `INC-2024…` IDs in source but a text-node walker rewrites them to the current year at load. Screen 4's 2024 strings turned out to be real CVE IDs and were correctly left untouched; `CVE-2024-XXXX` placeholders likewise.
- [x] **7. Defang all IOCs.** ✅ DONE — exercises now use SOC-standard notation: `hxxps://micros0ft-verify[.]com/login.php`, `185.220.101[.]45`, `45.33.32[.]156`, `103.224.182[.]0/24` (6 occurrences in student, 13 in instructor). The lesson was already correctly defanged; dashboard telemetry intentionally stays raw (realistic console output — analysts defang in documentation, not in the SIEM).
- [x] **8. Fix the UTC clock mislabel.** ✅ DONE — viewer clock now uses `getUTCHours/Minutes/Seconds`, so the "UTC" label is finally telling the truth (and UTC is the correct SOC convention anyway).
- [x] **9. Print stylesheet.** ✅ DONE — comprehensive `@media print` in lesson + both exercise editions: forced light theme, all sections/exercises/answer keys expanded, nav/buttons/videos hidden, page-break control on rubrics and quiz blocks, printed answer keys labeled, links underlined. (The exercises had a minimal print block already; it was extended rather than duplicated.)

## Improvements (integrated from the original review)

- [x] **13. Seeded randomness.** ✅ DONE — all 94 `Math.random()` calls across the four dashboards now route through a mulberry32 PRNG seeded from `?seed=<anything>` in the URL; the multi-screen viewer propagates its own `?seed=` to all four iframes. Same seed → identical sequence of alerts/incidents/IOCs (verified: 1,000-value sequences match exactly). Seeded pages append `[seed: …]` to the tab title as confirmation. Without a seed, behavior is unchanged. *Caveat: content sequence per feed is deterministic; exact wall-clock interleaving across feeds can drift slightly between machines, and pausing a tab (item 3) shifts timing — "same run" means same content in the same order, not frame-identical.*
- [x] **14. Single-source the exercise editions.** ✅ DONE — `soc-exercises-source.html` is now the only file you edit (it's the instructor superset, plaintext). `build-exercises.py` derives both editions: the student edition strips answer sections, teaching tips, facilitator guides, the instructor guide, and instructor CSS (rubrics intentionally remain — students see grading criteria); the instructor edition is encrypted automatically. The build asserts exact block counts (15 answer sections, 30 teaching tips, etc.) so structural typos fail the build instead of shipping broken files. Validated: generated student is content-identical to the previous hand-maintained student (0-line normalized diff); locked instructor round-trips byte-identical to source. **⚠ Never publish `soc-exercises-source.html` or place it in a web-hosted folder — it contains all answers in plaintext.**

## Improvement backlog (not yet started)

- [ ] **15. Shared simulation state via BroadcastChannel.** Let the four dashboards share one simulation so an incident on Screen 3 produces correlated alerts on Screens 1, 2, and 4. Highest-impact realism upgrade; zero infrastructure.
- [ ] **16. Instructor inject console.** A control page that broadcasts scenario events ("launch ransomware wave," "begin insider-exfil pattern") to all open dashboards — turns the ambient simulation into a live, instructor-paced exercise. Builds on item 15.
- [ ] **17. Cloud & identity content expansion.** CloudTrail/GuardDuty feed panel, Entra ID risky sign-ins, OAuth consent abuse, S3 exposure scenarios; new exercises for misconfigured-S3 breach, CI/CD token compromise, SaaS BEC with inbox rules, K8s runtime hunt.
- [ ] **18. AI-era scenarios.** AI-generated spearphishing, deepfake-voice vishing (psychology/criminal justice tie-ins), and an "audit the AI copilot's triage" exercise.
- [ ] **19. Static hosting + PWA.** GitHub Pages/Cloudflare Pages deployment (excluding the source file), service worker for offline lab use.

## Low priority

- [ ] **10. Remove Google Fonts CDN.** System-font fallback stack (or self-hosted fonts) so the suite works offline and on locked-down lab networks — required by the single-file module standard anyway.
- [ ] **11. Harden YouTube embeds.** Switch to `youtube-nocookie.com`, add visible fallback links/descriptions for when embeds are blocked.
- [ ] **12. Index cleanup.** Update/remove the "Draft — Work in Progress" banner and version string; verify nav links and descriptions match current file set.

## Done

(move completed items here)
