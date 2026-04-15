# Course Certificate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add on-demand professional PDF certificate downloads for completed courses and lower the completion threshold from 50% to 20%.

**Architecture:** Keep certificate generation entirely in the frontend. The course detail page will track completion eligibility and completion metadata locally, render a hidden certificate template, and export it to PDF on demand using a browser-side library.

**Tech Stack:** Vanilla JavaScript, HTML/CSS, localStorage, html2pdf.js, Node built-in test runner

---

### Task 1: Add Helper Tests for Completion and Certificate Data

**Files:**
- Create: `frontend/js/course-detail-helpers.js`
- Create: `tests/course-detail-helpers.test.mjs`

- [ ] **Step 1: Write the failing test**

```js
import test from 'node:test';
import assert from 'node:assert/strict';

import {
  COMPLETION_THRESHOLD_PERCENT,
  buildCertificateData,
  createCertificateId,
  isEligibleForCompletion,
} from '../frontend/js/course-detail-helpers.js';

test('completion threshold is 20 percent', () => {
  assert.equal(COMPLETION_THRESHOLD_PERCENT, 20);
  assert.equal(isEligibleForCompletion(19.9), false);
  assert.equal(isEligibleForCompletion(20), true);
});

test('certificate data includes required professional fields', () => {
  const data = buildCertificateData({
    user: { username: 'alice' },
    course: {
      id: 7,
      title: 'FastAPI Fundamentals',
      provider: 'Internal Academy',
      format: 'Online',
      duration_hours: 12,
      difficulty_level: 'Intermediate',
      skills: ['FastAPI', 'Python', 'APIs'],
    },
    completionRecord: {
      planId: '1',
      planItemId: '4',
      completedAt: '2026-04-15T12:30:00.000Z',
    },
  });

  assert.equal(data.learnerName, 'alice');
  assert.equal(data.courseTitle, 'FastAPI Fundamentals');
  assert.equal(data.certificateId, createCertificateId('1', '4', 7));
  assert.match(data.completionDate, /2026/);
  assert.equal(data.skillsText, 'FastAPI, Python, APIs');
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/course-detail-helpers.test.mjs`
Expected: FAIL because `frontend/js/course-detail-helpers.js` does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```js
export const COMPLETION_THRESHOLD_PERCENT = 20;

export function isEligibleForCompletion(progress) {
  return Number(progress) >= COMPLETION_THRESHOLD_PERCENT;
}

export function createCertificateId(planId, planItemId, courseId) {
  return `LPA-${planId}-${planItemId}-${courseId}`;
}

export function buildCertificateData({ user, course, completionRecord }) {
  const completedAt = new Date(completionRecord.completedAt);
  return {
    learnerName: user.username,
    courseTitle: course.title,
    provider: course.provider || 'Not specified',
    format: course.format || 'Not specified',
    durationHours: course.duration_hours || 0,
    difficulty: course.difficulty_level || 'Not specified',
    skillsText: (course.skills && course.skills.length > 0)
      ? course.skills.join(', ')
      : 'Not specified',
    completionDate: completedAt.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    }),
    certificateId: createCertificateId(
      completionRecord.planId,
      completionRecord.planItemId,
      course.id
    ),
  };
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/course-detail-helpers.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/js/course-detail-helpers.js tests/course-detail-helpers.test.mjs
git commit -m "Add certificate helper functions and tests"
```

### Task 2: Add Certificate UI and Hidden Template

**Files:**
- Modify: `frontend/course-detail.html`
- Modify: `frontend/css/styles.css`

- [ ] **Step 1: Write the failing test**

```js
test('certificate template contains required certificate hooks', async () => {
  const html = await fs.readFile('frontend/course-detail.html', 'utf8');
  assert.match(html, /downloadCertificateBtn/);
  assert.match(html, /certificateTemplate/);
  assert.match(html, /html2pdf/);
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/course-detail-helpers.test.mjs`
Expected: FAIL because the current HTML does not include the certificate button or template.

- [ ] **Step 3: Write minimal implementation**

```html
<button class="certificate-btn hidden" id="downloadCertificateBtn">Download Certificate</button>

<div class="certificate-template hidden" id="certificateTemplate">
  <div class="certificate-sheet">
    <div class="certificate-border"></div>
    <div class="certificate-brand">Learning Plan Agent</div>
    <div class="certificate-title">Certificate of Completion</div>
    <div class="certificate-name" id="certificateLearnerName"></div>
    <div class="certificate-statement" id="certificateStatement"></div>
    <div class="certificate-course" id="certificateCourseTitle"></div>
    <div class="certificate-meta-grid">
      ...
    </div>
  </div>
</div>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/course-detail-helpers.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/course-detail.html frontend/css/styles.css tests/course-detail-helpers.test.mjs
git commit -m "Add certificate UI and layout"
```

### Task 3: Implement Completion Threshold, Persistence, and PDF Download

**Files:**
- Modify: `frontend/js/course-detail.js`
- Modify: `frontend/js/course-detail-helpers.js`
- Test: `tests/course-detail-helpers.test.mjs`

- [ ] **Step 1: Write the failing test**

```js
test('completion record key is stable for plan item scoped certificates', () => {
  assert.equal(
    createCompletionStorageKey('1', '4'),
    'course_completion_1_4'
  );
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `node --test tests/course-detail-helpers.test.mjs`
Expected: FAIL because the storage-key helper does not exist yet.

- [ ] **Step 3: Write minimal implementation**

```js
export function createCompletionStorageKey(planId, planItemId) {
  return `course_completion_${planId}_${planItemId}`;
}
```

And in `frontend/js/course-detail.js`:

```js
if (!currentCourse || !isEligibleForCompletion(videoProgress)) {
  showAlert('Please watch at least 20% of the video before marking as complete', 'error');
  return;
}
```

Add:
- completion metadata persistence after successful backend completion
- completion-state restoration on load
- certificate button toggle
- certificate template population
- html2pdf download call

- [ ] **Step 4: Run test to verify it passes**

Run: `node --test tests/course-detail-helpers.test.mjs`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add frontend/js/course-detail.js frontend/js/course-detail-helpers.js tests/course-detail-helpers.test.mjs
git commit -m "Implement course completion certificates"
```

### Task 4: Verify End-to-End Behavior

**Files:**
- Verify: `frontend/course-detail.html`
- Verify: `frontend/js/course-detail.js`
- Verify: `frontend/js/course-detail-helpers.js`
- Verify: `frontend/css/styles.css`

- [ ] **Step 1: Run helper tests**

Run: `node --test tests/course-detail-helpers.test.mjs`
Expected: PASS

- [ ] **Step 2: Run Python syntax validation for touched backend-facing files**

Run: `python -m py_compile tests/test_plan_status_update.py`
Expected: PASS

- [ ] **Step 3: Manual browser verification**

Check:
- Course completion blocked below 20%.
- Course completion succeeds at or above 20%.
- `Download Certificate` appears after completion.
- Downloaded PDF is landscape, professional, and contains all required details.

- [ ] **Step 4: Commit**

```bash
git add frontend/course-detail.html frontend/js/course-detail.js frontend/js/course-detail-helpers.js frontend/css/styles.css tests/course-detail-helpers.test.mjs
git commit -m "Polish certificate PDF flow"
```
