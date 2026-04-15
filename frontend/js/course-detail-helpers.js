export const COMPLETION_THRESHOLD_PERCENT = 20;

export function isEligibleForCompletion(progress) {
    return Number(progress) >= COMPLETION_THRESHOLD_PERCENT;
}

export function createCertificateId(planId, planItemId, courseId) {
    return `LPA-${planId}-${planItemId}-${courseId}`;
}

export function createCompletionStorageKey(planId, planItemId) {
    return `course_completion_${planId}_${planItemId}`;
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
        skillsText: course.skills && course.skills.length > 0
            ? course.skills.join(', ')
            : 'Not specified',
        completionDate: completedAt.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        }),
        certificateId: createCertificateId(
            completionRecord.planId,
            completionRecord.planItemId,
            course.id
        )
    };
}
