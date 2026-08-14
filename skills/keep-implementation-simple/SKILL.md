---
name: keep-implementation-simple
description: Use when implementing or reviewing a repository change whose proposed design may be more complex than its requested observable outcome or concrete current evidence requires.
---

# Keep Implementation Simple

Keep the change no larger than the requested observable outcome and current evidence require.

## Inputs

- The requested observable outcome and accepted criteria.
- Applicable repository rules and concrete current repository evidence.
- The proposed or actual change surface.

## Outputs

- A one-sentence restatement of the observable outcome.
- The smallest existing owner and surface that can produce it.
- Changes mapped to an accepted criterion or concrete current evidence.
- Verification results or a review verdict with any concrete blocker.

## Required Capabilities

- Read the applicable repository instructions and accepted criteria.
- Inspect the existing owner, surface, and current evidence needed for the change or review.
- Run the existing relevant verification when implementation or review requires it.

If a required capability is unavailable, return `BLOCKED` with the missing capability and concrete cause.

## Method

1. Restate the requested observable outcome in one sentence.
2. Choose the smallest existing owner and surface that can produce it.
3. Map every added concept, component, state, protocol, classifier, resolver, and artifact to an accepted criterion or concrete current repository evidence. Remove anything without a map.
4. For an instruction-only problem, use behavioral evaluation and existing real repository boundaries; do not add a test-only runtime or model.
5. Expand the architecture only after the simple approach demonstrably fails, and cite that failure.
6. In review, block only for a requirement gap, repository rule violation, observable regression, or concrete current risk.
