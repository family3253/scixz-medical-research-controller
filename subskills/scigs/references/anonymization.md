# Anonymization

First confirm the journal's actual review model. For blinded review, create a copy with `anonymize_docx.py`, then scan it with `anonymity_scan.py` using every known author, institution, repository, grant, project, and trial term.

Check visible text, headers/footers, comments, tracked-change authors, core/custom properties, hyperlinks, filenames, embedded media metadata, and supplementary files. A scanner is a safety net, not proof of anonymity. Do not replace legitimate self-citations unless the journal explicitly requires it; flag repository links that reveal identity for manual handling.
