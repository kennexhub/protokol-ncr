# NCR GDC-NC-2026 — No Conformidades (Protokol / Ayacucho road)

Single self-contained web app: `index.html` (mobile-first, Spanish field form, ES/EN UI toggle).
The generated document is **always Spanish**, even in EN mode.

## How to deploy

1. Host `index.html` as a static page (any static host — e.g. Vercel, Render Static, GitHub Pages).
   No build step, no server code, no environment variables.
2. Open it in a browser (phone or desktop). It signs in anonymously to Firebase on load.
3. No PIN / access control yet — **this is the next step, not yet built**. Anyone with the link can read/write NCRs in this Firebase project until rules are tightened. Do not treat this as a production access-controlled system.

Firebase project (already created, do not create another): `protokol-ncr`
- Spark free plan, Firestore `southamerica-east1`, Anonymous auth enabled.
- Rules allow read/write on `ncrs/{id}` (+ `photos` and `audit` subcollections) and `counters/{id}` only when `request.auth != null`.
- Counter doc `counters/ncrSeq` `{next: 1}` must exist before the first save.

## Access control — PIN gate (added 2026-11-14, per Kenny)

- The app opens behind a **PIN gate**: only authorized users (David + 1 more) can use it. The PIN is remembered per device (localStorage `ncr-pin-ok`) after the first successful entry, so David enters it once on his phone.
- PIN lives in Firestore `settings/access` `{pin: "..."}`. **Initial PIN: `2026`** — Snehil must change it (in-app button "Cambiar PIN", top bar; asks current PIN, then a new 4–8 digit PIN). If the `settings/access` doc is missing, the app falls back to `2026` and tries to create the doc.
- Firestore rules must allow `settings/{id}` read/write for authenticated users (anonymous auth counts). Add the rule in the Firebase console — see "Firestore rules" below.
- Honest limit: this is a **field-test gate against casual access, not real security** — anonymous auth means anyone who can sign in can read the PIN doc via the API, and the PIN is in the page source as a fallback constant. If real per-user access is needed later, switch to email/password accounts for David + the second user and restrict the rules to their UIDs.

## Document number — David assigns it (added 2026-11-14, per Kenny)

- The "N.º NCR (CORRELATIVO)" field in section 2 is **editable**. On "Nueva NCR" the system suggests the next sequential number (read from `counters/ncrSeq`, no counter consumed until save); David can type his own number instead.
- On save: if David kept the suggestion (or left it blank) the counter transaction assigns the number as before. If he typed his own number, the app checks it is **unique** (a second NCR with the same number is refused) and, if it is a `GDC-NC-2026-NNN` number higher than the counter, advances the counter so the next suggestion never collides with it. Renaming an existing NCR works the same way (uniqueness check + audit entry "Número cambiado: old → new").
- Offline: a custom number is kept in the local draft and its uniqueness is verified when it syncs; if it collides by then, the sync assigns the next sequential number instead.
- Also fixed: refreshing while editing a **saved** NCR no longer loses the doc id (which used to make the next save create a duplicate NCR). Local (unsaved) drafts still behave as before.

## Status workflow (explained to Kenny 2026-11-14)

- **Abierta** — the non-conformity is recorded, awaiting the fix. **En corrección** — the corrective action is being carried out. **Cerrada** — David verified the fix and closes the process. **Only David closes.** Closing now requires a closure date (auto-filled with today when Cerrada is picked) and "Cerrado por". Every status change is in the audit trail.

## What changed 2026-11-14 (round 5 — logo, download, Muse-format signatures, form-first)

- **Logo:** the Gobierno Regional Ayacucho logo (red oval, sent by Snehil) is now in the app topbar and in the document header (top-left, next to "Gobierno Regional de Ayacucho"). Embedded as base64 (10 KB) so the single file stays self-contained; the downloaded document carries it too. Source: `logo-ayacucho.jpg` in this folder.
- **Download:** the document view now has "Descargar documento" next to "Imprimir / Descargar PDF". It downloads a standalone HTML file (`NCR-<número>.html`) with the full A4 document, logo and photos embedded — opens in any browser, prints to PDF, works offline. Print (window.print → Save as PDF) is unchanged.
- **Signatures — exactly like the Muse document:** the old 4-role grid + Revisado/Aprobado lines are gone. The document now has a "FIRMAS" table, 2 columns × 3 rows of blank boxes; only two titles at the top — "RESIDENTE DE OBRA" (left) and "ESPECIALISTA DE CALIDAD" (right) — everything else blank, for signing the printed copy by hand. Below it, "REGISTRO DEL DOCUMENTO" with "Fecha y hora de registro" + timestamp (the NCR's creation time if saved, else the current time). NOTE: the Muse screenshot showed "SUPERVISOR DE OBRA" as the second title; Snehil's message explicitly named "ESPECIALISTA DE CALIDAD" instead, so that is what is used — one-word change if he wants Supervisor. The form's "5 FIRMAS" input section is unchanged (names are still stored as data); the printed document keeps the boxes blank.
- **Impact checkboxes:** already ☐/☑ exactly like Muse's ("IMPACTO: ☐ LEVE ☐ MODERADO ☑ GRAVE") — no change needed.
- **Form-first (Kenny's "New NCR" bug):** opening the link now shows the FULL FORM immediately (not the list). Root cause: the app landed on the list, and "New NCR" was guarded by a native confirm() that ate the first click (the dialog confused Kenny; the test browser auto-cancels it). The confirm is gone — "Nueva NCR" now works with one click; if there's a draft with content it is stashed to a backup key (`ncr-draft-prev-v1`) first so nothing is lost, then a fresh form appears. "Limpiar todo" uses the same path (no confirm). The suggested number is filled once auth is ready (retry in onAuthStateChanged). The list is one tap away ("Ver lista").

Verification of round 5 (2026-11-14 ~10:29 IST): ALL 5 STEPS PASSED — (1) first view is the full FORM (sections 1, 2, 3, 5; number GDC-NC-2026-001 filled); (2) "Nueva NCR" works on ONE click, no popup (number appears after ~5 s once auth completes); (3) document has the logo top-left, FIRMAS as a 2×3 table with only RESIDENTE DE OBRA + ESPECIALISTA DE CALIDAD, rest blank, REGISTRO DEL DOCUMENTO with timestamp 14/11/2026 10:29:40, impact ☐ LEVE ☐ MODERADO ☑ GRAVE; (4) "Descargar documento" started a real download (38 KB file, NCR-GDC-NC-2026-001.html) — independently re-checked from the downloaded file: logo embedded, heading "FIRMAS" (not "5 FIRMAS"), no SUPERVISOR/REVISADO, proyecto = the AY-728 example (the report's "agua potable" line described the restored draft, not the example); (5) save works — GDC-NC-2026-001, server-confirmed, audit entries with timestamps. Test record deleted after the run; counter reset to 1; 0 NCRs; PIN 2026. Still open: print dialog + 390px viewport (test-browser limits), David's field test, David's exact numbering scheme, PIN change by Snehil.

- **Section 4 "Acción Correctiva y Cierre" REMOVED.** Kenny was right: it was NOT in the MVP (Muse's version) — it came from the review's feedback list. The original form (ECOP-GC-FR-012) doesn't have it either. The form now goes 1 Datos Generales, 2 Identificación, 3 Descripción, 5 Firmas. Closing is just the status change to Cerrada (logged with a timestamp in the audit trail). The status workflow (Abierta → En corrección → Cerrada, only David closes) stays — it lives in Section 2, not Section 4. If David ever asks for corrective-action tracking, the section can be added back in minutes.
- **Document generation is frictionless (MVP logic).** The old save-gate ("Guarde primero la NCR...") is gone: "Generar documento" works from any filled form, saved or not, with or without a photo. If there's no number yet the document shows "BORRADOR (sin número)" plus a yellow draft banner; if there's no photo it shows "Sin foto de evidencia". Saving a REAL NCR still requires a photo (evidence) and stores the data + server timestamps + audit trail — that part is unchanged.
- Validation split: `validate()` (save) still requires a photo; `validate(true)` (generate) does not.

Verification of round 4 (2026-11-14 ~09:00 IST): ALL THREE CHECKS PASSED — (1) Section 4 is gone from the form AND the document (searched "Acción Correctiva", "Causa raíz", "Cerrado por", "Fecha de cierre" — no matches); (2) Load example → Generate works immediately with no save and no photo — the A4 preview shows the BORRADOR banner and "Sin foto de evidencia"; (3) saving still stores data — test NCR saved with photo, server-confirmed, audit entries with timestamps, list shows it. (It saved as PRUEBA-002, not the suggested GDC-NC-2026-001, because the test browser's restored draft carried that number in the field — the custom-number logic working as intended, not a bug.) Test record deleted after the run; counter reset to 1; 0 NCRs; PIN 2026. The "Nueva NCR" button again looked unresponsive in the test browser — same native confirm() guard for unsaved work, auto-cancelled by the automation; handler sound, guard intentional.

- Editable N.º NCR (David assigns; suggestion + uniqueness check + counter bump).
- PIN gate + in-app "Cambiar PIN" (initial PIN `2026` — change it).
- Signature roles now match the original form ECOP-GC-FR-012: Responsable de la Ejecución, Especialista de Calidad, Ing. Residente, Supervisor de Obra (+ 2 adicionales opcionales). The generated document now shows each signature as Firma / Nombre / Cargo / Fecha and adds the "Revisado Por: Especialista de Calidad / Aprobado Por: Ing. Residente" line from the original.
- Photos in the A4 document are bigger (max 260 px tall, was 180 px) and the signature grid is 4 columns like the original.
- Closing an NCR requires fecha de cierre + cerrado por.
- Refresh-while-editing a saved NCR no longer duplicates it on save.
- Vercel Authentication (SSO) turned OFF on the project so David can open the link without a Vercel login.

## Bug fixes 2026-11-14 (found by the field-test verification, fixed same night)

1. **Custom number save failed** (`seq: undefined` → Firestore rejected the write): `bumpCounterIfHigher` returned `undefined` for non-`GDC-NC-2026-NNN` numbers (e.g. PRUEBA-001). Now returns `null`, and the payload uses `seq ?? null`.
2. **"Cargar ejemplo real" wiped the typed NCR number**: `fill()` unconditionally overwrote the number input. Now it only touches the number when the data carries one; "Nueva NCR" clears it explicitly.
3. **CONSTRUCTOR showed "function Object() { [native code] }"** on a fresh form: `d.constructor` on a plain object literal returns the Object constructor. Now guarded with a `typeof === "string"` check.
4. **PIN screen flashed the app first**: the gate was `display:none` until the module ran. Now visible by default in the HTML and hidden by JS only when already unlocked.
5. **"Nueva NCR" discarded an unsaved draft silently**: now asks for confirmation when the current form has unsaved content.
6. **Cerrada requirements were invisible until save**: the estado change now refreshes the missing-fields list, so the fecha de cierre / cerrado por requirement shows immediately.

8. **Banner lied about the number after loading the example (found by the 02:13 final run)**: the example handler reset `state.ncrNumber` to null while the input still showed the typed number, so the banner read "sin número" until the save. Now the handler keeps the input's current number in state and refreshes the banner.

Verification note: the first field-test run (2026-11-14 ~02:00 IST) FAILED at Save because of bug 1, so the document/print steps were never reached. The 02:03 re-test passed the PIN screen (visible on first paint, list never flashed), the example-preservation fix, the Constructor fix, and the full A4 document (photo large, impact ☑ GRAVE, four signature roles + Revisado/Aprobado, entirely Spanish, 2 pages estimated) — but FAILED the custom-number save because of bug 7 (saved as GDC-NC-2026-001 instead of PRUEBA-001) and could not verify print (environment-blocked) or a 390px viewport (tooling cannot set it). The re-test's GDC-NC-2026-001 record was deleted afterwards and the counter reset to 1. FINAL run 02:13–02:28 IST: custom-number save VERIFIED — PRUEBA-002 survived the example load and the save, confirmed by Firestore ("Guardado en Firestore: PRUEBA-002 (confirmado por el servidor)"); document VERIFIED again with PRUEBA-002 (header, photo large, ☑ GRAVE, four roles + Revisado/Aprobado, Spanish-only). The PIN screen showed on first paint, then cleared itself within ~10 s WITHOUT a PIN entry — that is the remembered unlock from the earlier test runs in the same shared browser profile (the gate hides once the module runs if localStorage has the unlock); a fresh device has no remembered unlock, so David will see the PIN screen until he enters 2026. "Nueva NCR"/"Limpiar todo" appeared unresponsive in the test browser — both use a native confirm() guard for unsaved work, which the automation auto-cancels; the handler is sound and the guard is intentional. Print dialog and 390px viewport remain unverified (test-browser limits, not app errors) — David's field test is the real check for both. PRUEBA-002 record deleted after the run; counter reset to 1; 0 NCRs.

## Firestore rules

Rules allow read/write on `ncrs/{id}` (+ `photos` and `audit` subcollections), `counters/{id}` and `settings/{id}` only when `request.auth != null`. Counter doc `counters/ncrSeq` `{next: 1}` must exist before the first save.

### `ncrs/{id}` (one doc per NCR)
| Field | Type / example |
|---|---|
| `ncrNumber` | string, e.g. `"GDC-NC-2026-001"` |
| `seq` | number, e.g. `1` |
| `proyecto`, `cliente`, `constructor`, `supervision` | string |
| `ubicacion`, `progresiva`, `planoRef` | string |
| `fecha` | string `dd/mm/yyyy` (Peru format, used in the document) |
| `fechaISO` | string `yyyy-mm-dd` (for sorting / the date picker) |
| `items` | array of `{etapa, responsable, ubicacion, elemento, partida}` |
| `descripcion` | string |
| `impacto` | `"LEVE"` \| `"MODERADO"` \| `"GRAVE"` |
| `estado` | `"Abierta"` \| `"En corrección"` \| `"Cerrada"` (default `Abierta`) |
| `causaRaiz`, `accionCorrectiva`, `responsableCorreccion` | string |
| `fechaLimite`, `fechaVerificacion`, `fechaCierre` | string `yyyy-mm-dd` (empty if unset) |
| `verificacion`, `cerradoPor` | string |
| `signatures` | array of `{rol, nombre, cargo, signed, signedAt, dataUrl}` (6 entries: Residente, Supervisor, 4 adicionales) |
| `createdAt`, `updatedAt` | Firestore server timestamps |
| `createdByUid` | anonymous uid |
| `syncStatus` | `"synced"` |

Photos are **not** in this doc (1 MB Firestore doc limit).

### `ncrs/{ncrId}/photos/{photoId}`
`{dataUrl, caption, order, createdAt}` — one doc per photo, max 8 per NCR.

### `ncrs/{ncrId}/audit/{auditId}`
`{action, uid, createdAt}` — one entry per create, save/edit, status change, signature, photo add/remove/replace.

### `counters/ncrSeq`
`{next: <number>}` — assigned by a Firestore transaction on first save, so two NCRs can never get the same number while online.

## Photo storage limits

- Max **8 photos** per NCR.
- Each photo has a caption field, delete, and replace.
- Compressed client-side before storing: max **1200 px** longest side, **JPEG quality 0.75**; a second pass at 900 px / 0.6 is tried if still over the limit.
- **Rejected with an honest error if still over 700 KB** after compression.
- No Cloud Storage, no Cloudinary, no external upload service — photos live as `dataUrl` strings in the `photos` subcollection. This is a deliberate free-tier trade-off: it works offline-first on Spark, but a photo-heavy NCR uses Firestore document storage. If photo volume grows, move to Cloud Storage (requires a billing-enabled project) — do not silently exceed limits.

## Offline-first

- Firestore offline persistence is enabled, plus a `localStorage` draft autosave on every change (`ncr-draft-v1`), so a refresh never loses a form in progress. An unsaved-draft warning is shown.
- If the first save happens offline, the NCR is kept in `localStorage` (`ncr-pending-v1`) as a local draft with a **provisional** label. The real sequential number is assigned by transaction on sync. A provisional draft **cannot** generate the final document — the document requires a real `GDC-NC-2026-###` number.
- Sync status is shown: En línea / Sin conexión / Pendiente de sincronizar.
- Firestore query rule respected: no `where()` combined with `orderBy()` on a different field (no composite index exists). The list fetches the collection and filters/sorts in JavaScript, newest first.

## Validation (fixes from the 2026-11-13 MVP review)

An empty form cannot save or generate a document. Required: all Section 1 fields, Ubicación, Fecha, at least 1 item with Etapa + Responsable, Descripción, at least 1 photo, Impacto. Missing items are listed inline and in the status pill.
Other fixes: sequential NCR number, save + searchable/filterable list, status workflow with audit, separate corrective-action/closure section, photo captions/replace/limits, document always Spanish, date shown as dd/mm/yyyy, dynamic page estimate in the preview plus `Página X de Y` in the print footer, per-signer timestamps, mobile-first single column (max 800 px, 44 px touch targets).

## What was NOT verified

- No live Firestore write was done from this VM: the Firebase JS SDK `signInWithEmailAndPassword` / anonymous auth path is known to hang on this VM (`auth/network-request-failed`), while the browser is unaffected. The code was syntax-checked only — test the first save, the counter transaction, and photo upload in a real browser before field use.
- Mobile layout was not tested at 390 px in a live browser here; the CSS is mobile-first but confirm on a real phone before the field test.

## Round 6 (2026-11-14 afternoon) — full end-to-end test at Snehil's request + fixes

Snehil: "I don't know Spanish.. so you test everything and lmk when everything is to the point." Full 11-check browser run 16:15–16:24 IST, then fixes for what it found.

**Test results — 7 pass, 2 partial, 2 fail:**
- PASS: form-first full form (1, 2, 3, 5; no Section 4); N.º NCR suggestion GDC-NC-2026-001; "Nueva NCR" one click, no popup; document generation frictionless (logo, FIRMAS 2×3 with only the two titles, REGISTRO DEL DOCUMENTO, BORRADOR banner); download (22 KB standalone HTML, contents verified); save server-confirmed ("Guardado en Firestore: GDC-NC-2026-001 (confirmado por el servidor)"); status to Cerrada audit-logged ("Estado: Abierta → Cerrada").
- PARTIAL: PIN gate — auto-unlocked via the remembered device, so typing 2026 / a wrong PIN was not demonstrated this run. Example content mismatch (see fixes).
- FAIL — "Cambiar PIN": button did nothing in the test browser (8 attempts). NOT a proven bug: the handler (line 691) uses native `prompt()`/`alert()`, and the test browser auto-dismisses native dialogs (same reason `confirm()` was auto-cancelled in round 5). Code is correct; it needs a real phone to prove. PIN remains 2026 (required final value).
- FAIL — no delete function: "Eliminar" appears nowhere in the app. The test record had to be removed via Firestore REST (doc + 1 photo + 4 audit entries deleted, counter reset to 1). For David this is arguably correct (an audit trail should not be deletable from the UI), but a mistaken record cannot be removed from the app.
- Still tooling-blocked: true 390px phone layout and the print dialog (desktop viewport 1919×998 only) — need David's phone.
- Minor observations: on reload the list briefly shows "0 NCR" while "Conectando…" (loading state only, not data loss); a restored draft claims "Faltan: 1 foto de evidencia" even though its photo thumbnail is present (restored photo does not satisfy the completeness check).

**Fixes applied after the test (same day, redeployed, live file byte-identical to local, 75,169 bytes):**
1. **Example replaced with the TRUE original** from `NO_CONFORMIDADES_UBS.xlsx` (verified cell-by-cell): Lircayccasa water/sewerage project, Municipalidad Distrital de Congalla, Consorcio ECOPSA, Consorcio Supervisor Saneamiento Lircayccasa, item Estructura / Columna / Concreto Armado FC=175, description "Cangrejeras en las columnas…" (3 lines incl. the desencofrado/curado notes), impacto LEVE. The old example (AY-728 road header + 9 UBS steel-spacing defect, GRAVE) was not the original and was internally inconsistent. The new-form default proyecto stays the AY-728 road (David's current project); only the example changed.
2. **Header code restored to the original form code ECOP-GC-FR-012** (form header line 151 + buildDoc line 610). The NCR number still shows in its own "N.º NCR" row. Previously "CÓDIGO: GDC-NC-2026".
- **Firestore state after cleanup (REST-verified): 0 NCRs, counters/ncrSeq next=1, settings/access pin=2026.**
- Re-verification of the fixed example + document in the live app: short browser check (no save) — run after redeploy; result recorded in chat, not here.

## Round 7 (2026-11-14 evening) — Client / Contractor pre-filled, exactly as in the Muse MVP

Snehil (with the Muse MVP link + a screenshot of its Section 1): the CLIENT field must already be filled with the Regional Government of Ayacucho and the CONTRACTOR field pre-filled from the MVP, as defaults as soon as the engineer opens the link. Everything else stays exactly as in the MVP.

**Root cause:** only PROYECTO had a default. `newForm()` calls `fill({proyecto, estado})`, and `fill()` assigns EVERY field explicitly (`d.cliente||""`), so it was actively clearing CLIENT and CONTRACTOR to empty on every fresh open. The HTML inputs had no `value` either.

**Fix (index.html):**
- CLIENT default `GOBIERNO REGIONAL DE AYACUCHO` and CONTRACTOR default `GOBIERNO REGIONAL DE AYACUCHO - SEDE CENTRAL` — set both as the HTML `value` attributes AND in `newForm()`'s `fill()` call, so the defaults survive first paint and "Nueva NCR".
- PROYECTO default corrected to the full MVP text (was truncated after "PENAL DE YANAMILLA"): `… HASTA EL TRAMO AY-729 (PTAR) LONGITUD 2.38 KM, EN EL DISTRITO DE ANDRES AVELINO CACERES - PROVINCIA DE HUAMANGA - DEPARTAMENTO DE AYACUCHO`, in both the HTML and `newForm()`.
- SUPERVISIÓN stays empty (the MVP shows it empty — placeholder only).
- The example ("Cargar ejemplo real") still loads the original Lircayccasa values (Municipalidad / Consorcio ECOPSA) — it overrides the defaults, as intended. Saved NCRs keep their own values when opened.
- JS syntax checked (node --check on the inline module script); redeployed; live file byte-identical to local (75,637 bytes).
- Verification in the live app: short browser check (fresh form via "Nueva NCR", no save) — result recorded in chat, not here.

## Round 8 (2026-11-15, 00:21 IST) — "MVP only": form + document aligned exactly to the Muse MVP

Snehil: the earlier corrections were Kenny's messages — make the app as per the MVP only, nothing else, only like the MVP. Kizie read the MVP end-to-end in a live browser (https://muse.ai/s/no-conformidades-ubs-xexl6xgxkrxbfrxbxu/...) and aligned the form + document to it.

**MVP ground truth (live read 2026-11-15 00:23 IST):** no PIN, no list, no save, no status, no download, no NCR number; header code GDC-NC-2026; title "NO CONFORMIDADES" (small "FORMATO" above); S1 intro ends "...sin ellos el documento no se puede registrar."; proyecto/cliente/constructor pre-filled (full road text / Gobierno Regional / Gobierno Regional - Sede Central), supervisión empty (placeholder "Nombre de la supervisión..."); FECHA empty; no placeholders on progresiva/plano ref.; "4 FIRMAS" (Residente de Obra + Supervisor de Obra with CARGO, 4× FIRMA ADICIONAL (OPCIONAL) nombre-only); document generates ALWAYS, even with missing data; doc header "CÓDIGO GDC-NC-2026", "PÁGINA 1"; doc FIRMAS 2×3 titled only RESIDENTE + SUPERVISOR; REGISTRO note "Registro generado automáticamente..."; back button "← Volver al formato"; Ctrl+P instruction; no "*" on labels.

**Changes applied (index.html, 64 replacements, JS syntax-checked, redeployed, live file byte-identical 76,251 bytes):**
- Header code back to **GDC-NC-2026** (form + document). Round 6's ECOP-GC-FR-012 was the spreadsheet's template code, NOT the MVP's — reverted.
- Title "NO CONFORMIDADES" (small "FORMATO" above) in form + document.
- "4 FIRMAS" + the MVP's full intro; SIG_ROLES now Residente de Obra + Supervisor de Obra + 4× FIRMA ADICIONAL (OPCIONAL); CARGO field only on the first two; document's second title changed **ESPECIALISTA DE CALIDAD → SUPERVISOR DE OBRA** (this settles the round-5 discrepancy in favour of the MVP; Snehil's round-5 words said Especialista, the MVP says Supervisor).
- Document generates ALWAYS — the "missing fields" block on Generar documento is removed. Save still requires all fields.
- FECHA empty on fresh open (todayISO defaults removed from fill/newForm/init).
- Exact MVP wording: S1 intro, items intro, s5 intro (ES + EN); descripcion placeholder added; progresiva/planoRef placeholders removed; "← Volver al formato"; Ctrl+P instruction as the doc note; REGISTRO auto-note in the document; doc headings "1. / 2. / 3." with periods; doc items-table headers in full (Item, Etapa de obra, Responsable de no conformidad, ...); doc impact line "Impacto: ☐ Leve ..."; doc header page "PÁGINA 1"; "*" removed from all field labels; PENDIENTE pill reworded ("Pendiente. Falta N cosas.").
- Document no longer shows ESTADO (the MVP document has no status row); the N.º NCR row stays.

**KEPT (product features the MVP lacks, because they are the app's purpose — Snehil to confirm if any should go):** PIN gate + Cambiar PIN (1–2 authorized users); list view with search/filters; Firebase save; N.º NCR number field with sequential suggestion (David assigns); ESTADO field + status workflow + audit; "Descargar documento" button (Snehil's round-5 ask); photosHelp compression note; offline drafts/autosave.
- Verification: live browser check of the fresh form + generate-with-missing-data — result recorded in chat, not here.
- Storage test (2026-11-15 ~00:31 IST): a complete test NCR (GDC-NC-2026-001, all fields, 1 photo with caption, 1 drawn + signed signature, estado En corrección) saved live ("Guardado en Firestore: GDC-NC-2026-001 (confirmado por el servidor)") and read back from Firestore via REST: every field present, 1 photo doc (caption + 16 KB dataUrl), all 6 signature records (Residente signed with name + timestamp + 5.7 KB drawn image; Supervisor + 4 additional unsigned), 4 audit entries (Creada, Estado Abierta → En corrección, Foto agregada, Firma). Test record + subcollections deleted; counter back to 1; 0 NCRs; PIN 2026.
