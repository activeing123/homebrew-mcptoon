#!/usr/bin/env python3
"""bump_formula.py — 把 Homebrew formula 的 url+sha256 顶到指定版本。

**这份逻辑是唯一真源**，两个地方共用，刻意不做两份：
  ① 本仓 `.github/workflows/auto-bump.yml`（每天自动跑，把人从记忆里摘掉）
  ② 上游 `marketing/mcptoon/scripts/release_sync.py --apply`（手动补跑 / Action 挂了时用）

为什么值得单独成文件：formula 只钉 `url`+`sha256` 两个字段，**sha 算错 = 用户
brew install 直接失败**，所以「算 sha → 写 → 读回断言 → 提交」这条链必须只有一处实现，
否则两份迟早漂移（和 tap 会落后 4 版是同一类病：同一件事有两个真相）。

纯标准库，无依赖 —— Linux CI 与 Windows 本机都能跑。

用法：
    python bump_formula.py --check                  # 只报当前版本与 PyPI 最新
    python bump_formula.py --target 0.8.5           # 改文件（不提交）
    python bump_formula.py --target auto --commit --push   # 改+提交+推
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

UA = {"User-Agent": "mcptoon-tap-bump/1.0"}
FORMULA_RELP = "Formula/mcptoon.rb"
TARBALL = "https://github.com/activeing123/mcptoon/archive/refs/tags/v{v}.tar.gz"
MIN_TARBALL_BYTES = 100_000   # 低于此值判定下载残缺，宁可失败也不写错 hash

ANCHOR = re.compile(r'url\s+"[^"]+"\s*\n\s*sha256\s+"[0-9a-f]{64}"')
CUR_VER = re.compile(r"tags/v(\d+\.\d+\.\d+)\.tar\.gz")


def fetch_text(url: str, timeout: int = 300) -> bytes:
    op = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with op.open(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def pypi_latest() -> str:
    d = json.loads(fetch_text("https://pypi.org/pypi/mcptoon/json", timeout=60).decode("utf-8"))
    return d["info"]["version"]


def tarball_sha256(version: str) -> tuple[str, int]:
    data = fetch_text(TARBALL.format(v=version))
    size = len(data)
    if size < MIN_TARBALL_BYTES:
        raise SystemExit(f"✗ tarball 只有 {size} 字节（<{MIN_TARBALL_BYTES}），疑似残缺 —— 拒绝写 hash")
    tmp = Path(tempfile.gettempdir()) / f"mcptoon-v{version}.tar.gz"
    tmp.write_bytes(data)
    h = hashlib.sha256()
    with tmp.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest(), size


def current_version(formula: Path) -> str | None:
    m = CUR_VER.search(formula.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def rewrite(formula: Path, version: str) -> tuple[bool, str]:
    text = formula.read_text(encoding="utf-8")
    if not ANCHOR.search(text):
        return False, "ANCHOR-MISSING：formula 里找不到 url/sha256 对，拒绝盲改"
    cur = current_version(formula)
    if cur == version:
        return False, f"已是 {version}，无需改"
    sha, size = tarball_sha256(version)
    new = ANCHOR.sub(
        f'url "{TARBALL.format(v=version)}"\n  sha256 "{sha}"', text, count=1)
    formula.write_text(new, encoding="utf-8")
    back = formula.read_text(encoding="utf-8")
    if f"v{version}.tar.gz" not in back or sha not in back:
        return False, "✗ 写回校验失败，已中止"
    return True, f"{cur or '?'} -> {version}（{size:,}B / sha256 {sha}）"


def git(*args, cwd: Path, env=None, check=True):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True,
                          text=True, encoding="utf-8", errors="replace", env=env, check=check)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--formula", default=FORMULA_RELP)
    ap.add_argument("--target", default="auto", help="版本号，或 auto=取 PyPI 最新")
    ap.add_argument("--check", action="store_true", help="只报告，不改")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()

    formula = Path(a.formula).resolve()
    if not formula.exists():
        print(f"✗ 找不到 {formula}")
        return 1

    target = pypi_latest() if a.target == "auto" else a.target
    cur = current_version(formula)
    print(f"当前 = {cur or '?'} | 目标 = {target}")

    if a.check:
        print("CHANGED" if cur != target else "IN-SYNC")
        return 0

    ok, msg = rewrite(formula, target)
    print(msg)
    if not ok:
        return 1
    if not a.commit:
        return 0

    git("add", str(formula), cwd=formula.parent.parent)
    git("commit", "-m", f"mcptoon -> {target} (auto-bump)", cwd=formula.parent.parent)
    if a.push:
        git("push", "origin", "HEAD", cwd=formula.parent.parent)
        print(f"✅ 已推 origin/{git('rev-parse','--abbrev-ref','HEAD',cwd=formula.parent.parent).stdout.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())