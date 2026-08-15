# 🚀 Overleaf Studio (Open-Source LaTeX Web IDE)

[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![LaTeX](https://img.shields.io/badge/LaTeX-Tectonic%20Engine-008080?logo=latex&logoColor=white)](https://tectonic-typesetting.github.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A complete, profound, open-source **Overleaf-style LaTeX Web IDE & Compiler** built with **FastAPI, Monaco Editor, and the Tectonic LaTeX Engine**. Features real-time split-screen PDF preview, multi-file project workspaces, intelligent autocompletion, an **Auto-Healing compiler**, and an integrated **AI LaTeX Copilot & Code Fixer Agent**.

---

## ✨ Features

- ⚡ **Standalone Open-Source LaTeX Engine**: Powered by **Tectonic**, compiling full LaTeX packages (math, amsmath, tikz, beamer, geometry, graphicx, hyperref, bibtex) without needing a heavy 4GB TeXLive distribution.
- 🪄 **Intelligent LaTeX Auto-Healer**: Automatically catches and repairs syntax bugs (e.g. `\text{` unclosed across paragraph breaks, unescaped `%` / `&`, unbalanced braces, unclosed environments) to guarantee valid PDF output even with imperfect code.
- 📏 **Automated `\hbox` & `\vbox` Badness (10000) Solver**: Automatically resolves `Underfull \vbox (badness 10000)`, `Overfull \hbox`, and margin overflows using `microtype`, `\raggedbottom`, and flexible emergency stretch.
- 🤖 **Interactive AI LaTeX Copilot**: Integrated AI Agent (powered by Google Gemini / Free LLM / Offline LaTeX Expert Engine) to diagnose compiler warnings, polish academic tone, format tables, and apply 1-click code repairs.
- 💻 **Overleaf-Grade Editor (Monaco)**: Dark Emerald theme with 100+ LaTeX snippets, Greek symbols, math environments, dynamic `\ref{...}` labels, and dynamic `\cite{...}` BibTeX citation autocompletion.
- 📄 **Real-Time Side-by-Side PDF Viewer**: Split-screen live preview with zoom controls, debounced auto-compilation on typing, PDF download, and ZIP project export.
- 🔒 **User Authentication & Workspaces**: Secure user login/register with salted bcrypt password hashing and JWT sessions.
- 📦 **Rich Starter Templates**: Built-in templates for Blank Papers, IEEE Academic Research, CV/Resumes, Beamer Presentation Slides, and Lab Reports.

---

## ⚡ Quick Start with Python (Recommended)

Run directly on your PC with zero setup, zero virtualization, and zero heavy TeXLive downloads!

```bash
# 1. Clone the repository
git clone https://github.com/Sifatkhan-1915020/Latex-Studio.git
cd Latex-Studio

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the application
python run.py
```

👉 The app will automatically initialize the database, prepare the standalone compiler, and open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser!

---

## 🐳 Optional: Quick Start with Docker

If you have Docker Desktop installed and running on your system:

```bash
# Clone the repository
git clone https://github.com/Sifatkhan-1915020/Latex-Studio.git
cd Latex-Studio

# Start the container
docker compose up -d --build
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser.

To stop the container:
```bash
docker compose down
```


---

## ⚙️ Environment Variables (Optional)

You can set these in a `.env` file or in `docker-compose.yml`:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `SECRET_KEY` | JWT token encryption key | `overleaf-super-secret-production-jwt-key-987654321` |
| `GEMINI_API_KEY` | (Optional) Google Gemini API Key for AI Copilot | Free Public LLM & Built-in Expert Engine fallback |
| `PORT` | Application HTTP port | `8000` |

---

## 📁 Project Structure

```
overleafBypass/
├── app/
│   ├── config.py                 # Paths, JWT, and cross-platform Tectonic discovery
│   ├── database.py               # SQLite schema (users, projects, project_files)
│   ├── auth.py                   # bcrypt hashing & JWT token dependencies
│   ├── compiler.py               # Multi-stage compiler & LaTeXHealer engine
│   ├── ai_agent.py               # AI LaTeX Copilot & Diagnostics Agent
│   ├── templates_data.py         # Pre-built starter LaTeX templates
│   ├── routes/
│   │   ├── auth_routes.py        # /api/auth (register, login, me, logout)
│   │   ├── project_routes.py     # /api/projects (CRUD, duplicate, export ZIP)
│   │   ├── file_routes.py        # /api/projects/{id}/files (read, save, upload)
│   │   ├── compile_routes.py     # /api/projects/{id}/compile, /pdf, /download-pdf
│   │   ├── ai_routes.py          # /api/ai/assist (AI diagnostic & code repair)
│   │   └── view_routes.py        # Jinja2 views (/login, /register, /dashboard, /project/{id})
│   ├── static/
│   │   ├── css/                  # main.css, dashboard.css, editor.css
│   │   └── js/                   # auth.js, dashboard.js, latex-completions.js, pdf-viewer.js, editor.js, ai-copilot.js
│   └── templates/                # Jinja2 HTML templates
├── bin/                          # Windows standalone Tectonic binary
├── data/                         # Persistent SQLite DB and user project workspaces
├── Dockerfile                    # Container definition with native Linux Tectonic & Python 3.12
├── docker-compose.yml            # Docker Compose orchestration with persistent data volume
├── requirements.txt              # Python package dependencies
├── run.py                        # Local runner script
└── test_system.py                # System verification test suite
```

---

## 📄 License

MIT License. Open-source and free for personal, academic, and commercial usage.
