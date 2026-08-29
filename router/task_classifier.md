# Task classifier

Classify the request by the user's actual goal, not by an incidental file type. Select one primary class and zero or more secondary classes.

| Class | Signals | Typical outputs |
|---|---|---|
| research-question | idea, gap, hypothesis, PICO, feasibility | refined question, rationale, hypotheses |
| literature-review | find papers, systematic review, meta-analysis, PRISMA | search plan, evidence map, synthesis |
| study-design | cohort, RCT, target trial, RWE, protocol | estimand, eligibility, time zero, bias plan |
| protocol-ethics | IRB, ethics application, consent, protocol form | protocol sections, ethics checklist, completed template |
| sample-size | power, sample size, events per variable, precision | assumptions, method, reproducible calculation |
| data-preparation | clean data, deidentify, codebook, missingness profile | audit report, data dictionary, approved cleaning plan |
| statistical-analysis | regression, Cox, IPTW, missing data, power, sensitivity | analysis plan, assumptions, estimands, code route |
| manuscript-writing | outline, draft, revise, scientific writing, IMRAD | manuscript section or submission-ready draft |
| manuscript-review | review, peer review, referee, major/minor concerns | reviewer report, decision rationale |
| reviewer-response | rebuttal, response to reviewers, revision plan | point-by-point response and task table |
| revision-after-review | revise after comments, R1/R2, major revision, resubmit, tracked changes | revised manuscript, response letter, revision ledger, re-review |
| journal-lookup | known journal name, query journal, IF, JCR, CAS, 中科院分区, 新锐分区, review speed | structured journal metadata card with dated sources and missing-field status |
| journal-selection | select journal, scope, APC, impact, fit | ranked fit and submission cascade |
| citation-management | DOI, references, citation check, BibTeX, Zotero | verified references and normalized citations |
| figure-presentation | figures, plots, visual abstract, slides | publication figure or presentation artifact |
| project-management | project status, memory, release, reproducibility | project manifest, checklist, timeline |
| geo-analysis | GEO, bulk RNA-seq, DEGs, GEOquery | dataset rationale, reproducible pipeline |
| scrna-analysis | scRNA-seq, Seurat, Scanpy, cell annotation | QC, integration, annotation, downstream plan |
| multiomics | proteomics, metabolomics, epigenomics, MOFA, DIABLO | integration design, validation, mechanism |
| document-operation | PDF, DOCX, XLSX, PPTX, OCR, conversion | deterministic extraction or artifact |

If the request spans classes, keep one primary owner and declare the secondary handoffs. If the user has not supplied a necessary input, ask for the smallest missing item rather than guessing.
