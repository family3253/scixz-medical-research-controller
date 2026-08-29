# Local Course Asset Bridge

## Purpose

This reference teaches `academic-write-all-skill` how to absorb reusable methods from **local teaching/course asset libraries** without confusing them with ordinary attachments.

Use this when the user points to folders that behave like a paired knowledge base, or when the user's topic strongly overlaps with a reusable local method family and the skill should check those folders proactively.

- course PDFs or slide decks
- chapter-organized `temp_code` directories
- local `R`, `Rc`, `qmd`, notebook, or Shiny app collections
- method-specific folders that bundle teaching materials with runnable examples

Typical local roots may look like:

- `F:\e\实战\ppt`
- `F:\e\实战\code`

## Core Rule

Treat these sources as a **method library**.

That means the goal is usually not to quote them verbatim. The goal is to:

1. identify the relevant method family
2. locate the matching chapter and code
3. extract the operational workflow
4. adapt it to the user's current thesis, manuscript, dataset, figure, or analysis question

## Proactive Trigger Rule

Do not wait for the user to say “go search the local course folders.”

If the task mentions a topic that strongly overlaps with a known reusable method family, check the local course/code library by default first.

Typical proactive triggers include:

- missing data / multiple imputation / outliers / DAG / variable selection
- Table 1 / baseline summary / descriptive statistics
- mediation / interaction / RERI / trend analysis
- survival analysis / KM / Cox / conditional survival
- ROC / calibration / nomogram / clinical prediction
- statistical learning / machine learning / xgboost / mlr3
- dynamic prediction

If no meaningful local match exists, fall back to the ordinary academic-writing route without forcing the bridge.

## Default Routing Pattern

### Step 1: Identify the method family

Map the request to one of the likely topic groups:

- missingness / outliers / variable selection / DAG
- baseline table / descriptive summary / Table 1
- interaction / mediation / trend / RERI
- survival analysis / KM / Cox / conditional survival
- clinical prediction / ROC / nomogram / calibration
- statistical learning / machine learning / feature selection / tuning
- dynamic prediction / time-updated prediction

### Step 2: Find the local source pair

Prefer to find both:

- a framing source (course PDF / chapter title / slide deck)
- an executable source (`R`, `Rc`, `qmd`, app directory, notebook)

When both exist:

- use the PDF/slides for **topic framing and method-selection logic**
- use the code for **actual reusable workflow evidence**

### Step 3: Extract the minimum reusable workflow unit

For each matched source, try to recover:

- required input structure
- variable roles
- required packages or functions
- ordered analysis steps
- output forms (table, figure, PPT, HTML, app, report)

### Step 4: Adapt, do not merely summarize

Convert the local material into one of these downstream outputs:

- adapted analysis script
- methods-writing scaffold
- results-writing scaffold
- figure/table workflow
- chapter-learning memo
- migration checklist for the user's own dataset

## Evidence Priority

Use this order:

1. runnable local code
2. local workflow documents such as `qmd` or structured README files
3. local PDF/slides with readable content
4. PDF filenames or chapter names as coarse routing clues only

## Hard Boundaries

- Do not claim you fully learned a PDF if you only saw its filename or a weak summary.
- Do not present course example results as if they were the user's findings.
- Do not overfit to teaching language when the user needs a manuscript-ready artifact.
- Do not ignore existing local code in favor of generic external advice.
- Do not lose path traceability; always keep the exact local source path available in the response when it matters.
- Do not force a local-library lookup when the topic overlap is weak or obviously outside the local corpus.

## Recommended Output Shape

When this mode is active, prefer:

1. matched topic
2. local source paths
3. reusable workflow distilled from the local assets
4. adaptation notes for the user's current task
5. concrete next artifact (script / prose scaffold / figure plan / table workflow)

## Concrete Local Example Map

### Method-selection framework
- `F:\e\实战\ppt\实战医学统计--轻松SCI-统计8法-授课1h版202501.pdf`

### Missingness / outliers / variable selection
- `F:\e\实战\code\9_异常值缺失值变量选择_陈烨超18915955690\temp_code\缺失值-实战医学统计.qmd`
- `F:\e\实战\code\9_异常值缺失值变量选择_陈烨超18915955690\temp_code\异常值汇总.R`
- `F:\e\实战\code\9_异常值缺失值变量选择_陈烨超18915955690\temp_code\智荟缺失值合并.Rc`

### Table 1 / baseline summary
- `F:\e\实战\code\5_一键table_陈烨超18915955690\temp_code\table1基线表汇总-同数据比对.qmd`
- `F:\e\实战\code\5_一键table_陈烨超18915955690\temp_code\table1基线表汇总-同数据比对.R`

### Interaction / mediation / RERI
- `F:\e\实战\code\13_交互中介趋势检验A款1期_陈烨超18915955690\temp_code\案例打包中介效应2024.R`
- `F:\e\实战\code\13_交互中介趋势检验A款1期_陈烨超18915955690\temp_code\交互作用可视化.R`

### Survival analysis / conditional survival
- `F:\e\实战\code\14.生存分析\文献\condsurv-master\gg_conditional_surv.R`
- `F:\e\实战\code\14.生存分析\文献\condsurv-master\conditional_surv_est.R`

### Clinical prediction / ROC / nomogram
- `F:\e\实战\code\陈烨超18915955690_23_临床预测part1\temp_code`
- `F:\e\实战\code\陈烨超18915955690_24_临床预测part2\temp_code`

### Statistical learning / machine learning
- `F:\e\实战\code\陈烨超18915955690_32_统计学习1\temp_code`
- `F:\e\实战\code\陈烨超18915955690_33_统计学习2\temp_code`
- `F:\e\实战\code\陈烨超18915955690_34_统计学习3\temp_code`
- `F:\e\实战\code\陈烨超18915955690_35_机器学习mlr3(1)\temp_code`

### Dynamic prediction
- `F:\e\实战\ppt\陈烨超18915955690_36动态预测2章.pdf`
- `F:\e\实战\code\动态预测智荟案例数据.RData`
