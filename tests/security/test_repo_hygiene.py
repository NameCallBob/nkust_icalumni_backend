"""公開 repo 的衛生檢查：不該被提交的東西，不能被提交。

這個專案是公開 repo。一旦密鑰、資料庫傾印或 `.env` 被推上去，即使事後
`git rm` 也救不回來——內容永遠留在 git 歷史裡，而且會被各種自動掃描器
在幾分鐘內收走。這組測試在 commit 之前就把它擋下來。

檢查對象是「git 追蹤中的檔案」，不是工作目錄，所以本機留著 `.env`
（正常且必要）不會讓測試失敗，只有真的被 `git add` 進去才會。
"""
import pathlib
import re
import subprocess

import pytest

pytestmark = pytest.mark.security

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(scope="module")
def tracked_files():
    result = _git("ls-files")
    if result.returncode != 0:
        pytest.skip("不是 git repository，略過 repo 衛生檢查")
    return [line for line in result.stdout.splitlines() if line]


# ══════════════════════════════════════════════════════════════════════
# 不該被追蹤的檔案
# ══════════════════════════════════════════════════════════════════════
FORBIDDEN_EXACT = {
    ".env",
    ".env.local",
    ".env.production",
    "db.sqlite3",
}

FORBIDDEN_PATTERNS = (
    # 密鑰／憑證
    re.compile(r"\.pem$"),
    re.compile(r"\.key$"),
    re.compile(r"(^|/)id_rsa"),
    re.compile(r"\.p12$"),
    re.compile(r"\.pfx$"),
    # 資料庫傾印（本專案根目錄底下就有一份 17MB 的 .sql，絕不能進 repo）
    re.compile(r"\.sql$"),
    re.compile(r"\.sqlite3?$"),
    # 憑證檔
    re.compile(r"credentials\.json$"),
    re.compile(r"service[-_]account.*\.json$"),
)


def test_no_secret_files_are_tracked(tracked_files):
    offenders = [
        f
        for f in tracked_files
        if f in FORBIDDEN_EXACT or any(p.search(f) for p in FORBIDDEN_PATTERNS)
    ]
    assert not offenders, (
        "以下檔案被 git 追蹤，但不該進入公開 repo：\n"
        + "\n".join(f"  {f}" for f in offenders)
        + "\n\n處理方式：`git rm --cached <檔案>`、加進 .gitignore，"
        "並把已外洩的密鑰全部輪換（歷史裡的內容清不掉）。"
    )


def test_gitignore_covers_the_essentials():
    """`.gitignore` 必須涵蓋最容易誤提交的項目。"""
    gitignore = REPO_ROOT / ".gitignore"
    assert gitignore.exists(), "公開 repo 必須有 .gitignore"

    content = gitignore.read_text(encoding="utf-8")
    required = [".env", "__pycache__", "venv", "*.sql", "log"]
    missing = [entry for entry in required if entry not in content]
    assert not missing, f".gitignore 缺少：{missing}"


def test_env_example_exists_and_contains_no_real_values():
    """`.env.example` 必須存在（讓新進者知道要設哪些變數），且不得含真值。"""
    example = REPO_ROOT / ".env.example"
    assert example.exists(), "缺少 .env.example，新進者無從得知需要哪些環境變數"

    suspicious = []
    for line_number, line in enumerate(
        example.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip().strip("\"'")
        # 空值、佔位字串、明顯的範例值都可以；真的像密鑰的長字串不行。
        if len(value) >= 20 and not value.startswith(("change-me", "your-", "example")):
            suspicious.append(f"  第 {line_number} 行：{key.strip()}")

    assert not suspicious, (
        ".env.example 裡疑似含有真實密鑰：\n" + "\n".join(suspicious)
    )


# ══════════════════════════════════════════════════════════════════════
# 原始碼中的硬編碼密鑰
# ══════════════════════════════════════════════════════════════════════
SECRET_PATTERNS = {
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "私鑰檔內容": re.compile(r"-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----"),
    "Slack token": re.compile(r"xox[abprs]-[0-9A-Za-z-]{10,}"),
    "Google API key": re.compile(r"AIza[0-9A-Za-z_-]{35}"),
    "Resend API key": re.compile(r"re_[0-9A-Za-z]{20,}"),
    "JWT 字面值": re.compile(r"eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\."),
}

SCANNED_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yml", ".yaml", ".sh", ".conf"}

SCAN_EXCLUDED_DIRS = {
    "venv-alumni", "node_modules", "static", "static_files", "migrations",
    "log", "__pycache__", ".git",
}


def test_no_hardcoded_secrets_in_tracked_source(tracked_files):
    """掃描所有被追蹤的原始碼，找出硬編碼的密鑰。

    這是最後一道防線。前面的檔名檢查擋得住整個 `.env` 被提交，但擋不住有人
    為了「先讓它動起來」把 API key 直接貼進 `settings.py` 或某支 script。
    """
    findings = []
    for relative in tracked_files:
        path = REPO_ROOT / relative
        if path.suffix not in SCANNED_SUFFIXES:
            continue
        if set(pathlib.PurePath(relative).parts) & SCAN_EXCLUDED_DIRS:
            continue
        # 這支測試自己就寫滿了密鑰的正則樣式，掃自己一定會中。
        if pathlib.PurePath(relative).name == pathlib.PurePath(__file__).name:
            continue
        if not path.exists():
            continue

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        for label, pattern in SECRET_PATTERNS.items():
            match = pattern.search(content)
            if match:
                line_number = content[: match.start()].count("\n") + 1
                findings.append(f"  {relative}:{line_number} — {label}")

    assert not findings, (
        "在被追蹤的原始碼中發現疑似硬編碼密鑰：\n"
        + "\n".join(findings)
        + "\n\n請改用環境變數，並將該密鑰立即輪換。"
    )
