# CryptoTracker Pro - Development Guidelines for Claude Code

**Last Updated**: 2026-01-10
**Project**: Real-time cryptocurrency price tracking dashboard
**Architecture**: Full-stack web application (FastAPI + React)

---

## 🎯 Project Mission

Build a professional-grade cryptocurrency price tracker with real-time updates, focusing on reliability, type safety, and mobile-first design.

---

## 📋 Constitution Principles

The project follows 7 core principles that guide all architectural and implementation decisions:

### I. Security-First Development
- Never commit secrets (.env files excluded via .gitignore)
- API keys managed through environment variables only
- CORS properly configured for frontend-backend communication
- Input validation on all external API data

### II. Type Safety Without Compromise
- **Frontend**: TypeScript 5.7+ strict mode (tsconfig.json)
- **Backend**: Python 3.11+ with mypy strict mode (setup.cfg)
- **Shared**: TypeScript interfaces in `shared/types/` for cross-stack consistency
- Zero tolerance for `any` types or untyped code

### III. API Reliability Through Fallback
- Primary: CoinGecko API (free tier with optional API key)
- Fallback: CoinMarketCap API (automatic failover)
- Retry logic: Exponential backoff (1s, 2s, 4s, 8s, max 30s)
- Graceful degradation: Serve stale cached data with warnings

### IV. Mobile-First Responsive Design
- Minimum supported width: 320px (iPhone SE)
- Breakpoints: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)
- CSS-first approach with mobile breakpoints
- Touch-friendly UI elements

### V. Real-Time Updates (30-Second Refresh)
- Native WebSocket connection for live price updates
- Automatic reconnection with exponential backoff
- Auto-refresh interval: 30 seconds
- Connection status indicators

### VI. Error Resilience and User Experience
- Never crash - always degrade gracefully
- User-friendly error messages (no stack traces to users)
- React ErrorBoundary for component-level isolation
- Validation of all external API data before display

### VII. Clean Architecture Separation
- Backend: `models/` → `services/` → `api/` → endpoints
- Frontend: `services/` → `hooks/` → `components/` → `pages/`
- Shared types in `shared/types/` for consistency
- No business logic in UI components

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.115+ (async Python web framework)
- **Server**: Uvicorn 0.32+ (ASGI server)
- **Language**: Python 3.11+ with type hints
- **Caching**: Redis 7.x (5-minute TTL for prices, 1-hour for sparklines)
- **HTTP Client**: HTTPX (async requests to external APIs)
- **Validation**: Pydantic 2.0+ (data models and validation)
- **Type Checking**: mypy 1.13+ (strict mode)
- **Linting**: Ruff 0.7+ (fast Python linter)
- **Testing**: pytest 8.0+ with pytest-asyncio

### Frontend
- **Framework**: React 19 (latest features)
- **Build Tool**: Vite 6+ (fast dev server and bundler)
- **Language**: TypeScript 5.7+ (strict mode)
- **Charts**: Lightweight Charts 4.2+ (TradingView library)
- **Linting**: ESLint with TypeScript plugins
- **Formatting**: Prettier
- **Testing**: Vitest (to be configured)

### Infrastructure
- **Cache**: Redis 7.x (installed via Homebrew on macOS)
- **Version Control**: Git with GitHub
- **Package Management**: pip (Python), npm (Node.js)

### External APIs
- **Primary**: CoinGecko API v3 (free tier)
- **Fallback**: CoinMarketCap API v1 (requires API key)

---

## 📁 Project Structure

```
crypto-price-tracker/
├── backend/                    # Python FastAPI backend
│   ├── src/
│   │   ├── api/
│   │   │   └── routes/        # API endpoint definitions
│   │   │       ├── health.py         # Health check endpoint
│   │   │       └── cryptocurrencies.py (pending)
│   │   ├── lib/               # Utility libraries
│   │   │   ├── redis_client.py       # Redis connection pool
│   │   │   ├── retry.py              # Exponential backoff retry logic
│   │   │   ├── error_handling.py     # Custom exceptions
│   │   │   └── formatters.py         # Number formatting utilities
│   │   ├── models/            # Pydantic data models
│   │   │   ├── cryptocurrency.py
│   │   │   ├── price_data_point.py
│   │   │   └── market_category.py
│   │   ├── services/          # Business logic layer
│   │   │   ├── coingecko_client.py   # Primary API client
│   │   │   ├── coinmarketcap_client.py # Fallback API client
│   │   │   ├── cache_service.py      # Redis caching
│   │   │   ├── validation_service.py # Data validation
│   │   │   └── price_service.py (pending)
│   │   └── main.py            # FastAPI application entry point
│   ├── tests/                 # Backend tests
│   ├── requirements.txt       # Python dependencies
│   ├── setup.cfg              # mypy configuration
│   ├── pyproject.toml         # Ruff configuration
│   └── .env.example           # Environment variable template
│
├── frontend/                   # React + Vite frontend
│   ├── src/
│   │   ├── components/        # Reusable React components
│   │   │   ├── ErrorBoundary.tsx     # Error handling wrapper
│   │   │   └── SkeletonScreen.tsx    # Loading placeholders
│   │   ├── pages/             # Page-level components
│   │   ├── services/          # API and WebSocket clients
│   │   │   ├── api.ts                # HTTP API client
│   │   │   └── websocket.ts          # WebSocket client
│   │   ├── hooks/             # Custom React hooks
│   │   │   └── useWebSocket.ts       # WebSocket state management
│   │   ├── utils/             # Utility functions
│   │   │   └── formatters.ts         # Number formatting
│   │   └── styles/            # Global CSS
│   │       └── global.css            # Mobile-first styles
│   ├── tests/                 # Frontend tests
│   ├── package.json           # Node.js dependencies
│   ├── vite.config.ts         # Vite configuration (code splitting)
│   ├── tsconfig.json          # TypeScript configuration (strict mode)
│   ├── .eslintrc.json         # ESLint rules
│   ├── .prettierrc            # Prettier formatting rules
│   └── .env.example           # Environment variable template
│
├── shared/                     # Shared TypeScript types
│   └── types/
│       ├── cryptocurrency.ts   # Core data models
│       └── api.ts              # API response types
│
├── specs/                      # Feature specifications
│   └── 001-crypto-tracker-pro/
│       ├── spec.md             # User stories and requirements
│       ├── plan.md             # Implementation plan
│       ├── tasks.md            # Detailed task breakdown (108 tasks)
│       ├── data-model.md       # Entity definitions
│       ├── research.md         # Technical decisions
│       └── contracts/          # API specifications
│           └── api-specification.yaml
│
├── .github/                    # GitHub configuration
│   └── workflows/              # CI/CD workflows (pending)
│
├── .gitignore                  # Git ignore rules (secrets excluded)
├── CLAUDE.md                   # This file - Claude Code guidelines
└── README.md                   # Project documentation
```

---

## 🔧 Development Tools & Commands

### Backend Commands

```bash
# Navigate to backend
cd backend

# Create virtual environment (one-time setup)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Type checking with mypy
venv/bin/mypy src/

# Linting with Ruff
venv/bin/ruff check .

# Format code with Ruff
venv/bin/ruff format .

# Run tests
venv/bin/pytest

# Start development server
venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Test Redis connectivity
venv/bin/python test_redis.py
```

### Frontend Commands

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server (http://localhost:5173)
npm run dev

# Type checking
npm run build  # TypeScript compilation happens during build

# Linting
npm run lint

# Format code
npm run format

# Check formatting
npm run format:check

# Run tests (when configured)
npm test

# Build for production
npm run build

# Preview production build
npm run preview
```

### Redis Commands

```bash
# Start Redis server (macOS with Homebrew)
brew services start redis

# Stop Redis server
brew services stop redis

# Check Redis status
brew services list | grep redis

# Connect to Redis CLI
redis-cli

# Ping Redis
redis-cli ping  # Should return PONG

# Monitor Redis commands (debugging)
redis-cli monitor

# Clear all cache
redis-cli FLUSHALL
```

---

## 🚀 Development Workflows

### Branch Strategy

**Feature Branches**: Each user story is developed in its own branch

```bash
# Branch naming convention: <issue-number>-<feature-name>
# Example: 004-user-story-1-live-prices

# Create and switch to feature branch
git checkout -b 004-user-story-1-live-prices

# Work on tasks, commit regularly
git add .
git commit -m "feat(us1): implement price service business logic

Implements T038: Price service with top 20 cryptocurrencies
- Fetches data from CoinGecko with fallback to CoinMarketCap
- Implements 5-minute caching strategy
- Validates all external API data

Refs #42"

# Push to remote
git push -u origin 004-user-story-1-live-prices
```

### Task Completion Workflow

**For each task (T001-T108):**

1. **Start the task**: Mark as in-progress in todo list
2. **Implement the task**: Write code following constitution principles
3. **Test the implementation**: Verify it works as expected
4. **Commit the changes**: Include task ID and GitHub issue reference
5. **Update GitHub issue**: Comment on progress, close if task is complete
6. **Mark task complete**: Update todo list

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

Refs #<issue-number>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
Scope: `us1`, `us2`, `us3`, `us4`, `setup`, `foundation`, etc.

**Example:**
```bash
git commit -m "feat(us1): add cryptocurrency list endpoint

Implements T039: GET /api/v1/cryptocurrencies endpoint
- Returns top 20 cryptocurrencies by market cap
- Includes sparkline data
- Implements caching with 5-minute TTL
- Handles API failures gracefully

Closes #43"
```

### User Story Completion Workflow

**When all tasks for a user story are complete:**

1. **Verify all tasks**: Ensure all tasks (T038-T055 for US1) are done
2. **Run all tests**: Backend and frontend tests pass
3. **Manual testing**: Test the feature end-to-end
4. **Create Pull Request**:
   ```bash
   # Push final changes
   git push origin 004-user-story-1-live-prices

   # Create PR via GitHub CLI
   gh pr create --title "User Story 1: View Live Cryptocurrency Prices" \
                --body "Implements FR-001 through FR-005 (18 tasks)

   ## Summary
   - ✅ Backend: Price service, API endpoints, WebSocket support
   - ✅ Frontend: Price list UI, real-time updates, auto-refresh
   - ✅ Testing: All acceptance criteria met

   ## Linked Issues
   Closes #42, #43, #44, #45, #46, #47, #48, #49, #50, #51, #52, #53, #54, #55, #56, #57, #58, #59

   ## Test Plan
   - [ ] Navigate to dashboard
   - [ ] Verify 20 cryptocurrencies display
   - [ ] Verify prices update every 30 seconds
   - [ ] Verify green/red indicators for price changes
   - [ ] Test on mobile (320px width)

   🤖 Built with [Claude Code](https://claude.com/claude-code)" \
                --base main
   ```

5. **Request review**: Tag reviewers, wait for approval
6. **Merge PR**: Use "Squash and merge" or "Merge commit" based on team preference
7. **Delete branch**: Clean up feature branch after merge

### Issue Management

**GitHub Issue Status:**
- **Open**: Task not started
- **In Progress**: Currently working on task (add comment)
- **Closed**: Task completed and verified

**Update issues regularly:**
```bash
# Comment on issue via GitHub CLI
gh issue comment 42 --body "Started T038: Implementing price service business logic"

# Close issue when task complete
gh issue close 42 --comment "✅ Task T038 complete. Price service implemented with CoinGecko/CoinMarketCap fallback and caching."
```

---

## 🔐 MCP Tools Permissions

### Required MCP Tools

Claude Code may need the following MCP tools enabled:

1. **GitHub MCP** (for issue and PR management):
   - `issue_read` - Read GitHub issues
   - `issue_write` - Create and update issues
   - `pull_request_read` - Read pull requests
   - `pull_request_write` - Create and update pull requests
   - `repository operations` - Push branches

2. **Browser MCP** (optional, for testing):
   - `browser_navigate` - Open local dev server
   - `browser_snapshot` - Take screenshots of UI
   - Useful for visual testing during development

### Setting up MCP Tools

If GitHub operations fail, ensure MCP server is configured:

```json
// Claude Desktop config: ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your_github_personal_access_token"
      }
    }
  }
}
```

---

## 🧪 Testing Strategy

### Backend Testing

```python
# Test file: backend/tests/test_price_service.py
import pytest
from src.services.price_service import PriceService

@pytest.mark.asyncio
async def test_get_top_cryptocurrencies():
    service = PriceService()
    cryptos = await service.get_top_cryptocurrencies()

    assert len(cryptos) == 20
    assert cryptos[0].rank == 1
    assert cryptos[0].currentPrice > 0
```

### Frontend Testing

```typescript
// Test file: frontend/tests/formatters.test.ts
import { describe, it, expect } from 'vitest';
import { formatPrice } from '../src/utils/formatters';

describe('formatPrice', () => {
  it('formats small prices with decimals', () => {
    expect(formatPrice(42.50)).toBe('$42.50');
  });

  it('formats large prices with abbreviations', () => {
    expect(formatPrice(1500000)).toBe('$1.50M');
  });
});
```

---

## 📝 Code Quality Standards

### Python Code Style (Backend)

```python
# ✅ GOOD: Type hints, docstrings, validation
async def get_cryptocurrency_by_id(crypto_id: str) -> Cryptocurrency:
    """
    Fetch cryptocurrency by ID from cache or external API

    Args:
        crypto_id: Cryptocurrency identifier (e.g., 'bitcoin')

    Returns:
        Cryptocurrency data model

    Raises:
        NotFoundError: If cryptocurrency not found
    """
    # Try cache first
    cached = await cache_service.get_cryptocurrency_details(crypto_id)
    if cached:
        return Cryptocurrency(**cached)

    # Fetch from API with retry logic
    data = await coingecko_client.get_cryptocurrency_by_id(crypto_id)
    return Cryptocurrency(**data)

# ❌ BAD: No types, no validation, no error handling
async def get_crypto(id):
    data = await api.get(id)
    return data
```

### TypeScript Code Style (Frontend)

```typescript
// ✅ GOOD: Strict types, interfaces, error handling
export async function getCryptocurrencyById(
  id: string
): Promise<Cryptocurrency> {
  try {
    const response = await fetch(`${API_BASE_URL}/cryptocurrencies/${id}`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to fetch cryptocurrency: ${error.message}`);
  }
}

// ❌ BAD: Any types, no error handling
export async function getCrypto(id: any): Promise<any> {
  const res = await fetch(`/api/${id}`);
  return res.json();
}
```

---

## 🐛 Debugging Tips

### Backend Debugging

```bash
# Check FastAPI logs
venv/bin/uvicorn src.main:app --reload --log-level debug

# Test endpoint directly
curl http://localhost:8000/api/v1/health | jq

# Monitor Redis cache
redis-cli monitor

# Test CoinGecko API
curl "https://api.coingecko.com/api/v3/ping" | jq
```

### Frontend Debugging

```javascript
// Enable React DevTools
// Install: https://chrome.google.com/webstore/detail/react-developer-tools

// Debug WebSocket connection
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/prices');
ws.onmessage = (event) => console.log('WS:', event.data);
ws.onerror = (error) => console.error('WS Error:', error);

// Check network requests in browser DevTools (Network tab)
// Verify API responses and caching headers
```

---

## 📚 Key Files to Reference

| File | Purpose |
|------|---------|
| `specs/001-crypto-tracker-pro/spec.md` | User stories and requirements |
| `specs/001-crypto-tracker-pro/tasks.md` | All 108 tasks with dependencies |
| `specs/001-crypto-tracker-pro/data-model.md` | Entity definitions and validation rules |
| `specs/001-crypto-tracker-pro/contracts/api-specification.yaml` | OpenAPI spec for all endpoints |
| `.specify/constitution.md` | Complete constitution with all principles |
| `backend/.env.example` | Required environment variables (backend) |
| `frontend/.env.example` | Required environment variables (frontend) |

---

## 🎯 Current Progress

### ✅ Phase 1: Setup (T001-T010) - COMPLETE
- Project structure
- Dependencies installed
- Type checking configured
- Redis installed and verified

### ✅ Phase 2: Foundational (T011-T037) - COMPLETE
- Shared TypeScript types
- Backend infrastructure (FastAPI, Redis, API clients)
- Frontend infrastructure (React, API/WebSocket services)

### 🔄 Phase 3: User Story 1 - MVP (T038-T055) - IN PROGRESS
- Backend: Price service and endpoints
- Frontend: Dashboard UI with real-time updates
- **This is the MVP milestone**

### ⏳ Phase 4: User Story 2 - Gainers/Losers (T056-T065)
### ⏳ Phase 5: User Story 3 - Search/Filter (T066-T077)
### ⏳ Phase 6: User Story 4 - Charts (T078-T089)
### ⏳ Phase 7: Polish & Production (T090-T108)

---

## 💡 Tips for Claude Code

1. **Always check constitution principles** before making architectural decisions
2. **Reference tasks.md** for complete task details and dependencies
3. **Update GitHub issues** after completing each task
4. **Follow commit message format** for traceability
5. **Test locally** before pushing (run linters, type checkers, tests)
6. **Never commit secrets** - always use .env files
7. **Mobile-first** - test at 320px width
8. **Type everything** - no `any` types allowed
9. **Handle errors gracefully** - user-friendly messages only
10. **Document as you go** - clear docstrings and comments

---

**Last Updated**: 2026-01-10
**Next Milestone**: Phase 3 - User Story 1 (MVP)
**Total Tasks**: 108 (37 complete, 71 remaining)
