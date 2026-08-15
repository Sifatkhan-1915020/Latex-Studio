import sys
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.ai_agent import ai_agent

def test_ai_agent_warnings():
    print("========================================")
    print("🤖 TESTING AI LATEX COPILOT AGENT")
    print("========================================")

    sample_latex = r"""\documentclass{article}
\usepackage{amsmath}
\begin{document}

\section{Introduction & Methodology}

Here is a paragraph that causes typesetting warnings.
Supercalifragilisticexpialidociousverylongunbrokenwordwithoutanyhyphenationpointsthatwilldefinitelyoverflowthecolumnmargin.

\begin{equation}
\text{Accuracy (%)} = \frac{TP + TN}{TP + TN + FP + FN}
\end{equation}

\end{document}
"""

    mock_warnings = [
        {"line": 49, "message": r"Underfull \vbox (badness 10000) has occurred while \output is active"},
        {"line": 121, "message": r"Underfull \hbox (badness 10000) in paragraph at lines 118--121"},
        {"line": 121, "message": r"Overfull \hbox (3.07361pt too wide) in paragraph at lines 118--121"},
        {"line": 142, "message": r"Overfull \hbox (45.6813pt too wide) in paragraph at lines 136--142"},
        {"line": 150, "message": r"Underfull \vbox (badness 1062) has occurred while \output is active"}
    ]

    mock_errors = []

    print("\n1. Testing AI Agent with user warnings and prompt...")
    res = ai_agent.generate_fix(
        latex_code=sample_latex,
        errors=mock_errors,
        warnings=mock_warnings,
        user_prompt="Fix all Underfull and Overfull box warnings, and explain line by line."
    )

    print("  Model Used:", res.get("model_used"))
    print("  Changes Count:", len(res.get("changes_summary", [])))
    for ch in res.get("changes_summary", []):
        print("    ->", ch)
    print("\n  Explanation Preview:")
    print(res.get("explanation", "")[:300] + "...")

    assert "fixed_code" in res, "AI Agent must return fixed_code!"
    assert "microtype" in res["fixed_code"], "AI Agent should have recommended/injected microtype!"
    assert "raggedbottom" in res["fixed_code"], "AI Agent should have recommended/injected raggedbottom!"

    print("\n========================================")
    print("🎉 AI LATEX COPILOT TESTS PASSED!")
    print("========================================")

if __name__ == "__main__":
    test_ai_agent_warnings()
