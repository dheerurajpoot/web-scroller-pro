# Workspace

## Overview

pnpm workspace monorepo using TypeScript. Each package manages its own dependencies.

---

## Traffic Guru (Python Desktop App)

Located at `traffic_guru/` — a cross-platform (Windows & macOS) Python desktop application.

### Stack
- **Python** 3.11
- **GUI**: PyQt6 (dark theme)
- **Browser automation**: Selenium + webdriver-manager
- **Sitemap parsing**: requests + BeautifulSoup4 + lxml
- **Database**: SQLite (via sqlite3)
- **License system**: HMAC-SHA256 + Fernet encryption
- **Proxy support**: HTTP/HTTPS/SOCKS4/SOCKS5

### Run
```bash
cd traffic_guru
python3 main.py
```

### Generate License Key (admin tool)
```bash
cd traffic_guru
python3 generate_license.py
```

### Build Standalone Executable
```bash
pip install pyinstaller
pyinstaller --noconfirm --onedir --windowed --name "TrafficGuru" traffic_guru/main.py
```

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
