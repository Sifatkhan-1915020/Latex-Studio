import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from app.database import init_db, get_db_cursor
from app.auth import hash_password, verify_password, create_access_token, decode_access_token
from app.compiler import compiler_service
from app.templates_data import TEMPLATES
from app.config import WORKSPACES_DIR

def run_tests():
    print("========================================")
    print("🧪 RUNNING OVERLEAF SYSTEM VERIFICATION")
    print("========================================")

    # 1. Test Database Init
    print("\n1. Testing Database Initialization...")
    init_db()
    print("  ✓ Database schema created successfully.")

    # 2. Test Auth & Password Hashing
    print("\n2. Testing Authentication & Password Hashing...")
    pwd = "secretpassword123"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed), "Password verification failed!"
    assert not verify_password("wrongpassword", hashed), "Invalid password check failed!"
    
    token = create_access_token({"sub": "testuser", "uid": 1})
    payload = decode_access_token(token)
    assert payload["sub"] == "testuser", "JWT token decoding failed!"
    print("  ✓ Auth, bcrypt hashing, and JWT tokens functioning correctly.")

    # 3. Test Templates & Workspace Creation
    print("\n3. Testing Template Seeding & Compilation...")
    test_user_id = 999
    
    for tpl_key, tpl in TEMPLATES.items():
        print(f"\n  Testing template: '{tpl['name']}' ({tpl_key})...")
        proj_id = f"test_{tpl_key}"
        proj_dir = WORKSPACES_DIR / str(test_user_id) / proj_id
        os.makedirs(proj_dir, exist_ok=True)

        # Write files
        for fname, fcontent in tpl["files"].items():
            fpath = proj_dir / fname
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(fcontent)

        # Compile
        res = compiler_service.compile(user_id=test_user_id, project_id=proj_id, main_file="main.tex")
        print(f"    Compile Success: {res['success']}, Duration: {res['duration_ms']}ms")
        if not res["success"]:
            print(f"    Errors: {res['errors']}")
            print(f"    Log: {res['raw_log'][:300]}")
        assert res["success"], f"Compilation failed for template {tpl_key}!"
        assert res["pdf_path"] and os.path.exists(res["pdf_path"]), f"PDF not found for template {tpl_key}!"
        pdf_size = os.path.getsize(res["pdf_path"])
        print(f"    ✓ Generated PDF '{Path(res['pdf_path']).name}' ({pdf_size} bytes)")

    # 4. Test Error Diagnostics Parser
    print("\n4. Testing Error Diagnostics & Line Number Parser...")
    err_proj_id = "test_error_proj"
    err_dir = WORKSPACES_DIR / str(test_user_id) / err_proj_id
    os.makedirs(err_dir, exist_ok=True)
    
    bad_latex = r"""\documentclass{article}
\begin{document}
Line 3 is good
\invalidCommandThatDoesNotExist{test}
Line 5 is also good
\end{document}
"""
    with open(err_dir / "main.tex", "w", encoding="utf-8") as f:
        f.write(bad_latex)

    err_res = compiler_service.compile(user_id=test_user_id, project_id=err_proj_id, main_file="main.tex")
    print(f"    Error detection status: Success={err_res['success']}")
    assert not err_res["success"], "Compiler should have failed on invalid command!"
    print(f"    Parsed errors count: {len(err_res['errors'])}")
    for err in err_res["errors"]:
        print(f"    -> Line {err['line']}: {err['message']} (Context: {err.get('context')})")
    assert len(err_res["errors"]) > 0, "Log parser should have extracted errors!"
    print("  ✓ Error diagnostics correctly identified line and error message.")

    print("\n========================================")
    print("🎉 ALL SYSTEM VERIFICATION TESTS PASSED!")
    print("========================================")

if __name__ == "__main__":
    run_tests()
