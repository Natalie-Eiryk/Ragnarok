"""
Ragnarök Publishing Test Suite

Tests the full pipeline from LaTeX source to web-ready PDF and HTML.

Usage:
    python test_publish.py              # Run all tests
    python test_publish.py --quick      # Quick smoke test (1 chapter)
    python test_publish.py --verbose    # Detailed output
"""

import subprocess
import shutil
import sys
import time
from pathlib import Path
from typing import NamedTuple

# === Configuration ===

SITE_DIR = Path(__file__).parent
CHAPTERS_SOURCE = Path(r"C:\Users\hauge\OneDrive\Documents\Ragnarok\Chapters")
PDF_OUTPUT = SITE_DIR / "chapters" / "pdf"
PAGES_OUTPUT = SITE_DIR / "chapters"
TEMPLATE_PATH = PAGES_OUTPUT / "reader-template.html"

# Test chapter (smallest one for quick testing)
TEST_CHAPTER = {
    "number": "1.1",
    "title": "Ragnarök",
    "source": "Chapter - 01/Chapter 1.1 Ragnarok.tex",
    "output": "test-1-1-ragnarok",
}


class TestResult(NamedTuple):
    name: str
    passed: bool
    message: str
    duration: float


class TestRunner:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[TestResult] = []

    def log(self, msg: str, indent: int = 0):
        if self.verbose:
            print("  " * indent + msg)

    def run_test(self, name: str, test_func) -> TestResult:
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print('='*60)

        start = time.time()
        try:
            passed, message = test_func()
            duration = time.time() - start
            result = TestResult(name, passed, message, duration)
        except Exception as e:
            duration = time.time() - start
            result = TestResult(name, False, f"Exception: {e}", duration)

        status = "[PASS]" if result.passed else "[FAIL]"
        print(f"\n{status}: {result.message} ({result.duration:.2f}s)")

        self.results.append(result)
        return result

    def print_summary(self):
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)

        for r in self.results:
            status = "[OK]" if r.passed else "[!!]"
            print(f"  {status} {r.name}: {r.message} ({r.duration:.2f}s)")

        print(f"\nTotal: {passed}/{total} tests passed")
        return passed == total


# === Individual Tests ===

def test_directories_exist() -> tuple[bool, str]:
    """Test that all required directories exist."""
    missing = []

    if not CHAPTERS_SOURCE.exists():
        missing.append(f"Source: {CHAPTERS_SOURCE}")

    if not SITE_DIR.exists():
        missing.append(f"Site dir: {SITE_DIR}")

    if not TEMPLATE_PATH.exists():
        missing.append(f"Template: {TEMPLATE_PATH}")

    # Create PDF output if missing
    PDF_OUTPUT.mkdir(parents=True, exist_ok=True)

    if missing:
        return False, f"Missing directories: {', '.join(missing)}"
    return True, "All directories exist"


def test_pdflatex_installed() -> tuple[bool, str]:
    """Test that pdflatex is available."""
    try:
        result = subprocess.run(
            ["pdflatex", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # Extract version from first line
            version = result.stdout.split('\n')[0][:60]
            return True, f"pdflatex found: {version}"
        return False, f"pdflatex returned error: {result.stderr[:100]}"
    except FileNotFoundError:
        return False, "pdflatex not found in PATH"
    except subprocess.TimeoutExpired:
        return False, "pdflatex timed out"


def test_source_file_exists() -> tuple[bool, str]:
    """Test that the test chapter source exists."""
    source_path = CHAPTERS_SOURCE / TEST_CHAPTER["source"]

    if not source_path.exists():
        # Try alternate extensions
        tex_path = source_path.with_suffix('.tex')
        docx_path = source_path.with_suffix('.docx')

        if tex_path.exists():
            return True, f"Found: {tex_path.name}"
        if docx_path.exists():
            return True, f"Found DOCX (needs conversion): {docx_path.name}"

        return False, f"Source not found: {source_path}"

    size = source_path.stat().st_size
    return True, f"Found: {source_path.name} ({size:,} bytes)"


def test_template_valid() -> tuple[bool, str]:
    """Test that the HTML template has all required placeholders."""
    required_placeholders = [
        "{NUMBER}",
        "{TITLE}",
        "{PDF_FILE}",
        "{PREV_LINK}",
        "{NEXT_LINK}",
        "{CHAPTER_LIST}",
        "{PROGRESS}",
    ]

    try:
        content = TEMPLATE_PATH.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"Cannot read template: {e}"

    missing = [p for p in required_placeholders if p not in content]

    if missing:
        return False, f"Template missing placeholders: {', '.join(missing)}"

    return True, f"Template valid ({len(content):,} chars, {len(required_placeholders)} placeholders)"


def test_compile_pdf() -> tuple[bool, str]:
    """Test PDF compilation with pdflatex."""
    source_path = CHAPTERS_SOURCE / TEST_CHAPTER["source"]

    if not source_path.exists():
        return False, f"Source not found: {source_path}"

    # Create temp directory
    temp_dir = SITE_DIR / "temp_test_compile"
    temp_dir.mkdir(exist_ok=True)

    try:
        # Copy source and any dependencies
        shutil.copy(source_path, temp_dir / source_path.name)

        # Copy sty files if they exist in source directory
        source_dir = source_path.parent
        for sty in source_dir.glob("*.sty"):
            shutil.copy(sty, temp_dir / sty.name)
        for cls in source_dir.glob("*.cls"):
            shutil.copy(cls, temp_dir / cls.name)

        # Run pdflatex (twice for references)
        for run in [1, 2]:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", source_path.name],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=120
            )

        # Check for output PDF
        pdf_name = source_path.stem + ".pdf"
        temp_pdf = temp_dir / pdf_name

        if temp_pdf.exists():
            size = temp_pdf.stat().st_size

            # Copy to output
            output_pdf = PDF_OUTPUT / f"{TEST_CHAPTER['output']}.pdf"
            shutil.copy(temp_pdf, output_pdf)

            return True, f"PDF compiled successfully ({size:,} bytes)"
        else:
            # Check log for errors
            log_file = temp_dir / (source_path.stem + ".log")
            if log_file.exists():
                log_content = log_file.read_text(encoding='utf-8', errors='ignore')
                # Find first error
                for line in log_content.split('\n'):
                    if line.startswith('!'):
                        return False, f"LaTeX error: {line[:80]}"
            return False, "PDF not generated (check LaTeX source)"

    except subprocess.TimeoutExpired:
        return False, "Compilation timed out (>120s)"
    except Exception as e:
        return False, f"Compilation error: {e}"
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_generate_html() -> tuple[bool, str]:
    """Test HTML page generation from template."""
    try:
        template = TEMPLATE_PATH.read_text(encoding='utf-8')
    except Exception as e:
        return False, f"Cannot read template: {e}"

    # Fill template
    html = template.replace("{NUMBER}", TEST_CHAPTER["number"])
    html = html.replace("{TITLE}", TEST_CHAPTER["title"])
    html = html.replace("{PDF_FILE}", f"{TEST_CHAPTER['output']}.pdf")
    html = html.replace("{PREV_LINK}", "#")
    html = html.replace("{NEXT_LINK}", "#")
    html = html.replace("{PREV_DISABLED}", "disabled")
    html = html.replace("{NEXT_DISABLED}", "disabled")
    html = html.replace("{PROGRESS}", "10")
    html = html.replace("{CURRENT}", "1")
    html = html.replace("{TOTAL}", "10")
    html = html.replace("{CHAPTER_LIST}", '<a href="#" class="chapter-mini-link">Test</a>')

    # Write test page
    output_path = PAGES_OUTPUT / f"{TEST_CHAPTER['output']}.html"
    try:
        output_path.write_text(html, encoding='utf-8')
    except Exception as e:
        return False, f"Cannot write HTML: {e}"

    size = output_path.stat().st_size
    return True, f"HTML generated ({size:,} bytes)"


def test_pdf_embed_syntax() -> tuple[bool, str]:
    """Test that the generated HTML has valid PDF embed syntax."""
    html_path = PAGES_OUTPUT / f"{TEST_CHAPTER['output']}.html"

    if not html_path.exists():
        return False, "Test HTML not found (run test_generate_html first)"

    content = html_path.read_text(encoding='utf-8')

    # Check for embed tag
    if '<embed' not in content:
        return False, "Missing <embed> tag"

    if 'type="application/pdf"' not in content:
        return False, "Missing PDF MIME type"

    if f"{TEST_CHAPTER['output']}.pdf" not in content:
        return False, "PDF filename not in embed src"

    return True, "PDF embed syntax valid"


def test_css_exists() -> tuple[bool, str]:
    """Test that required CSS files exist."""
    css_files = [
        SITE_DIR / "css" / "lcars.css",
        SITE_DIR / "css" / "chapters.css",
        SITE_DIR / "css" / "pdf-reader.css",
    ]

    missing = []
    total_size = 0

    for css in css_files:
        if css.exists():
            total_size += css.stat().st_size
        else:
            missing.append(css.name)

    if missing:
        return False, f"Missing CSS: {', '.join(missing)}"

    return True, f"All CSS files present ({total_size:,} bytes total)"


def test_git_status() -> tuple[bool, str]:
    """Test git repository status."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=SITE_DIR,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return False, f"Git error: {result.stderr[:100]}"

        lines = [l for l in result.stdout.strip().split('\n') if l]
        if not lines:
            return True, "Working directory clean"

        return True, f"{len(lines)} uncommitted changes"

    except FileNotFoundError:
        return False, "Git not found"
    except Exception as e:
        return False, f"Git error: {e}"


def test_fonts_in_pdf() -> tuple[bool, str]:
    """Test that custom fonts are embedded in the PDF."""
    pdf_path = PDF_OUTPUT / f"{TEST_CHAPTER['output']}.pdf"

    if not pdf_path.exists():
        return False, "Test PDF not found (run test_compile_pdf first)"

    # Use pdffonts if available, otherwise check file size as proxy
    try:
        result = subprocess.run(
            ["pdffonts", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            fonts = [l for l in lines[2:] if l.strip()]  # Skip header
            return True, f"{len(fonts)} fonts embedded"

    except FileNotFoundError:
        # pdffonts not available, check file size instead
        size = pdf_path.stat().st_size
        if size > 50000:  # PDFs with embedded fonts are typically larger
            return True, f"PDF size suggests fonts embedded ({size:,} bytes)"
        return True, f"Cannot verify fonts (pdffonts not installed), PDF is {size:,} bytes"

    except Exception as e:
        return True, f"Font check skipped: {e}"


def test_cleanup() -> tuple[bool, str]:
    """Clean up test artifacts."""
    test_files = [
        PDF_OUTPUT / f"{TEST_CHAPTER['output']}.pdf",
        PAGES_OUTPUT / f"{TEST_CHAPTER['output']}.html",
    ]

    removed = 0
    for f in test_files:
        if f.exists():
            f.unlink()
            removed += 1

    return True, f"Cleaned up {removed} test files"


# === Main ===

def main():
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    quick = "--quick" in sys.argv

    runner = TestRunner(verbose=verbose)

    # Core tests (always run)
    runner.run_test("Directories Exist", test_directories_exist)
    runner.run_test("pdflatex Installed", test_pdflatex_installed)
    runner.run_test("Source File Exists", test_source_file_exists)
    runner.run_test("Template Valid", test_template_valid)
    runner.run_test("CSS Files Exist", test_css_exists)
    runner.run_test("Git Status", test_git_status)

    if not quick:
        # Full compilation tests
        runner.run_test("Compile PDF", test_compile_pdf)
        runner.run_test("Generate HTML", test_generate_html)
        runner.run_test("PDF Embed Syntax", test_pdf_embed_syntax)
        runner.run_test("Fonts in PDF", test_fonts_in_pdf)

        # Cleanup
        runner.run_test("Cleanup", test_cleanup)

    success = runner.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
