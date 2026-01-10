# Tasks: CryptoTracker Pro

**Input**: Design documents from `/specs/001-crypto-tracker-pro/`
**Prerequisites**: plan.md (tech stack), spec.md (user stories), research.md, data-model.md, contracts/

**Tests**: Tests are NOT explicitly requested in the specification, so test tasks are OMITTED per template guidelines.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

Web application structure (from plan.md):
- **Backend**: `backend/src/` for source code, `backend/tests/` for tests
- **Frontend**: `frontend/src/` for source code, `frontend/tests/` for tests
- **Shared**: `shared/types/` for TypeScript interfaces

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure per Constitution principles

- [ ] T001 Create project directory structure (backend/, frontend/, shared/types/) per plan.md
- [ ] T002 Initialize Python backend with FastAPI 0.115+ and dependencies in backend/requirements.txt
- [ ] T003 Initialize React 19 frontend with Vite 6+ in frontend/package.json
- [ ] T004 [P] Configure TypeScript strict mode in frontend/tsconfig.json (Constitution Principle II)
- [ ] T005 [P] Configure Python type hints with mypy in backend/setup.cfg (Constitution Principle II)
- [ ] T006 [P] Setup environment variable management with .env and .env.example files (Constitution Principle I)
- [ ] T007 [P] Add .env files to .gitignore to prevent secret exposure (Constitution Principle I)
- [ ] T008 [P] Configure ESLint and Prettier for frontend code quality in frontend/.eslintrc.json
- [ ] T009 [P] Configure Ruff linter for backend Python code in backend/pyproject.toml
- [ ] T010 [P] Install Redis 7.x and verify connectivity with redis-cli ping

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Shared Type Definitions

- [ ] T011 [P] Create Cryptocurrency interface in shared/types/cryptocurrency.ts (from data-model.md)
- [ ] T012 [P] Create PriceDataPoint interface in shared/types/cryptocurrency.ts (from data-model.md)
- [ ] T013 [P] Create MarketCategory enum in shared/types/cryptocurrency.ts (from data-model.md)
- [ ] T014 [P] Create API response types in shared/types/api.ts

### Backend Core Infrastructure

- [ ] T015 Create backend project structure (models/, services/, api/, lib/) in backend/src/
- [ ] T016 [P] Create FastAPI application instance in backend/src/main.py with CORS middleware
- [ ] T017 [P] Setup Redis connection pool with async support in backend/src/lib/redis_client.py (Constitution Principle III)
- [ ] T018 [P] Implement retry logic with exponential backoff in backend/src/lib/retry.py (Constitution Principle III)
- [ ] T019 [P] Create error handling utilities in backend/src/lib/error_handling.py (Constitution Principle VI)
- [ ] T020 [P] Create number formatting utilities in backend/src/lib/formatters.py (for large/small prices)
- [ ] T021 [P] Implement validation service in backend/src/services/validation_service.py (FR-018, from data-model.md)
- [ ] T022 Implement CoinGecko API client in backend/src/services/coingecko_client.py with rate limiting
- [ ] T023 Implement CoinMarketCap API client in backend/src/services/coinmarketcap_client.py as fallback (FR-022)
- [ ] T024 Implement cache service with 5-minute TTL in backend/src/services/cache_service.py (FR-016)
- [ ] T025 [P] Create health check endpoint in backend/src/api/routes/health.py (from contracts/api-specification.yaml)

### Backend Data Models

- [ ] T026 [P] Create Cryptocurrency Pydantic model in backend/src/models/cryptocurrency.py (from data-model.md)
- [ ] T027 [P] Create PriceDataPoint Pydantic model in backend/src/models/price_data_point.py (from data-model.md)
- [ ] T028 [P] Create MarketCategory enum in backend/src/models/market_category.py (from data-model.md)

### Frontend Core Infrastructure

- [ ] T029 Create frontend project structure (components/, pages/, services/, hooks/, utils/) in frontend/src/
- [ ] T030 [P] Setup Vite configuration with code splitting in frontend/vite.config.ts
- [ ] T031 [P] Create API client service in frontend/src/services/api.ts
- [ ] T032 [P] Create WebSocket client service in frontend/src/services/websocket.ts (Constitution Principle V)
- [ ] T033 [P] Implement useWebSocket custom hook in frontend/src/hooks/useWebSocket.ts with reconnection logic
- [ ] T034 [P] Create number formatter utilities in frontend/src/utils/formatters.ts
- [ ] T035 [P] Create ErrorBoundary component in frontend/src/components/ErrorBoundary.tsx (Constitution Principle VI)
- [ ] T036 [P] Create SkeletonScreen component in frontend/src/components/SkeletonScreen.tsx (FR-024)
- [ ] T037 [P] Setup global CSS with mobile-first breakpoints in frontend/src/styles/global.css (320px min, FR-020)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - View Live Cryptocurrency Prices (Priority: P1) 🎯 MVP

**Goal**: Display top 20 cryptocurrencies by market cap with current prices, 24-hour changes, and market indicators

**Independent Test**: Load application and verify 20 cryptocurrencies display with prices, 24h percentage changes, and visual indicators (green/red). Auto-refresh works every 30 seconds. Delivers immediate value as a price monitoring tool.

### Backend Implementation for User Story 1

- [ ] T038 [P] [US1] Implement price service business logic in backend/src/services/price_service.py (top 20 by market cap, FR-001)
- [ ] T039 [P] [US1] Implement GET /api/v1/cryptocurrencies endpoint in backend/src/api/routes/cryptocurrencies.py (FR-002, FR-003, FR-005)
- [ ] T040 [US1] Add data mapping from CoinGecko response to Cryptocurrency model in backend/src/services/coingecko_client.py
- [ ] T041 [US1] Add data mapping from CoinMarketCap response to Cryptocurrency model in backend/src/services/coinmarketcap_client.py
- [ ] T042 [US1] Implement automatic fallback logic (CoinGecko → CoinMarketCap) in backend/src/services/price_service.py (FR-022)
- [ ] T043 [P] [US1] Create WebSocket endpoint /api/v1/ws/prices in backend/src/api/routes/websocket.py (FR-013, from contracts/websocket-spec.md)
- [ ] T044 [US1] Implement Redis pub/sub for price broadcasting in backend/src/services/cache_service.py
- [ ] T045 [US1] Setup 30-second auto-refresh background task in backend/src/main.py (FR-013)

### Frontend Implementation for User Story 1

- [ ] T046 [P] [US1] Create Dashboard page component in frontend/src/pages/Dashboard.tsx
- [ ] T047 [P] [US1] Create CryptoList component in frontend/src/components/CryptoList.tsx
- [ ] T048 [P] [US1] Create CryptoCard component in frontend/src/components/CryptoCard.tsx (shows price, 24h change, volume, market cap)
- [ ] T049 [US1] Implement useCryptocurrencies hook in frontend/src/hooks/useCryptocurrencies.ts (data fetching)
- [ ] T050 [US1] Add visual indicators logic (green/red) in frontend/src/components/CryptoCard.tsx based on priceChangePercent24h (FR-004)
- [ ] T051 [P] [US1] Create RefreshButton component in frontend/src/components/RefreshButton.tsx (FR-014)
- [ ] T052 [P] [US1] Create LastUpdated timestamp component in frontend/src/components/LastUpdated.tsx (FR-015)
- [ ] T053 [US1] Integrate WebSocket for real-time updates in frontend/src/hooks/useCryptocurrencies.ts (30s auto-refresh, FR-013)
- [ ] T054 [US1] Add connection state indicators in frontend/src/components/Dashboard.tsx (online/offline, FR-015)
- [ ] T055 [US1] Implement skeleton loading screens during initial fetch in frontend/src/components/CryptoList.tsx (FR-024)

**Checkpoint**: User Story 1 complete - Application displays top 20 cryptocurrencies with live prices and auto-refresh

---

## Phase 4: User Story 2 - Discover Top Gainers and Losers (Priority: P2)

**Goal**: Provide ranked lists of top 20 performing and worst performing cryptocurrencies by 24-hour percentage change with tab navigation

**Independent Test**: Access gainers/losers tabs and verify cryptocurrencies are correctly ranked by 24h percentage change with prominent percentage displays. Delivers value for opportunity discovery.

### Backend Implementation for User Story 2

- [ ] T056 [P] [US2] Implement getTopGainers method in backend/src/services/price_service.py (FR-006, from data-model.md)
- [ ] T057 [P] [US2] Implement getTopLosers method in backend/src/services/price_service.py (FR-007, from data-model.md)
- [ ] T058 [P] [US2] Create GET /api/v1/cryptocurrencies/gainers endpoint in backend/src/api/routes/cryptocurrencies.py
- [ ] T059 [P] [US2] Create GET /api/v1/cryptocurrencies/losers endpoint in backend/src/api/routes/cryptocurrencies.py
- [ ] T060 [US2] Add caching for gainers/losers lists with 5-minute TTL in backend/src/services/cache_service.py (cache keys: crypto:gainers:top20, crypto:losers:top20)

### Frontend Implementation for User Story 2

- [ ] T061 [P] [US2] Create TabNavigation component in frontend/src/components/TabNavigation.tsx (All/Gainers/Losers tabs, FR-023)
- [ ] T062 [US2] Integrate TabNavigation in frontend/src/pages/Dashboard.tsx
- [ ] T063 [US2] Update useCryptocurrencies hook to support view modes (all/gainers/losers) in frontend/src/hooks/useCryptocurrencies.ts
- [ ] T064 [US2] Update CryptoCard to emphasize percentage change for gainers/losers views in frontend/src/components/CryptoCard.tsx
- [ ] T065 [US2] Add WebSocket subscription filtering for gainers/losers views in frontend/src/hooks/useWebSocket.ts

**Checkpoint**: User Stories 1 AND 2 complete - Dashboard now has All/Gainers/Losers navigation with real-time updates

---

## Phase 5: User Story 3 - Search and Filter Cryptocurrencies (Priority: P3)

**Goal**: Enable users to find specific cryptocurrencies or filter by price range and market cap categories

**Independent Test**: Enter search terms and apply filters, verify the displayed list updates correctly. Delivers value for focused portfolio tracking.

### Backend Implementation for User Story 3

- [ ] T066 [P] [US3] Implement searchCryptocurrencies method in backend/src/services/price_service.py (FR-008, from data-model.md)
- [ ] T067 [P] [US3] Implement filterByPriceRange method in backend/src/services/price_service.py (FR-009, from data-model.md)
- [ ] T068 [P] [US3] Implement filterByMarketCapCategory method in backend/src/services/price_service.py (FR-010, from data-model.md)
- [ ] T069 [P] [US3] Add computeMarketCapCategory utility function in backend/src/lib/formatters.py
- [ ] T070 [US3] Update GET /api/v1/cryptocurrencies endpoint with query parameters (search, min_price, max_price, market_cap_category) in backend/src/api/routes/cryptocurrencies.py

### Frontend Implementation for User Story 3

- [ ] T071 [P] [US3] Create SearchBar component in frontend/src/components/SearchBar.tsx (FR-008)
- [ ] T072 [P] [US3] Create FilterPanel component in frontend/src/components/FilterPanel.tsx (price range, market cap category, FR-009, FR-010)
- [ ] T073 [US3] Create useSearch custom hook in frontend/src/hooks/useSearch.ts for client-side search/filter logic
- [ ] T074 [US3] Integrate SearchBar in frontend/src/pages/Dashboard.tsx
- [ ] T075 [US3] Integrate FilterPanel in frontend/src/pages/Dashboard.tsx
- [ ] T076 [US3] Add empty state message when no results found in frontend/src/components/CryptoList.tsx (FR-008 acceptance scenario 5)
- [ ] T077 [US3] Add clear filters button in frontend/src/components/FilterPanel.tsx

**Checkpoint**: User Stories 1, 2, AND 3 complete - Full search and filter functionality operational

---

## Phase 6: User Story 4 - View Price Trend Charts (Priority: P3)

**Goal**: Display sparkline charts showing 7-day price trends with expandable detailed views for technical analysis

**Independent Test**: Verify sparkline charts display correctly and expand on click to show detailed views. Delivers value for technical analysis and trend identification.

### Backend Implementation for User Story 4

- [ ] T078 [US4] Add sparkline data mapping in backend/src/services/coingecko_client.py (mapSparklineData function from data-model.md)
- [ ] T079 [US4] Update Cryptocurrency model response to include sparklineData in backend/src/models/cryptocurrency.py
- [ ] T080 [US4] Add sparkline caching with 1-hour TTL in backend/src/services/cache_service.py (cache key: crypto:sparkline:{id})
- [ ] T081 [P] [US4] Create GET /api/v1/cryptocurrencies/{id} endpoint for detailed cryptocurrency data in backend/src/api/routes/cryptocurrencies.py (FR-012)

### Frontend Implementation for User Story 4

- [ ] T082 [P] [US4] Install Lightweight Charts 4.2+ library in frontend/package.json
- [ ] T083 [P] [US4] Create SparklineChart component in frontend/src/components/SparklineChart.tsx using Lightweight Charts (FR-011)
- [ ] T084 [P] [US4] Create ChartDetailView component in frontend/src/components/ChartDetailView.tsx for expanded chart view (FR-012)
- [ ] T085 [US4] Integrate SparklineChart in frontend/src/components/CryptoCard.tsx
- [ ] T086 [US4] Add click handler to expand chart in frontend/src/components/SparklineChart.tsx
- [ ] T087 [US4] Implement modal/overlay for ChartDetailView in frontend/src/components/ChartDetailView.tsx
- [ ] T088 [US4] Handle insufficient data case (< 7 days) with message in frontend/src/components/SparklineChart.tsx (FR-011 acceptance scenario 4)
- [ ] T089 [US4] Optimize chart rendering for mobile with canvas-based rendering in frontend/src/components/SparklineChart.tsx (Constitution Principle IV)

**Checkpoint**: All user stories (1-4) complete - Full cryptocurrency tracking dashboard with charts operational

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and ensure production readiness

### Error Handling & Resilience (Constitution Principle VI)

- [ ] T090 [P] Add graceful degradation when external APIs fail in backend/src/services/price_service.py (serve cached data with warning)
- [ ] T091 [P] Implement WebSocket reconnection with exponential backoff in frontend/src/hooks/useWebSocket.ts (1s, 2s, 4s, 8s, max 30s)
- [ ] T092 [P] Add offline indicator in frontend/src/components/Dashboard.tsx when network connectivity is poor
- [ ] T093 [P] Display user-friendly error messages in frontend/src/components/ErrorBoundary.tsx (FR-019)

### Mobile Optimization (Constitution Principle IV)

- [ ] T094 [P] Verify mobile responsiveness at 320px minimum width in frontend/src/styles/global.css (FR-020)
- [ ] T095 [P] Ensure touch targets meet 44x44px minimum size in frontend/src/components/ (FR-021)
- [ ] T096 [P] Test mobile browsers (iOS Safari, Chrome Android) per SC-006

### Performance Optimization

- [ ] T097 [P] Optimize bundle size with Vite code splitting in frontend/vite.config.ts (<2s load time, SC-001)
- [ ] T098 [P] Implement lazy loading for ChartDetailView component in frontend/src/components/ChartDetailView.tsx
- [ ] T099 [P] Add performance monitoring for update latency (<500ms, SC-002)
- [ ] T100 [P] Load test backend with 100+ concurrent WebSocket connections (SC-003)

### Security & Type Safety

- [ ] T101 [P] Run security audit: verify no hardcoded API keys in backend/src/ (Constitution Principle I)
- [ ] T102 [P] Run TypeScript type checking: tsc --noEmit in frontend/ (Constitution Principle II)
- [ ] T103 [P] Run Python type checking: mypy src/ in backend/ (Constitution Principle II)
- [ ] T104 [P] Verify .env files in .gitignore (Constitution Principle I)

### Documentation & Validation

- [ ] T105 [P] Validate quickstart.md setup instructions work end-to-end
- [ ] T106 [P] Update CLAUDE.md agent context file with final technology stack (from research.md)
- [ ] T107 [P] Create API documentation using FastAPI /docs endpoint validation
- [ ] T108 [P] Add inline code documentation for complex business logic

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Phase 2 completion
- **User Story 2 (Phase 4)**: Depends on Phase 2 completion (can run in parallel with US1 if staffed)
- **User Story 3 (Phase 5)**: Depends on Phase 2 completion (can run in parallel with US1, US2 if staffed)
- **User Story 4 (Phase 6)**: Depends on Phase 2 completion (can run in parallel with US1, US2, US3 if staffed)
- **Polish (Phase 7)**: Depends on all user stories completion

### User Story Completion Order

**Recommended Sequential Order** (for MVP-first delivery):
1. User Story 1 (P1) - Core price viewing capability
2. User Story 2 (P2) - Gainers/Losers discovery
3. User Story 3 (P3) - Search and filter
4. User Story 4 (P3) - Chart visualization

**Parallel Execution** (if multiple developers available):
- After Phase 2 completes, US1, US2, US3, and US4 can all proceed in parallel
- Each user story is independently testable and deliverable

### Critical Path

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational) ← BLOCKING
    ↓
┌───────┬───────┬───────┬───────┐
│  US1  │  US2  │  US3  │  US4  │ (Parallel if staffed)
└───────┴───────┴───────┴───────┘
    ↓
Phase 7 (Polish)
```

---

## Parallel Execution Examples

### Within Phase 2 (Foundational):
**Group A** (Shared Types):
- T011, T012, T013, T014 (all marked [P])

**Group B** (Backend Infrastructure):
- T017, T018, T019, T020, T021 (all marked [P])

**Group C** (Backend Models):
- T026, T027, T028 (all marked [P])

**Group D** (Frontend Infrastructure):
- T030, T031, T032, T033, T034, T035, T036, T037 (all marked [P])

### Within User Story 1:
**Group A** (Backend):
- T038, T039, T043 (all marked [P])

**Group B** (Frontend):
- T046, T047, T048, T051, T052 (all marked [P])

### Within User Story 2:
**Group A** (Backend):
- T056, T057, T058, T059 (all marked [P])

**Group B** (Frontend):
- T061 (can start immediately after foundational)

### Within User Story 3:
**Group A** (Backend):
- T066, T067, T068, T069 (all marked [P])

**Group B** (Frontend):
- T071, T072 (all marked [P])

### Within User Story 4:
**Group A** (Backend):
- T081 (marked [P])

**Group B** (Frontend):
- T082, T083, T084 (all marked [P])

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)
**Recommendation**: User Story 1 (Phase 3) only
- Provides core value: viewing top 20 cryptocurrencies with real-time prices
- Independently testable and deliverable
- Meets SC-001 through SC-009 success criteria
- Foundation for all other features

### Incremental Delivery
1. **Release 1 (MVP)**: User Story 1 - Live cryptocurrency price viewing
2. **Release 2**: Add User Story 2 - Gainers/Losers discovery
3. **Release 3**: Add User Story 3 - Search and filtering
4. **Release 4**: Add User Story 4 - Price trend charts
5. **Release 5**: Polish phase - production hardening

### Validation Checkpoints
- After Phase 2: Verify foundation with health check endpoint and Redis connectivity
- After each User Story: Run independent test criteria from spec.md
- After Phase 7: Run full quickstart.md validation and performance benchmarks (SC-001 through SC-009)

---

## Task Count Summary

- **Phase 1 (Setup)**: 10 tasks
- **Phase 2 (Foundational)**: 27 tasks (T011-T037)
- **Phase 3 (User Story 1)**: 18 tasks (T038-T055)
- **Phase 4 (User Story 2)**: 10 tasks (T056-T065)
- **Phase 5 (User Story 3)**: 12 tasks (T066-T077)
- **Phase 6 (User Story 4)**: 12 tasks (T078-T089)
- **Phase 7 (Polish)**: 19 tasks (T090-T108)

**Total**: 108 tasks

**Parallel Opportunities**: 62 tasks marked [P] can run concurrently with other tasks in same phase

**Independent Test Criteria**: Each user story phase includes acceptance criteria from spec.md for independent validation
