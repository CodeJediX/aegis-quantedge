# Submission manifest

AEGIS / Quantum-X | QuantEdge 1.0 Final Challenge | prepared 24 October 2026; release verified 25 October 2026

Data cutoff: 2026-09-30. Technical report 13 pages plus editable Word companion; tear sheet 1; memo 1; pitch 12 slides and 660-second rehearsal target. All five technical layers and twelve workspaces are implemented.

Source repository: https://github.com/CodeJediX/aegis-quantedge (private; ensure judge access). **Pending external actions:** complete cloud provisioning and verified deployment, and record independent human-team validation and the final investment decision. No live app URL or human approval is claimed until verified.

The application runs locally with one command after dependency installation: `streamlit run app.py`. Numerical/PDF report reproduction: `python run.py --reproduce`. Optional pitch authoring uses a separate Node artifact-tool runtime; the provided PPTX/PDF is ready to open.

All CSV/JSON outputs and figures are genuine executed results. Synthetic data appear only in numerical unit-test fixtures; the hypothetical scenario is explicitly an assumed shock. No model result is invented.

Virtual environments, secrets, intermediate deck builds and external QA render directories are excluded. This inventory omits its own checksum to avoid self-reference.

| File | Bytes | SHA-256 |
|---|---:|---|
| .env.example | 509 | 3acb6bce2e45b6fa75b7eeaca8717383896e77de399cc8f9e273a16358863924 |
| .gitattributes | 129 | 5cfc825676fbb0cd1e7b381f9aeadea517cb70e9a59f9e981babc5dc2073f7bd |
| .gitignore | 125 | 6bec6d82c3cde22b714c365e94a5ede8958c02588a809688857b4b6503cb809e |
| .streamlit/config.toml | 214 | 5aebd9a63a3346345b1a7826f9f148dc326f904ad71c13fa9ac0eb384996da26 |
| app.py | 6173 | 1c58f2ff3e68c01c1abd7df0a43360905d60d043541817ee6021e94781a3a8e7 |
| assets/style.css | 1600 | 459859d4a0491e9f0d281fe6e35cebd54acb6e1747116bee96940c6e27f9fece |
| data/metadata/fred.json | 302 | b1bb1b8aa1d13460942ec2e31244d84369e19c0bf1dd5abc48ab8de64e21cef3 |
| data/metadata/prices.json | 405 | 7748ac014c2bafaf3f333254958900fe5e7d56faf1bc1abb0e7c8f5c3e5a6e9c |
| data/README.md | 760 | 0fc146e39879a0fa43b7615789abcc17e237a6848990ce6377d7901c4d1dfd0c |
| data/snapshots/adjusted_prices.csv | 595496 | 7948d99f7ba6b79b6c8425ecd48482d76d914115088adc84c3c8ff90df0f2af1 |
| data/snapshots/DTB3.csv | 95398 | 40897a0518d118159f8af98fa4e57b124bec9ceb419bed747e838b7195594eb2 |
| documentation/AI_Disclosure.md | 1697 | 284ad4308573315b92d433f93b437673788c6b916b88cb75fbfed46910a5d76e |
| documentation/Assumptions_and_Limitations.md | 6226 | cceb0732c7432d9cb6468eb7fe442f4a86000eac36f2961c1a1f654a67ebbc11 |
| documentation/Data_Governance.md | 2020 | c728825016b102ed96749edb17ef7ce8a7a1d8f48311cc786991bdd7cb8a7f8b |
| documentation/Deployment_Guide.md | 2484 | 4db8926690c770210e7d0e75fb79f6a41a42e2d75c1a6e2b9d904db7d4f5f1c4 |
| documentation/Final_Competition_Audit.md | 3668 | 906cf67db335000060a70103293255ad99a2c431c5a4342a4eca0a2b75ddf9c5 |
| documentation/Hosted_Database.md | 4188 | 2179ce814e6d06b6b9418475e688a0ba144fc1a779c545fccbeeb6abdd2c5d83 |
| documentation/Judges_QA.md | 6558 | 3b9ba2526319d30901ffa942fe9d7f2d8d44536bd3f93bcde63bb3f1629a84f7 |
| documentation/Methodology.md | 4125 | 5cfd8e1140f23aecd73ac1101ddad00a3c5d43d9ca2751f9742ce016c6f2e2fc |
| documentation/Prior_Work_Audit.md | 1656 | 130911efcfbba63d4e6f15e600af5e7300379f7d12464c851bbd02d50db83e66 |
| documentation/Requirements_Traceability.md | 6422 | d17848aa315209256040c215859b908055823cb87df8e9a83e280ae77e495f5e |
| documentation/Sources.md | 3160 | c5ea5cb5bc714cdc243a6b5ab2390bc0e379af958464396b45735bf0de5ceffb |
| documentation/Team_Approval_Checklist.md | 1391 | 256a0fece2a24a24754383e797a61fdda6c4dd8f8bbae88c80ace2bea34507c8 |
| documentation/Testing_and_Validation.md | 7593 | d8747c49301d6ec710c4ebd8bfb41b62c974c6eb8bedf5ec3098c60f77e93fd7 |
| outputs/figures/allocation.png | 31191 | a9759d848a851dd67597da1ecfd56ef7341966c85f8c3e37b3c38ad9e731669a |
| outputs/figures/backtest.png | 135847 | 07bba54b2f55f64f0c36571841e36777bfce07baccf4a4fa0234238fc1928751 |
| outputs/figures/evt.png | 61950 | 7af919f0bbafdc7516c289ee5b773dd62977d1601f0c331a8afa0dd1a8d3d9bf |
| outputs/figures/frontier.png | 59963 | 32dde1a4f2f020adb0d6cb3658ca128c9d20e5c7ae22d2dc7949f0187b4a3fc8 |
| outputs/figures/performance.png | 203398 | c07d0327deedc5178a21617279df8c34a719deebc9e1df9fc8f1fa350f3fe8c9 |
| outputs/figures/risk.png | 38657 | 34bc62d2c0fc12a34e7aa347aa467160d4b1b0e8988279e5781e98ccccb2687e |
| outputs/figures/stress.png | 40249 | 3432a3d316f50c59dd98369da2f6f3e0822a10b9c8484515433cd99256b321e6 |
| outputs/results/app_checks.json | 2452 | 3b71b517450c454260f97ae8aef000975454fecb287b913868f7b6e3941ba1be |
| outputs/results/data_audit.json | 760 | c8f676d9d716c88fe7e0bbe29ae02b3b033d60854494c5a41f548ddac98230f1 |
| outputs/results/summary.json | 3900 | 034204771912a52409eb3118c2579c0fb19a19a597fe981d77f7c755e00d1013 |
| outputs/tables/adf.csv | 555 | dfe74f476beb9c22575f0bb6901a52884dc88701f2da60c54c19c8afc1eac575 |
| outputs/tables/allocations.csv | 429 | 6a58ff88213acbc32ff927441f73519c9dd8e892710c0808e90540fb8265c275 |
| outputs/tables/backtesting_development.csv | 4471 | 73fe40baa4d16db1ecc052150c46c8ed854c334691fe3d4ec72cdb0f2881b982 |
| outputs/tables/backtesting_test.csv | 4435 | 6b77e3675c4c45d5cf5ef90bde753cbe150a17b40984bfc4342b595b219f101a |
| outputs/tables/capm_training.csv | 400 | dfd02e8144d8d41ee69fa47ed21eaa8e560c9eb3638eb7400d402943be8f5107 |
| outputs/tables/cost_sensitivity.csv | 702 | 931b4362f8f41ccfc5449846600d0a932539c6d7c17f65411892f5b1dba844ae |
| outputs/tables/coverage.csv | 285 | 7626993f11dc33f76e88f86d6d569e61d56c062046557a754405b4d3832333f4 |
| outputs/tables/crisis_paths.csv | 211243 | 828f7baf050971b2cb8c70c5a2a8da3d3b5fa7ce6675bdb4e4aa7c7487a3d09f |
| outputs/tables/data_flags.csv | 16759 | 70d732ea5ba435896e66a5f9931b71d380202b341925ba84ba08117732b1c9e6 |
| outputs/tables/diversification.csv | 405 | cb918ed5a2ef58f6f6e2eb1073a8ac9f15f072c3bb6ba2abfdf1da6fd6621f62 |
| outputs/tables/evidence_ledger.csv | 4065 | 80aed7eb0e1d000551c7b6d9a26fa6ca2b2b79ad107b9f840b9e2ae0fac141b9 |
| outputs/tables/evt_sensitivity.csv | 967 | c056de43b588a039cccb4ec925bb4695916e86a0bf368cfa9eb82b015972d26a |
| outputs/tables/forecasts.csv | 2857305 | 35b8098d2b1e1ef4fe505b2b6dbb9ee7409eed8e28237b9790c2fd12be381f59 |
| outputs/tables/frontier.csv | 1495 | 1d77b125ed5ceca6d611c0d78a5a7e0df8d855ce50ad5e4b2d458766cf0d39d3 |
| outputs/tables/kpis.csv | 3474 | db160cd36846281544f252a8c8d9f136870d2723d108b2ec30d79eca86401a66 |
| outputs/tables/log_returns.csv | 889796 | 2e81611254f048a03087e869210a86798fdc6e35dd6e68202a401d2821b5bb01 |
| outputs/tables/mc_convergence.csv | 171 | 3a19aa5ac3e366770602435eec43410a4f969d2a39cf0145c9c7fdade655699c |
| outputs/tables/policy_sensitivity.csv | 136 | f82e6cde876553d2dda74fa5d447e46c8dd084ff6c7f9af65747e09b13a8d5f0 |
| outputs/tables/portfolio_returns.csv | 544026 | 66459ba7e445bc9d8e77f39ac2d1019d02c9f25d3df49d1eec99f88b62fc52fd |
| outputs/tables/risk_contributions.csv | 605 | 7e01a737f2fa9a83ecc5316c0cedac5c38cd728cf0ca714720b4f1cd1942558b |
| outputs/tables/risk_free.csv | 187833 | 5fda32e98c162fdb74da4f0910dab41b84feae015d0b7286605b5fc84a7b5ac6 |
| outputs/tables/risk_snapshot.csv | 887 | 3e699361c0c677cf5a680951365e91b34136b7485b2dc29049acbbf7e42c706f |
| outputs/tables/scorecard.csv | 538 | 53b9cf409b51f887909ac6c9fcee197450140306c5a39d3cf7cda79072e548be |
| outputs/tables/simple_returns.csv | 889851 | 316ef357df16aee676ace14d15e68fbf19afa3e2fef5eb09ea5659ffcd5cec41 |
| outputs/tables/stress.csv | 4445 | 5be196060efed2fbf74261d689600c203925c596a4b6eeee6ed1f2ed89361e68 |
| presentation/Final_Pitch.pdf | 360487 | 622f983e362e4046b67a812900eef667493c1eb3124932d20525dd8dea5303bb |
| presentation/Final_Pitch.pptx | 64469 | 9e173258ca7f2f58d68db4ca88fbdedb42ae29cad71299c60e278c805ce1457a |
| presentation/pitch_data.json | 8802 | a490dcc6fd1b125275c30b8111bc9ad9e5b8e8c04a50e1afe535a43e589c607f |
| presentation/Rehearsal_Script.md | 8334 | d6d85661cfe6a10acb241f59478bceacddf6b1a67f7c59ba56f369e57bc2335e |
| presentation/Speaker_Notes.md | 3535 | c3e34c95641c4cc9bd2c6df8d292e6c96ba71f5a0726c1e0e24a03e222bdd6b9 |
| README.md | 9605 | 471ef058594479693a6e2a392243bb993abba9f6a203913bbbce16bda6ee1610 |
| render.yaml | 647 | 87327f69ab3ee610a687e3cd69d0fc1fe7a74523fa52629c53b126b8a5e26aeb |
| reports/Executive_Tear_Sheet.pdf | 3348 | a04f0a265c3b3484caecb3863978fafb308cf9bbd30a234625d399cf38b9c2d1 |
| reports/Investment_Committee_Memo.pdf | 3462 | 0c26cd8953d4a7be84ad67e7e0d68ff5e9e9098e55d0021c5c3d5cd3c584d55e |
| reports/Technical_Report.docx | 538591 | 906b83765232f92a44f9e2e88117842cc3e3d8c17905786eb2a8ce75635e7803 |
| reports/Technical_Report.pdf | 593615 | b168f0ee5aad73844144171757f40472bdaab4f3976911388284034c8bdb10b1 |
| reports/Technical_Report_Source.md | 21581 | 7ea9b52b4b172061616be2059788dc718e1563cec4511f752c93dad4add99137 |
| requirements.txt | 205 | e8122c294ea0f114bba6ff64bd6f21fc5acfd1b14304c5bd15051fe65bc26e82 |
| run.py | 8570 | 0f0d276188ac13278bdb2ff53013b2a515122de74492e2a5abfae3f5e9a00f4f |
| scripts/bootstrap_database.py | 648 | adbadf76aec9e68b558e4e16ebf0362b0bdad6880dbc3be5106bc459c58261f2 |
| scripts/build_pitch.mjs | 5546 | 44d7efbb19a80c9be3468247c750a1bf5b258c3e146bcdd04b10845ba93e452c |
| scripts/build_word_report.py | 6306 | ec2319343d3783f46ddf38670e0ba13c613ed6e94faf90c9f9cc0765802a0b35 |
| scripts/check_app.py | 2653 | 9a22b920305b9af835c20bd1ad69fdec11b9a08ea250972e12abcae76bfea8e7 |
| scripts/check_database_app.py | 2693 | 2f000cc8a575c1bb2c5d88e8e60b8ac1c60580978f4b8a8cd60a25e8abac8086 |
| scripts/package_submission.py | 4252 | ef7ded8385928f6d9d2b5b98dc7634db9516d8e04ea9c50c2b42061eb350a270 |
| scripts/prepare_qa.py | 8671 | b772441f1d801248ed01a290afbf875bfc8277351b6ecf03bbff2433212ed116 |
| scripts/rehearsal.py | 8813 | a8287aa7e6418a86bbe2d29dbcc0a91f96e6c7ff72bb941ff5fade0318763e07 |
| scripts/render_pitch_pdf.py | 622 | 1c56143674c98017fef4a015a7c3add5993844526bec92250f8e4fb65c61dd91 |
| scripts/verify_manifest.py | 884 | 6d7cb242ccba631508f68a25e8951840ff1b28196896064794a4d6426f543119 |
| src/__init__.py | 50 | e39401b15960178f95750ddc281533aa893bc74b82f705b7be627b53d8626c38 |
| src/backtesting.py | 6147 | 8e7b6bbad01fa14893b32ded6320f9e3cbd838cf92a5b18900b6b0e4576c4a90 |
| src/config.py | 1382 | 44be4ba3ce177d25e223861eaa5e0f0e8fe3cea9780caa312772fd4e71a53189 |
| src/data.py | 7665 | c7a0efff5266bbd2d688ccd909a7541ab72cc166b0c8277175b4e93e82a89a1e |
| src/database.py | 12067 | 208282f64fe8619f6a584b006555e7021e86fb5ec2611b841c4169eb5ef5a5d3 |
| src/decision.py | 6090 | e2831ac984f2db0559ad6d27826583ae51c6d48c7536b1cc65a82deb295120c6 |
| src/evt.py | 3391 | b55185e4f13279376a310d8fa7f8e9db235307521fa757322964060cf5fe18e8 |
| src/figures.py | 4973 | 4440a979a460563e51452b41c0155da6bc2f4db372a46a7321a04f423e75efd7 |
| src/portfolio.py | 5702 | 669cb3a2070e09cf50666e59e3b304f36565b55262df26b080ffe4bc8567ea96 |
| src/reporting.py | 42235 | 74a74a191b27a003ea87557a22d1d8a34cf99810f3b1dfb76558e06e7a27873d |
| src/risk.py | 3920 | 603ea775be3877b95d5128bf909b054168e21727ffa838081382c7d2fa300b40 |
| src/stress.py | 3244 | 7a7ef52a33b7d3fb48cbacd9c6e43b02af1d11374c21b040e6a164db17ccf0bd |
| src/ui.py | 25583 | 7f31ddfe342fffcfde7c4dc58e29c3c2dfc55c31e61f5fd96c9f41eda5f06acb |
| tests/test_database.py | 4285 | bbc977869db9cab561be3bc5277c67e4c23558e3e4c53ffbe6ce6d9d894ff60b |
| tests/test_integration.py | 2623 | bdffa0d31a01610938b6830cfcddf40e7d306c2686d583060328272cb922c781 |
| tests/test_quant.py | 5300 | e1251b9da49246be8b9f2bea3aef27457e9157596bc92ac8def210da45310832 |
