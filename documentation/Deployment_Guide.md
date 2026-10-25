# Local launch and repository publishing

Mandatory local run after installing requirements: `streamlit run app.py`. No API key, AI provider or database is required. All twelve workspaces and delivered reports work with cached inputs. Numerical reproduction: `python run.py --reproduce`.

The final challenge requires a public or judge-accessible private GitHub repository. The public source repository is https://github.com/CodeJediX/aegis-quantedge. The live application is https://quantumx-aegis.streamlit.app/ (verified 25 October 2026). For publishing a separate copy from an extracted folder, initialize Git, review files and publish to a repository the team owns:

The deployed service uses Streamlit Community Cloud, branch `main`, entry point `hosted_app.py`, Python 3.11, and no secrets or payment details. Its read-only SQLite research store rebuilds from verified snapshots on startup. Shared saves are disabled. See `Hosted_Database.md` for storage details; `render.yaml` is an unused alternative.

```powershell
git init
git add .
git commit -m "QuantEdge final research submission"
git branch -M main
git remote add origin https://github.com/YOUR_ACCOUNT/YOUR_REPOSITORY.git
git push -u origin main
```

The account/repository placeholders in this deployment instruction are values the team must supply, not a published deliverable URL. Ensure judges have access if private. No secret is needed in `.env`; do not commit Streamlit secrets or personal credentials. Check approved-data sharing terms before publishing a public repository; a private judge-accessible repository is permitted by the brief.

To reproduce the hosted configuration on Streamlit Community Cloud, connect the repository, select `hosted_app.py`, choose Python 3.11, and deploy using requirements.txt. No secrets are needed. Bundled outputs avoid long startup computations. If storage limits matter, preserve inputs, outputs used by the app, reports and methods; exclude only regenerable QA material. Free hosting can sleep when idle.

Presentation source requires a separate optional Node authoring environment with @oai/artifact-tool. A provided PPTX and PDF need no such environment to view. For rerendering, point `ARTIFACT_TOOL_MODULE` to its artifact_tool.mjs and run `node scripts/build_pitch.mjs`; AEGIS_ROOT optionally selects the project root. Source charts use computed evidence rounded to six decimals for Excel preservation. Review a regenerated deck and speaker timings before presenting.
