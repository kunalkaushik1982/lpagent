import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';

import {
    COMPLETION_THRESHOLD_PERCENT,
    buildCertificateData,
    createCertificateId,
    createCompletionStorageKey,
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

test('completion record key is stable for plan item scoped certificates', () => {
    assert.equal(
        createCompletionStorageKey('1', '4'),
        'course_completion_1_4'
    );
});

test('certificate template contains required certificate hooks', async () => {
    const html = await fs.readFile('frontend/course-detail.html', 'utf8');
    assert.match(html, /downloadCertificateBtn/);
    assert.match(html, /certificateTemplate/);
    assert.match(html, /html2pdf/);
});
