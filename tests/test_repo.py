"""Structure checks for Matriarch. Run: python3 -m pytest"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build  # noqa: E402

SKILLS = build.skills()
PERSONAS = build.personas()
METHOD_FILES = (
    [s / "SKILL.md" for s in SKILLS]
    + list((ROOT / "personas").glob("*.md"))
    + list((ROOT / "core").glob("*.md"))
    + list((ROOT / "standards").glob("*.md"))
)
PUBLIC_DOCS = [ROOT / "README.md"] + list((ROOT / "docs").glob("*.md"))
ROOT_BLOCK = "Matriarch's shared files live in the plugin root (`ROOT`)"


def test_generated_files_current():
    r = subprocess.run([sys.executable, str(ROOT / "scripts/build.py"), "--check"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_skill_frontmatter(skill):
    meta, body = build.frontmatter(skill / "SKILL.md")
    assert meta["name"] == skill.name
    assert 40 < len(meta["description"]) <= 1024
    assert ROOT_BLOCK in body, "missing the 'Before you start' ROOT block"


@pytest.mark.parametrize("persona", PERSONAS, ids=lambda p: p.name)
def test_persona_frontmatter(persona):
    meta, body = build.frontmatter(persona)
    assert meta["name"] == persona.stem
    assert meta["description"]
    if persona.stem != "synthesizer":
        assert "_mandates.md" in body
        assert "Write" not in meta.get("claude-tools", []), "goldfish must be read-only"


ROOT_REF = re.compile(r"ROOT/((?:core|personas|standards|settings)/[\w.-]+\.(?:md|yaml|json))")
LENS_REF = re.compile(r"`(business|code-quality|zoom-out|comprehension|design-critic|implementation-readiness|codebase-fit|decision-fit|correctness|security|test-evidence|spec-compliance|premortem|synthesizer)`")


@pytest.mark.parametrize("path", METHOD_FILES, ids=lambda p: str(p.relative_to(ROOT)))
def test_references_exist(path):
    text = path.read_text(encoding="utf-8")
    for ref in ROOT_REF.findall(text):
        assert (ROOT / ref).exists(), f"{path.name} names missing file {ref}"
    for link in re.findall(r"\]\((\.{1,2}/[^)#]+)", text):
        assert (path.parent / link).resolve().exists(), f"{path.name}: broken link {link}"
    for lens in LENS_REF.findall(text):
        assert (ROOT / "personas" / f"{lens}.md").exists(), f"{path.name}: unknown lens {lens}"


FACT_PATTERNS = [
    (re.compile(r"collection://[0-9a-f]{8}-"), "a Notion collection ID"),
    (re.compile(r"notion\.(so|com)/p/[0-9a-f]{20,}"), "a Notion page URL"),
]
# Project-specific names (people, repositories) are listed one per line in
# tests/forbidden-terms.local.txt, which is git-ignored so this repository does
# not carry them.
_LOCAL = Path(__file__).with_name("forbidden-terms.local.txt")
if _LOCAL.exists():
    for term in filter(None, (l.strip() for l in _LOCAL.read_text().splitlines())):
        FACT_PATTERNS.append((re.compile(rf"\b{re.escape(term)}\b", re.I), f"the project term {term!r}"))


@pytest.mark.parametrize("path", METHOD_FILES + PUBLIC_DOCS, ids=lambda p: str(p.relative_to(ROOT)))
def test_no_project_facts_in_method(path):
    text = path.read_text(encoding="utf-8")
    for pattern, what in FACT_PATTERNS:
        assert not pattern.search(text), f"{path.relative_to(ROOT)} contains {what}"


def test_manifests_agree():
    base = json.loads((ROOT / "plugin.json").read_text())
    for rel in (".claude-plugin/plugin.json", ".codex-plugin/plugin.json"):
        m = json.loads((ROOT / rel).read_text())
        assert m["name"] == base["name"] and m["version"] == base["version"], rel
    claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    for agent in claude["agents"]:
        assert (ROOT / agent).exists(), agent


def test_zip_layout(tmp_path):
    import zipfile

    zips = build.build_zips()
    assert len(zips) == len(SKILLS)
    names = zipfile.ZipFile(zips[0]).namelist()
    skill = zips[0].stem
    assert skill.startswith("matriarch-")
    assert f"{skill}/SKILL.md" in names
    assert f"name: {skill}" in zipfile.ZipFile(zips[0]).read(f"{skill}/SKILL.md").decode()
    for shared in build.SHARED:
        assert any(n.startswith(f"{skill}/matriarch/{shared}/") for n in names), shared
    for z in zips:
        bad = [n for n in zipfile.ZipFile(z).namelist() if "__pycache__" in n or "/." in n]
        assert not bad, bad


def test_settings_defaults_match_schema():
    import jsonschema
    import yaml
    defaults = yaml.safe_load((ROOT / "settings/defaults.yaml").read_text())
    schema = json.loads((ROOT / "settings/schema.json").read_text())
    jsonschema.validate(defaults, schema)
    lenses = set(schema["$defs"]["lenses"]["items"]["enum"])
    assert lenses == {p.stem for p in PERSONAS if p.stem != "synthesizer"}


def test_panels_used_by_skills_exist():
    import yaml
    panels = yaml.safe_load((ROOT / "settings/defaults.yaml").read_text())["project"]["review"]["panels"]
    for path in METHOD_FILES:
        for point in re.findall(r"review point `([a-z_]+)`", path.read_text(encoding="utf-8")):
            assert point in panels, f"{path.name}: unknown review point {point}"


def test_files_tool_roundtrip(tmp_path):
    tool = ROOT / "core/backends/files_tool.py"
    run = lambda *a: json.loads(subprocess.run([sys.executable, str(tool), *a], capture_output=True, text=True, check=True).stdout)
    d = tmp_path / "decisions"
    run("new", str(d), "ORD-D01", "ID=ORD-D01", "Decision=One item table", "Status=Proposed", "Area=ORD", "Date=2026-11-16")
    run("new", str(d), "ORD-D02", "ID=ORD-D02", "Decision=Cost in cents", "Status=Decided", "Area=ORD", "Date=2026-11-17")
    assert [r["ID"] for r in run("query", str(d), "Area=ORD")] == ["ORD-D02", "ORD-D01"]
    assert [r["ID"] for r in run("query", str(d), "Decision~item")] == ["ORD-D01"]
    run("set", str(d / "ORD-D01.md"), "Status=Superseded")
    assert run("get", str(d / "ORD-D01.md"))["properties"]["Status"] == "Superseded"
    dup = subprocess.run([sys.executable, str(tool), "new", str(d), "ORD-D01"], capture_output=True, text=True)
    assert dup.returncode == 1 and "exists" in dup.stdout
    assert [r["ID"] for r in run("query", str(d), "Status!=Superseded")] == ["ORD-D02"]
    assert len(run("query", str(d), "Status=Superseded|Decided")) == 2
    assert [r["ID"] for r in run("query", str(d), "Date>=2026-11-17")] == ["ORD-D02"]
    note = tmp_path / "progress.txt"
    note.write_text("ORD-API-03.data · B · round 1\nORD-API-03.logic · A · round 1\n")
    run("section", str(d / "ORD-D02.md"), "Progress", str(note))
    run("section", str(d / "ORD-D02.md"), "Progress", str(note))
    got = run("get", str(d / "ORD-D02.md"))
    assert got["sections"]["Progress"].count("ORD-API-03.data") == 1
    for bad in (["query", str(tmp_path / "missing")], ["query", str(d), "Status"], ["get", str(d / "nope.md")]):
        r = subprocess.run([sys.executable, str(tool), *bad], capture_output=True, text=True)
        assert r.returncode == 1 and "error" in r.stdout, bad


TOOL = ROOT / "core/tools/matriarch.py"
SHA_A = "a" * 64
SHA_B = "b" * 64
SUBTASK_PANEL = ["spec-compliance", "code-quality", "business", "test-evidence"]


def _tool(*args):
    r = subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True)
    return r.returncode, json.loads(r.stdout)


def _record(lenses=None, findings=None, point="subtask", sha=SHA_A, **extra):
    names = {l["name"]: l for l in (lenses or [])}
    full = [names.pop(n, {"name": n, "status": "completed"}) for n in SUBTASK_PANEL] if point == "subtask" else []
    return {"point": point, "target_sha256": sha, "lenses": full + list(names.values()),
            "findings": findings or [], **extra}


def _gate(tmp_path, record, *previous, extra_args=()):
    f = tmp_path / "round.json"
    f.write_text(json.dumps(record))
    args = ["gate", str(f), *extra_args]
    for i, rec in enumerate(previous):
        pf = tmp_path / f"prev{i}.json"
        pf.write_text(json.dumps(rec))
        args += ["--previous", str(pf)]
    return _tool(*args)


WAIVER = {"owner": "o", "reason": "r", "decision": "ORD-D01", "review_by": "2026-12-01"}


@pytest.mark.parametrize("lenses,findings,expected", [
    ([{"name": "business", "status": "not_run", "reason": "timeout"}], [], "INCOMPLETE"),
    ([], [{"id": "F1", "severity": "Nit", "resolution": "open"}], "INCOMPLETE"),
    ([], [{"id": "F1", "severity": "Blocker", "resolution": "open"}], "FAIL"),
    ([], [{"id": "F1", "severity": "Blocker", "resolution": "waived", **WAIVER}], "PASS_WITH_WAIVERS"),
    ([], [{"id": "F1", "severity": "Major", "resolution": "action", "owner": "o", "where": "X.edge"}], "PASS_WITH_ACTIONS"),
    ([], [{"id": "F1", "severity": "Blocker", "resolution": "fixed"}, {"id": "F2", "severity": "Nit", "resolution": "declined"}], "PASS"),
    ([{"name": "business", "status": "skipped", "reason": "no business logic", "owner": "o"}], [], "PASS_WITH_WAIVERS"),
])
def test_gate(tmp_path, lenses, findings, expected):
    code, out = _gate(tmp_path, _record(lenses, findings))
    assert out["gate"] == expected, out


def test_gate_requires_the_whole_panel(tmp_path):
    record = {"point": "pr", "target_sha256": SHA_A, "lenses": [{"name": "comprehension", "status": "completed"}], "findings": []}
    code, out = _gate(tmp_path, record)
    assert out["gate"] == "INCOMPLETE" and code == 1
    assert "spec-compliance" in out["reasons"][0]


def test_gate_adds_sensitive_panel(tmp_path):
    code, out = _gate(tmp_path, _record(sensitive=True))
    assert out["gate"] == "INCOMPLETE" and "security" in out["expected_lenses"]
    code, out = _gate(tmp_path, _record([{"name": "correctness", "status": "completed"},
                                         {"name": "security", "status": "completed"}], sensitive=True))
    assert out["gate"] == "PASS" and code == 0


def test_gate_uses_mode_panels(tmp_path):
    rec = {"point": "subtask", "mode": "quick", "target_sha256": SHA_A, "findings": [],
           "lenses": [{"name": "spec-compliance", "status": "completed"}, {"name": "test-evidence", "status": "completed"}]}
    code, out = _gate(tmp_path, rec)
    assert out["gate"] == "PASS" and out["move_on"] and code == 0


def test_streak_counts_rounds_on_the_same_version(tmp_path):
    spec = lambda sha: {"point": "spec", "target_sha256": sha, "findings": [],
                        "lenses": [{"name": n, "status": "completed"} for n in
                                   ["comprehension", "zoom-out", "business", "decision-fit", "design-critic", "implementation-readiness"]]}
    code, out = _gate(tmp_path, spec(SHA_A))
    assert out["streak"] == 1 and out["needed"] == 2 and not out["move_on"] and code == 1
    code, out = _gate(tmp_path, spec(SHA_A), spec(SHA_A))
    assert out["streak"] == 2 and out["move_on"] and code == 0
    code, out = _gate(tmp_path, spec(SHA_B), spec(SHA_A))
    assert out["streak"] == 1 and not out["move_on"]


def test_fixed_round_is_not_clean(tmp_path):
    code, out = _gate(tmp_path, _record(findings=[{"id": "F1", "severity": "Blocker", "resolution": "fixed"}]))
    assert out["gate"] == "PASS" and out["clean"] is False and not out["move_on"]


@pytest.mark.parametrize("record", [
    [],
    {"point": "subtask", "target_sha256": SHA_A, "lenses": [{"status": "completed"}], "findings": []},
    {"point": "subtask", "target_sha256": "abc", "lenses": [{"name": "x", "status": "completed"}], "findings": []},
    {"point": "nope", "target_sha256": SHA_A, "lenses": [{"name": "x", "status": "completed"}], "findings": []},
    {"point": "subtask", "target_sha256": SHA_A, "lenses": [{"name": "x", "status": "completed"}], "findings": ["F1"]},
    {"point": "subtask", "target_sha256": SHA_A, "lenses": [{"name": "x", "status": "completed"}],
     "findings": [{"id": "F1", "severity": "Major", "resolution": "declined"}]},
    {"point": "subtask", "target_sha256": SHA_A, "lenses": [{"name": "x", "status": "completed"}],
     "findings": [{"id": "F1", "severity": "Major", "resolution": "waived", "owner": "o", "reason": "r"}]},
    {"point": "subtask", "target_sha256": SHA_A, "lenses": [{"name": "x", "status": "completed"}],
     "findings": [{"id": "F1", "severity": "Blocker", "resolution": "action", "owner": "o", "where": "x"}]},
])
def test_gate_bad_input_is_an_error(tmp_path, record):
    code, out = _gate(tmp_path, record)
    assert code == 2 and "error" in out, out


def test_scan_and_export(tmp_path):
    clean = tmp_path / "clean.md"
    clean.write_text("Use the user's email from settings; contact dev@example.com.\n")
    dirty = tmp_path / "dirty.md"
    dirty.write_text('db_password = "S3cretValue!"\nurl: postgres://app:hunter22@db:5432/x\n')
    assert _tool("scan", str(clean))[0] == 0
    code, out = _tool("scan", str(dirty))
    assert code == 1 and {h["kind"] for h in out["hits"]} >= {"secret assignment", "credential in URL"}
    assert "hunter22" not in json.dumps(out)
    proj = tmp_path / "p.yaml"
    proj.write_text("project:\n  confidentiality:\n    level: confidential\n    external_review: ask\n    store_code_in_memory: false\n")
    assert _tool("export", "--to", "external", "--project", str(proj), str(clean))[0] == 1
    assert _tool("export", "--to", "external", "--approved-by", "owner", "--project", str(proj), str(clean))[0] == 0
    assert _tool("export", "--to", "memory", "--project", str(proj), str(clean))[0] == 1
    assert _tool("export", "--to", "external", "--approved-by", "owner", "--project", str(proj), str(dirty))[0] == 1


def test_config_rejects_overlapping_memory_paths(tmp_path):
    central = tmp_path / "central"
    (central / "me").mkdir(parents=True)
    user = tmp_path / "u.yaml"
    user.write_text(f"memory:\n  central: {{backend: files, path: '{central}'}}\n  personal: {{backend: files, path: '{central / 'me'}'}}\n")
    code, out = _tool("config", "--user", str(user))
    assert code == 1 and any("contain each other" in e for e in out["errors"])
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    user.write_text(f"memory:\n  personal: {{backend: files, path: '{repo / 'notes'}'}}\n")
    code, out = _tool("config", "--user", str(user))
    assert code == 1 and any("git repository" in e for e in out["errors"])


def test_config_defaults_valid():
    code, out = _tool("config")
    assert code == 0 and out["ok"], out["errors"]


@pytest.mark.parametrize("text,needle", [
    ("project:\n  bogus: 1\n", "unknown key"),
    ("project:\n  review:\n    panels:\n      sensitive: [correctness]\n", "security"),
    ("project:\n  confidentiality:\n    level: confidential\n", "confidential"),
    ("project:\n  merge_method: squash\n", "merge-commit or rebase"),
    ("user:\n  language: en\n", "not a project key"),
])
def test_config_rejects(tmp_path, text, needle):
    f = tmp_path / "project.yaml"
    f.write_text(text)
    code, out = _tool("config", "--project", str(f))
    assert code == 1 and any(needle in e for e in out["errors"]), out["errors"]


@pytest.mark.parametrize("layer,text,needle", [
    ("--project", "project:\n  review:\n    modes:\n      quick:\n        panels:\n          sensitive: [correctness]\n", "sensitive panel must include security"),
    ("--project", "project:\n  review:\n    modes:\n      critical:\n        clean_rounds_needed: {code: 5}\n", "at most max_rounds"),
    ("--project", "project:\n  review:\n    clean_rounds_needed: {spec: 0}\n", "at least 1"),
    ("--user", "models:\n  lenses:\n    strong: []\n", "security, spec-compliance"),
    ("--user", "models:\n  advisor:\n    tier: fast\n", "advisor tier"),
])
def test_config_rejects_weakening(tmp_path, layer, text, needle):
    f = tmp_path / "s.yaml"
    f.write_text(text)
    code, out = _tool("config", layer, str(f))
    assert code == 1 and any(needle in e for e in out["errors"]), out["errors"]


def _git_repo(path, remote):
    path.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "remote", "add", "origin", remote], check=True)
    return path


def test_which_picks_the_project_by_folder_then_remote(tmp_path):
    work = _git_repo(tmp_path / "work" / "billing", "git@gitlab.example.test:corp/billing-api.git")
    side = _git_repo(tmp_path / "side", "https://github.com/me/side-app.git")
    other = _git_repo(tmp_path / "other", "https://github.com/me/unrelated.git")
    user = tmp_path / "u.yaml"
    user.write_text(
        "projects:\n"
        f"  Billing:\n    match: {{path: ['{tmp_path / 'work'}']}}\n"
        "    memory: {central: {backend: files, path: '" + str(tmp_path / "billing-memory") + "'}}\n"
        "  Side:\n    match: {repo: ['me/side-app*']}\n"
        "    user: {language: en}\n"
    )
    code, out = _tool("which", "--user", str(user), "--cwd", str(work))
    assert code == 0 and out["project"] == "Billing" and out["how"].startswith("path")
    code, out = _tool("which", "--user", str(user), "--cwd", str(side))
    assert code == 0 and out["project"] == "Side" and out["remote"] == "github.com/me/side-app"
    code, out = _tool("which", "--user", str(user), "--cwd", str(other))
    assert code == 1 and out["project"] is None
    code, out = _tool("config", "--user", str(user), "--cwd", str(work))
    assert out["project_match"]["project"] == "Billing"
    assert out["effective"]["memory"]["central"]["backend"] == "files"
    code, out = _tool("config", "--user", str(user), "--cwd", str(side))
    assert out["effective"]["memory"]["central"]["backend"] == "notion"


def test_dashboard_invariants_match_the_tool():
    """The dashboard checks the same invariants as matriarch.py config."""
    sys.path.insert(0, str(ROOT / "core/tools"))
    import matriarch  # noqa: PLC0415

    template = (ROOT / "dashboard/template.html").read_text(encoding="utf-8")
    js = set(re.findall(r'^\s*\["([^"]+)", \(s\) =>', template, re.M))
    py = {text for text, _ in matriarch.INVARIANTS}
    assert js == py, {"only in dashboard": js - py, "only in tool": py - js}


def test_dashboard_has_the_current_settings():
    html = (ROOT / "dashboard/settings.html").read_text(encoding="utf-8")
    data = json.loads(re.search(r"const DATA = (\{.*?\});\n", html, re.S).group(1))
    import yaml
    assert data["defaults"] == yaml.safe_load((ROOT / "settings/defaults.yaml").read_text())
    assert data["docs"]["project.review.mode"].startswith("Default review mode")


def test_doctor_reports_checks(tmp_path):
    code, out = _tool("doctor", "--cwd", str(tmp_path))
    names = {c["check"] for c in out["checks"]}
    assert {"python", "pyyaml", "git", "settings valid", "project here", "repository"} <= names
    assert all(c["status"] in ("ok", "info", "warn", "fail") for c in out["checks"])


def test_doctor_explicit_missing_user_file_fails(tmp_path):
    code, out = _tool("doctor", "--cwd", str(tmp_path), "--user", str(tmp_path / "nope.yaml"))
    assert code == 1
    assert any(c["check"] == "user settings" and c["status"] == "fail" for c in out["checks"])


def test_doctor_marks_notion_memory_as_not_checked(tmp_path):
    code, out = _tool("doctor", "--cwd", str(tmp_path))
    notion = [c for c in out["checks"] if c["check"].endswith("memory")]
    assert notion and all(c["status"] == "info" for c in notion)


def test_config_malformed_yaml_is_an_input_error(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("user: [unclosed\n")
    code, out = _tool("config", "--user", str(bad))
    assert code == 2


def test_config_outputs_raw_layers(tmp_path):
    u = tmp_path / "u.yaml"
    u.write_text("user:\n  language: ar\n")
    code, out = _tool("config", "--user", str(u), "--cwd", str(tmp_path))
    assert code == 0 and out["layers"]["user"] == {"user": {"language": "ar"}}


def test_project_override_to_files_may_inherit_its_path(tmp_path):
    mem = tmp_path / "central"; mem.mkdir()
    work = tmp_path / "work"; work.mkdir()
    u = tmp_path / "u.yaml"
    u.write_text(f"memory:\n  central:\n    backend: files\n    path: {mem}\n"
                 f"projects:\n  side:\n    match:\n      path: [{work}]\n"
                 f"    memory:\n      central:\n        backend: files\n")
    code, out = _tool("config", "--user", str(u), "--cwd", str(work))
    assert code == 0, out["errors"]
    assert out["project_match"]["project"] == "side"
    assert out["effective"]["memory"]["central"]["path"] == str(mem)


def test_config_bad_inputs_are_reported_not_crashes(tmp_path):
    cases = {
        "bytes.yaml": b"user:\n  language: \xff\xfe en\n",
        "tilde.yaml": b"projects:\n  w:\n    match:\n      path: ['~nosuchuser-matriarch/work']\n",
    }
    for name, raw in cases.items():
        f = tmp_path / name
        f.write_bytes(raw)
        code, out = _tool("config", "--user", str(f), "--cwd", str(tmp_path))
        expected = 1 if name == "tilde.yaml" else 2  # a path error, not unreadable input
        assert code == expected, (name, out)
        code, out = _tool("doctor", "--user", str(f), "--cwd", str(tmp_path))
        assert code == 1 and any(c["status"] == "fail" for c in out["checks"]), (name, out)


def test_config_wrong_types_keep_schema_errors(tmp_path):
    for text in ("projects: [a, b]\n", "projects:\n  w:\n    match:\n      path: 5\n",
                 "user:\n  language: 2024-01-01\n"):
        f = tmp_path / "u.yaml"
        f.write_text(text)
        code, out = _tool("config", "--user", str(f), "--cwd", str(tmp_path))
        assert code == 1 and out["errors"], (text, out)
        code, out = _tool("doctor", "--user", str(f), "--cwd", str(tmp_path))
        assert any(c["check"] == "settings valid" and c["status"] == "fail" for c in out["checks"]), out


def test_config_more_bad_inputs(tmp_path):
    f = tmp_path / "u.yaml"
    f.write_text("user: &a {x: *a}\n")
    code, out = _tool("config", "--user", str(f), "--cwd", str(tmp_path))
    assert code == 2 and "error" in out
    f.write_text("projects:\n  1: {}\n  b: {}\n")
    code, out = _tool("config", "--user", str(f), "--cwd", str(tmp_path))
    assert code == 1 and any("keys must be text" in e for e in out["errors"])
    f.write_text('schedule:\n  tidy:\n    reset: "Fri 18:00\\n"\n')
    code, out = _tool("config", "--user", str(f), "--cwd", str(tmp_path))
    assert code == 1


def test_doctor_reports_unreadable_settings(tmp_path):
    d = tmp_path / "dir.yaml"
    d.mkdir()
    code, out = _tool("doctor", "--user", str(tmp_path / "missing.yaml"), "--project", str(d), "--cwd", str(tmp_path))
    assert code == 1 and out["checks"]


def test_unusable_memory_path_is_an_error_not_a_crash(tmp_path):
    f = tmp_path / "u.yaml"
    f.write_text("memory:\n  central:\n    backend: files\n    path: '~nosuchuser-matriarch/mem'\n")
    code, out = _tool("config", "--user", str(f), "--cwd", str(tmp_path))
    assert code == 1 and any("cannot be used" in e for e in out["errors"])
    f.write_text(f.read_text() + "models:\n  floor_for_strong_lenses: fast\n")
    code, out = _tool("doctor", "--user", str(f), "--cwd", str(tmp_path))
    assert code == 1 and out["checks"]


def test_which_same_folder_twice_is_not_ambiguous(tmp_path):
    work = tmp_path / "work"
    work.mkdir()
    import matriarch  # noqa: PLC0415
    projects = {"A": {"match": {"path": [str(work), str(work) + "/"]}}}
    assert matriarch.which(projects, work)["project"] == "A"


def test_which_rejects_relative_match_paths(tmp_path):
    import matriarch  # noqa: PLC0415
    with pytest.raises(matriarch.InputError):
        matriarch.which({"A": {"match": {"path": ["work"]}}}, tmp_path)


def test_config_date_in_a_list_is_a_schema_error(tmp_path):
    f = tmp_path / "u.yaml"
    f.write_text("models:\n  lenses:\n    fast: [2024-01-01]\n")
    code, out = _tool("config", "--user", str(f), "--cwd", str(tmp_path))
    assert code == 1 and any("fast[0]" in e for e in out["errors"])


def test_claude_ai_zips_use_only_accepted_frontmatter_keys():
    import zipfile
    allowed = {"name", "description", "license", "allowed-tools", "metadata", "compatibility"}
    for z in build.build_zips():
        text = zipfile.ZipFile(z).read(f"{z.stem}/SKILL.md").decode()
        head = re.match(r"^---\n(.*?)\n---\n", text, re.S).group(1)
        keys = set(re.findall(r"^([A-Za-z][\w-]*):", head, re.M))
        assert keys <= allowed, (z.name, keys - allowed)
        desc = re.search(r"^description: (.*)$", head, re.M).group(1)
        assert "<" not in desc and ">" not in desc, z.name


def test_model_tiers_must_keep_their_order(tmp_path):
    f = tmp_path / "u.yaml"
    f.write_text("models:\n  tiers:\n    claude-code: {strong: sonnet, standard: opus, fast: haiku}\n")
    code, out = _tool("config", "--user", str(f), "--cwd", str(tmp_path))
    assert code == 1 and any("strong must be at least as strong" in e for e in out["errors"])
    f.write_text("models:\n  tiers:\n    claude-code: {strong: claude-opus-4, standard: claude-opus-4, fast: haiku}\n"
                 "    codex: {strong: my-big, standard: my-small, fast: ''}\n")
    code, out = _tool("config", "--user", str(f), "--cwd", str(tmp_path))
    assert code == 0, out["errors"]
    f.write_text("models:\n  order: [my-big, my-small]\n  tiers:\n    codex: {strong: my-small, standard: my-big, fast: ''}\n")
    code, out = _tool("config", "--user", str(f), "--cwd", str(tmp_path))
    assert code == 1


def test_versions_agree_and_changelog_names_the_current_one():
    version = json.loads((ROOT / "plugin.json").read_text())["version"]
    py = re.search(r'^version = "([^"]+)"', (ROOT / "pyproject.toml").read_text(), re.M).group(1)
    assert py == version
    first = re.search(r"^## (\S+)", (ROOT / "CHANGELOG.md").read_text(), re.M).group(1)
    assert first == version, "add a CHANGELOG.md entry for the new version"
    market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text())
    assert market["plugins"][0]["version"] == version
