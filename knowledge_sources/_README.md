# Knowledge sources — drop reference documents here

Everything in this folder (except files starting with `_` or `.`) is **searched**
by the assistant's `search_knowledge` tool. The assistant pulls only the relevant
sections per question, so this scales to a large, growing library without
bloating every request.

## How to add knowledge
1. Drop a file into this folder. Supported: **`.md`**, **`.txt`**, **`.pdf`**.
   - Plain text / Markdown is ideal (cleanest extraction). PDFs work too.
   - Use clear **section headings** — they become the "section" label shown with
     each result and improve retrieval. (Markdown `#`/`##`, or short title lines.)
   - Big documents are fine; they're automatically split into focused chunks.
2. Pick it up one of two ways:
   - **Restart** the backend (`uvicorn app.main:app --reload` auto-reloads), or
   - **`curl -X POST http://localhost:8000/api/reindex`** (no restart needed).
3. Check what's indexed: **`GET http://localhost:8000/api/knowledge`**
   → `{ "files": [...], "file_count": N, "chunk_count": M }`.

## Notes
- Files named `_*.md` (like this one) are **ignored** — use that prefix for notes
  you don't want searched.
- Keep one document per topic where practical (e.g. `terms_and_conditions.md`,
  `tier_rules.md`, `co_brand_partners.md`) — it makes results easy to trace.
- The assistant answers **only** from retrieved text and cites the section; if
  nothing relevant is found it says so rather than guessing.

## Current contents
- `bluchip_earning_faqs.md` — the earning/accrual FAQ (moved here from the prompt).
- *(Add the full IndiGo BluChip Terms & Conditions here, e.g.
  `terms_and_conditions.md`.)*
