# Course Certificate Design

Date: 2026-04-15

## Goal

Add on-demand certificate generation for completed courses from the course detail page, reduce the completion threshold from 50% to 20%, and produce a professional-looking PDF certificate that includes course metadata and learner details.

## Scope

In scope:
- Lowering the course completion gate from 50% watched to 20% watched.
- Exposing a `Download Certificate` action after a course is completed.
- Generating a polished PDF certificate on demand in the browser.
- Showing certificate details based on the logged-in user, current course, and completion timestamp.
- Persisting completion metadata locally so the certificate remains available after page reload.

Out of scope:
- Server-side certificate generation or storage.
- Cryptographic signing or verification.
- Multi-tenant branding customization.
- Backfilling historical completion timestamps from the backend.

## Current Context

The app uses:
- FastAPI backend for user, course, and plan endpoints.
- Static frontend pages with vanilla JavaScript.
- Local storage for lightweight client-side state such as the logged-in user and course progress.

The current course completion flow lives in `frontend/js/course-detail.js` and:
- Simulates progress locally.
- Requires at least 50% watched before completion.
- Marks the plan item as completed through the backend.

This makes the certificate feature a strong fit for frontend-driven, on-demand PDF generation.

## Approach

Recommended approach: client-side PDF generation from the course detail page.

Why:
- Matches the current architecture with minimal backend changes.
- Avoids binary file storage and additional API complexity.
- Keeps certificate styling fully controllable in HTML/CSS.
- Allows immediate download after completion.

The certificate will be rendered from a hidden DOM template and exported to PDF using a browser-side PDF library.

## User Experience

### Completion flow

1. User opens a course detail page.
2. User watches or simulates progress until reaching at least 20%.
3. User clicks `Mark as Completed`.
4. The frontend marks the plan item complete via the existing backend endpoint.
5. The frontend records the local completion timestamp for that course and plan item.
6. The UI updates to show the course as completed and reveals `Download Certificate`.

### Certificate flow

1. User clicks `Download Certificate`.
2. The page assembles certificate data from the current user, course, and completion metadata.
3. A hidden certificate layout is populated and exported as a landscape PDF.
4. The file downloads immediately using a deterministic filename.

Filename format:
- `certificate-<course-id>-<yyyy-mm-dd>.pdf`

## Certificate Visual Design

The certificate should look formal and professional rather than like a debug export or browser printout.

Visual direction:
- Landscape layout.
- Ivory or warm-white background.
- Navy primary typography.
- Muted gold accent borders and separators.
- Large centered `Certificate of Completion` heading.
- Learner name as the strongest typographic element.
- Course title prominently centered below the completion statement.
- Seal-style badge or emblem element for visual authority.
- Structured metadata section in the lower area.

Content hierarchy:
1. Learning Plan Agent brand line.
2. Certificate title.
3. Learner name.
4. Completion statement.
5. Course title.
6. Completion date and certificate ID.
7. Metadata block containing provider, format, duration, difficulty, and skills.

Tone:
- Clean, restrained, and professional.
- No novelty graphics.
- No excessive color or animation in the exported output.

## Data Model

No backend schema changes are required.

Certificate data sources:
- User name: from frontend local storage login state.
- Course details: fetched from `/courses/{course_id}`.
- Completion status: existing backend plan-item update endpoint.
- Completion timestamp: new local storage record written when completion succeeds.

Proposed local storage key:
- `course_completion_<planId>_<planItemId>`

Stored fields:
- `courseId`
- `planId`
- `planItemId`
- `completedAt`
- `username`
- `courseTitle`

This keeps certificate generation stable even after a reload while avoiding new backend persistence.

## Frontend Changes

### `frontend/course-detail.html`

Add:
- A second action button for certificate download.
- A hidden certificate template container for PDF export.
- Small helper text near progress to explain the 20% threshold.

### `frontend/js/course-detail.js`

Add behavior for:
- Lowering the threshold constant from 50 to 20.
- Persisting completion metadata when backend completion succeeds.
- Restoring completion state on page load when local storage indicates completion.
- Toggling the `Download Certificate` button visibility and state.
- Populating the certificate template with live course and user data.
- Generating the PDF on demand.

Refactoring target:
- Extract completion threshold and storage-key helpers into named functions/constants instead of keeping all logic inline.

### `frontend/css/styles.css`

Add:
- Certificate template styles.
- Professional certificate typography and layout styles.
- Print/PDF-safe spacing and color choices.
- Action-button layout updates where needed.

## Dependency Strategy

Use a client-side PDF library in the browser.

Preferred option:
- `html2pdf.js`

Reason:
- Fits the current static frontend.
- Minimal integration cost.
- Good enough for a polished certificate layout without introducing backend rendering.

Integration method:
- Add a script include on the course detail page.

If the library fails to load:
- Show a clear error alert and do not attempt a partial export.

## Certificate Content

Required fields:
- Certificate title.
- Learner name.
- Course title.
- Completion statement.
- Completion date.
- Certificate ID.
- Provider.
- Format.
- Duration.
- Difficulty.
- Skills covered.

Certificate ID format:
- `LPA-<planId>-<planItemId>-<courseId>`

Completion statement:
- `This certifies that <name> has successfully completed the course <course title> through Learning Plan Agent.`

Skills rendering:
- Comma-separated list.
- Fallback to `Not specified` if the course has no skills.

## Error Handling

Completion flow:
- If progress is below 20%, show a blocking alert.
- If the backend completion request fails, do not store completion metadata.
- If plan or plan item identifiers are missing, show a clear error and do not continue.

Certificate flow:
- If the course is not completed, do not generate the certificate.
- If required course data is missing, show a clear error and abort generation.
- If the PDF library is unavailable, show a clear error and abort generation.

## Testing Strategy

Test-first implementation is required.

Coverage targets:
- Backend regression test for plan item status update remains intact.
- Frontend behavior tests for:
  - completion gate uses 20% rather than 50%.
  - completion metadata is stored only after successful completion.
  - certificate action becomes available after completion.
  - certificate data assembly includes required fields.

If no frontend test harness exists, add small isolated tests for extracted helper functions or document the gap and verify through targeted manual checks.

Manual verification checklist:
- User cannot complete course below 20%.
- User can complete course at or above 20%.
- Download button appears only after completion.
- PDF downloads successfully.
- PDF contains learner name, course title, completion date, certificate ID, and course metadata.
- PDF layout remains readable and professional on standard desktop PDF viewers.

## Risks and Constraints

Known constraints:
- Course progress is currently simulated, not derived from real YouTube playback events.
- Completion timestamp is stored locally, so clearing browser storage removes certificate history.
- The repo’s checked-in virtual environment is stale, so local runtime verification may require environment repair.

Main risk:
- Browser-to-PDF rendering can vary if the certificate layout is too dependent on unsupported CSS features.

Mitigation:
- Keep the certificate template static and print-safe.
- Use a single-page landscape design with simple layout primitives.

## Implementation Notes

Expected file touch set:
- `frontend/course-detail.html`
- `frontend/js/course-detail.js`
- `frontend/css/styles.css`
- test files if a frontend test path is available

No backend API contract changes are required for the certificate feature itself.

## Acceptance Criteria

- Users can mark a course completed at 20% watched progress.
- Users can download a certificate only after completion.
- The certificate is generated on demand as a PDF.
- The certificate looks professional and includes course details plus learner/completion data.
- Existing course completion backend integration continues to work.
