# Local launch and repository publishing

Mandatory local run after installing requirements: `streamlit run app.py`. No API key, AI provider or database is required. All twelve workspaces and delivered reports work with cached inputs. Numerical reproduction: `python run.py --reproduce`.

The final challenge requires a public or judge-accessible private GitHub repository. The source repository is https://github.com/CodeJediX/aegis-quantedge (private). Judges must receive access before submission. For publishing a separate copy from an extracted folder, initialize Git, review files and publish to a repository the team owns:

GitHub authentication was rechecked on25 October2026 and succeeded. The earlier invalid-credential blocker is resolved. The user requested hosting and SQL persistence after the initial local handoff; see `Hosted_Database.md` and `render.yaml` for that deployment path. No cloud deployment is claimed until the actual provider state and live URL are checked.

```powershell
git init
git add .
git commit -m "QuantEdge final research submission"
git branch -M main
git remote add origin https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY.git
git push -u origin main
```

The account/repository placeholders in this deployment instruction are values the team must supply, not a published deliverable URL. Ensure judges have access if private. No secret is needed in `.env`; do not commit Streamlit secrets or personal credentials. Check approved-data sharing terms before publishing a public repository; a private judge-accessible repository is permitted by the brief.

Optional Streamlit Community Cloud: connect the actual repository, select `app.py`, choose Python 3.11, and deploy using requirements.txt. The mandatory application does not need secrets. Bundled outputs avoid long startup computations. If storage limits matter, preserve inputs, outputs used by the app, reports and methods; exclude only regenerable QA material. No deployed service has been created by local packaging.

Presentation source requires a separate optional Node authoring environment with @oai/artifact-tool. A provided PPTX and PDF need no such environment to view. For rerendering, point `ARTIFACT_TOOL_MODULE` to its artifact_tool.mjs and run `node scripts/build_pitch.mjs`; AEGIS_ROOT optionally selects the project root. Source charts use computed evidence rounded to six decimals for Excel preservation. Review a regenerated deck and speaker timings before presenting.
