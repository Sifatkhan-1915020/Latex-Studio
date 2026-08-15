import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.compiler import compiler_service
from app.config import WORKSPACES_DIR

def test_auto_healer():
    print("========================================")
    print("🧪 TESTING LATEX AUTO-HEALER & TOLERANCE")
    print("========================================")

    test_user_id = 888
    proj_id = "test_user_bug_report"
    proj_dir = WORKSPACES_DIR / str(test_user_id) / proj_id
    os.makedirs(proj_dir, exist_ok=True)

    # Recreate the exact bug: unclosed \text{ without closing brace before blank line / paragraph
    buggy_latex = r"""\documentclass{article}
\usepackage{amsmath}
\begin{document}

\section{Introduction}
Here is some normal text.

\begin{equation}
E = mc^2 + \text{some unclosed text command here

\end{equation}

More text follows here.

\end{document}
"""

    with open(proj_dir / "main.tex", "w", encoding="utf-8") as f:
        f.write(buggy_latex)

    print("\n1. Compiling document with 'Paragraph ended before \\text@ was complete' bug...")
    res = compiler_service.compile(user_id=test_user_id, project_id=proj_id, main_file="main.tex")

    print(f"  Compile Success: {res['success']}")
    print(f"  Healed Flag: {res.get('healed')}")
    print(f"  Fixes Applied Count: {len(res.get('fixes_applied', []))}")
    for fix in res.get("fixes_applied", []):
        print(f"    -> Line {fix['line']}: {fix['message']}")

    assert res["success"], "Auto-healer should have successfully compiled the PDF!"
    assert res.get("healed"), "Healed flag should be True!"
    assert res.get("pdf_path") and os.path.exists(res["pdf_path"]), "PDF output must exist!"
    pdf_size = os.path.getsize(res["pdf_path"])
    print(f"  ✓ PDF Successfully Generated: {pdf_size} bytes")

    print("\n2. Testing unclosed environment & unescaped ampersand auto-healing...")
    buggy_latex_2 = r"""\documentclass{article}
\usepackage{amsmath}
\begin{document}

\section{Test Section}
Python & Tectonic are working together.

\begin{itemize}
\item Item 1
\item Item 2

\end{document}
"""
    proj_id_2 = "test_user_bug_report_2"
    proj_dir_2 = WORKSPACES_DIR / str(test_user_id) / proj_id_2
    os.makedirs(proj_dir_2, exist_ok=True)
    with open(proj_dir_2 / "main.tex", "w", encoding="utf-8") as f:
        f.write(buggy_latex_2)

    res_2 = compiler_service.compile(user_id=test_user_id, project_id=proj_id_2, main_file="main.tex")
    print(f"  Compile Success: {res_2['success']}")
    print(f"  Healed Flag: {res_2.get('healed')}")
    for fix in res_2.get("fixes_applied", []):
        print(f"    -> Line {fix['line']}: {fix['message']}")
    assert res_2["success"], "Auto-healer should have closed the itemize environment and escaped &!"

    print("\n========================================")
    print("🎉 ALL AUTO-HEALER TESTS PASSED!")
    print("========================================")

if __name__ == "__main__":
    test_auto_healer()
