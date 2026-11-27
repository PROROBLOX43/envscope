"""Small, dependency-free checker for undocumented environment variables."""

import argparse
import json
import re
import sys
from pathlib import Path

PATTERNS = {
    ".py": [re.compile(r"\bos\.(?:environ\[(?:\s*)|getenv\(\s*)['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]")],
    ".js": [re.compile(r"\bprocess\.env\.([A-Za-z_][A-Za-z_0-9]*)"), re.compile(r"\bprocess\.env\[['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]\]")],
    ".ts": [re.compile(r"\bprocess\.env\.([A-Za-z_][A-Za-z_0-9]*)"), re.compile(r"\bprocess\.env\[['\"]([A-Za-z_][A-Za-z_0-9]*)['\"]\]")],
    ".jsx": [re.compile(r"\bprocess\.env\.([A-Za-z_][A-Za-z_0-9]*)")],
    ".tsx": [re.compile(r"\bprocess\.env\.([A-Za-z_][A-Za-z_0-9]*)")],
}
SKIP = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__", "vendor"}
ASSIGNMENT = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z_0-9]*)\s*=")


def scan(root):
    found = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in PATTERNS or any(part in SKIP or part.startswith(".env") for part in path.relative_to(root).parts):
            continue
        try:
            if path.stat().st_size > 1_000_000:
                continue
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            continue
        for number, line in enumerate(lines, 1):
            for pattern in PATTERNS[path.suffix]:
                for match in pattern.finditer(line):
                    found.setdefault(match.group(1), set()).add(f"{path.relative_to(root).as_posix()}:{number}")
    return {key: sorted(value) for key, value in sorted(found.items())}


def documented(path):
    names = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = ASSIGNMENT.match(line)
        if match:
            names.add(match.group(1))
    return names


def main(argv=None):
    parser = argparse.ArgumentParser(description="Check that environment variables in source code appear in an example env file.")
    parser.add_argument("path", nargs="?", type=Path, default=Path("."), help="project directory (default: current directory)")
    parser.add_argument("--example", default=".env.example", help="example file relative to project directory")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args(argv)
    root = args.path.resolve()
    example = root / args.example
    if not root.is_dir() or not example.is_file():
        parser.error(f"project directory and example file must exist: {example}")
    try:
        used = scan(root)
        listed = documented(example)
    except (OSError, UnicodeError) as exc:
        parser.error(str(exc))
    missing = {name: locations for name, locations in used.items() if name not in listed}
    unused = sorted(listed - used.keys())
    if args.json:
        print(json.dumps({"missing": missing, "unused": unused, "used_count": len(used)}, indent=2))
    else:
        for name, locations in missing.items():
            print(f"MISSING {name}  {', '.join(locations)}")
        for name in unused:
            print(f"UNUSED  {name}")
        print(f"Checked {len(used)} variable(s): {len(missing)} missing, {len(unused)} unused")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
