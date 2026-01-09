<!--
Sync Impact Report:
Version: Initial → 1.0.0
Change Type: MINOR (Initial constitution creation)
Modified Principles: N/A (new document)
Added Sections: All (7 principles + Development Standards + Compliance)
Removed Sections: N/A
Templates Requiring Updates:
  ✅ spec-template.md - Aligned with security and error handling requirements
  ✅ plan-template.md - Constitution Check section references this file
  ✅ tasks-template.md - Task categorization reflects principle-driven types
  ✅ All command files - Generic guidance maintained (no agent-specific references)
Follow-up TODOs: None
-->

# Crypto Price Tracker Constitution

## Core Principles

### I. Security-First

All API keys, tokens, and credentials MUST be stored in environment variables, never hardcoded in source code. Configuration files containing secrets MUST be excluded from version control via `.gitignore`. Security scanning tools MUST be integrated into the CI/CD pipeline to detect accidental credential exposure.

**Rationale**: Cryptocurrency APIs often have rate limits and cost implications. Exposed credentials can lead to API abuse, data breaches, and financial loss. Environment-based configuration enables secure deployment across environments.

### II. Type Safety

The frontend MUST use TypeScript with strict mode enabled. The Python backend MUST use type hints for all function signatures and class definitions. Type checking MUST be enforced in CI/CD pipelines via `tsc` (TypeScript) and `mypy` (Python).

**Rationale**: Financial data requires precision. Type safety prevents runtime errors involving price calculations, currency conversions, and data transformations. Early detection of type mismatches reduces production bugs.

### III. API Reliability

All external API calls MUST implement rate limiting according to provider specifications. Responses MUST be cached with appropriate TTL (Time-To-Live) strategies. Failed API calls MUST trigger exponential backoff retry logic with maximum retry limits.

**Rationale**: Cryptocurrency price APIs have strict rate limits. Exceeding limits results in service disruption. Caching reduces API calls, improves performance, and ensures continuity during API downtime.

### IV. Mobile-First Design

All UI components MUST be responsive and functional on mobile devices (320px minimum width). Touch targets MUST meet WCAG 2.1 AA standards (minimum 44x44px). Mobile performance MUST be validated on 3G network conditions.

**Rationale**: Users check cryptocurrency prices on-the-go. Mobile-first design ensures accessibility and usability for the primary use case. Progressive enhancement provides optimal experience across all devices.

### V. Real-Time Updates

Price data MUST refresh automatically using WebSocket connections or server-sent events where supported. Fallback to polling MUST be implemented with configurable intervals (default: 30 seconds). Users MUST be notified of connection status and last update timestamp.

**Rationale**: Cryptocurrency prices are volatile and change rapidly. Stale data can lead to poor decision-making. Real-time updates provide users with current information without manual intervention.

### VI. Error Resilience

The application MUST handle external service failures gracefully by displaying cached data with timestamp warnings. User actions MUST NOT fail catastrophically; error states MUST show actionable feedback. The system MUST log errors with sufficient context for debugging without exposing sensitive data.

**Rationale**: External dependencies (price APIs, network) are unreliable. Graceful degradation maintains user trust and application usability during outages. Clear error messages reduce user frustration.

### VII. Clean Architecture

Business logic MUST be separated from data access and presentation layers. Data models, services, and UI components MUST reside in distinct directories with clear boundaries. Dependencies MUST flow inward (UI → Services → Data), never outward. Cross-cutting concerns (logging, caching, authentication) MUST use dependency injection.

**Rationale**: Separation of concerns enables independent testing, maintainability, and scalability. Clean architecture supports technology changes (e.g., swapping price API providers) without cascading modifications.

## Development Standards

### Technology Stack

- **Frontend**: TypeScript (strict mode), React or Vue.js, responsive CSS framework
- **Backend**: Python 3.11+, FastAPI or Flask, async/await for API calls
- **Data Storage**: Redis for caching, PostgreSQL for user data (if applicable)
- **API Integration**: REST clients with retry logic, WebSocket support
- **Testing**: pytest (backend), Jest/Vitest (frontend), contract tests for API integrations

### Code Quality Gates

- Type checking MUST pass: `tsc --noEmit` (frontend), `mypy` (backend)
- Linting MUST pass: ESLint (frontend), Ruff or Pylint (backend)
- Test coverage MUST meet 80% for business logic (services, data transformation)
- Security scans MUST run on every commit: `bandit` (Python), `npm audit` (Node.js)
- No hardcoded secrets: validated via pre-commit hooks and CI checks

### Testing Requirements

- **Contract Tests**: Verify external API response structures match expectations
- **Integration Tests**: Validate caching, rate limiting, and retry mechanisms
- **Unit Tests**: Cover price calculations, data transformations, error handling
- **E2E Tests**: Critical user journeys (view prices, refresh data, handle errors)
- Tests for mobile responsiveness and real-time update mechanisms MUST be automated

## Compliance

### Constitution Enforcement

This constitution supersedes all other development practices. All pull requests MUST demonstrate compliance with applicable principles. Code reviews MUST explicitly verify:

1. No hardcoded secrets (Principle I)
2. Type annotations present (Principle II)
3. API calls include caching and rate limiting (Principle III)
4. Mobile responsiveness validated (Principle IV)
5. Real-time updates functional (Principle V)
6. Error states handled gracefully (Principle VI)
7. Architectural boundaries maintained (Principle VII)

### Amendment Process

Constitution changes require:
1. Proposal documenting rationale and impact analysis
2. Review by project maintainers/stakeholders
3. Migration plan for existing code (if applicable)
4. Version increment following semantic versioning (MAJOR.MINOR.PATCH)
5. Update of all dependent templates and documentation

### Complexity Justification

Violations of architectural principles (e.g., bypassing layers, skipping error handling) MUST be documented in `plan.md` Complexity Tracking section with:
- Specific principle violated
- Business justification for violation
- Explanation of why compliant alternatives were rejected
- Plan for remediation (if temporary)

**Version**: 1.0.0 | **Ratified**: 2026-01-09 | **Last Amended**: 2026-01-09
