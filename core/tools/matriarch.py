#!/usr/bin/env python3
"""Deterministic checks for Matriarch. Agents run this instead of judging by hand.

  matriarch.py gate <round.json> [--previous <earlier round.json>]... [--user F] [--project F]
      Compute the review gate (core/gate.md) for one round: the panel it must
      have (from the settings and the task's mode), INCOMPLETE, FAIL,
      PASS_WITH_WAIVERS, PASS_WITH_ACTIONS or PASS, and whether work may move on
      (clean rounds in a row on the same target version). Exit 0 only when it may.

  matriarch.py scan <file>...
      Look for secrets and personal data. Exit 1 on any hit.

  matriarch.py export --to external|memory [--approved-by NAME] [--user F] [--project F] <file>...
      May these files go to another provider (external) or into memory, under
      project.confidentiality? Runs scan first. Exit 0 only when allowed.

  matriarch.py config [--user FILE] [--project FILE]
      Validate settings layers against settings/schema.json and the invariants,
      print the effective settings and their SHA-256. --project takes a YAML file
      holding the hub's Settings block. Needs PyYAML.

  matriarch.py which [--user F] [--cwd DIR]
      Which entry of your per-project settings (`projects:`) applies here: by
      folder path first, then by the git remote of the repository you are in.
      Exit 1 when none or several match: ask the owner, never guess.

  config, gate and export also take --project-name NAME or --cwd DIR to apply
  that project's personal settings.

  matriarch.py doctor [--user F] [--project F] [--cwd DIR]
      Local checks before use: Python, PyYAML, git, gh, Claude Code version,
      settings, which project applies here, memory folders, repository state.
      Exit 1 when a check fails. Memory connector checks are in the doctor skill.

  matriarch.py sha256 <file>
      SHA-256 of a file, for round records and locks.

Output is JSON. Exit code 0 when the check passes, 1 when it fails, 2 on usage
or input errors.
"""
from __future__ import annotations

import copy
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent  # plugin root (or the matriarch/ folder in a zip)

SEVERITIES = {"Blocker", "Major", "Nit"}
RESOLUTIONS = {"fixed", "contested", "action", "waived", "declined", "open"}


class InputError(Exception):
    pass


# ---------------------------------------------------------------- gate

SHA256 = re.compile(r"^[0-9a-f]{64}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KIND = {"spec": "spec", "doc": "spec", "prompt": "prompt", "tests": "tests",
        "subtask": "code", "task": "code", "pr": "code"}
SENSITIVE_POINTS = {"subtask", "task", "pr"}


def check_record(record) -> None:
    if not isinstance(record, dict):
        raise InputError("the round record must be a JSON object")
    lenses = record.get("lenses")
    findings = record.get("findings") or []
    if record.get("point") not in set(KIND) | {"idea", "decision", "area_guide"}:
        raise InputError("round record needs 'point' (a review point such as spec, subtask, pr)")
    if record.get("mode", "standard") not in ("quick", "standard", "critical"):
        raise InputError("'mode' must be quick, standard or critical")
    if not SHA256.match(str(record.get("target_sha256", ""))):
        raise InputError("'target_sha256' must be a 64-character lowercase hex SHA-256 (matriarch.py sha256 <file>)")
    if not isinstance(lenses, list) or not lenses or not all(isinstance(l, dict) and l.get("name") for l in lenses):
        raise InputError("round record needs a non-empty 'lenses' list of objects with a 'name'")
    if not isinstance(findings, list) or not all(isinstance(f, dict) and f.get("id") for f in findings):
        raise InputError("'findings' must be a list of objects with an 'id'")
    for f in findings:
        res = f.get("resolution", "open")
        if f.get("severity") not in SEVERITIES:
            raise InputError(f"finding {f['id']}: severity must be one of {sorted(SEVERITIES)}")
        if res not in RESOLUTIONS:
            raise InputError(f"finding {f['id']}: resolution must be one of {sorted(RESOLUTIONS)}")
        if res == "waived" and not (f.get("owner") and f.get("reason") and f.get("decision")
                                    and DATE.match(str(f.get("review_by", "")))):
            raise InputError(f"finding {f['id']}: a waiver needs 'owner', 'reason', 'decision' (the Decisions row ID) "
                             "and 'review_by' (YYYY-MM-DD)")
        if res == "action" and not (f.get("owner") and f.get("where")):
            raise InputError(f"finding {f['id']}: an action needs 'owner' and 'where'")
        if res == "action" and f["severity"] == "Blocker":
            raise InputError(f"finding {f['id']}: a Blocker cannot be an action; fix, contest or waive it")
        if res == "declined" and f["severity"] != "Nit":
            raise InputError(f"finding {f['id']}: only a Nit can be declined; track a Major as an action")
    for l in lenses:
        if l.get("status") == "skipped" and not (l.get("reason") and l.get("owner")):
            raise InputError(f"lens {l['name']}: a skipped lens needs the owner's name and reason")


def expected_lenses(settings: dict, record: dict) -> list[str]:
    """The panel this round must have, from the effective settings and the task's mode."""
    point, mode = record["point"], record.get("mode", "standard")
    view = mode_views(settings)[mode]
    panel = list(view["panels"].get(point, []))
    overlay = settings["project"]["review"].get("modes", {}).get(mode, {})
    if point in SENSITIVE_POINTS and (record.get("sensitive") or overlay.get("always_sensitive")):
        panel += [l for l in view["panels"]["sensitive"] if l not in panel]
    return panel


def gate(record: dict, settings: dict | None = None) -> dict:
    check_record(record)
    reasons: list[str] = []
    lenses = record["lenses"]
    findings = record.get("findings") or []
    by_name = {l["name"]: l for l in lenses}

    expected = expected_lenses(settings, record) if settings else []
    missing = [n for n in expected if n not in by_name]
    skipped = [l["name"] for l in lenses if l.get("status") == "skipped"]
    not_run = [l["name"] for l in lenses if l.get("status") not in ("completed", "skipped")]
    open_ = [f["id"] for f in findings if f.get("resolution", "open") == "open" and f["severity"] != "Blocker"]
    if record.get("target_changed_during_round"):
        reasons.append("the target changed while the lenses were reviewing it")
    if missing:
        reasons.append("required lenses missing from the round: " + ", ".join(missing))
    if not_run:
        reasons.append("lenses not run: " + ", ".join(not_run))
    if open_:
        reasons.append("findings still open: " + ", ".join(open_))
    result = {"expected_lenses": expected}
    if reasons:
        return {**result, "gate": "INCOMPLETE", "clean": False, "reasons": reasons}

    blockers = [f["id"] for f in findings if f["severity"] == "Blocker"
                and f.get("resolution", "open") not in ("fixed", "contested", "waived")]
    if blockers:
        return {**result, "gate": "FAIL", "clean": False, "reasons": ["open blockers: " + ", ".join(blockers)]}

    waived = [f["id"] for f in findings if f["resolution"] == "waived"]
    if waived or skipped:
        why = (["waived: " + ", ".join(waived)] if waived else []) + \
              (["lenses skipped by the owner: " + ", ".join(skipped)] if skipped else [])
        return {**result, "gate": "PASS_WITH_WAIVERS", "clean": False, "reasons": why}
    fixed = [f["id"] for f in findings if f["resolution"] == "fixed" and f["severity"] in ("Blocker", "Major")]
    recheck = ["fixed in this round, needs a new round on the changed target: " + ", ".join(fixed)] if fixed else []
    actions = [f["id"] for f in findings if f["resolution"] == "action"]
    if actions:
        return {**result, "gate": "PASS_WITH_ACTIONS", "clean": not fixed,
                "reasons": ["tracked actions: " + ", ".join(actions)] + recheck}
    return {**result, "gate": "PASS", "clean": not fixed, "reasons": recheck}


def move_on(current: dict, previous: list[dict], settings: dict) -> dict:
    """Clean rounds in a row on the same target version, against the number needed."""
    kind = KIND.get(current["point"])
    mode = current.get("mode", "standard")
    needed = mode_views(settings)[mode]["clean_rounds_needed"][kind] if kind else 1
    streak = 0
    for rec in [*previous, current][::-1]:
        if rec["target_sha256"] != current["target_sha256"]:
            break
        if not gate(rec, settings)["clean"]:
            break
        streak += 1
    return {"streak": streak, "needed": needed, "move_on": streak >= needed}


# ---------------------------------------------------------------- config

def validate(value, schema: dict, defs: dict, path: str, errors: list[str], layer: bool = False) -> None:
    """A small JSON Schema subset: the keywords settings/schema.json uses.
    layer=True checks one settings layer: conditional (if/then) rules are skipped,
    because a lower layer may supply the keys they need."""
    if "$ref" in schema:
        schema = defs[schema["$ref"].split("/")[-1]]
    if "const" in schema and value != schema["const"]:
        errors.append(f"{path}: must be {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{path}: {value!r} is not one of {schema['enum']}")
        return
    t = schema.get("type")
    types = {"object": dict, "array": list, "string": str, "boolean": bool}
    if t == "integer":
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"{path}: must be an integer")
            return
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: must be at least {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: must be at most {schema['maximum']}")
    elif t in types and not isinstance(value, types[t]):
        errors.append(f"{path}: must be a {t}")
        return
    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: must not be empty" if schema["minLength"] == 1
                          else f"{path}: needs at least {schema['minLength']} characters")
        if "pattern" in schema and not re.search(schema["pattern"].replace("$", r"\Z") if schema["pattern"].endswith("$") else schema["pattern"], value):
            errors.append(f"{path}: {value!r} does not match {schema['pattern']}")
    if isinstance(value, list):
        if schema.get("uniqueItems") and len(set(json.dumps(v, default=str, sort_keys=True) for v in value)) != len(value):
            errors.append(f"{path}: items must be unique")
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(f"{path}: needs at least {schema['minItems']} items")
        for i, item in enumerate(value):
            validate(item, schema.get("items", {}), defs, f"{path}[{i}]", errors, layer)
    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in value:
            if not isinstance(key, str):
                errors.append(f"{path}.{key!r}: keys must be text")
        for key, sub in value.items():
            if key in props:
                validate(sub, props[key], defs, f"{path}.{key}", errors, layer)
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}.{key}: unknown key")
            elif isinstance(schema.get("additionalProperties"), dict):
                validate(sub, schema["additionalProperties"], defs, f"{path}.{key}", errors, layer)
        if "if" in schema and not layer:
            probe: list[str] = []
            validate(value, schema["if"], defs, path, probe)
            if not probe:
                for req in schema["then"].get("required", []):
                    if req not in value:
                        errors.append(f"{path}.{req}: required here")
                validate(value, {k: v for k, v in schema["then"].items() if k != "required"}, defs, path, errors)
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{path}.{req}: required")


def merge(base, over):
    if isinstance(base, dict) and isinstance(over, dict):
        out = copy.deepcopy(base)
        for k, v in over.items():
            out[k] = merge(base.get(k), v) if k in base else copy.deepcopy(v)
        return out
    return copy.deepcopy(over)  # lists and scalars replace


TIER_RANK = {"fast": 0, "standard": 1, "strong": 2}


def mode_views(s):
    """The standard review settings and each mode merged over them."""
    review = s["project"]["review"]
    base = {k: review[k] for k in ("clean_rounds_needed", "panels")}
    views = {"standard": base}
    for name, overlay in review.get("modes", {}).items():
        views[name] = merge(base, {k: v for k, v in overlay.items() if k in base})
    return views


def _model_rank(order, name):
    """Position of a model in models.order (0 = strongest), or None if unknown.
    The longest matching name wins, so gpt-5-mini is not read as gpt-5."""
    name = (name or "").lower()
    hits = [(len(known), i) for i, known in enumerate(order) if known.lower() in name]
    return max(hits)[1] if hits else None


def _tiers_in_order(s):
    order = s["models"].get("order", [])
    for tiers in s["models"]["tiers"].values():
        ranks = [_model_rank(order, tiers.get(t)) for t in ("strong", "standard", "fast")]
        known = [r for r in ranks if r is not None]
        if known != sorted(known):
            return False
    return True


INVARIANTS = [
    ("models.tiers: in every tool, strong must be at least as strong as standard, and standard at least as strong as fast (see models.order)",
     _tiers_in_order),
    ("in every mode, the sensitive panel must include security",
     lambda s: all("security" in v["panels"]["sensitive"] for v in mode_views(s).values())),
    ("in every mode, every review panel needs at least one lens",
     lambda s: all(all(p for p in v["panels"].values()) for v in mode_views(s).values())),
    ("in every mode, every clean_rounds_needed value must be at least 1 and at most max_rounds",
     lambda s: all(1 <= n <= s["project"]["review"]["max_rounds"]
                   for v in mode_views(s).values() for n in v["clean_rounds_needed"].values())),
    ("models: lenses that can stop work (security, spec-compliance) must be in models.lenses.strong, with floor strong",
     lambda s: {"security", "spec-compliance"} <= set(s["models"]["lenses"]["strong"])
     and s["models"]["floor_for_strong_lenses"] == "strong"),
    ("models: the advisor tier must be at least the tier of every session it advises",
     lambda s: not s["models"]["advisor"]["enabled"]
     or all(TIER_RANK[s["models"]["advisor"]["tier"]] >= TIER_RANK[s["models"]["sessions"].get(x, "standard")]
            for x in s["models"]["advisor"]["for"])),
    ("quick mode panels must still include spec-compliance for subtask and security for task",
     lambda s: "spec-compliance" in s["project"]["review"]["modes"]["quick"]["panels"]["subtask"]
     and "security" in s["project"]["review"]["modes"]["quick"]["panels"]["task"]),
    ("lenses that can stop work may not be set to the fast tier",
     lambda s: not set(s["models"]["lenses"]["strong"]) & set(s["models"]["lenses"]["fast"])),
    ("confidential projects need external_review ask or deny and store_code_in_memory false",
     lambda s: s["project"]["confidentiality"]["level"] != "confidential"
     or (s["project"]["confidentiality"]["external_review"] != "allow"
         and not s["project"]["confidentiality"]["store_code_in_memory"])),
    ("a merge-commit or rebase merge is needed when commits are per sub-task and tests lock by commit",
     lambda s: not (s["project"]["commits"]["per_subtask"] and s["project"]["tests"]["lock"] == "commit"
                    and s["project"]["merge_method"] == "squash")),
]


WARNINGS = [
    ("schedule.tidy.reset is empty: the weekly tidy cannot be scheduled before your reset until you set it",
     lambda s: s["schedule"]["tidy"]["when"] != "before_reset" or bool(s["schedule"]["tidy"]["reset"])),
    ("memory.personal.url is empty: setup writes it after creating your personal page",
     lambda s: s["memory"]["personal"]["backend"] != "notion" or bool(s["memory"]["personal"].get("url"))),
]


def load_yaml(path: str) -> dict:
    try:
        import yaml  # noqa: PLC0415
    except ImportError:
        raise InputError("PyYAML is needed: pip install pyyaml")
    p = Path(path)
    if not p.is_file():
        raise InputError(f"no such file: {p}")
    try:
        data = yaml.safe_load(p.read_text(encoding="utf-8-sig")) or {}
    except UnicodeDecodeError:
        raise InputError(f"{p}: not valid UTF-8")
    except OSError as e:
        raise InputError(f"{p}: cannot read: {e.strerror or e}")
    except yaml.YAMLError as e:
        raise InputError(f"{p}: not valid YAML: {e}")
    if not isinstance(data, dict):
        raise InputError(f"{p}: settings must be a mapping")
    try:
        json.dumps(data, default=str)
    except ValueError:
        raise InputError(f"{p}: a YAML alias refers to itself")
    return data


def git_remote(cwd: Path) -> str | None:
    """origin of the repository that contains cwd, as host/owner/name, or None."""
    try:
        out = subprocess.run(["git", "-C", str(cwd), "remote", "get-url", "origin"],
                             capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    url = out.stdout.strip()
    if out.returncode != 0 or not url:
        return None
    url = re.sub(r"\.git$", "", url)
    m = re.match(r"^(?:[a-z+]+://)?(?:[^@/]+@)?([^/:]+)[:/](.+)$", url)
    return f"{m.group(1)}/{m.group(2)}" if m else url


def which(projects: dict, cwd: Path) -> dict:
    """Pick the per-project entry for cwd: path first, then git remote. Never guesses."""
    cwd = cwd.expanduser().resolve()
    by_path = []
    def listed(entry, key):
        v = (entry.get("match") or {}).get(key) or []
        return [v] if isinstance(v, str) else list(v)
    for name, entry in projects.items():
        best = None
        for raw in listed(entry, "path"):
            if not str(raw).startswith(("/", "~")) and not re.match(r"^[A-Za-z]:[\\/]", str(raw)):
                raise InputError(f"projects.{name}.match.path {raw!r}: use a full path or one starting with ~")
            try:
                root = Path(str(raw)).expanduser().resolve()
            except (RuntimeError, ValueError, OSError) as e:
                raise InputError(f"projects.{name}.match.path {raw!r}: {e}")
            if _inside(cwd, root) and (best is None or len(root.parts) > best[0]):
                best = (len(root.parts), name, str(root))
        if best:  # one match per project: its deepest folder
            by_path.append(best)
    if by_path:
        by_path.sort(reverse=True)
        if len(by_path) > 1 and by_path[0][0] == by_path[1][0]:
            top = by_path[0][0]
            return {"project": None, "how": "ambiguous",
                    "candidates": sorted(n for d, n, _ in by_path if d == top), "remote": None}
        return {"project": by_path[0][1], "how": f"path {by_path[0][2]}", "remote": None}
    remote = git_remote(cwd)
    if remote:
        short = remote.split("/", 1)[1] if "/" in remote else remote
        hits = sorted({name for name, entry in projects.items()
                       for pat in listed(entry, "repo")
                       if fnmatch.fnmatch(remote, pat) or fnmatch.fnmatch(short, pat)})
        if len(hits) == 1:
            return {"project": hits[0], "how": f"repo {remote}", "remote": remote}
        if len(hits) > 1:
            return {"project": None, "how": "ambiguous", "candidates": hits, "remote": remote}
    return {"project": None, "how": "no match: ask the owner which project", "remote": remote}


def config(user: str | None, project: str | None, project_name: str | None = None,
           cwd: str | None = None) -> tuple[dict, bool]:
    schema = json.loads((ROOT / "settings/schema.json").read_text())
    defs = schema.get("$defs", {})
    defaults = load_yaml(str(ROOT / "settings/defaults.yaml"))
    errors: list[str] = []
    layers = {}
    if user:
        layers["user"] = load_yaml(user)
        bad = [k for k in layers["user"] if k not in ("user", "memory", "models", "schedule", "projects")]
        errors += [f"user file: {k} is not a user key" for k in bad]
    if project:
        layers["project"] = load_yaml(project)
        bad = [k for k in layers["project"] if k != "project"]
        errors += [f"project settings: {k} is not a project key" for k in bad]
    for name, data in layers.items():
        validate(data, schema, defs, name, errors, layer=True)
    if errors:
        # Wrong types would break matching and merging; report what was found.
        return {"ok": False, "errors": errors, "warnings": [], "project_match": {},
                "sha256": None, "layers": layers, "effective": {}}, False
    effective = defaults
    if "user" in layers:
        effective = merge(effective, layers["user"])
    projects = effective.get("projects", {})
    if project_name:
        if project_name not in projects:
            errors.append(f"projects.{project_name}: no such entry in your user settings")
            match = {"project": None, "how": "named, not found"}
        else:
            match = {"project": project_name, "how": "named"}
    else:
        try:
            match = which(projects, Path(cwd or os.getcwd()))
        except InputError as e:
            errors.append(str(e))
            match = {"project": None, "how": "match rule unusable"}
    if match.get("project"):
        override = {k: v for k, v in projects[match["project"]].items() if k != "match"}
        effective = merge(effective, override)
    if "project" in layers:
        effective = merge(effective, layers["project"])
    # projects: entries are layers too; they were checked with the user file.
    validate({k: v for k, v in effective.items() if k != "projects"}, schema, defs, "effective", errors)
    if not errors:
        for text, check in INVARIANTS:
            try:
                ok = check(effective)
            except (KeyError, TypeError, ValueError):
                ok = False
            if not ok:
                errors.append(f"invariant: {text}")
    if not errors:
        errors += path_errors(effective)
    warnings = []
    for text, check in WARNINGS:
        try:
            if not check(effective):
                warnings.append(text)
        except (KeyError, TypeError):
            pass
    digest = hashlib.sha256(json.dumps(effective, sort_keys=True, default=str).encode()).hexdigest()
    return {"ok": not errors, "errors": errors, "warnings": warnings, "project_match": match,
            "sha256": digest, "layers": layers, "effective": effective}, not errors


def _inside(child: Path, parent: Path) -> bool:
    return child == parent or parent in child.parents


def _git_root(path: Path) -> Path | None:
    for p in [path, *path.parents]:
        if (p / ".git").exists():
            return p
    return None


def path_errors(s: dict) -> list[str]:
    """Personal and central memory folders must stay apart (files backend)."""
    errs = []
    mem = s.get("memory", {})
    central, personal = mem.get("central", {}), mem.get("personal", {})
    home_mx = Path("~/.matriarch").expanduser().resolve()
    def usable(name, mem):
        if mem.get("backend") != "files" or not mem.get("path"):
            return None
        try:
            return Path(str(mem["path"])).expanduser().resolve()
        except (RuntimeError, ValueError, OSError) as e:
            errs.append(f"memory.{name}.path {mem['path']!r} cannot be used: {e}")
            return None
    cpath, ppath = usable("central", central), usable("personal", personal)
    for name, path in (("central", cpath), ("personal", ppath)):
        if path and _inside(path, home_mx):
            errs.append(f"memory.{name}.path must not be inside ~/.matriarch (review folders live there)")
    if cpath and ppath and (_inside(ppath, cpath) or _inside(cpath, ppath)):
        errs.append("memory.personal.path and memory.central.path must not contain each other")
    if ppath:
        try:
            root = _git_root(ppath)
        except OSError as e:
            errs.append(f"memory.personal.path {ppath} cannot be checked: {e.strerror or e}")
            root = None
        if root:
            errs.append(f"memory.personal.path is inside the git repository {root}; personal memory must not "
                        "be in a repository that can be pushed or searched")
    return errs


SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b")),
    ("Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    ("JWT", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{5,}")),
    ("credential in URL", re.compile(r"[a-z][a-z0-9+.-]*://[^/\s:@]+:[^@\s/]+@")),
    ("secret assignment", re.compile(r"(?i)\b\w*(password|passwd|pwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token)\w*"
                                     r"\s*[:=]\s*['\"]?(?!<|\$\{|\*{3}|x{3}|\.\.\.)[^\s'\"]{6,}")),
    ("email address", re.compile(r"\b[A-Za-z0-9._%+-]+@(?!example\.(com|org|test)\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("phone number", re.compile(r"(?<![\w.])\+?\d[\d -]{9,14}\d(?![\w.])")),
]


def scan(files: list[str]) -> list[dict]:
    hits = []
    for name in files:
        path = Path(name)
        if not path.is_file():
            raise InputError(f"no such file: {path}")
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            for kind, pattern in SECRET_PATTERNS:
                m = pattern.search(line)
                if m:
                    shown = m.group(0)
                    hits.append({"file": str(path), "line": n, "kind": kind,
                                 "match": shown[:4] + "…" if len(shown) > 4 else "…"})
    return hits


def export_check(to: str, files: list[str], approved_by: str | None, settings: dict) -> tuple[dict, bool]:
    conf = settings["project"]["confidentiality"]
    hits = scan(files)
    reasons = []
    if hits:
        reasons.append(f"{len(hits)} possible secret or personal data hit(s): remove or mask them first")
    if to == "external":
        if conf["external_review"] == "deny":
            reasons.append("project.confidentiality.external_review is deny")
        elif conf["external_review"] == "ask" and not approved_by:
            reasons.append("project.confidentiality.external_review is ask: rerun with --approved-by <owner> "
                           "after the owner says yes for these files and this tool")
    elif to == "memory":
        if not conf["store_code_in_memory"]:
            reasons.append("project.confidentiality.store_code_in_memory is false: put findings with file:line "
                           "in memory, keep code and full reports local")
    else:
        raise InputError("--to must be external or memory")
    ok = not reasons
    return {"allowed": ok, "to": to, "reasons": reasons, "hits": hits, "approved_by": approved_by}, ok


MIN_CLAUDE_CODE = (2, 1, 271)


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=20, cwd=cwd)
        return r.returncode, (r.stdout or r.stderr).strip()
    except (OSError, ValueError, subprocess.TimeoutExpired) as e:
        return 127, str(e)


def doctor(user: str | None, project: str | None, cwd: Path) -> tuple[dict, bool]:
    """Local checks before using Matriarch. Memory checks need the connector and
    are done by the doctor skill."""
    checks: list[dict] = []

    def add(name, status, detail, fix=""):
        checks.append({"check": name, "status": status, "detail": detail, "fix": fix})

    v = sys.version_info
    add("python", "ok" if v >= (3, 10) else "fail", f"{v.major}.{v.minor}.{v.micro}",
        "" if v >= (3, 10) else "install Python 3.10 or later")
    try:
        import yaml  # noqa: F401, PLC0415
        add("pyyaml", "ok", "installed")
    except ImportError:
        add("pyyaml", "fail", "missing", "pip install pyyaml")

    code, out = _run(["git", "--version"])
    add("git", "ok" if code == 0 else "fail", out if code == 0 else "not found", "" if code == 0 else "install git")
    code, out = _run(["gh", "--version"])
    add("gh (GitHub CLI)", "ok" if code == 0 else "warn", (out.splitlines() or ["gh"])[0] if code == 0 else "not found",
        "" if code == 0 else "needed by review to post and to merge with the SHA guard: install gh and run gh auth login")
    if code == 0:
        code, _ = _run(["gh", "auth", "status"])
        add("gh sign-in", "ok" if code == 0 else "warn", "signed in" if code == 0 else "not signed in",
            "" if code == 0 else "run gh auth login")
    code, out = _run(["claude", "--version"])
    if code == 0:
        m = re.search(r"(\d+)\.(\d+)\.(\d+)", out)
        ver = tuple(int(x) for x in m.groups()) if m else None
        good = ver is not None and ver >= MIN_CLAUDE_CODE
        add("claude (Claude Code)", "ok" if good else "warn", out,
            "" if good else "update Claude Code to 2.1.271 or later for read-only goldfish agents")
    else:
        add("claude (Claude Code)", "warn", "not found", "only needed for Claude Code sessions and claude -p goldfish")
    code, out = _run(["codex", "--version"])
    add("codex", "ok" if code == 0 else "warn", out if code == 0 else "not found",
        "" if code == 0 else "optional: a second model for cross-model goldfish")

    user_file = user or str(Path("~/.matriarch/config.yaml").expanduser())
    if user and not Path(user_file).is_file():
        add("user settings", "fail", f"{user_file} not found", "check the --user path")
        user_file = None
    elif not Path(user_file).is_file():
        add("user settings", "warn", f"{user_file} not found: defaults apply",
            "run setup, or create it with the settings dashboard")
        user_file = None
    elif not os.access(user_file, os.R_OK):
        add("user settings", "fail", f"{user_file} cannot be read", "check the file's permissions")
    else:
        add("user settings", "ok", user_file)
    try:
        result, ok = config(user_file, project, None, str(cwd))
    except (InputError, OSError, KeyError, TypeError, AttributeError, ValueError, RuntimeError) as e:
        result, ok = {"errors": [str(e)], "warnings": [], "project_match": {}, "effective": {}}, False
    add("settings valid", "ok" if ok else "fail", "; ".join(result["errors"]) or "schema and invariants pass",
        "" if ok else "fix the listed keys (settings dashboard or matriarch.py config)")
    for w in result.get("warnings", []):
        add("settings warning", "warn", w, "set it in your user settings, or run setup")
    match = result.get("project_match") or {}
    if match.get("project"):
        add("project here", "ok", f"{match['project']} ({match['how']})")
    else:
        add("project here", "warn", match.get("how", "unknown"),
            "name the project when you start a session, or add a projects: entry with a match rule")

    eff = result.get("effective") or {}
    for which_mem in ("central", "personal"):
        mem = eff.get("memory", {}).get(which_mem, {})
        if mem.get("backend") == "files":
            try:
                path = Path(str(mem.get("path") or "")).expanduser()
                exists = bool(mem.get("path")) and path.is_dir()
            except (RuntimeError, ValueError, OSError):
                path, exists = Path(str(mem.get("path"))), False
            add(f"{which_mem} memory folder", "ok" if exists else "fail", str(path) if mem.get("path") else "path empty",
                "" if exists else f"create the folder or fix memory.{which_mem}.path")
        elif mem.get("backend") == "notion":
            add(f"{which_mem} memory", "info", "notion: not checked here; the doctor skill checks it through the connector")

    code, top = _run(["git", "rev-parse", "--show-toplevel"], cwd)
    if code == 0:
        _, branch = _run(["git", "branch", "--show-current"], cwd)
        _, dirty = _run(["git", "status", "--porcelain"], cwd)
        add("repository", "ok" if not dirty else "warn", f"{top} on {branch or '(detached)'}"
            + ("" if not dirty else f", {len(dirty.splitlines())} uncommitted change(s)"),
            "" if not dirty else "commit or stash before plan or exec")
    else:
        add("repository", "warn", "not inside a git repository", "fine for discuss and status; plan and exec need the repository")

    failed = any(c["status"] == "fail" for c in checks)  # statuses: ok, info, warn, fail
    return {"ok": not failed, "checks": checks}, not failed


# ---------------------------------------------------------------- main

def parse_opts(args: list[str], names: set[str]) -> tuple[dict, list[str]]:
    opts, rest = {}, []
    while args:
        if args[0] in names:
            if len(args) < 2:
                raise InputError(f"{args[0]} needs a value")
            if args[0] == "--previous":
                opts.setdefault("--previous", []).append(args[1])
            else:
                opts[args[0]] = args[1]
            args = args[2:]
        elif args[0].startswith("--"):
            raise InputError(f"unknown option {args[0]}")
        else:
            rest.append(args[0])
            args = args[1:]
    return opts, rest


def effective_settings(user: str | None, project: str | None, name: str | None = None,
                       cwd: str | None = None) -> dict:
    result, ok = config(user, project, name, cwd)
    if not ok:
        raise InputError("settings are invalid: " + "; ".join(result["errors"]))
    return result["effective"]


def read_json(path: str):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def main(argv: list[str]) -> int:
    cmd, args = (argv[1], argv[2:]) if len(argv) > 1 else ("", [])
    try:
        if cmd == "gate":
            opts, rest = parse_opts(args, {"--user", "--project", "--previous", "--project-name", "--cwd"})
            if len(rest) != 1:
                raise InputError("gate takes one round record")
            settings = effective_settings(opts.get("--user"), opts.get("--project"),
                                          opts.get("--project-name"), opts.get("--cwd"))
            current = read_json(rest[0])
            previous = [read_json(f) for f in opts.get("--previous", [])]
            for rec in previous:
                check_record(rec)
            result = gate(current, settings)
            result.update(move_on(current, previous, settings))
            ok = result["move_on"]
        elif cmd == "config":
            opts, rest = parse_opts(args, {"--user", "--project", "--project-name", "--cwd"})
            if rest:
                raise InputError(f"unexpected argument {rest[0]!r}")
            result, ok = config(opts.get("--user"), opts.get("--project"),
                                opts.get("--project-name"), opts.get("--cwd"))
        elif cmd == "doctor":
            opts, rest = parse_opts(args, {"--user", "--project", "--cwd"})
            if rest:
                raise InputError(f"unexpected argument {rest[0]!r}")
            result, ok = doctor(opts.get("--user"), opts.get("--project"), Path(opts.get("--cwd") or os.getcwd()))
        elif cmd == "which":
            opts, rest = parse_opts(args, {"--user", "--cwd"})
            if rest:
                raise InputError(f"unexpected argument {rest[0]!r}")
            projects = load_yaml(opts["--user"]).get("projects", {}) if opts.get("--user") else {}
            result = which(projects, Path(opts.get("--cwd") or os.getcwd()))
            ok = bool(result["project"])
        elif cmd == "scan":
            if not args:
                raise InputError("scan takes one or more files")
            hits = scan(args)
            result, ok = {"clean": not hits, "hits": hits}, not hits
        elif cmd == "export":
            opts, rest = parse_opts(args, {"--to", "--approved-by", "--user", "--project", "--project-name", "--cwd"})
            if not rest or "--to" not in opts:
                raise InputError("export --to external|memory [--approved-by NAME] <files>")
            settings = effective_settings(opts.get("--user"), opts.get("--project"),
                                          opts.get("--project-name"), opts.get("--cwd"))
            result, ok = export_check(opts["--to"], rest, opts.get("--approved-by"), settings)
        elif cmd == "sha256" and len(args) == 1:
            result, ok = {"sha256": hashlib.sha256(Path(args[0]).read_bytes()).hexdigest()}, True
        else:
            print(__doc__)
            return 2
    except (InputError, json.JSONDecodeError, OSError, KeyError, TypeError, AttributeError, ValueError, RuntimeError) as e:
        print(json.dumps({"error": str(e)}))
        return 2
    text = json.dumps(result, ensure_ascii=False, indent=2, default=str)
    try:
        print(text)
    except UnicodeEncodeError:
        print(json.dumps(result, ensure_ascii=True, indent=2, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
