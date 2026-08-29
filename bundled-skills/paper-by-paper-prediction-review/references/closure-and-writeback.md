# Closure and Writeback Rules

## True Closure Standard

A paper is only truly closed when:

1. retained models are fixed
2. all tracked fields are resolved as:
   - filled
   - 未记录
   - 无数据
   - 不适用
3. scoring is actually represented in `TRIPOD_WIDE` / `PROBAST_DEV_WIDE` / `PROBAST_EVAL_WIDE`, or an explicit source-based fallback is documented for the missing scorer path
4. stable final files are written
5. queue state is updated

## What Does Not Count As Closure

The following alone are **not enough**:
- a vague summary
- a stage snapshot
- a failed scorer task
- a field left blank without a missingness label

## Writeback Rule

Preferred workflow:
1. collect extraction outputs
2. collect scoring outputs
3. adjudicate conflicts
4. write stable JSON artifacts
5. update Excel collection workbook

If Excel is unstable, the JSON files are still the authoritative staging layer until Excel catches up.

## Project-Specific Writeback Target

For the current MDR-GNB workflow, the preferred workbook to keep filling is:

- `D:\下载\MDR_GNB_detailed_data_collection_with_scoring_v2.xlsx`

Use this as the primary collection workbook for user-facing data entry and review.

The workbook under `<PRIVATE_PROJECT_WORKSPACE>\MDR_master_collection_split_aware.xlsx` may still exist as a working or staging workbook, but it is not the preferred long-term collection surface for this project.

The safe operating sequence is:

1. read original source and supplement from `<PRIVATE_PROJECT_WORKSPACE>\python\pdf_downloads2\纳入` and `...\补充材料`
2. inspect the structure and key headers of `D:\下载\MDR_GNB_detailed_data_collection_with_scoring_v2.xlsx` before extraction so the paper is collected against the intended schema
3. stage extraction/scoring in JSON files under `<PRIVATE_PROJECT_WORKSPACE>`
4. merge paper-scoped results into the preferred collection workbook under `D:\下载\...`
5. only then refresh any secondary Excel views if still needed

## Required Stable Files

Per paper, prefer:
- `paperX_model_choice.json`
- `paperX_stage_snapshot.json`
- `paperX_final_summary.json`
- `paperX_scoring_provenance.json`

## Queue State Language

Use explicit states such as:
- `awaiting_model_confirmation`
- `foreground_source_extraction_pending`
- `closure_pending_extraction_and_scoring_completion`
- `closed_field_complete`

Avoid ambiguous “almost done” wording.
