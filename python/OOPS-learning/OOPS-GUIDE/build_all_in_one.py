from __future__ import annotations

import ast
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import runpy
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = PROJECT_ROOT / "_document_build"
ASSET_ROOT = BUILD_ROOT / "generated_assets"
TARGET_DOCX = PROJECT_ROOT / "Python_OOP_All_In_One_Complete_Guide.docx"
INVENTORY_JSON = BUILD_ROOT / "source_inventory.json"
INVENTORY_MD = BUILD_ROOT / "source_inventory.md"
SOURCE_GUIDE_GENERATOR = PROJECT_ROOT.parent / "scripts" / "generate_oop_book.py"
SVG_INPUT = PROJECT_ROOT / "python_class_object_infographic.svg"
SVG_PREVIEW = ASSET_ROOT / "original_class_object_infographic.png"
REDRAWN_PREVIEW = ASSET_ROOT / "refined_class_object_infographic.png"
NAVY = "15324B"
TEAL = "168C8C"
ORANGE = "E99838"
INK = "263746"


SOURCE_NOTES = {
    "class_1.py": (
        "A Student class with name, age, and course values, followed by creation of one instance and attribute reads.",
        "The values are class attributes because they are assigned in the class body. Every instance can see them; they are not separately initialized for each student. `int(16)` is valid but unnecessary; `16` is already an integer.",
        "Chapter 3: attributes and object state; source-material appendix.",
    ),
    "class-2.py": (
        "A Student instance method that prints a greeting and the supplied name and age.",
        "The first parameter `xyz` receives the instance when the method is called through `s.studentdetails(...)`. `self` is the conventional clearer name, not a keyword. The example receives values as parameters but does not store them on the object.",
        "Chapter 5: self and bound methods; source-material appendix.",
    ),
    "class-3.py": (
        "A Car class with class-level name/color data and an instance method that prints a speed and reads attributes through self.",
        "`self.name` and `self.color` find the values through the instance (and then the class if no instance value shadows them). The speed is hard-coded behavior in this example, not a stored per-car speed.",
        "Chapters 2–3: classes, objects, attributes, and methods; source-material appendix.",
    ),
    "class-4.py": (
        "A Car class with shared name/color, an initializer that prints those values and a speed message, and a separate method that prints another message.",
        "`__init__` is called automatically to initialize a newly created instance; it is not technically the method that creates the object. Printing in an initializer is possible, though initializing attributes is usually more reusable than printing there.",
        "Chapter 4: initialization; source-material appendix.",
    ),
    "class-5.py": (
        "Two Car objects receive different name, color, and speed values; display prints each object's values.",
        "Each assignment such as `self.name = name` creates instance state. The speed values mix an integer (`200`) and a string (`'100kmph'`); consistent numeric units are easier to calculate and validate.",
        "Chapters 2–5: instance state, __init__, and self; source-material appendix.",
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def render_svg_with_browser() -> None:
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    if not SVG_INPUT.exists():
        raise FileNotFoundError(f"Expected source infographic missing: {SVG_INPUT}")
    ET.parse(SVG_INPUT)
    browser_candidates = [
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"))
        / "Microsoft" / "Edge" / "Application" / "msedge.exe",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
        / "Google" / "Chrome" / "Application" / "chrome.exe",
    ]
    browser = next((candidate for candidate in browser_candidates if candidate.exists()), None)
    if browser is None:
        raise RuntimeError("No supported local Chromium browser was found to render the existing SVG.")

    profile = ASSET_ROOT / "headless_browser_profile"
    url = SVG_INPUT.as_uri()
    command = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        f"--user-data-dir={profile}",
        "--window-size=1800,1200",
        "--force-device-scale-factor=1",
        f"--screenshot={SVG_PREVIEW}",
        url,
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=90, check=False)
    for _ in range(40):
        if SVG_PREVIEW.exists() and SVG_PREVIEW.stat().st_size > 10_000:
            break
        time.sleep(0.25)
    if result.returncode != 0 or not SVG_PREVIEW.exists() or SVG_PREVIEW.stat().st_size < 10_000:
        raise RuntimeError(
            "The browser could not render the source SVG. "
            f"exit={result.returncode}; stderr={result.stderr[-2000:]}"
        )


def create_refined_infographic() -> None:
    fig, ax = plt.subplots(figsize=(11, 7.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")
    fig.patch.set_facecolor("#F5F8FA")
    ax.set_facecolor("#F5F8FA")
    ax.text(6, 7.45, "PYTHON CLASSES & OBJECTS", ha="center", va="center",
            fontsize=22, weight="bold", color=f"#{NAVY}")
    ax.text(6, 7.0, "A class describes a kind; each object stores its own values.",
            ha="center", va="center", fontsize=12, color=f"#{INK}")

    def panel(x, y, width, height, title, edge):
        shape = FancyBboxPatch((x, y), width, height,
                               boxstyle="round,pad=0.12,rounding_size=0.18",
                               facecolor="white", edgecolor=edge, linewidth=2)
        ax.add_patch(shape)
        ax.text(x + width / 2, y + height - 0.42, title,
                ha="center", va="center", fontsize=15, weight="bold", color=f"#{NAVY}")

    panel(0.5, 2.55, 4.25, 3.8, "CLASS: Car", f"#{TEAL}")
    panel(7.25, 4.25, 4.25, 2.1, "OBJECT: car1", f"#{ORANGE}")
    panel(7.25, 1.5, 4.25, 2.1, "OBJECT: car2", f"#{ORANGE}")

    ax.text(0.95, 5.25, "Describes available data and behavior:",
            fontsize=10, color=f"#{INK}")
    ax.text(1.15, 4.6, "Attributes: brand, year",
            fontsize=12, weight="bold", color=f"#{TEAL}")
    ax.text(1.15, 4.1, "Method: drive()",
            fontsize=12, weight="bold", color=f"#{TEAL}")
    ax.text(1.15, 3.42, "class Car:", fontsize=11, family="monospace", color=f"#{NAVY}")
    ax.text(1.15, 3.05, "    def __init__(self, brand, year):",
            fontsize=9.6, family="monospace", color=f"#{NAVY}")
    ax.text(1.15, 2.72, "        self.brand = brand",
            fontsize=9.6, family="monospace", color=f"#{NAVY}")

    for x, y, brand, year in [
        (7.7, 4.25, "BMW", "2025"),
        (7.7, 1.5, "Tesla", "2024"),
    ]:
        ax.text(x, y + 1.05, f"brand = {brand!r}",
                fontsize=12, color=f"#{INK}")
        ax.text(x, y + 0.62, f"year = {year}",
                fontsize=12, color=f"#{INK}")
        ax.text(x, y + 0.22, "car.drive() uses this object's data",
                fontsize=9.5, color=f"#{INK}")

    ax.annotate("creates independent instances",
                xy=(7.15, 4.6), xytext=(4.95, 5.9),
                arrowprops={"arrowstyle": "->", "lw": 1.8, "color": f"#{TEAL}"},
                fontsize=10, ha="center", color=f"#{TEAL}")
    ax.annotate("", xy=(7.15, 2.5), xytext=(5.0, 3.25),
                arrowprops={"arrowstyle": "->", "lw": 1.8, "color": f"#{ORANGE}"})

    reminder = FancyBboxPatch((1.0, 0.35), 10.0, 0.65,
                              boxstyle="round,pad=0.08,rounding_size=0.14",
                              facecolor=f"#{NAVY}", edgecolor=f"#{NAVY}")
    ax.add_patch(reminder)
    ax.text(6, 0.67, "MEMORY: Class = blueprint  •  Object = one instance with its own state",
            ha="center", va="center", fontsize=12, weight="bold", color="white")
    fig.tight_layout()
    fig.savefig(REDRAWN_PREVIEW, dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def load_textbook_generator():
    if not SOURCE_GUIDE_GENERATOR.exists():
        raise FileNotFoundError(
            "The existing complete textbook generator used as supplemental curriculum "
            f"was not found: {SOURCE_GUIDE_GENERATOR}"
        )
    spec = importlib.util.spec_from_file_location("existing_oop_textbook_generator", SOURCE_GUIDE_GENERATOR)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load the existing textbook generator: {SOURCE_GUIDE_GENERATOR}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    module.ROOT = PROJECT_ROOT
    module.OUT = ASSET_ROOT
    module.ASSETS = ASSET_ROOT / "textbook_diagrams"
    module.DOCX_PATH = TARGET_DOCX
    return module


def execute_source(path: Path) -> tuple[str, str]:
    source = path.read_text(encoding="utf-8")
    ast.parse(source, filename=str(path))
    output = io.StringIO()
    with contextlib.redirect_stdout(output):
        runpy.run_path(str(path), run_name="__main__")
    return source, output.getvalue().rstrip()


def add_source_material(doc: Document, generator, original_files: list[Path]) -> None:
    doc.add_page_break()
    generator.add_heading(doc, "Appendix A — Your Original OOP Learning Files", 1)
    generator.add_body(
        doc,
        "This appendix preserves the five original Python lesson files as code listings and records the output obtained by running each file in the local Python environment. The source code is shown as found; the teaching notes immediately after each listing explain terminology and correct misconceptions without silently rewriting the originals.",
    )
    generator.add_callout(
        doc,
        "SOURCE PRESERVATION",
        "The original files were read and executed, not edited. The code blocks below retain their source text; explanations clarify how Python evaluates it.",
    )

    for path in original_files:
        source, actual_output = execute_source(path)
        purpose, explanation, chapters = SOURCE_NOTES.get(
            path.name,
            ("Python learning material.", "See the surrounding explanation for context.", "Appendix."),
        )
        generator.add_heading(doc, f"Original file: {path.name}", 2)
        generator.add_body(doc, f"Original location: {path.relative_to(PROJECT_ROOT)}")
        generator.add_body(doc, f"What it teaches: {purpose}")
        generator.add_code(doc, source.rstrip(), "ORIGINAL SOURCE — PRESERVED")
        generator.add_heading(doc, "Actual output", 3)
        generator.add_code(doc, actual_output or "(No standard output)", "CAPTURED WHEN EXECUTED")
        generator.add_callout(doc, "EXPLANATION AND ACCURACY NOTE", explanation, ORANGE)
        generator.add_body(doc, f"Incorporated into: {chapters}")

    doc.add_page_break()
    generator.add_heading(doc, "Improved versions of the original lessons", 2)
    generator.add_body(
        doc,
        "These small programs keep the original examples' familiar Student and Car ideas while demonstrating the more reusable pattern: create instance data in __init__, keep data types consistent, and return values when a caller needs to reuse a result.",
    )
    improved = [
        (
            "Student records with per-object attributes",
            """class Student:
    def __init__(self, name, age, course):
        self.name = name
        self.age = age
        self.course = course

    def summary(self):
        return f"{self.name}, age {self.age}, studies {self.course}"


first = Student("Chaithanya", 16, "Diploma-CSE")
second = Student("Abhi", 16, "Diploma-CSE")
print(first.summary())
print(second.summary())
print(first is second)""",
            "Chaithanya, age 16, studies Diploma-CSE\nAbhi, age 16, studies Diploma-CSE\nFalse",
            "Both objects use one class definition but have independent instance attributes. `is` checks that the objects are distinct.",
        ),
        (
            "Cars with consistent speed values and reusable behavior",
            """class Car:
    def __init__(self, name, color, speed_kmph):
        if speed_kmph < 0:
            raise ValueError("speed cannot be negative")
        self.name = name
        self.color = color
        self.speed_kmph = speed_kmph

    def display(self):
        return f"{self.name} ({self.color}) — {self.speed_kmph} km/h"


first = Car("RR", "Blue", 200)
second = Car("BMW", "Red", 100)
print(first.display())
print(second.display())""",
            "RR (Blue) — 200 km/h\nBMW (Red) — 100 km/h",
            "The speed is a number for both cars, making comparison and arithmetic possible. The display method formats it for people. Validation rejects an impossible negative speed.",
        ),
    ]
    for title, code, expected, note in improved:
        generator.add_heading(doc, title, 3)
        generator.add_code(doc, code)
        generator.add_code(doc, expected, "EXPECTED OUTPUT")
        generator.add_body(doc, note)
        compile(code, title, "exec")
        actual = io.StringIO()
        with contextlib.redirect_stdout(actual):
            exec(compile(code, title, "exec"), {"__name__": "__main__"})
        if actual.getvalue().strip() != expected.strip():
            raise AssertionError(f"Output mismatch in improved source example: {title}")

    doc.add_page_break()
    generator.add_heading(doc, "Appendix B — Original Class and Object Infographic", 1)
    generator.add_body(
        doc,
        "The following image is rendered from the SVG infographic already present in OOPS-learning. It summarizes class as a blueprint and objects as instances with their own state. The printed code example is an introductory illustration; the full guide explains these ideas in greater detail.",
    )
    generator.add_heading(doc, "Clear, print-ready summary based on the original topics", 2)
    image_paragraph = doc.add_paragraph()
    image_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    image_paragraph.add_run().add_picture(str(REDRAWN_PREVIEW), width=Inches(6.2))
    caption = doc.add_paragraph(
        "Figure B.1 — Newly redrawn class/object diagram using the ideas in the original project infographic."
    )
    caption.style = doc.styles["Caption"]
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    generator.add_heading(doc, "Original source artwork, rendered without editing the source file", 2)
    image_paragraph = doc.add_paragraph()
    image_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    image_paragraph.add_run().add_picture(str(SVG_PREVIEW), width=Inches(5.6))
    caption = doc.add_paragraph(
        "Figure B.2 — Existing `python_class_object_infographic.svg`, embedded as a local PNG rendering."
    )
    caption.style = doc.styles["Caption"]
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    generator.add_callout(
        doc,
        "EDITORIAL NOTE",
        "The original illustration is preserved. In its rendered layout, some connector labels overlap the panels and the code line reaches the panel edge. The redrawn version above keeps the original class/object message while presenting a cleaner print layout. Also, self is a conventional method parameter representing the current instance; it is not a separate class attribute.",
        ORANGE,
    )

    doc.add_page_break()
    generator.add_heading(doc, "Appendix C — Source Material Crosswalk", 1)
    rows = [
        ("class_1.py", "Student class attributes and reading values", "Classes/objects; attributes vs instance state"),
        ("class-2.py", "Instance method and its first argument", "self; bound methods; method parameters"),
        ("class-3.py", "Car method and attribute access", "Methods; attributes; self"),
        ("class-4.py", "Automatic initializer execution", "__init__; initialization versus object creation"),
        ("class-5.py", "Two Car instances with different values", "Instance attributes; independent object state; data consistency"),
        ("python_class_object_infographic.svg", "Visual comparison of class blueprint and objects", "Class/object diagram, attributes, methods, self, memory cues"),
    ]
    table = doc.add_table(rows=1, cols=3)
    table.style = "Light Shading Accent 1"
    table.alignment = 1
    for cell, title in zip(table.rows[0].cells, ["Original file", "Content found", "Where included"]):
        cell.text = title
        for run in cell.paragraphs[0].runs:
            run.bold = True
            run.font.color.rgb = RGBColor.from_string("FFFFFF")
        tc_pr = cell._tc.get_or_add_tcPr()
        shading = OxmlElement("w:shd")
        shading.set(qn("w:fill"), NAVY)
        tc_pr.append(shading)
    for row in rows:
        cells = table.add_row().cells
        for cell, value in zip(cells, row):
            cell.text = value
            cell.vertical_alignment = 1


def write_inventory(input_files: list[Path], failures: list[dict], validation: dict) -> None:
    records = []
    for path in input_files:
        try:
            relative = str(path.relative_to(PROJECT_ROOT))
            suffix = path.suffix.lower()
            if suffix == ".py":
                source = path.read_text(encoding="utf-8")
                ast.parse(source, filename=str(path))
                records.append({
                    "path": relative,
                    "type": "Python source",
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "inspected": True,
                    "incorporated": True,
                    "incorporation": "Verbatim source listing, captured actual output, explanation, and corrected teaching example.",
                })
            elif suffix == ".svg":
                ET.parse(path)
                records.append({
                    "path": relative,
                    "type": "SVG infographic",
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "inspected": True,
                    "incorporated": True,
                    "incorporation": "Rendered to PNG and embedded; cited in infographic appendix.",
                })
            else:
                records.append({
                    "path": relative,
                    "type": suffix or "file",
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                    "inspected": True,
                    "incorporated": False,
                    "incorporation": "No relevant content handler was required for this file type.",
                })
        except Exception as error:
            failures.append({"path": str(path), "reason": f"{type(error).__name__}: {error}"})
            records.append({
                "path": str(path),
                "type": path.suffix.lower(),
                "inspected": False,
                "incorporated": False,
                "failure": f"{type(error).__name__}: {error}",
            })

    manifest = {
        "project_root": str(PROJECT_ROOT),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "deliverable": str(TARGET_DOCX),
        "files_discovered_at_initial_inspection": records,
        "file_count": len(input_files),
        "inspection_failures": failures,
        "supplemental_curriculum": {
            "source": str(SOURCE_GUIDE_GENERATOR),
            "note": "The complete 23-chapter beginner-to-intermediate curriculum was reused as supplemental editorial material. This generator is outside OOPS-learning and is not counted among the original project-folder inputs.",
        },
        "new_material_added": [
            "Verbatim source listings and captured output for the five original Python lessons.",
            "Accuracy notes distinguishing class attributes from instance attributes, self convention, and __init__ initialization.",
            "Improved Student and Car examples based on original project topics, with executed outputs.",
            "Rendered original SVG infographic embedded in the DOCX.",
            "Source crosswalk and this auditable manifest.",
        ],
        "validation": validation,
    }
    INVENTORY_JSON.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# OOPS-learning source inventory and build manifest",
        "",
        f"- Project: `{PROJECT_ROOT}`",
        f"- Output: `{TARGET_DOCX}`",
        f"- Discovered source files: {len(records)}",
        f"- Inspection failures: {len(failures)}",
        "",
        "## Discovered files",
        "",
        "| File | Type | Inspected | Incorporated | SHA-256 |",
        "|---|---|---:|---:|---|",
    ]
    for item in records:
        lines.append(
            f"| `{item['path']}` | {item['type']} | {item['inspected']} | "
            f"{item['incorporated']} | `{item.get('sha256', 'unavailable')}` |"
        )
        if item.get("incorporation"):
            lines.append(f"\n  - {item['incorporation']}")
    lines.extend([
        "",
        "## Processing notes",
        "",
        "- Every original `.py` file was parsed, read in full, and executed; its original output is recorded in the DOCX.",
        "- The original SVG was parsed as XML and rendered locally using Microsoft Edge before embedding.",
        "- No original file was modified, renamed, moved, or deleted.",
        "- The comprehensive curriculum also reuses an existing generator at "
        f"`{SOURCE_GUIDE_GENERATOR}`. That generator is outside the specified project folder; it is supplemental content, not a discovered source file.",
        "- The prior complete guide supplies the beginner-to-intermediate chapter material; the original project examples and infographic are preserved in appendices and cross-referenced.",
        "",
        "## Validation",
        "",
    ])
    for key, value in validation.items():
        lines.append(f"- **{key}:** {value}")
    if failures:
        lines.extend(["", "## Files that could not be processed", ""])
        lines.extend(f"- `{item['path']}` — {item['reason']}" for item in failures)
    else:
        lines.extend(["", "## Files that could not be processed", "", "- None."])
    INVENTORY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_final(generator, input_files: list[Path]) -> dict:
    if not TARGET_DOCX.exists():
        raise FileNotFoundError(f"Final DOCX was not created: {TARGET_DOCX}")
    reopened = Document(TARGET_DOCX)
    text = "\n".join(p.text for p in reopened.paragraphs)
    text += "\n" + "\n".join(
        cell.text for table in reopened.tables for row in table.rows for cell in row.cells
    )
    source_file_names = [path.name for path in input_files]
    required = [
        "Introduction to Programming and OOP",
        "Chapter 23: Final Master Revision Guide",
        "Appendix A — Your Original OOP Learning Files",
        "Appendix B — Original Class and Object Infographic",
        "Appendix C — Source Material Crosswalk",
        "class_1.py",
        "class-2.py",
        "class-3.py",
        "class-4.py",
        "class-5.py",
        "EXPLANATION AND ACCURACY NOTE",
        "ORIGINAL SOURCE — PRESERVED",
    ]
    missing = [marker for marker in required if marker not in text]
    if missing:
        raise AssertionError(f"Required source/curriculum text missing from DOCX: {missing}")
    for name in source_file_names:
        if name not in text:
            raise AssertionError(f"Discovered project file was not mentioned in DOCX: {name}")
    if not any(shape.width > 0 for shape in reopened.inline_shapes):
        raise AssertionError("No diagrams or images were embedded.")
    if len(reopened.tables) < 10:
        raise AssertionError("Expected textbook tables and source crosswalk not found.")
    if len(text.split()) < 20_000:
        raise AssertionError("Consolidated guide is unexpectedly short.")
    for placeholder in ["TODO", "PLACEHOLDER", "INSERT TEXT HERE"]:
        if placeholder in text.upper():
            raise AssertionError(f"Placeholder text found: {placeholder}")
    for number in range(1, 24):
        if f"Chapter {number}:" not in text:
            raise AssertionError(f"Missing chapter {number} heading.")

    from zipfile import ZipFile

    with ZipFile(TARGET_DOCX) as archive:
        corrupt_member = archive.testzip()
        if corrupt_member:
            raise AssertionError(f"Corrupt DOCX zip member: {corrupt_member}")
        media = [name for name in archive.namelist() if name.startswith("word/media/")]
        xml = archive.read("word/document.xml").decode("utf-8")
        if "TOC" not in xml:
            raise AssertionError("Table-of-contents field not found.")
        if len(media) < 10:
            raise AssertionError(f"Too few embedded diagram files: {len(media)}")

    return {
        "docx_exists": True,
        "docx_bytes": TARGET_DOCX.stat().st_size,
        "reopened_with_python_docx": True,
        "zip_integrity": True,
        "paragraphs": len(reopened.paragraphs),
        "tables": len(reopened.tables),
        "embedded_image_instances": len(reopened.inline_shapes),
        "unique_embedded_media": len(media),
        "word_count": len(text.split()),
        "chapter_headings_present": 23,
        "original_files_incorporated": len(input_files),
        "original_svg_embedded": True,
        "toc_field_present": True,
        "placeholder_scan": "passed",
        "visual_pdf_rendering": "unavailable: no Word/LibreOffice executable detected",
    }


def main() -> None:
    if TARGET_DOCX.exists():
        previous = Document(TARGET_DOCX)
        previous_text = "\n".join(paragraph.text for paragraph in previous.paragraphs)
        if "Appendix A — Your Original OOP Learning Files" not in previous_text:
            raise FileExistsError(
                f"Target exists and does not appear to be this builder's prior output: {TARGET_DOCX}"
            )
        backup_directory = BUILD_ROOT / "backups"
        backup_directory.mkdir(parents=True, exist_ok=True)
        backup = backup_directory / "Python_OOP_All_In_One_Complete_Guide.previous.docx"
        if backup.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup = backup_directory / f"Python_OOP_All_In_One_Complete_Guide.{timestamp}.docx"
        shutil.copy2(TARGET_DOCX, backup)
        print(f"Backed up prior generated output: {backup}")
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    ASSET_ROOT.mkdir(parents=True, exist_ok=True)
    input_files = sorted(
        path for path in PROJECT_ROOT.rglob("*")
        if path.is_file()
        and BUILD_ROOT not in path.parents
        and path != TARGET_DOCX
        and path.suffix.lower() in {
            ".py", ".md", ".txt", ".docx", ".pdf", ".html", ".htm",
            ".ipynb", ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".svg",
            ".webp", ".csv", ".json",
        }
    )
    python_files = [path for path in input_files if path.suffix.lower() == ".py"]
    svg_files = [path for path in input_files if path.suffix.lower() == ".svg"]
    failures: list[dict] = []

    for path in python_files:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            execute_source(path)
        except Exception as error:
            failures.append({"path": str(path), "reason": f"{type(error).__name__}: {error}"})
    for path in svg_files:
        try:
            ET.parse(path)
        except Exception as error:
            failures.append({"path": str(path), "reason": f"{type(error).__name__}: {error}"})
    if failures:
        raise RuntimeError(f"Some source material could not be processed: {failures}")

    render_svg_with_browser()
    create_refined_infographic()
    generator = load_textbook_generator()
    diagrams = generator.make_diagrams()
    code_examples = generator.verify_code_examples()
    project_checks = generator.verify_project_behavior()
    generator.build_doc(diagrams)

    doc = Document(TARGET_DOCX)
    add_source_material(doc, generator, python_files)
    doc.save(TARGET_DOCX)

    validation = verify_final(generator, input_files)
    validation.update({
        "existing_guide_examples_executed_and_output_checked": len(code_examples),
        "project_behavior_validation_suites_passed": project_checks,
        "original_python_files_executed": len(python_files),
        "original_svg_xml_parsed_and_browser_rendered": len(svg_files),
        "all_discovered_input_sha256_recorded": True,
        "pdf_rendering_available": False,
    })
    write_inventory(input_files, failures, validation)

    print(f"Final DOCX: {TARGET_DOCX}")
    print(f"Source files inspected and incorporated: {len(input_files)}")
    print(f"Python examples from complete guide verified: {len(code_examples)}")
    print(f"Project behavior suites passed: {project_checks}")
    print(f"Original Python lessons executed: {len(python_files)}")
    print(f"Embedded image instances: {validation['embedded_image_instances']}")
    print(f"Document bytes: {validation['docx_bytes']}")
    print(f"Manifest: {INVENTORY_MD}")
    print(f"PDF rendering: {validation['visual_pdf_rendering']}")


if __name__ == "__main__":
    main()
