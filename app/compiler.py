import os
import re
import time
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from app.config import TECTONIC_EXE, WORKSPACES_DIR

class LaTeXHealer:
    """
    Intelligent LaTeX sanitizer and error healer that automatically
    detects and repairs common LaTeX syntax bugs, unbalanced braces,
    unescaped characters, missing packages, broken environments,
    and automatically solves \hbox and \vbox badness issues.
    """

    KNOWN_PACKAGES = {
        r"\\(begin|end)\{align\*?\}": "amsmath",
        r"\\(begin|end)\{matrix|pmatrix|bmatrix|vmatrix|cases\}": "amsmath",
        r"\\(eqref|text|boldsymbol|mathbb|mathcal)": "amsmath,amssymb",
        r"\\includegraphics": "graphicx",
        r"\\(toprule|midrule|bottomrule)": "booktabs",
        r"\\(href|url|hypersetup)": "hyperref",
        r"\\(definecolor|textcolor|colorbox)": "xcolor",
        r"\\(setlist)": "enumitem",
        r"\\(titleformat|titlespacing)": "titlesec",
        r"\\(fancyhf|rhead|lhead|cfoot|pagestyle\{fancy\})": "fancyhdr",
    }

    def heal(self, content: str, error_lines: Optional[List[int]] = None) -> Tuple[str, List[Dict[str, Any]]]:
        fixes = []
        lines = content.splitlines()
        modified_lines = list(lines)

        # 1. Auto-Solve \vbox and \hbox Badness & Margin Overflow in Preamble
        # Injects \raggedbottom, \usepackage{microtype}, \emergencystretch, and badness tolerances
        full_text = "\n".join(modified_lines)
        if r"\documentclass" in full_text:
            preamble_match = re.search(r"(\\documentclass.*?\\begin\{document\})", full_text, re.DOTALL)
            if preamble_match:
                preamble_str = preamble_match.group(1)
                injections = []

                if "\\raggedbottom" not in preamble_str:
                    injections.append("\\raggedbottom % Solves Underfull \\vbox (badness 10000) on page breaks")
                    fixes.append({
                        "line": 1,
                        "type": "box_badness_auto_fix",
                        "message": "Auto-injected \\raggedbottom to solve Underfull \\vbox (badness 10000) vertical page stretch",
                        "original": "",
                        "fixed": "\\raggedbottom"
                    })

                if "microtype" not in preamble_str:
                    injections.append("\\usepackage{microtype} % Solves Overfull and Underfull \\hbox margin issues")
                    fixes.append({
                        "line": 1,
                        "type": "box_badness_auto_fix",
                        "message": "Auto-injected \\usepackage{microtype} for font expansion and kerning",
                        "original": "",
                        "fixed": "\\usepackage{microtype}"
                    })

                if "\\emergencystretch" not in preamble_str:
                    injections.append("\\emergencystretch=3em % Gives TeX flexible tolerance for long words and citations")
                    injections.append("\\hfuzz=2pt \\vfuzz=2pt \\hbadness=10000 \\vbadness=10000 % Suppresses minor box threshold alarms")
                    fixes.append({
                        "line": 1,
                        "type": "box_badness_auto_fix",
                        "message": "Auto-configured \\emergencystretch and box tolerance thresholds",
                        "original": "",
                        "fixed": "\\emergencystretch=3em"
                    })

                if injections:
                    injection_block = "\n" + "\n".join(injections) + "\n"
                    # Place right before \begin{document}
                    new_preamble = preamble_str.replace(r"\begin{document}", injection_block + r"\begin{document}")
                    full_text = full_text.replace(preamble_str, new_preamble, 1)
                    modified_lines = full_text.splitlines()

        # 2. Fix unescaped % inside \text{...}, \textbf{...}, \textit{...} or before closing braces
        for idx, line in enumerate(modified_lines):
            line_num = idx + 1
            if re.search(r"\\(text|textbf|textit|texttt|emph|mathrm|mathbf)\{[^}\n]*(?<!\\)%", line):
                fixed_line = re.sub(r"(\\(?:text|textbf|textit|texttt|emph|mathrm|mathbf)\{[^}\n]*)(?<!\\)%([^}\n]*\})", r"\1\\%\2", line)
                if fixed_line != line:
                    modified_lines[idx] = fixed_line
                    fixes.append({
                        "line": line_num,
                        "type": "unescaped_percent",
                        "message": "Escaped unescaped '%' symbol as '\\%' inside formatting command",
                        "original": line,
                        "fixed": fixed_line
                    })
                    line = fixed_line

            if re.search(r"(?<!\\)%\s*[\)\}]", line):
                fixed_line = re.sub(r"(?<!\\)%\s*([\)\}])", r"\\%\1", line)
                if fixed_line != line:
                    modified_lines[idx] = fixed_line
                    fixes.append({
                        "line": line_num,
                        "type": "unescaped_percent",
                        "message": "Escaped literal '%' character as '\\%'",
                        "original": line,
                        "fixed": fixed_line
                    })
                    line = fixed_line

        # 3. Clean blank lines inside math environments (equations, aligns, $$)
        in_math_env = False
        for idx, line in enumerate(modified_lines):
            line_num = idx + 1
            stripped = line.strip()

            if re.search(r"\\begin\{(equation|align|gather|multline|flalign|alignat)\*?\}", stripped) or stripped == "$$":
                in_math_env = True
                continue
            if re.search(r"\\end\{(equation|align|gather|multline|flalign|alignat)\*?\}", stripped) or (in_math_env and stripped == "$$"):
                in_math_env = False
                continue

            if in_math_env and not stripped:
                modified_lines[idx] = "%"
                fixes.append({
                    "line": line_num,
                    "type": "blank_line_in_math",
                    "message": "Removed illegal blank line inside math environment",
                    "original": "",
                    "fixed": "%"
                })

        # 4. Fix unclosed \text{...} / \textbf{...} / inline formatting commands
        inline_cmds = ["text", "textbf", "textit", "texttt", "emph", "mathrm", "mathbf", "mathit", "underline", "mbox"]
        for idx, line in enumerate(modified_lines):
            line_num = idx + 1
            for cmd in inline_cmds:
                cmd_tag = f"\\{cmd}{{"
                if cmd_tag in line:
                    parts = line.split(cmd_tag)
                    for p_idx in range(1, len(parts)):
                        segment = parts[p_idx]
                        opens = segment.count("{") - segment.count(r"\{")
                        closes = segment.count("}") - segment.count(r"\}")
                        if opens >= closes:
                            modified_lines[idx] = line + "}"
                            fixes.append({
                                "line": line_num,
                                "type": "unclosed_command_brace",
                                "message": f"Closed missing brace for \\{cmd}{{...}}",
                                "original": line,
                                "fixed": modified_lines[idx]
                            })
                            line = modified_lines[idx]

        # 5. Fix unescaped & in plain text and headings
        in_table_or_align = False
        for idx, line in enumerate(modified_lines):
            line_num = idx + 1
            stripped = line.strip()

            if re.search(r"\\begin\{(tabular|array|align|bmatrix|pmatrix|matrix|cases|aligned)\*?\}", stripped):
                in_table_or_align = True
                continue
            if re.search(r"\\end\{(tabular|array|align|bmatrix|pmatrix|matrix|cases|aligned)\*?\}", stripped):
                in_table_or_align = False
                continue

            if not in_table_or_align and not stripped.startswith("%"):
                fixed_line = re.sub(r"(?<!\\)&", r"\&", line)
                if fixed_line != line:
                    modified_lines[idx] = fixed_line
                    fixes.append({
                        "line": line_num,
                        "type": "unescaped_ampersand",
                        "message": "Escaped unescaped '&' symbol as '\\&'",
                        "original": line,
                        "fixed": fixed_line
                    })

        # 6. Check for unclosed environments
        env_stack = []
        env_pattern = re.compile(r"\\(begin|end)\{([a-zA-Z*0-9]+)\}")
        for idx, line in enumerate(modified_lines):
            if line.strip().startswith("%"):
                continue
            for match in env_pattern.finditer(line):
                action, env_name = match.groups()
                if action == "begin":
                    if env_name != "document":
                        env_stack.append((env_name, idx + 1))
                elif action == "end":
                    if env_name != "document":
                        if env_stack and env_stack[-1][0] == env_name:
                            env_stack.pop()
                        elif env_name in [e[0] for e in env_stack]:
                            while env_stack and env_stack[-1][0] != env_name:
                                unclosed = env_stack.pop()
                            if env_stack:
                                env_stack.pop()

        if env_stack:
            closing_tags = []
            for env_name, line_num in reversed(env_stack):
                closing_tags.append(f"\\end{{{env_name}}}")
                fixes.append({
                    "line": line_num,
                    "type": "unclosed_environment",
                    "message": f"Auto-closed missing \\end{{{env_name}}}",
                    "original": f"\\begin{{{env_name}}}",
                    "fixed": f"\\end{{{env_name}}}"
                })
            
            insert_str = "\n" + "\n".join(closing_tags) + "\n"
            full_text = "\n".join(modified_lines)
            if r"\end{document}" in full_text:
                full_text = full_text.replace(r"\end{document}", insert_str + r"\end{document}")
            else:
                full_text += insert_str
            modified_lines = full_text.splitlines()

        # 7. Check for unbalanced curly braces
        full_text = "\n".join(modified_lines)
        open_braces = full_text.count("{") - full_text.count(r"\{")
        close_braces = full_text.count("}") - full_text.count(r"\}")

        if open_braces > close_braces:
            diff = open_braces - close_braces
            if r"\end{document}" in full_text:
                full_text = full_text.replace(r"\end{document}", ("}" * diff) + "\n\\end{document}")
            else:
                full_text += ("}" * diff)
            fixes.append({
                "line": len(modified_lines),
                "type": "unbalanced_braces",
                "message": f"Auto-closed {diff} missing '}}' brace(s) in document",
                "original": "",
                "fixed": "}" * diff
            })
            modified_lines = full_text.splitlines()

        # 8. Check for missing document preamble
        full_text = "\n".join(modified_lines)
        if r"\documentclass" not in full_text:
            preamble = "\\documentclass[12pt]{article}\n\\usepackage{amsmath,amssymb,graphicx,hyperref,microtype}\n\\raggedbottom\n\\emergencystretch=3em\n\\begin{document}\n"
            full_text = preamble + full_text
            fixes.append({
                "line": 1,
                "type": "missing_preamble",
                "message": "Auto-added missing \\documentclass and \\begin{document}",
                "original": "",
                "fixed": preamble
            })
            modified_lines = full_text.splitlines()

        if r"\end{document}" not in full_text:
            full_text += "\n\\end{document}\n"
            fixes.append({
                "line": len(modified_lines),
                "type": "missing_end_document",
                "message": "Auto-added missing \\end{document}",
                "original": "",
                "fixed": "\\end{document}"
            })
            modified_lines = full_text.splitlines()

        # 9. Auto-inject required packages in preamble if missing
        preamble_match = re.search(r"(\\documentclass.*?\\begin\{document\})", full_text, re.DOTALL)
        if preamble_match:
            preamble_str = preamble_match.group(1)
            packages_to_add = []

            for pat, pkg_str in self.KNOWN_PACKAGES.items():
                if re.search(pat, full_text):
                    pkgs = [p.strip() for p in pkg_str.split(",")]
                    for p in pkgs:
                        if f"{{{p}}}" not in preamble_str and p not in packages_to_add:
                            packages_to_add.append(p)

            if packages_to_add:
                pkg_injection = "\n" + "\n".join([f"\\usepackage{{{p}}}" for p in packages_to_add]) + "\n"
                doc_class_end = preamble_str.find("}")
                if doc_class_end != -1:
                    new_preamble = preamble_str[:doc_class_end+1] + pkg_injection + preamble_str[doc_class_end+1:]
                    full_text = full_text.replace(preamble_str, new_preamble, 1)
                    fixes.append({
                        "line": 1,
                        "type": "missing_packages",
                        "message": f"Auto-imported required packages: {', '.join(packages_to_add)}",
                        "original": "",
                        "fixed": pkg_injection.strip()
                    })

        return full_text, fixes


class LaTeXCompiler:
    def __init__(self, tectonic_path: Optional[Path] = None):
        self.tectonic_path = tectonic_path or TECTONIC_EXE
        self.healer = LaTeXHealer()

    def compile(self, user_id: int, project_id: str, main_file: str = "main.tex") -> Dict[str, Any]:
        """
        Compiles the LaTeX document in the project's workspace directory to PDF.
        Features a multi-stage compilation pipeline with automatic box badness and syntax healing.
        """
        project_dir = WORKSPACES_DIR / str(user_id) / str(project_id)
        if not project_dir.exists():
            return {
                "success": False,
                "duration_ms": 0,
                "errors": [{"line": 1, "file": main_file, "message": "Project workspace directory does not exist"}],
                "warnings": [],
                "fixes_applied": [],
                "healed": False,
                "raw_log": "Project workspace not found."
            }

        main_path = project_dir / main_file
        if not main_path.exists():
            return {
                "success": False,
                "duration_ms": 0,
                "errors": [{"line": 1, "file": main_file, "message": f"Main file '{main_file}' not found"}],
                "warnings": [],
                "fixes_applied": [],
                "healed": False,
                "raw_log": f"File '{main_file}' does not exist in workspace."
            }

        start_time = time.time()
        output_pdf_name = main_path.stem + ".pdf"
        output_pdf_path = project_dir / output_pdf_name

        try:
            with open(main_path, "r", encoding="utf-8", errors="replace") as f:
                original_content = f.read()
        except Exception:
            original_content = ""

        # STAGE 1: Compile original file
        res = self._run_tectonic(project_dir, main_path.name, output_pdf_name)
        duration_ms = round((time.time() - start_time) * 1000, 2)

        errors, warnings = self._parse_tex_log(res["combined_log"], main_file)
        pdf_exists = output_pdf_path.exists() and output_pdf_path.stat().st_size > 0

        # If clean success with no fatal errors
        if (res["returncode"] == 0 or pdf_exists) and len(errors) == 0:
            return {
                "success": True,
                "duration_ms": duration_ms,
                "pdf_filename": output_pdf_name,
                "pdf_path": str(output_pdf_path),
                "healed": False,
                "fixes_applied": [],
                "errors": [],
                "warnings": warnings,
                "raw_log": res["combined_log"]
            }

        # STAGE 2: Auto-Healing & Tolerance Retry (automatically heals box issues & syntax errors)
        error_lines = [e["line"] for e in errors if "line" in e]
        healed_content, fixes_applied = self.healer.heal(original_content, error_lines)

        if fixes_applied:
            healed_filename = "_build_" + main_file
            healed_path = project_dir / healed_filename
            healed_pdf_name = Path(healed_filename).stem + ".pdf"
            healed_pdf_path = project_dir / healed_pdf_name

            with open(healed_path, "w", encoding="utf-8") as f:
                f.write(healed_content)

            healed_res = self._run_tectonic(project_dir, healed_filename, healed_pdf_name)
            healed_errors, healed_warnings = self._parse_tex_log(healed_res["combined_log"], main_file)

            if (healed_res["returncode"] == 0 or healed_pdf_path.exists()) and healed_pdf_path.stat().st_size > 0:
                shutil.copyfile(healed_pdf_path, output_pdf_path)
                healed_duration = round((time.time() - start_time) * 1000, 2)

                return {
                    "success": True,
                    "duration_ms": healed_duration,
                    "pdf_filename": output_pdf_name,
                    "pdf_path": str(output_pdf_path),
                    "healed": True,
                    "healed_content": healed_content,
                    "fixes_applied": fixes_applied,
                    "errors": healed_errors,
                    "warnings": healed_warnings,
                    "raw_log": res["combined_log"] + "\n\n=== AUTO-HEALED COMPILATION SUCCESSFUL ===\n" + healed_res["combined_log"]
                }

        # STAGE 3: Fallback / Reporting
        if len(errors) == 0 and not pdf_exists:
            errors.append({
                "line": 1,
                "file": main_file,
                "message": "LaTeX syntax error detected. Check logs for details.",
                "context": ""
            })

        return {
            "success": pdf_exists,
            "duration_ms": duration_ms,
            "pdf_filename": output_pdf_name if pdf_exists else None,
            "pdf_path": str(output_pdf_path) if pdf_exists else None,
            "healed": False,
            "fixes_applied": fixes_applied,
            "errors": errors,
            "warnings": warnings,
            "raw_log": res["combined_log"]
        }

    def _run_tectonic(self, project_dir: Path, target_file: str, output_pdf: str) -> Dict[str, Any]:
        if self.tectonic_path.exists():
            cmd = [
                str(self.tectonic_path),
                target_file,
                "--outdir", str(project_dir),
                "--synctex",
                "--keep-logs"
            ]
        elif shutil.which("pdflatex"):
            cmd = ["pdflatex", "-interaction=nonstopmode", "-synctex=1", target_file]
        else:
            return {"returncode": 1, "combined_log": "No LaTeX compiler found."}

        try:
            proc = subprocess.run(
                cmd,
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=60,
                encoding="utf-8",
                errors="replace"
            )
            raw_stdout = proc.stdout or ""
            raw_stderr = proc.stderr or ""
            raw_output = raw_stdout + "\n" + raw_stderr

            log_file = project_dir / (Path(target_file).stem + ".log")
            log_content = ""
            if log_file.exists():
                try:
                    with open(log_file, "r", encoding="utf-8", errors="replace") as lf:
                        log_content = lf.read()
                except Exception:
                    pass

            return {
                "returncode": proc.returncode,
                "combined_log": (raw_output + "\n" + log_content).strip()
            }
        except Exception as e:
            return {"returncode": 1, "combined_log": f"Execution error: {str(e)}"}

    def _parse_tex_log(self, log: str, default_file: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        errors = []
        warnings = []
        seen_errors = set()
        seen_warnings = set()

        lines = log.splitlines()
        current_file = default_file

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # 1. Parse Box Badness & Layout Notices as Warnings (NOT fatal errors)
            # e.g., Underfull \vbox, Overfull \hbox, Underfull \hbox, badness 10000
            is_box_warning = bool(re.search(r"(Underfull|Overfull)\s*\\(hbox|vbox)", line))
            
            if is_box_warning:
                warn_line_num = 1
                m_direct = re.search(r"(\w+\.tex):(\d+):\s*(.*)", line)
                if m_direct:
                    warn_line_num = int(m_direct.group(2))
                    msg = m_direct.group(3).strip()
                else:
                    msg = line
                    m_at = re.search(r"lines?\s+(\d+)", line, re.IGNORECASE)
                    if m_at:
                        warn_line_num = int(m_at.group(1))

                warn_key = (warn_line_num, msg)
                if warn_key not in seen_warnings:
                    seen_warnings.add(warn_key)
                    warnings.append({
                        "line": warn_line_num,
                        "file": current_file,
                        "message": msg
                    })
                i += 1
                continue

            # 2. Parse standard TeX errors: ! <Error Message>
            if line.startswith("!"):
                msg = line[1:].strip()
                err_line_num = 1
                context_str = ""

                for j in range(i + 1, min(i + 8, len(lines))):
                    m = re.search(r"^l\.(\d+)\s*(.*)$", lines[j])
                    if m:
                        err_line_num = int(m.group(1))
                        context_str = m.group(2).strip()
                        break

                if not msg.startswith("note:") and not msg.startswith("warning:"):
                    err_key = (err_line_num, msg)
                    if err_key not in seen_errors:
                        seen_errors.add(err_key)
                        errors.append({
                            "line": err_line_num,
                            "file": current_file,
                            "message": msg,
                            "context": context_str
                        })

            # 3. Parse Tectonic error format: error: <message> or file:line: message
            elif line.startswith("error:") or re.search(r"(\w+\.tex):(\d+):\s*(.*)", line):
                m_direct = re.search(r"(\w+\.tex):(\d+):\s*(.*)", line)
                if m_direct:
                    f_name, l_num, msg = m_direct.group(1), int(m_direct.group(2)), m_direct.group(3).strip()
                    # If this message is a warning/box notice, treat as warning
                    if re.search(r"(Underfull|Overfull)\s*\\(hbox|vbox)", msg):
                        warn_key = (l_num, msg)
                        if warn_key not in seen_warnings:
                            seen_warnings.add(warn_key)
                            warnings.append({
                                "line": l_num,
                                "file": f_name,
                                "message": msg
                            })
                    else:
                        err_key = (l_num, msg)
                        if err_key not in seen_errors:
                            seen_errors.add(err_key)
                            errors.append({
                                "line": l_num,
                                "file": f_name,
                                "message": msg,
                                "context": ""
                            })
                else:
                    msg = line[6:].strip()
                    err_line_num = 1
                    m_num = re.search(r"line\s+(\d+)", msg, re.IGNORECASE)
                    if m_num:
                        err_line_num = int(m_num.group(1))
                    err_key = (err_line_num, msg)
                    if err_key not in seen_errors and not msg.startswith("note:"):
                        seen_errors.add(err_key)
                        errors.append({
                            "line": err_line_num,
                            "file": current_file,
                            "message": msg,
                            "context": ""
                        })

            # 4. Parse LaTeX standard warnings
            elif "LaTeX Warning:" in line or "Package " in line and "Warning:" in line:
                m_line = re.search(r"line\s+(\d+)", line, re.IGNORECASE)
                warn_line = int(m_line.group(1)) if m_line else 1
                warn_key = (warn_line, line.strip())
                if warn_key not in seen_warnings:
                    seen_warnings.add(warn_key)
                    warnings.append({
                        "line": warn_line,
                        "file": current_file,
                        "message": line.strip()
                    })

            i += 1

        return errors, warnings

compiler_service = LaTeXCompiler()
