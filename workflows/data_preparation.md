# Data-preparation workflow

## Entry and scope

Use for profiling, de-identification, codebook generation, missingness/duplicate checks, and a proposed cleaning plan. It does not silently modify raw data.

## Inputs

Require dataset path, format, data dictionary if available, intended unit of analysis, outcome/exposure definitions, and privacy constraints. A missing dataset or unknown analysis unit is blocking.

## Route

Controller → 户部 preflight/provenance → 刑部 privacy and integrity review → 尚书省 ticket. Primary: `clean-data` or `generate-codebook`. Supporting: `deidentify`, `version-dataset`, `anthropics-xlsx`, `pandas-pro`.

## Outputs

Profile report, variable/codebook table, flagged issues, de-identification status, proposed transformations, version fingerprint, and explicit user decisions required before cleaning.

## Verification

Check row/column counts, types, duplicates, missingness, ranges, identifiers, outcome coding, and reproducibility. Preserve the raw input and record every approved transformation.

## Failure/fallback

If the file cannot be read, use the documented file-type fallback once. If a cleaning decision is scientifically ambiguous, stop at the profile and ask for approval.
