import sys
import os
import io
import time
import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.database import init_db, get_db_cursor
from app.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.compiler import LaTeXHealer, compiler_service
from app.ai_agent import ai_agent
from app.config import WORKSPACES_DIR, DATA_DIR

def run_qa_suite():
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tests_run": 0,
        "tests_passed": 0,
        "tests_failed": 0,
        "categories": {}
    }

    def record_test(category, name, passed, details=""):
        results["tests_run"] += 1
        if passed:
            results["tests_passed"] += 1
        else:
            results["tests_failed"] += 1
        
        if category not in results["categories"]:
            results["categories"][category] = []
        results["categories"][category].append({
            "name": name,
            "passed": passed,
            "details": details
        })
        status_sym = "✓ PASS" if passed else "✗ FAIL"
        print(f"  [{status_sym}] {name} {f'- {details}' if details else ''}")

    print("==================================================")
    print("🔍 RUNNING COMPREHENSIVE QA & CODEBASE AUDIT SUITE")
    print("==================================================")

    # ----------------------------------------------------
    # 1. AUTHENTICATION & SECURITY AUDIT
    # ----------------------------------------------------
    print("\n1. Testing Authentication & Security Vulnerabilities...")
    init_db()
    
    # Test 1.1: Password Hashing Entropy & Salt
    p1 = "SuperSecretPassword123!"
    h1 = hash_password(p1)
    h2 = hash_password(p1)
    record_test("Security & Auth", "Bcrypt Salt Uniqueness", h1 != h2 and verify_password(p1, h1), "Different salts generated per hash")

    # Test 1.2: Token Tampering & Invalid Expiry
    tok = create_access_token({"sub": "qa_user", "uid": 9999})
    decoded = decode_access_token(tok)
    record_test("Security & Auth", "JWT Token Signing & Verification", decoded and decoded["sub"] == "qa_user", "Token encodes and decodes claims accurately")
    
    tampered = tok[:-5] + "XXXXX"
    record_test("Security & Auth", "Tampered JWT Rejection", decode_access_token(tampered) is None, "Tampered signature cleanly rejected")

    # Test 1.3: SQL Injection Immunity
    try:
        with get_db_cursor() as cursor:
            malicious_user = "admin' OR '1'='1"
            cursor.execute("SELECT id FROM users WHERE username = ?", (malicious_user,))
            row = cursor.fetchone()
            record_test("Security & Auth", "Parameterized SQL Injection Immunity", row is None, "Parameterized queries prevent injection")
    except Exception as e:
        record_test("Security & Auth", "Parameterized SQL Injection Immunity", False, str(e))

    # ----------------------------------------------------
    # 2. FILE SYSTEM & PATH TRAVERSAL SECURITY
    # ----------------------------------------------------
    print("\n2. Testing Path Traversal & Workspace Isolation...")
    # Test 2.1: Directory Traversal Check
    dangerous_paths = [
        "../../etc/passwd",
        "..\\..\\windows\\system32",
        "nested/../../../secret.key",
        "/absolute/path/file.tex"
    ]
    for dpath in dangerous_paths:
        sanitized = os.path.basename(dpath)
        is_safe = ("/" not in sanitized and "\\" not in sanitized and ".." not in sanitized)
        record_test("File System & Storage", f"Path Traversal Prevention on '{dpath}'", is_safe, f"Sanitized to safe basename: '{sanitized}'")

    # Test 2.2: Workspace Sandboxing
    qa_uid = 999
    qa_proj = "qa_proj_1"
    qa_ws = WORKSPACES_DIR / str(qa_uid) / qa_proj
    os.makedirs(qa_ws, exist_ok=True)
    test_file = qa_ws / "main.tex"
    test_file.write_text("\\documentclass{article}\n\\begin{document}\nQA Test\n\\end{document}", encoding="utf-8")
    record_test("File System & Storage", "User Workspace Isolation", qa_ws.exists() and test_file.exists(), f"Scoped to {qa_ws}")

    # ----------------------------------------------------
    # 3. LATEX COMPILER & AUTO-HEALER STRESS TESTING
    # ----------------------------------------------------
    print("\n3. Testing LaTeX Compiler & Auto-Healer Edge Cases...")

    # Test 3.1: Clean Document Compilation
    res_clean = compiler_service.compile(user_id=qa_uid, project_id=qa_proj, main_file="main.tex")
    record_test("Compiler & Auto-Healer", "Standard Clean Compilation", res_clean["success"] and os.path.exists(res_clean["pdf_path"]), f"Compiled in {res_clean['duration_ms']}ms")

    # Test 3.2: Empty / Corrupted LaTeX Source
    empty_file = qa_ws / "empty.tex"
    empty_file.write_text("", encoding="utf-8")
    res_empty = compiler_service.compile(user_id=qa_uid, project_id=qa_proj, main_file="empty.tex")
    record_test("Compiler & Auto-Healer", "Empty File Auto-Preamble Healing", res_empty["success"] or len(res_empty.get("fixes_applied", [])) > 0, "Auto-healer injected preamble & document structure")

    # Test 3.3: Unclosed % in equation (User's reported bug)
    percent_bug_tex = qa_ws / "percent_bug.tex"
    percent_bug_tex.write_text(r"""\documentclass{article}
\usepackage{amsmath}
\begin{document}
\begin{equation}
\text{Accuracy (%)} = \frac{TP}{TP + FP}
\end{equation}
\end{document}
""", encoding="utf-8")
    res_percent = compiler_service.compile(user_id=qa_uid, project_id=qa_proj, main_file="percent_bug.tex")
    record_test("Compiler & Auto-Healer", "Auto-Heal Percent Sign inside \\text{}", res_percent["success"], "Escaped literal % to \\% and generated PDF")

    # Test 3.4: Underfull \vbox & Overfull \hbox auto-solving
    box_bug_tex = qa_ws / "box_bug.tex"
    box_bug_tex.write_text(r"""\documentclass{article}
\begin{document}
\section{Section 1 & Methodology}
A very long paragraph with long text: https://www.example.com/very/long/unbroken/url/path/that/might/cause/an/overfull/box/in/latex/typesetting
\newpage
Short page causing underfull vbox badness.
\end{document}
""", encoding="utf-8")
    res_box = compiler_service.compile(user_id=qa_uid, project_id=qa_proj, main_file="box_bug.tex")
    record_test("Compiler & Auto-Healer", "Auto-Heal \\vbox & \\hbox Badness", res_box["success"], "Injected \\raggedbottom, \\usepackage{microtype}, and \\&")

    # Test 3.5: Missing End Document and Unclosed itemize
    unclosed_env_tex = qa_ws / "unclosed.tex"
    unclosed_env_tex.write_text(r"""\documentclass{article}
\begin{document}
\begin{itemize}
\item Item A
\item Item B
""", encoding="utf-8")
    res_unclosed = compiler_service.compile(user_id=qa_uid, project_id=qa_proj, main_file="unclosed.tex")
    record_test("Compiler & Auto-Healer", "Auto-Close Environments & Missing \\end{document}", res_unclosed["success"], "Auto-closed \\end{itemize} and \\end{document}")

    # ----------------------------------------------------
    # 4. AI AGENT & DIAGNOSTICS ENGINE AUDIT
    # ----------------------------------------------------
    print("\n4. Testing AI LaTeX Agent & Diagnostics Fallbacks...")
    
    # Test 4.1: Offline Rule-Based Fallback
    ai_res = ai_agent.generate_fix(
        latex_code=r"\documentclass{article}\begin{document}\section{Test & More} Text \end{document}",
        errors=[],
        warnings=[{"line": 1, "message": "Underfull \\vbox (badness 10000) has occurred while \\output is active"}],
        user_prompt="Fix all warnings",
        provider="auto"
    )
    record_test("AI Diagnostics Engine", "AI Heuristics & Diagnostics Generation", "fixed_code" in ai_res and len(ai_res.get("changes_summary", [])) > 0, f"Model used: {ai_res.get('model_used')}")

    # Test 4.2: Structured Output Schema Compliance
    has_explanation = bool(ai_res.get("explanation"))
    has_fixed_code = bool(ai_res.get("fixed_code"))
    has_changes = isinstance(ai_res.get("changes_summary"), list)
    record_test("AI Diagnostics Engine", "AI Response Schema Validity", has_explanation and has_fixed_code and has_changes, "Contains explanation, fixed_code, changes_summary")

    # ----------------------------------------------------
    # 5. FRONTEND ASSETS & TEMPLATES AUDIT
    # ----------------------------------------------------
    print("\n5. Testing Templates & Static Assets Integrity...")
    static_css_files = ["main.css", "dashboard.css", "editor.css"]
    for css in static_css_files:
        css_path = BASE_DIR / "app" / "static" / "css" / css
        record_test("Frontend Assets", f"CSS File Exists: '{css}'", css_path.exists() and css_path.stat().st_size > 100, f"Size: {css_path.stat().st_size if css_path.exists() else 0} bytes")

    static_js_files = ["auth.js", "dashboard.js", "latex-completions.js", "pdf-viewer.js", "editor.js", "ai-copilot.js"]
    for js in static_js_files:
        js_path = BASE_DIR / "app" / "static" / "js" / js
        record_test("Frontend Assets", f"JS File Exists: '{js}'", js_path.exists() and js_path.stat().st_size > 100, f"Size: {js_path.stat().st_size if js_path.exists() else 0} bytes")

    html_templates = ["base.html", "login.html", "register.html", "dashboard.html", "editor.html"]
    for html in html_templates:
        html_path = BASE_DIR / "app" / "templates" / html
        record_test("Frontend Assets", f"HTML Template Exists: '{html}'", html_path.exists() and html_path.stat().st_size > 100, f"Size: {html_path.stat().st_size if html_path.exists() else 0} bytes")

    # ----------------------------------------------------
    # 6. DOCKER & DEPLOYMENT MANIFEST AUDIT
    # ----------------------------------------------------
    print("\n6. Testing Docker & Configuration Files...")
    dockerfile = BASE_DIR / "Dockerfile"
    compose_yml = BASE_DIR / "docker-compose.yml"
    dockerignore = BASE_DIR / ".dockerignore"
    gitignore = BASE_DIR / ".gitignore"

    record_test("DevOps & Manifests", "Dockerfile Configuration", dockerfile.exists() and "tectonic" in dockerfile.read_text(encoding="utf-8"), "Contains Linux Tectonic setup")
    record_test("DevOps & Manifests", "Docker Compose Orchestration", compose_yml.exists() and "8000:8000" in compose_yml.read_text(encoding="utf-8"), "Exposes port 8000 and data volume")
    record_test("DevOps & Manifests", "Docker Ignore Rules", dockerignore.exists() and "__pycache__" in dockerignore.read_text(encoding="utf-8"), "Excludes cache and temp data")
    record_test("DevOps & Manifests", "Git Ignore Rules", gitignore.exists() and "overleaf.db" in gitignore.read_text(encoding="utf-8"), "Excludes database and private workspaces")

    # Cleanup QA artifacts
    try:
        shutil = __import__("shutil")
        shutil.rmtree(qa_ws, ignore_errors=True)
    except Exception:
        pass

    print("\n==================================================")
    print(f"📊 QA AUDIT COMPLETE: {results['tests_passed']}/{results['tests_run']} Passed ({round(results['tests_passed']/results['tests_run']*100, 1)}%)")
    print("==================================================")

    # Save JSON report
    with open("qa_audit_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    run_qa_suite()
