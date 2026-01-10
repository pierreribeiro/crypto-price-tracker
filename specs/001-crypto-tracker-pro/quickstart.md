# Quickstart Guide: CryptoTracker Pro

**Date**: 2026-01-09
**Branch**: `001-crypto-tracker-pro`
**Prerequisites**: Node.js 20+, Python 3.11+, Redis 7.x, Docker (optional)

---

## Table of Contents

1. [Overview](#overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Backend Setup (FastAPI)](#backend-setup-fastapi)
4. [Frontend Setup (React + Vite)](#frontend-setup-react--vite)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Common Issues](#common-issues)

---

## Overview

CryptoTracker Pro is a full-stack web application for cryptocurrency price tracking with real-time updates.

**Technology Stack**:
- **Frontend**: React 19, Vite 6, TypeScript 5.7+ (strict mode)
- **Backend**: FastAPI 0.115+, Python 3.11+
- **Charts**: Lightweight Charts 4.2+ (TradingView)
- **Real-Time**: Native WebSocket
- **Caching**: Redis 7.x
- **Testing**: Vitest (frontend), pytest (backend)

**Key Features**:
- Top 20 cryptocurrencies by market cap
- Top Gainers/Losers views with tab navigation
- Search and filter by price range and market cap
- 7-day sparkline charts (click to expand)
- Auto-refresh every 30 seconds via WebSocket
- Manual refresh button
- Mobile-responsive (320px minimum width)

---

## Development Environment Setup

### 1. Install Prerequisites

**macOS** (using Homebrew):
```bash
# Node.js 20+
brew install node

# Python 3.11+
brew install python@3.11

# Redis 7.x
brew install redis

# Start Redis service
brew services start redis
```

**Ubuntu/Debian**:
```bash
# Node.js 20+
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python 3.11+
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Redis 7.x
sudo apt-get install -y redis-server
sudo systemctl start redis-server
```

**Windows** (using Chocolatey):
```powershell
# Node.js 20+
choco install nodejs

# Python 3.11+
choco install python311

# Redis (via WSL or Docker)
# Option 1: Use WSL and follow Ubuntu instructions
# Option 2: Use Docker (see Docker section below)
```

### 2. Verify Installations

```bash
node --version   # Should be v20.x or higher
python3 --version # Should be 3.11 or higher
redis-cli ping   # Should respond with "PONG"
```

### 3. Clone Repository

```bash
git clone <repository-url>
cd crypto-price-tracker
git checkout 001-crypto-tracker-pro
```

---

## Backend Setup (FastAPI)

### 1. Create Python Virtual Environment

```bash
cd backend
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt

# requirements.txt should contain:
# fastapi>=0.115.0
# uvicorn[standard]>=0.32.0
# redis>=7.0.0
# httpx>=0.27.0          # For external API calls
# pydantic>=2.0.0
# python-dotenv>=1.0.0
# pytest>=8.0.0
# pytest-asyncio>=0.24.0
# mypy>=1.13.0
```

### 3. Configure Environment Variables

Create `.env` file in `backend/` directory:

```bash
# backend/.env
# External API Keys (Constitution Principle I: Security-First)
COINGECKO_API_KEY=your_coingecko_api_key_here  # Optional for free tier
COINMARKETCAP_API_KEY=your_coinmarketcap_api_key_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # Leave empty for local development

# Application Configuration
API_VERSION=v1
CACHE_TTL_SECONDS=300  # 5 minutes per FR-016
AUTO_REFRESH_INTERVAL_SECONDS=30  # FR-013

# Logging
LOG_LEVEL=INFO
```

**Important**: Add `.env` to `.gitignore` to prevent accidental commit of API keys.

### 4. Project Structure

```bash
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   ├── cryptocurrency.py  # Cryptocurrency, PriceDataPoint models
│   │   └── market_category.py # MarketCategory enum
│   ├── services/
│   │   ├── __init__.py
│   │   ├── coingecko_client.py   # CoinGecko API client
│   │   ├── coinmarketcap_client.py # CoinMarketCap API client
│   │   ├── cache_service.py      # Redis caching layer
│   │   ├── price_service.py      # Business logic for price operations
│   │   └── validation_service.py  # Data validation (FR-018)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── health.py         # Health check endpoint
│   │   │   ├── cryptocurrencies.py # REST endpoints
│   │   │   └── websocket.py      # WebSocket endpoint
│   │   └── dependencies.py       # FastAPI dependencies
│   └── lib/
│       ├── __init__.py
│       ├── retry.py              # Exponential backoff retry logic
│       ├── error_handling.py     # Error handling utilities
│       └── formatters.py         # Number formatting utilities
├── tests/
│   ├── contract/
│   │   ├── test_coingecko_contract.py
│   │   └── test_coinmarketcap_contract.py
│   ├── integration/
│   │   ├── test_cache_service.py
│   │   ├── test_fallback_mechanism.py
│   │   └── test_websocket.py
│   └── unit/
│       ├── test_price_service.py
│       ├── test_validation_service.py
│       └── test_formatters.py
├── requirements.txt
├── .env
└── .gitignore
```

### 5. Run Backend Development Server

```bash
# From backend/ directory with venv activated
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Backend will be available at:
# - API: http://localhost:8000/api/v1
# - Docs: http://localhost:8000/docs (OpenAPI/Swagger UI)
# - WebSocket: ws://localhost:8000/api/v1/ws/prices
```

---

## Frontend Setup (React + Vite)

### 1. Install Dependencies

```bash
cd frontend
npm install

# package.json should contain:
# react: ^19.0.0
# react-dom: ^19.0.0
# typescript: ^5.7.0
# vite: ^6.0.0
# lightweight-charts: ^4.2.0
# @testing-library/react: ^16.0.0
# vitest: ^2.0.0
```

### 2. Configure Environment Variables

Create `.env` file in `frontend/` directory:

```bash
# frontend/.env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_URL=ws://localhost:8000/api/v1/ws/prices
```

**Production**:
```bash
# frontend/.env.production
VITE_API_BASE_URL=https://api.cryptotracker.example/v1
VITE_WS_URL=wss://api.cryptotracker.example/v1/ws/prices
```

### 3. TypeScript Configuration

Ensure `tsconfig.json` has strict mode enabled (Constitution Principle II):

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "strict": true,              // Constitution requirement
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

### 4. Project Structure

```bash
frontend/
├── src/
│   ├── main.tsx                # Application entry point
│   ├── App.tsx                 # Root component
│   ├── components/
│   │   ├── CryptoList.tsx        # Top 20 cryptocurrencies list
│   │   ├── CryptoCard.tsx        # Individual cryptocurrency card
│   │   ├── SearchBar.tsx         # Search input (FR-008)
│   │   ├── FilterPanel.tsx       # Price/market cap filters (FR-009, FR-010)
│   │   ├── TabNavigation.tsx     # All/Gainers/Losers tabs (FR-023)
│   │   ├── SparklineChart.tsx    # 7-day sparkline (FR-011)
│   │   ├── ChartDetailView.tsx   # Expanded chart view (FR-012)
│   │   ├── RefreshButton.tsx     # Manual refresh (FR-014)
│   │   ├── LastUpdated.tsx       # Timestamp display (FR-015)
│   │   ├── SkeletonScreen.tsx    # Loading state (FR-024)
│   │   └── ErrorBoundary.tsx     # Error handling (Constitution Principle VI)
│   ├── pages/
│   │   └── Dashboard.tsx         # Main dashboard page
│   ├── services/
│   │   ├── api.ts                # REST API client
│   │   └── websocket.ts          # WebSocket client
│   ├── hooks/
│   │   ├── useWebSocket.ts       # Custom WebSocket hook
│   │   ├── useCryptocurrencies.ts # Data fetching hook
│   │   └── useSearch.ts          # Search/filter hook
│   ├── types/
│   │   ├── cryptocurrency.ts     # Shared TypeScript interfaces
│   │   └── api.ts                # API response types
│   ├── utils/
│   │   ├── formatters.ts         # Number formatting utilities
│   │   └── validation.ts         # Client-side validation
│   └── styles/
│       └── global.css            # Global styles
├── tests/
│   ├── e2e/
│   │   └── dashboard.spec.ts     # End-to-end tests
│   └── unit/
│       ├── components/
│       └── hooks/
├── vite.config.ts
├── tsconfig.json
├── package.json
├── .env
└── .gitignore
```

### 5. Run Frontend Development Server

```bash
# From frontend/ directory
npm run dev

# Frontend will be available at:
# http://localhost:5173
```

---

## Running the Application

### Option 1: Manual (Development)

**Terminal 1** (Backend):
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2** (Redis - if not running as service):
```bash
redis-server
```

**Terminal 3** (Frontend):
```bash
cd frontend
npm run dev
```

Open browser to `http://localhost:5173`

### Option 2: Docker Compose (Recommended)

Create `docker-compose.yml` in project root:

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - REDIS_PORT=6379
    env_file:
      - ./backend/.env
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ./backend/src:/app/src
    command: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    environment:
      - VITE_API_BASE_URL=http://localhost:8000/api/v1
      - VITE_WS_URL=ws://localhost:8000/api/v1/ws/prices
    volumes:
      - ./frontend/src:/app/src
    command: npm run dev -- --host

volumes:
  redis-data:
```

**Run with Docker Compose**:
```bash
docker-compose up --build
```

---

## Testing

### Backend Tests (pytest)

```bash
cd backend
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test types
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest tests/contract/          # Contract tests only

# Run type checking (Constitution Principle II)
mypy src/
```

### Frontend Tests (Vitest)

```bash
cd frontend

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run in watch mode
npm run test:watch

# Run E2E tests
npm run test:e2e

# Type checking (Constitution Principle II)
npm run type-check  # tsc --noEmit
```

---

## Common Issues

### Issue 1: Redis Connection Refused

**Symptoms**: Backend fails to start with "Connection refused" error

**Solution**:
```bash
# Check if Redis is running
redis-cli ping  # Should respond with "PONG"

# If not running, start Redis:
# macOS:
brew services start redis
# Ubuntu/Debian:
sudo systemctl start redis-server
# Docker:
docker run -d -p 6379:6379 redis:7-alpine
```

### Issue 2: API Rate Limiting

**Symptoms**: External API returns 429 Too Many Requests

**Solution**:
- CoinGecko free tier: 10-50 calls/minute (depends on plan)
- CoinMarketCap free tier: 333 calls/day
- Increase `CACHE_TTL_SECONDS` in `.env` to reduce API calls
- Verify rate limiting implementation in `cache_service.py`
- Check Redis cache is working: `redis-cli keys "crypto:*"`

### Issue 3: WebSocket Connection Fails

**Symptoms**: Frontend shows "Disconnected" indicator

**Solution**:
1. Verify backend is running: `curl http://localhost:8000/api/v1/health`
2. Test WebSocket endpoint: Use tool like `websocat` or browser console
3. Check CORS settings in FastAPI if frontend and backend on different origins
4. Verify firewall allows WebSocket connections (port 8000)

### Issue 4: Type Errors in TypeScript

**Symptoms**: `tsc --noEmit` shows type errors

**Solution**:
```bash
# Ensure strict mode is enabled in tsconfig.json
# Install missing type definitions:
npm install --save-dev @types/node

# Regenerate shared types if data model changed:
# Update frontend/src/types/cryptocurrency.ts to match backend models
```

### Issue 5: Sparkline Charts Not Displaying

**Symptoms**: Charts area is blank or shows error

**Solution**:
1. Verify Lightweight Charts is installed: `npm list lightweight-charts`
2. Check browser console for errors
3. Ensure sparkline data is included in API response: `include_sparkline=true`
4. Verify chart container has non-zero height in CSS

---

## Next Steps

After completing this quickstart:

1. **Familiarize with Codebase**:
   - Review [data-model.md](./data-model.md) for entity definitions
   - Review [contracts/api-specification.yaml](./contracts/api-specification.yaml) for REST API
   - Review [contracts/websocket-spec.md](./contracts/websocket-spec.md) for WebSocket protocol

2. **Explore Features**:
   - Open dashboard at `http://localhost:5173`
   - Test search and filter functionality
   - Click sparkline charts to expand detail view
   - Monitor WebSocket connection in browser DevTools Network tab
   - Trigger manual refresh and observe update latency

3. **Run Tests**:
   - Execute backend and frontend test suites
   - Review test coverage reports
   - Add tests for new features

4. **Development Workflow**:
   - Create feature branch from `001-crypto-tracker-pro`
   - Make changes, run tests, commit with descriptive messages
   - Follow Constitution principles (security, type safety, error handling)

---

## Support

For issues or questions:
- Check [spec.md](./spec.md) for requirements
- Check [plan.md](./plan.md) for implementation details
- Check [constitution.md](../.specify/memory/constitution.md) for project principles
- Review existing tests for usage examples

**Happy coding!** 🚀
