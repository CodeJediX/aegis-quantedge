"""Install and test native APK using Android framework instrumentation, no GUI shim."""
from pathlib import Path
import json
import os
import subprocess
import sys
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from build_mobile import ROOT,BUILD,compile_apk,tools


def main():
    sdk,_,_,_,_=tools();adb=sdk/"platform-tools/adb.exe";device=os.environ.get("AEGIS_TEST_DEVICE","emulator-5554")
    qa=BUILD/"instrumentation";qa.mkdir(parents=True,exist_ok=True);res=qa/"res/values";res.mkdir(parents=True,exist_ok=True);(res/"strings.xml").write_text('<resources><string name="app_name">AEGIS tests</string></resources>',encoding="utf-8");assets=qa/"assets";assets.mkdir(exist_ok=True)
    test_apk=qa/"AEGIS_Runtime_Tests.apk"
    compile_apk(ROOT/"mobile/tests/android/java",ROOT/"mobile/tests/android/AndroidManifest.xml",res.parent,assets,qa/"build",test_apk,extra_classpath=BUILD/"app/classes.jar")
    for apk in [ROOT/"mobile/releases/QuantumX_AEGIS_1.0.0.apk",test_apk]:subprocess.run([str(adb),"-s",device,"install","-r",str(apk)],check=True)
    run=subprocess.run([str(adb),"-s",device,"shell","am","instrument","-w","com.quantumx.aegis.qa/.SmokeInstrumentation"],text=True,capture_output=True,timeout=240)
    print(run.stdout);print(run.stderr)
    (BUILD/"instrumentation_output.txt").write_text(run.stdout+run.stderr,encoding="utf-8")
    if "result=PASS" not in run.stdout:raise AssertionError("Native instrumentation did not pass. See local instrumentation_output.txt.")
    shots=ROOT.parent/"aegis_mobile_build/runtime_screenshots";shots.mkdir(exist_ok=True)
    subprocess.run([str(adb),"-s",device,"pull","/sdcard/Android/data/com.quantumx.aegis/files/qa-screenshots/.",str(shots)],check=True)
    api=subprocess.check_output([str(adb),"-s",device,"shell","getprop","ro.build.version.sdk"],text=True).strip()
    record=dict(result="PASS",verified_utc=datetime.now(timezone.utc).isoformat(),device="Android emulator",android_api=int(api),instrumentation="Android framework; actual signed native APK",checks_output=run.stdout.strip(),screenshot_count=len(list(shots.glob("*.png"))),physical_device_tested=False,notes="Read-only emulator mode preserves the existing AVD; app data changes are ephemeral. App has no internet permission.")
    (ROOT/"outputs/results/mobile_runtime_checks.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":main()
