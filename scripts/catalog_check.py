import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess


REFERENCE = "catalog/en.txt"
LOCALES = ("catalog/es.txt", "catalog/fr.txt")
KEY = re.compile(r"[a-z][a-z0-9_]*")
FIELD = re.compile(r"\{([a-z][a-z0-9_]*)\}")


def read_catalog(path, report):
    records = {}
    file = Path(path)
    if not file.is_file():
        report(path, None, "Missing catalog", "Restore this catalog.")
        return records
    for number, text in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
        key, separator, value = text.partition("=")
        if not separator or not KEY.fullmatch(key) or not value.strip():
            report(path, number, "Invalid entry", "Use key=value.")
            continue
        if key in records:
            report(path, number, "Duplicate key", f"Keep one {key} entry.")
            continue
        fields = Counter(FIELD.findall(value))
        remainder = FIELD.sub("", value)
        if "{" in remainder or "}" in remainder:
            report(path, number, "Invalid field", "Use named fields such as {order}.")
        records[key] = (number, fields)
    return records


def describe(fields):
    return ", ".join(f"{name} x{count}" for name, count in sorted(fields.items())) or "none"


def validate(path, reference, report):
    translation = read_catalog(path, report)
    for key, (line, fields) in translation.items():
        if key not in reference:
            report(path, line, "Unknown key", f"{key} is absent from English.")
            continue
        expected = reference[key][1]
        if fields != expected:
            message = f"{key}: expected {describe(expected)}; found {describe(fields)}."
            report(path, line, "Placeholder mismatch", message)
    for key in sorted(reference.keys() - translation.keys()):
        report(path, None, "Missing key", f"Add the {key} entry.")


def build_payload(base, head, details):
    changed = subprocess.check_output(
        ["git", "diff", "--name-only", "--no-renames", "-z", f"{base}...{head}"],
    ).decode().split("\0")
    scope = [path for path in LOCALES if REFERENCE in changed or path in changed]
    annotations = []
    findings = []

    def report(path, line, title, message):
        location = f"{path}:{line}" if line else path
        findings.append(f"- `{location}` — {title}: {message}")
        if line and len(annotations) < 50:
            annotations.append({
                "path": path,
                "start_line": line,
                "end_line": line,
                "annotation_level": "failure",
                "title": title,
                "message": message,
            })

    if scope:
        reference = read_catalog(REFERENCE, report)
        if reference:
            for path in scope:
                validate(path, reference, report)
        elif Path(REFERENCE).is_file():
            report(REFERENCE, None, "Empty reference", "Add the English records.")

    checked = ", ".join(scope) or "none"
    skipped = ", ".join(path for path in LOCALES if path not in scope) or "none"
    result = "failure" if findings else "success" if scope else "neutral"
    title = f"{len(findings)} finding(s) | {len(scope)} translation(s) checked"
    summary = "\n".join([
        f"**Checked:** {checked}",
        "",
        f"**Skipped:** {skipped}",
        "",
        f"**Line annotations posted:** {len(annotations)} (max 50)",
        "",
        *findings[:100],
    ])
    if len(findings) > 100:
        summary += f"\n\n{len(findings) - 100} further findings omitted."
    return {
        "name": "Catalog placeholders",
        "head_sha": head,
        "details_url": details,
        "status": "completed",
        "conclusion": result,
        "output": {"title": title, "summary": summary, "annotations": annotations},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("base")
    parser.add_argument("head")
    parser.add_argument("details")
    args = parser.parse_args()
    payload = build_payload(args.base, args.head, args.details)
    Path("check.json").write_text(json.dumps(payload), encoding="utf-8")
