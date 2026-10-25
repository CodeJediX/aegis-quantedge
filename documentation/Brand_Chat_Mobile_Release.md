# Brand, website guide and native Android release - 26 October 2026

The user supplied the QuantumX AEGIS PNG logo and requested it as the main identity before new screenshots. `assets/quantumx_logo.png` preserves the original file bytes. The website uses a light logo plaque for legibility, actual snapshot-verification loading status, a short welcome transition and a reduced-motion alternative. Essential content is not delayed by an artificial sleep.

## Conversational website guide

The floating Ask AEGIS control accepts typed questions, retains a bounded session history, displays the allocation/dataset context for each answer and opens the suggested evidence workspace. It uses deterministic intent rules and current selected values; it does not call a generative model, place trades, grant human approval or access outside facts. Website chat text is processed by Streamlit in session memory, not sent to an external LLM. The existing Research guide route remains available.

Typed-input, evidence-navigation, clear and welcome-replay checks passed9tests. A visual check exposed that an explicit script rerun closed the popover; callbacks and a stable welcome placeholder repaired that interaction. Token boundaries also prevent accidental intent matches inside unrelated words. The ordinary numerical/application checks remain in force:49unit/integration/database tests,28base interface checks and129expanded interface checks passed.

## Independent native app

The APK uses native Android views, a Java numerical engine and native canvas charts. It has no WebView or internet permission. It bundles verified historical prices, lagged risk-free rates, reference allocations and the three requested PDFs. It provides offline custom weights, local saved profiles, historical/Gaussian risk, selected rolling Historical99 validation, stress/what-if controls, local guide chat and Android document export. The web app retains MC/EVT/state and optimizer features; the APK's smaller model scope is stated explicitly.

The Java engine passed222comparisons with Python across six allocations, three confidence levels, performance ratios, risk models, stress/contributions and actual rolling validation. Maximum observed absolute difference:3.06e-13. The actual signed APK passed24Android framework instrumentation checks on an API36 emulator, including a file-picker save whose exported bytes exactly matched the bundled technical PDF. The test used read-only emulator mode to preserve existing AVD state. No physical-device or universal OS/device certification is claimed.

APK signing material lives outside the repository and is excluded from delivery archives. `mobile/releases/APK_MANIFEST.json` identifies the final APK hash and installation/API information. `mobile/README.md` provides installation, source structure and a working Windows SDK build command. No paid hosting, paid APIs or payment details were used.

## Current documents and screenshots

- `Current_Technical_Report.pdf`:15pages, consisting of the unchanged13-page locked study plus two current software/verification pages. The original ADJUST terminology is explicitly related to current REVISE; default policy failures remain visible.
- `Current_Investment_Tear_Sheet.pdf`:1page for the reference allocation, identified with dataset, date, capital and pending human approval.
- `AI_Usage_Details.pdf`:2pages covering material Codex assistance, deterministic chat behavior, native scope, checks/privacy and genuinely pending independent human review.

Current files are offered separately from selected-allocation generated reports and the locked research package. Original PDF/Word/pitch materials are retained. The final screenshot ZIP is captured after deployment of this release, includes only changed/new feature views relative to the earlier83-image bundle, and adds native-app captures. Partial pre-logo captures are excluded. Screenshot captions identify custom allocations and any adjusted research limits; they are never relabelled as approved mandates.

Human investment approval remains PENDING. The default automated recommendation remains REVISE, with16.71% training net drawdown,15.23% terminal scenario loss and17.52% worst historical replay drawdown against15% proposed limits.
