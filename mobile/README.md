# QuantumX AEGIS native Android app

`releases/QuantumX_AEGIS_1.0.0.apk` is a signed, directly installable native Android application. It uses Android views, native canvas charts and a separate Java numerical engine. It has **no WebView and no internet permission**. Android8.0/API26 or newer is supported by the manifest; runtime testing was on an Android API36 emulator, not every physical phone.

## What works offline

- Decision desk with the original risk limits, actual failed checks and pending human approval.
- Five reference allocations and a seven-ETF custom editor with strict full-investment validation.
- Net performance metrics and a touch/keyboard-inspectable capital chart.
- Historical and Gaussian portfolio-log VaR/ES at90/95/99% confidence.
- Actual selected-weight rolling Historical99 validation, using756 prior returns per forecast, exact full/latest250 counts and Kupiec/Christoffersen diagnostics.
- Historical2008/2020/2022 replay, assumed funding squeeze, contribution accounting and equity/gold/rate/duration what-if controls.
- Private on-device named allocation library that survives an app restart.
- Local deterministic guide chat, Android PDF export and a user-controlled research-summary share action.

The web app retains additional Monte Carlo, EVT, volatility-state, optimizer and broader diagnostics. Native model scope is explicit; this APK does not pretend to run missing methods. Data are frozen through2026-09-30, SHA256-verified at startup and bundled in the APK. All dollar calculations use USD10m. The default remains REVISE with three policy failures.

## Install

Copy or download the APK to an Android8.0+ phone and open it. Android may ask you to permit installation from that browser/file manager. No account, subscription, payment details or API keys are needed. This is a local-distribution signed APK; Google Play publication is not claimed.

## Build on Windows

Use Python with the root requirements, JDK21 and the free Android SDK: platform35 and build tools36. Existing Android Studio installations include the required Java runtime. These commands do not use Gradle or a remote build service:

```powershell
python scripts/build_current_deliverables.py
python scripts/check_mobile_engine.py
python scripts/build_mobile.py
```

`ANDROID_SDK_ROOT`/`ANDROID_HOME` and `JAVA_HOME` override the detected SDK/JDK locations. Build intermediates go to `../aegis_mobile_build/native`, outside the repository. The app assets are copied from the original root snapshots/reports, avoiding separate edited data copies in source.

The build performs AAPT2 resource packaging, Java8-target compilation, D8 dexing, ZIP alignment and APK signing/verification. It generates a private local distribution key under `../aegis_mobile_build/keys` if one does not exist. **Preserve that private key and its password locally for future updates.** Signing material is intentionally excluded from Git and all delivery ZIPs. Rebuilding without the same key produces an independently signed installation, not an update of an existing install.

## Verification

`scripts/check_mobile_engine.py` compares222 Java outputs with independent Python results, at2e-9 tolerance; the observed maximum absolute difference was3.06e-13. It also checks invalid weights and what-if unit/additivity behavior.

With a running Android emulator:

```powershell
python scripts/check_mobile_runtime.py
```

The framework instrumentation installs the actual signed APK and tests navigation, real custom calculations/backtesting, saved-profile persistence across a cold activity restart, chat, rate controls, all three bundled PDFs, the actual Android document picker/export callback, exported-file byte identity and absence of internet permission. It passed24checks on API36. `outputs/results/mobile_runtime_checks.json` records evidence. Its test APK is generated outside the source tree and is not a user deliverable. Emulator screenshots are original PNG captures; physical-device certification is not claimed.

## Source map

`ResearchEngine.java` contains independent financial calculations, `MainActivity.java` contains native views and local storage/export flows, and `ChartView.java` draws interactive charts. Tests and build scripts are provided in `mobile/tests` and root `scripts`. No external generative AI runs in this app. Material AI-assisted development and pending independent human review are documented in the AI usage PDF.
