# Security Policy

## Supported versions

We actively maintain the latest `main` branch. Security fixes are applied there and released as new tags.

| Version | Supported |
|---------|-----------|
| `main`  | ✅ Yes    |
| older   | ❌ No     |

## Privacy model

`pdf-chunk-reader` is designed to be **safe for confidential documents**:

- The splitter (`scripts/pdf_splitter.py`) runs **entirely on your local machine**.
- It does **not** make any network requests, upload files, or send telemetry.
- No data leaves your disk except the chunk files and summary you explicitly generate in a local output directory you choose.

Treat the output directory like any other working folder: if you split a sensitive document, clean up `_split_*` / `chunks/` afterwards and keep only the `consolidated_summary.md` you intend to retain.

## Reporting a vulnerability

If you discover a security issue (e.g. unexpected network access, path-traversal in output paths, unsafe deserialization), please **do not open a public issue**.

Instead, report it privately:

1. Go to the repository's **Security → Report a vulnerability** tab on GitHub, **or**
2. Email the maintainer (see the profile linked from the repo) with the subject `pdf-chunk-reader security report`.

Please include:

- A clear description of the issue and its impact.
- Steps to reproduce (command + environment).
- Any relevant logs (with sensitive content redacted).

We will acknowledge within a few days and work with you on a fix and coordinated disclosure.

## Scope

Out of scope for this policy:

- General bugs that do not affect security (use public Issues).
- Performance or quality of extracted text on scanned PDFs (tracked as enhancement requests).
