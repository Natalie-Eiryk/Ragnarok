"""
Ragnarök Web Publisher

Compiles chapters via BookWriter (pdflatex) and generates
LCARS-styled reader pages for the website.

Usage:
    python publish_chapters.py              # Publish all chapters
    python publish_chapters.py 1.1 1.2      # Publish specific chapters
    python publish_chapters.py --list       # List available chapters
"""

import subprocess
import shutil
from pathlib import Path
from typing import Optional

# === Configuration ===

# BookWriter location (for pdflatex compilation)
BOOKWRITER_DIR = Path(r"F:\Lumi286\LUMI-OS\apps\lcars-next\src\components\bookwriter")

# Source chapter files (DOCX or TEX)
CHAPTERS_SOURCE = Path(r"C:\Users\hauge\OneDrive\Documents\Ragnarok\Chapters")

# Website output
SITE_DIR = Path(__file__).parent
PDF_OUTPUT = SITE_DIR / "chapters" / "pdf"
PAGES_OUTPUT = SITE_DIR / "chapters"

# Chapter definitions: (number, title, source_file, output_name)
CHAPTERS = [
    # Prologue
    ("0.4", "The Vision", "Chapter - 01/prologue-0-4.tex", "prologue-0-4"),
    ("0.5", "The Spectre", "Chapter - 01/prologue-0-5.tex", "prologue-0-5"),
    ("0.6", "Acceptance", "Chapter - 01/prologue-0-6.tex", "prologue-0-6"),
    # Chapter 1
    ("1.0", "Recursive Recursion", "Chapter - 01/Chapter 1.0 - Title Page.tex", "1-0-recursive-recursion"),
    ("1.1", "Ragnarök", "Chapter - 01/Chapter 1.1 Ragnarok.tex", "1-1-ragnarok"),
    ("1.2", "Stories of Yesteryear", "Chapter - 01/Chapter 1.2 Stories of Yesteryear.tex", "1-2-stories-of-yesteryear"),
    ("1.3", "Incoming", "Chapter - 01/Chapter 1.3 Incoming.tex", "1-3-incoming"),
    ("1.4", "Heinrikr", "Chapter - 01/Chapter 1.4 Heinrikr.tex", "1-4-heinrikr"),
    ("1.5", "The Bet", "Chapter - 01/Chapter 1.5 The Bet.tex", "1-5-the-bet"),
    ("1.6", "Reprieve", "Chapter - 01/Chapter 1.6 Reprieve.tex", "1-6-reprieve"),
    ("1.7", "Something New", "Chapter - 01/Chapter 1.7 - Something New.tex", "1-7-something-new"),
    ("1.8", "The Elder", "Chapter - 01/Chapter 1.8 - The Elder.tex", "1-8-the-elder"),
    ("1.9", "Aftermath", "Chapter - 01/Chapter 1.9 - Aftermath.tex", "1-9-aftermath"),
    ("1.10", "The Kárak", "Chapter - 01/Chapter 1.10 The Kárak.tex", "1-10-the-karak"),
    ("1.11", "In the Morning", "Chapter - 01/Chapter 1.11 Astrid.tex", "1-11-in-the-morning"),
    ("1.12", "New Beginnings", "Chapter - 01/Chapter 1.12 - New Beginnings.tex", "1-12-new-beginnings"),
    ("1.13", "New Horizons", "Chapter - 01/Chapter 1.13 - New Horizons.tex", "1-13-new-horizons"),
    ("1.14", "Work in Progress", "Chapter - 01/Chapter 1.14 - WiP.tex", "1-14-wip"),
    ("1.15", "The Truth Will Set You Free", "Chapter - 01/Chapter 1.15 - WiP.tex", "1-15-the-truth"),
    ("1.16", "Chapter 1.16", "Chapter - 01/Chapter 1.16.tex", "1-16"),
    # Chapter 2
    ("2.0", "A Shot in the Dark", "Chapter 2.0 Heinrikr vs The Cabin.tex", "2-0-shot-in-the-dark"),
    ("2.1", "The Name", "Chapter 2.1 - The Name.tex", "2-1-the-name"),
    ("2.2", "The Cabin", "Chapter 2.2.tex", "2-2-the-cabin"),
    ("2.3", "The Consequences", "Chapter 2.3.tex", "2-3-the-consequences"),
    ("2.7", "Chapter 2.7", "Chapter 2.7.tex", "2-7"),
    ("2.8", "Chapter 2.8", "Chapter 2.8.tex", "2-8"),
    ("2.9", "Chapter 2.9", "Chapter 2.9.tex", "2-9"),
    ("2.10", "Chapter 2.10", "Chapter 2.10.tex", "2-10"),
    ("2.11", "Chapter 2.11", "Chapter 2.11.tex", "2-11"),
    # Chapter 3
    ("3.0", "Chapter 3.0", "Chapter 3/3.0.tex", "3-0"),
    ("3.1", "Ælska", "Chapter 3/Chapter 3.1 - AElska.tex", "3-1-aelska"),
    # Chapter 4
    ("4.0", "Chapter 4.0", "4.0.tex", "4-0"),
    # Chapter 5
    ("5.0", "Chapter 5.0", "5.0.tex", "5-0"),
]


def read_template() -> str:
    """Read the HTML template."""
    template_path = PAGES_OUTPUT / "reader-template.html"
    return template_path.read_text(encoding='utf-8')


def generate_chapter_list_html(current_output: str) -> str:
    """Generate the sidebar chapter list HTML."""
    items = []
    for num, title, _, output in CHAPTERS:
        active = "active" if output == current_output else ""
        items.append(f'''                    <a href="{output}.html" class="chapter-mini-link {active}">
                        <span class="chapter-mini-num">{num}</span>
                        <span>{title}</span>
                    </a>''')
    return "\n".join(items)


def compile_chapter_pdf(source_file: str, output_name: str) -> Optional[Path]:
    """
    Compile a chapter to PDF using pdflatex.
    Returns the path to the generated PDF, or None on failure.
    """
    source_path = CHAPTERS_SOURCE / source_file

    # Check for .tex file
    if not source_path.exists():
        # Try without .tex extension variations
        print(f"  ! Source not found: {source_path}")
        return None

    print(f"  Compiling {source_file}...")

    # Create temp directory for compilation
    temp_dir = SITE_DIR / "temp_compile"
    temp_dir.mkdir(exist_ok=True)

    try:
        # Copy source to temp dir
        temp_source = temp_dir / source_path.name
        shutil.copy(source_path, temp_source)

        # Run pdflatex
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", temp_source.name],
            cwd=temp_dir,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Check for output PDF
        pdf_name = temp_source.stem + ".pdf"
        temp_pdf = temp_dir / pdf_name

        if temp_pdf.exists():
            # Move to output directory
            output_pdf = PDF_OUTPUT / f"{output_name}.pdf"
            shutil.move(temp_pdf, output_pdf)
            print(f"  + Generated: {output_pdf.name}")
            return output_pdf
        else:
            print(f"  ! Compilation failed for {source_file}")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")
            return None

    except subprocess.TimeoutExpired:
        print(f"  ! Timeout compiling {source_file}")
        return None
    except Exception as e:
        print(f"  ! Error: {e}")
        return None
    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)


def generate_reader_page(number: str, title: str, output_name: str, index: int) -> bool:
    """Generate the HTML reader page for a chapter."""
    template = read_template()

    # Calculate navigation
    prev_link = "#"
    next_link = "#"
    prev_disabled = "disabled"
    next_disabled = "disabled"

    if index > 0:
        prev_link = f"{CHAPTERS[index - 1][3]}.html"
        prev_disabled = ""
    if index < len(CHAPTERS) - 1:
        next_link = f"{CHAPTERS[index + 1][3]}.html"
        next_disabled = ""

    # Calculate progress
    progress = int((index + 1) / len(CHAPTERS) * 100)

    # Generate chapter list
    chapter_list = generate_chapter_list_html(output_name)

    # Fill template
    html = template.replace("{NUMBER}", number)
    html = html.replace("{TITLE}", title)
    html = html.replace("{PDF_FILE}", f"{output_name}.pdf")
    html = html.replace("{PREV_LINK}", prev_link)
    html = html.replace("{NEXT_LINK}", next_link)
    html = html.replace("{PREV_DISABLED}", prev_disabled)
    html = html.replace("{NEXT_DISABLED}", next_disabled)
    html = html.replace("{PROGRESS}", str(progress))
    html = html.replace("{CURRENT}", str(index + 1))
    html = html.replace("{TOTAL}", str(len(CHAPTERS)))
    html = html.replace("{CHAPTER_LIST}", chapter_list)

    # Write output
    output_path = PAGES_OUTPUT / f"{output_name}.html"
    output_path.write_text(html, encoding='utf-8')
    print(f"  + Created page: {output_name}.html")
    return True


def publish_chapter(number: str, title: str, source: str, output: str, index: int, compile_pdf: bool = True) -> bool:
    """Publish a single chapter (compile PDF + generate page)."""
    print(f"\n[{number}] {title}")

    # Check if PDF exists or needs compilation
    pdf_path = PDF_OUTPUT / f"{output}.pdf"

    if compile_pdf and not pdf_path.exists():
        compiled = compile_chapter_pdf(source, output)
        if not compiled:
            # Still generate page, but PDF won't load
            print(f"  ! Warning: PDF not available")

    # Generate the reader page
    generate_reader_page(number, title, output, index)
    return True


def update_chapter_index():
    """Update the main chapter index to link to new reader pages."""
    # This regenerates the index.html with links to PDF reader pages
    # For now, keep existing HTML-based chapters but we can switch them over
    print("\nChapter index would be updated here...")


def list_chapters():
    """List all available chapters."""
    print("\nAvailable chapters:")
    print("-" * 50)
    for num, title, source, output in CHAPTERS:
        source_path = CHAPTERS_SOURCE / source
        exists = "✓" if source_path.exists() else "✗"
        print(f"  {exists} [{num}] {title}")
        print(f"      Source: {source}")
    print()


def main():
    import sys

    PDF_OUTPUT.mkdir(parents=True, exist_ok=True)

    if "--list" in sys.argv:
        list_chapters()
        return

    # Determine which chapters to publish
    if len(sys.argv) > 1 and sys.argv[1] != "--list":
        # Publish specific chapters
        targets = sys.argv[1:]
        for i, (num, title, source, output) in enumerate(CHAPTERS):
            if num in targets or output in targets:
                publish_chapter(num, title, source, output, i)
    else:
        # Publish all chapters
        print("Publishing all Ragnarök chapters...")
        print(f"Source: {CHAPTERS_SOURCE}")
        print(f"Output: {SITE_DIR}")

        for i, (num, title, source, output) in enumerate(CHAPTERS):
            publish_chapter(num, title, source, output, i, compile_pdf=False)

    update_chapter_index()
    print("\nDone!")


if __name__ == "__main__":
    main()
