"""
Convert Ragnarök markdown chapters to HTML pages.
"""

import re
from pathlib import Path

# Source directory
SOURCE_DIR = Path(r"C:\Users\hauge\OneDrive\Documents\ChatGPT - School & Legal\Luminara\Cognition - 2025-03-30-2122hr\Cognition\Identity\Helpin_Natalie_with_stuff\Works of my mine and Natalie\Writing\Fiction\Ragnarok")

# Output directory
OUTPUT_DIR = Path(__file__).parent / "chapters"

# Chapter template
CHAPTER_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Ragnarök</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&family=Crimson+Text:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="../css/lcars.css">
    <link rel="stylesheet" href="../css/chapters.css">
</head>
<body class="chapter-reader">
    <div class="scanlines"></div>

    <!-- LCARS Header -->
    <header class="lcars-header">
        <div class="header-bar">
            <div class="header-elbow"></div>
            <a href="../index.html" class="header-home">RAGNARÖK</a>
            <div class="header-blocks">
                <span class="block orange"></span>
                <span class="block cyan"></span>
                <span class="block purple"></span>
            </div>
            <div class="header-spacer"></div>
            <a href="index.html" class="header-donate">CHAPTERS</a>
            <div class="header-end"></div>
        </div>
    </header>

    <main class="chapter-content">
        <div class="chapter-header">
            <span class="chapter-number">{number}</span>
            <h1 class="chapter-title">{title}</h1>
        </div>

        <article class="chapter-text">
{content}
        </article>

        <nav class="chapter-nav">
            <a href="{prev_link}" class="nav-link prev {prev_disabled}">← Previous</a>
            <a href="index.html" class="nav-link">Index</a>
            <a href="{next_link}" class="nav-link next {next_disabled}">Next →</a>
        </nav>
    </main>

    <!-- Footer -->
    <footer class="lcars-footer">
        <div class="footer-bar">
            <div class="footer-elbow"></div>
            <span class="footer-text">RAGNARÖK by Natalie Eiryk</span>
            <div class="footer-spacer"></div>
            <span class="footer-status">FREE TO READ</span>
            <div class="footer-end"></div>
        </div>
    </footer>
</body>
</html>
'''

# Chapter mapping
CHAPTERS = [
    # Prologue
    ("Prologue/0.4_____Heinrikr_vs._The_Vision.md", "prologue-0-4-the-vision.html", "0.4", "Heinrikr vs. The Vision"),
    ("Prologue/0.5______Heinrikr_vs._The_Spectre.md", "prologue-0-5-the-spectre.html", "0.5", "Heinrikr vs. The Spectre"),
    ("Prologue/0.6_____Heinrikr_vs._Acceptance.md", "prologue-0-6-acceptance.html", "0.6", "Heinrikr vs. Acceptance"),
    # Chapter 1
    ("Chapter 1/1.1______Ragnarök.md", "1-1-ragnarok.html", "1.1", "Ragnarök"),
    ("Chapter 1/1.2______Stories_of_Yesteryear.md", "1-2-stories-of-yesteryear.html", "1.2", "Stories of Yesteryear"),
    ("Chapter 1/1.3_______Incoming.md", "1-3-incoming.html", "1.3", "Incoming"),
    ("Chapter 1/1.4______Heinrikr.md", "1-4-heinrikr.html", "1.4", "Heinrikr"),
    ("Chapter 1/1.5______The_Bet.md", "1-5-the-bet.html", "1.5", "The Bet"),
    ("Chapter 1/1.10_The_Kárak_[9].md", "1-10-the-karak.html", "1.10", "The Kárak"),
    ("Chapter 1/1.11_Kára_and_Ástríðr_In_the_morning!_Part_One!.md", "1-11-kara-and-astridr-morning.html", "1.11", "Kára and Ástríðr: In the Morning"),
    ("Chapter 1/1.12_-_Kára_and_Ástríðr__New_Beginnings.md", "1-12-new-beginnings.html", "1.12", "New Beginnings"),
    ("Chapter 1/1.13_-_New_Horizons.md", "1-13-new-horizons.html", "1.13", "New Horizons"),
    ("Chapter 1/1.14_-_WiP.md", "1-14-wip.html", "1.14", "Work in Progress"),
    ("Chapter 1/1.15_-_The_Truth_will_Set_you_Free.md", "1-15-the-truth.html", "1.15", "The Truth Will Set You Free"),
    # Chapter 2
    ("Chapter 2/2.0_-_A_shot_in_the_dark..md", "2-0-shot-in-the-dark.html", "2.0", "A Shot in the Dark"),
    ("Chapter 2/2.1______The_Name.md", "2-1-the-name.html", "2.1", "The Name"),
    ("Chapter 2/2.2_____Heinrikr_vs._The_Cabin.md", "2-2-vs-the-cabin.html", "2.2", "Heinrikr vs. The Cabin"),
    ("Chapter 2/2.3_____Heinrikr_vs._The_Consequences.md", "2-3-vs-consequences.html", "2.3", "Heinrikr vs. The Consequences"),
]


def markdown_to_html(md_content: str) -> str:
    """Convert markdown content to HTML paragraphs."""
    lines = md_content.strip().split('\n')
    html_parts = []
    current_para = []

    for line in lines:
        line = line.strip()

        # Skip title line (starts with #)
        if line.startswith('#'):
            continue

        # Skip metadata brackets
        if line.startswith('[[') and line.endswith(']]'):
            continue

        # Empty line = paragraph break
        if not line:
            if current_para:
                para_text = ' '.join(current_para)
                # Convert italics for internal thoughts
                para_text = convert_italics(para_text)
                html_parts.append(f'            <p>{para_text}</p>')
                current_para = []
        else:
            current_para.append(line)

    # Handle last paragraph
    if current_para:
        para_text = ' '.join(current_para)
        para_text = convert_italics(para_text)
        html_parts.append(f'            <p>{para_text}</p>')

    return '\n\n'.join(html_parts)


def convert_italics(text: str) -> str:
    """Convert text that looks like internal thoughts to italics."""
    # Lines that are clearly internal monologue patterns
    # Look for lines that are clearly thoughts (often short, introspective)

    # If the whole line seems like internal thought, make it italic
    # This is a heuristic - we can refine it

    return text


def process_chapter(source_file: str, output_file: str, number: str, title: str, prev_link: str, next_link: str):
    """Process a single chapter."""
    source_path = SOURCE_DIR / source_file

    if not source_path.exists():
        print(f"  ! Source not found: {source_path}")
        return False

    # Read markdown
    content = source_path.read_text(encoding='utf-8')

    # Convert to HTML
    html_content = markdown_to_html(content)

    # Determine navigation states
    prev_disabled = "disabled" if prev_link == "#" else ""
    next_disabled = "disabled" if next_link == "#" else ""

    # Fill template
    html = CHAPTER_TEMPLATE.format(
        title=title,
        number=number,
        content=html_content,
        prev_link=prev_link,
        next_link=next_link,
        prev_disabled=prev_disabled,
        next_disabled=next_disabled,
    )

    # Write output
    output_path = OUTPUT_DIR / output_file
    output_path.write_text(html, encoding='utf-8')
    print(f"  + Created: {output_file}")
    return True


def main():
    print("Converting Ragnarök chapters to HTML...")
    print(f"Source: {SOURCE_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    OUTPUT_DIR.mkdir(exist_ok=True)

    for i, (source, output, number, title) in enumerate(CHAPTERS):
        # Determine prev/next links
        prev_link = CHAPTERS[i-1][1] if i > 0 else "#"
        next_link = CHAPTERS[i+1][1] if i < len(CHAPTERS) - 1 else "#"

        process_chapter(source, output, number, title, prev_link, next_link)

    print()
    print(f"Done! {len(CHAPTERS)} chapters processed.")


if __name__ == "__main__":
    main()
