"""Build a native signed APK using installed, free Android SDK tools (no Gradle).

Signing material stays outside the source tree and is never added to a ZIP.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"mobile/app/src/main"
BUILD=ROOT.parent/"aegis_mobile_build/native"
KEYS=ROOT.parent/"aegis_mobile_build/keys"


def run(args,env=None):
    subprocess.run([str(x) for x in args],check=True,env=env)


def prepare_assets(destination):
    from sys import path
    path.insert(0,str(ROOT))
    from src.database import research_version
    destination.mkdir(parents=True,exist_ok=True)
    originals={"adjusted_prices.csv":ROOT/"data/snapshots/adjusted_prices.csv",
        "risk_free.csv":ROOT/"outputs/tables/risk_free.csv","allocations.csv":ROOT/"outputs/tables/allocations.csv",
        "quantumx_logo.png":ROOT/"assets/quantumx_logo.png",
        "technical.pdf":ROOT/"reports/Current_Technical_Report.pdf",
        "tear_sheet.pdf":ROOT/"reports/Current_Investment_Tear_Sheet.pdf",
        "ai_usage.pdf":ROOT/"reports/AI_Usage_Details.pdf"}
    for name,source in originals.items():
        if not source.is_file():
            raise FileNotFoundError(f"Required mobile asset is missing: {source}. Run scripts/build_current_deliverables.py first.")
        shutil.copyfile(source,destination/name)
    meta=dict(dataset_version=research_version(),data_through="2026-09-30",capital_USD=10000000,
        training_end="2018-12-31",test_start="2023-01-03",models_native=["Historical","Gaussian portfolio log"],
        processing="Exact daily simple-return aggregation, 10bp prior-drift L1 turnover cost; one-day gross risk and stress",
        sha256={name:hashlib.sha256((destination/name).read_bytes()).hexdigest() for name in originals})
    (destination/"dataset.json").write_text(json.dumps(meta,indent=2),encoding="utf-8")


def tools():
    sdk=Path(os.environ.get("ANDROID_SDK_ROOT",os.environ.get("ANDROID_HOME",str(Path.home()/"AppData/Local/Android/Sdk"))))
    build_tools=sorted((sdk/"build-tools").iterdir(),key=lambda x:tuple(int(v) for v in x.name.split(".")))[-1]
    java_home=Path(os.environ.get("JAVA_HOME",r"C:\Program Files\Android\Android Studio\jbr"))
    java_bin=java_home/"bin"
    env=os.environ.copy();env["JAVA_HOME"]=str(java_home);env["PATH"]=str(java_bin)+os.pathsep+env["PATH"]
    android=sdk/"platforms/android-35/android.jar"
    if not android.is_file():
        raise FileNotFoundError("Android API35 platform is required; install it using Android Studio's SDK Manager.")
    return sdk,build_tools,java_bin,android,env


def compile_apk(source,manifest,res,assets,work,out,alias="aegis",extra_classpath=None):
    sdk,bt,jb,android,env=tools()
    for part in ["classes","generated","dex"]:(work/part).mkdir(parents=True,exist_ok=True)
    run([bt/"aapt2.exe","compile","--dir",res,"-o",work/"compiled.zip"],env)
    run([bt/"aapt2.exe","link","-o",work/"resources.apk","-I",android,"--manifest",manifest,"--java",work/"generated","--auto-add-overlay","-A",assets,work/"compiled.zip"],env)
    sources=[*source.rglob("*.java"),*(work/"generated").rglob("*.java")]
    classpath=str(android)+(os.pathsep+str(extra_classpath) if extra_classpath else "")
    run([jb/"javac.exe","-encoding","UTF-8","--release","8","-classpath",classpath,"-d",work/"classes",*sources],env)
    with zipfile.ZipFile(work/"classes.jar","w") as z:
        for file in (work/"classes").rglob("*.class"):z.write(file,file.relative_to(work/"classes").as_posix())
    d8=[bt/"d8.bat","--lib",android,"--min-api","26","--output",work/"dex"]
    if extra_classpath:d8.extend(["--classpath",extra_classpath])
    run([*d8,work/"classes.jar"],env)
    shutil.copyfile(work/"resources.apk",work/"unsigned.apk")
    with zipfile.ZipFile(work/"unsigned.apk","a") as z:
        for file in (work/"dex").glob("*.dex"):z.write(file,file.name,compress_type=zipfile.ZIP_STORED)
    run([bt/"zipalign.exe","-f","-p","4",work/"unsigned.apk",work/"aligned.apk"],env)
    KEYS.mkdir(parents=True,exist_ok=True)
    secret_file=KEYS/"release-password.txt";key=KEYS/"aegis-release.jks"
    if not key.exists():
        secret_file.write_text(secrets.token_urlsafe(40),encoding="utf-8")
        env["AEGIS_APK_PASSWORD"]=secret_file.read_text().strip()
        run([jb/"keytool.exe","-genkeypair","-keystore",key,"-storepass:env","AEGIS_APK_PASSWORD","-keypass:env","AEGIS_APK_PASSWORD","-alias",alias,"-keyalg","RSA","-keysize","3072","-validity","10000","-dname","CN=QuantumX AEGIS, O=Local APK Distribution, C=LK"],env)
    env["AEGIS_APK_PASSWORD"]=secret_file.read_text().strip()
    out.parent.mkdir(parents=True,exist_ok=True)
    run([bt/"apksigner.bat","sign","--ks",key,"--ks-key-alias",alias,"--ks-pass","env:AEGIS_APK_PASSWORD","--key-pass","env:AEGIS_APK_PASSWORD","--out",out,work/"aligned.apk"],env)
    run([bt/"apksigner.bat","verify","--verbose","--print-certs",out],env)
    run([bt/"zipalign.exe","-c","-p","4",out],env)


def main():
    BUILD.mkdir(parents=True,exist_ok=True)
    assets=BUILD/"assets";prepare_assets(assets)
    res=BUILD/"res";shutil.copytree(SOURCE/"res",res,dirs_exist_ok=True)
    (res/"drawable").mkdir(exist_ok=True);shutil.copyfile(ROOT/"assets/quantumx_logo.png",res/"drawable/quantumx_logo.png")
    out=ROOT/"mobile/releases/QuantumX_AEGIS_1.0.0.apk"
    compile_apk(SOURCE/"java",SOURCE/"AndroidManifest.xml",res,assets,BUILD/"app",out)
    record=dict(apk=out.name,bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),
        native=True,webview=False,internet_permission=False,min_android_api=26,target_android_api=35,release_signed=True,
        notes="Local distribution certificate; private signing key is outside the repository. Emulator/runtime checks recorded separately.")
    (ROOT/"mobile/releases/APK_MANIFEST.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(record,indent=2))


if __name__=="__main__":main()
