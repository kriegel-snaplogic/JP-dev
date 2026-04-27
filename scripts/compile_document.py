#!/usr/bin/env python3
"""
SnapLogic Document Compiler
Converts JSON structure to professionally branded PDF documents using LaTeX
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Tuple


class SnapLogicDocumentCompiler:
    """Compiles JSON document structure to branded PDF using LaTeX"""

    def __init__(self, skill_dir: Path = None):
        """Initialize compiler with skill directory"""
        if skill_dir is None:
            skill_dir = Path(__file__).parent.parent
        self.skill_dir = Path(skill_dir)
        self.templates_dir = self.skill_dir / "templates"
        self.assets_dir = self.skill_dir / "assets"
        # Global counters to ensure unique placeholders across all sections
        self.image_counter = 0
        self.global_image_map = {}
        self.table_counter = 0

    def compile(self, input_json: str, output_pdf: str, doc_type: str = "general",
                font_size: str = "11pt", paper_size: str = "letterpaper",
                color_scheme: str = "default", title_page_style: str = "navy") -> Dict[str, Any]:
        """
        Compile JSON to PDF

        Args:
            input_json: Path to input JSON file
            output_pdf: Path for output PDF file
            doc_type: Document type (general, technical, internal)
            font_size: LaTeX font size (10pt, 11pt, 12pt)
            paper_size: Paper size (letterpaper, a4paper)
            color_scheme: Color scheme (default, monochrome, high_contrast)
            title_page_style: Title page style (navy=colored background with white logo, white=white background with blue logo)

        Returns:
            Dict with status, output_path, pages, version
        """
        # Load JSON
        with open(input_json, 'r') as f:
            structure = json.load(f)

        # Create temp working directory
        work_dir = tempfile.mkdtemp(prefix='snaplogic_doc_')

        try:
            # Reset global state for new compilation
            self.image_counter = 0
            self.global_image_map = {}
            self.table_counter = 0

            # Generate LaTeX content
            latex_content = self._generate_latex(structure, doc_type, font_size,
                                                 paper_size, color_scheme, title_page_style)

            # Write LaTeX file
            tex_file = Path(work_dir) / "document.tex"
            with open(tex_file, 'w', encoding='utf-8') as f:
                f.write(latex_content)

            # Copy assets
            self._copy_assets(work_dir, structure)

            # Compile with pdflatex
            pdf_file = self._compile_latex(work_dir)

            # Copy to output location
            shutil.copy(pdf_file, output_pdf)

            # Get page count
            pages = self._get_page_count(output_pdf)

            # Clean up
            shutil.rmtree(work_dir)

            return {
                "status": "success",
                "output_path": output_pdf,
                "pages": pages,
                "version": structure.get("version", "1.0")
            }

        except Exception as e:
            # Preserve work_dir on error for debugging
            print(f"Error: {str(e)}", file=sys.stderr)
            print(f"Working directory preserved: {work_dir}", file=sys.stderr)
            return {
                "status": "error",
                "error": str(e),
                "work_dir": work_dir
            }

    def _generate_latex(self, structure: Dict[str, Any], doc_type: str,
                       font_size: str, paper_size: str, color_scheme: str,
                       title_page_style: str) -> str:
        """Generate complete LaTeX document"""

        # Load template
        template_file = self.templates_dir / "snaplogic_document.tex"
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()

        # Define color scheme
        if color_scheme == "default":
            color_defs = r"""
\definecolor{snapNavy}{RGB}{0,51,153}       % #003399 - Primary dark / headers
\definecolor{snapBlue}{RGB}{47,141,254}     % #2F8DFE - Primary brand / buttons
\definecolor{snapJade}{RGB}{44,163,146}     % #2CA392 - Accent / highlights
\definecolor{snapLinkBlue}{RGB}{0,56,153}   % #003899 - Hyperlinks / interactive
\definecolor{snapOrange}{RGB}{249,127,110}  % #F97F6E - Warm accent / stats
\definecolor{snapCamel}{RGB}{255,248,240}   % #FFF8F0 - Warm alternating row background
\definecolor{snapLightGray}{RGB}{231,245,255}  % #E7F5FF - Backgrounds / zebra rows
\definecolor{snapDarkGray}{RGB}{14,24,48}   % #0E1830 - Body text / secondary
"""
            primary_color = "snapNavy"
            accent_color = "snapJade"
            link_color = "snapLinkBlue"
        else:
            color_defs = r"""
\definecolor{snapNavy}{RGB}{0,0,0}
\definecolor{snapBlue}{RGB}{0,0,0}
\definecolor{snapJade}{RGB}{100,100,100}
\definecolor{snapLinkBlue}{RGB}{0,0,0}
\definecolor{snapOrange}{RGB}{100,100,100}
\definecolor{snapLightGray}{RGB}{200,200,200}
\definecolor{snapDarkGray}{RGB}{50,50,50}
"""
            primary_color = "black"
            accent_color = "black"
            link_color = "black"

        # Conditional packages
        conditional_packages = ""
        if doc_type == "technical":
            conditional_packages = r"\usepackage[backend=biber,style=numeric]{biblatex}"

        # Generate document parts
        title_page = self._generate_title_page(structure, doc_type, title_page_style)
        abstract = self._generate_abstract(structure)

        # TOC only if 3+ sections
        num_sections = len(structure.get('sections', []))
        toc = "\\tableofcontents\\newpage" if num_sections >= 3 else ""

        # LOF (List of Figures) - configurable via include_lof flag
        # Auto-enabled if images exist AND not explicitly disabled
        include_lof = structure.get('include_lof', True)  # Default: true
        has_figures = self._has_figures(structure)
        lof = "\\listoffigures\\newpage" if (include_lof and has_figures) else ""

        # LOT (List of Tables) - configurable via include_lot flag
        # Auto-enabled if tables exist AND not explicitly disabled
        include_lot = structure.get('include_lot', True)  # Default: true
        has_tables = self._has_tables(structure)
        lot = "\\listoftables\\newpage" if (include_lot and has_tables) else ""

        main_content = self._generate_main_content(structure)
        next_steps = self._generate_next_steps(structure)
        contacts = self._generate_contacts(structure)

        # Replace all template placeholders
        title = self._escape_latex(structure.get('title', 'Untitled'))
        author = self._escape_latex(structure.get('author', ''))
        date = self._escape_latex(structure.get('date', ''))
        version = structure.get('version', '1.0')

        # Generate headers/footers based on document type
        if doc_type == "technical":
            # Technical: Document title in header left, page number in header right, metadata in footer center
            header_content = r'''\fancyhead[L]{\small\textit{''' + title + r'''}}
\fancyhead[R]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}'''
            footer_content = r'''\fancyfoot[C]{\footnotesize ''' + date + r''' | Version ''' + version + r'''}
\renewcommand{\footrulewidth}{0pt}'''
        elif doc_type == "internal":
            # Internal: Minimal header with title and page number
            header_content = r'''\fancyhead[L]{\small''' + title + r'''}
\fancyhead[R]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}'''
            footer_content = r'''\fancyfoot[C]{\footnotesize ''' + date + r'''}
\renewcommand{\footrulewidth}{0pt}'''
        else:  # general/customer-facing
            # Customer-facing: Clean footer only with page numbers and metadata
            header_content = r'''\renewcommand{\headrulewidth}{0pt}'''
            footer_content = r'''\fancyfoot[L]{\footnotesize ''' + date + r'''}
\fancyfoot[C]{\footnotesize Page \thepage\ of \pageref{LastPage}}
\fancyfoot[R]{\footnotesize Version ''' + version + r'''}
\renewcommand{\footrulewidth}{0pt}'''

        replacements = {
            '{{DOC_TYPE}}': doc_type,
            '{{VERSION}}': version,
            '{{FONT_SIZE}}': font_size,
            '{{PAPER_SIZE}}': paper_size,
            '{{PAGE_LAYOUT}}': 'oneside',
            '{{CONDITIONAL_PACKAGES}}': conditional_packages,
            '{{COLOR_DEFINITIONS}}': color_defs,
            '{{LINK_COLOR}}': link_color,
            '{{PRIMARY_COLOR}}': primary_color,
            '{{ACCENT_COLOR}}': accent_color,
            '{{TITLE}}': title,
            '{{AUTHOR}}': author,
            '{{DATE}}': date,
            '{{HEADER_CONTENT}}': header_content,
            '{{FOOTER_CONTENT}}': footer_content,
            '{{HEADER_LEFT}}': title,
            '{{FOOTER_RIGHT}}': f'Page \\thepage\\ of \\pageref{{LastPage}}',
            '{{TITLE_PAGE_CONTENT}}': '',
            '{{TITLE_PAGE}}': title_page,
            '{{TOC_SECTION}}': toc,
            '{{LOF_SECTION}}': lof,
            '{{LOT_SECTION}}': lot,
            '{{ABSTRACT_SECTION}}': abstract,
            '{{MAIN_CONTENT}}': main_content,
            '{{NEXT_STEPS}}': next_steps,
            '{{CONTACTS_SECTION}}': contacts,
            '{{BIBLIOGRAPHY_SECTION}}': ''
        }

        latex = template
        for placeholder, value in replacements.items():
            latex = latex.replace(placeholder, value)

        return latex

    def _generate_title_page(self, structure: Dict[str, Any], doc_type: str, title_page_style: str) -> str:
        """Generate title page with optional navy background or white background"""
        title = self._escape_latex(structure.get('title', 'Untitled'))
        subtitle = self._escape_latex(structure.get('subtitle', ''))
        author = self._escape_latex(structure.get('author', ''))
        date = self._escape_latex(structure.get('date', ''))
        version = self._escape_latex(structure.get('version', '1.0'))
        customer_name = self._escape_latex(structure.get('customer_name', ''))

        if title_page_style == "navy":
            # Navy background with white text and white logo
            content = [
                "\\begin{titlepage}",
                "\\pagecolor{snapNavy}",
                "\\color{white}",
                "\\centering",
                "\\vspace*{2cm}",
            ]

            # Use white logo for navy background
            logo_path = self.assets_dir / "logos" / "snaplogic-logo-white.png"
            if logo_path.exists():
                content.append("\\includegraphics[width=0.3\\textwidth]{snaplogic-logo-white.png}\\\\[1cm]")

            content.extend([
                f"{{\\Huge\\bfseries {title}}}\\\\[0.5cm]",
            ])

            if subtitle:
                content.append(f"{{\\Large {subtitle}}}\\\\[1cm]")

            if customer_name:
                content.append(f"{{\\large Prepared for: {customer_name}}}\\\\[1cm]")

            content.extend([
                "\\vspace{2cm}",
                f"{{\\large {author}}}\\\\[0.3cm]",
                f"{{\\large {date}}}\\\\[0.3cm]",
                f"{{\\large Version {version}}}",
                "\\end{titlepage}",
                "\\nopagecolor",  # Reset page color for rest of document
                "\\color{black}",  # Reset text color
                "\\newpage"
            ])
        else:
            # White background with blue logo (default style)
            content = [
                "\\begin{titlepage}",
                "\\centering",
                "\\vspace*{2cm}",
            ]

            # Use blue logo for white background
            logo_path = self.assets_dir / "logos" / "snaplogic-logo-blue.png"
            if logo_path.exists():
                content.append("\\includegraphics[width=0.3\\textwidth]{snaplogic-logo-blue.png}\\\\[1cm]")

            content.extend([
                f"{{\\Huge\\bfseries {title}}}\\\\[0.5cm]",
            ])

            if subtitle:
                content.append(f"{{\\Large {subtitle}}}\\\\[1cm]")

            if customer_name:
                content.append(f"{{\\large Prepared for: {customer_name}}}\\\\[1cm]")

            content.extend([
                "\\vspace{2cm}",
                f"{{\\large {author}}}\\\\[0.3cm]",
                f"{{\\large {date}}}\\\\[0.3cm]",
                f"{{\\large Version {version}}}",
                "\\end{titlepage}",
                "\\newpage"
            ])

        return '\n'.join(content)

    def _has_figures(self, structure: Dict[str, Any]) -> bool:
        """Check if document contains any images with captions"""
        content_str = json.dumps(structure)
        # Look for [IMAGE:path:caption:width] where caption is not empty or _
        matches = re.findall(r'\[IMAGE:[^:]+:([^:]*)', content_str)
        return any(caption and caption != '_' for caption in matches)

    def _has_tables(self, structure: Dict[str, Any]) -> bool:
        """Check if document contains any tables with captions"""
        content_str = json.dumps(structure)
        # Look for wrapped tables [TABLE:style:caption] where caption is not _
        wrapped_matches = re.findall(r'\[TABLE:[^:]+:([^\]]+)\]', content_str)
        has_wrapped = any(caption and caption != '_' for caption in wrapped_matches)
        # Unwrapped markdown tables get automatic captions during processing
        has_unwrapped = bool(re.search(r'\|[^\n]+\|', content_str))
        return has_wrapped or has_unwrapped

    def _generate_abstract(self, structure: Dict[str, Any]) -> str:
        """Generate management summary or abstract"""
        summary = structure.get('management_summary') or structure.get('abstract')

        if not summary:
            return ""

        # Process content through markdown pipeline
        content = self._process_content(summary)

        return f"""
\\section*{{Management Summary}}
\\addcontentsline{{toc}}{{section}}{{Management Summary}}
{content}
\\newpage
"""

    def _generate_main_content(self, structure: Dict[str, Any]) -> str:
        """Generate main document content from sections with recursive subsection support"""
        content = []
        section_counter = 0
        appendix_started = False

        for section in structure.get('sections', []):
            section_counter += 1

            # Check for appendix
            if not appendix_started and 'Appendix' in section['title']:
                content.append('\\appendix')
                appendix_started = True

            # Page break before each section (except first)
            if section_counter > 1:
                content.append("\\newpage")

            # Process section recursively (handles subsections)
            content.append(self._process_section(section, level=1, section_num=section_counter))

        return '\n\n'.join(content)

    def _process_section(self, section: Dict[str, Any], level: int = 1, section_num: int = None) -> str:
        """Recursively process section, subsections, and subsubsections"""
        parts = []

        # Section header commands by depth
        latex_commands = {
            1: 'section',
            2: 'subsection',
            3: 'subsubsection',
            4: 'paragraph',
            5: 'subparagraph'
        }

        cmd = latex_commands.get(level, 'subparagraph')
        title = self._escape_latex(section.get('title', ''))

        # Add label for top-level sections
        if level == 1 and section_num:
            parts.append(f"\\{cmd}{{{title}}}\\label{{sec:{section_num}}}")
        else:
            parts.append(f"\\{cmd}{{{title}}}")

        # Section content
        if section.get('content'):
            parts.append(self._process_content(section['content']))

        # Recursive subsections
        for subsection in section.get('subsections', []):
            parts.append(self._process_section(subsection, level=level+1))

        # Handle subsubsections
        for subsubsection in section.get('subsubsections', []):
            parts.append(self._process_section(subsubsection, level=level+1))

        return '\n\n'.join(parts)

    def _generate_next_steps(self, structure: Dict[str, Any]) -> str:
        """Generate next steps section"""
        next_steps = structure.get('next_steps', [])

        if not next_steps:
            return ""

        items_latex = '\n'.join([f"\\item {self._escape_latex(item)}" for item in next_steps])

        return f"""
\\section*{{Next Steps}}
\\begin{{enumerate}}
{items_latex}
\\end{{enumerate}}
"""

    def _generate_contacts(self, structure: Dict[str, Any]) -> str:
        """Generate contacts section"""
        contacts = structure.get('contacts', [])

        if not contacts:
            return ""

        contact_lines = []
        for contact in contacts:
            name = self._escape_latex(contact.get('name', ''))
            role = self._escape_latex(contact.get('role', ''))
            email = self._escape_latex(contact.get('email', ''))

            contact_lines.append(f"\\textbf{{{name}}} \\\\ {role} \\\\ \\texttt{{{email}}}")

        contacts_latex = '\\\\[1cm]\n'.join(contact_lines)

        return f"""
\\section*{{Contacts}}
{contacts_latex}
"""

    def _process_content(self, text: str) -> str:
        """
        Process content through complete markdown/LaTeX pipeline

        Order matters:
        1. Extract images and boxes (preserve them)
        2. Process markdown
        3. Escape LaTeX special characters
        4. Restore boxes and images
        """
        if not text:
            return ""

        # Step 1: Extract images
        text, image_map = self._extract_images(text)

        # Step 2: Process highlight boxes (KPI, FEATURE, BOX)
        text = self._process_highlight_boxes(text)

        # Step 3: Process tables
        text = self._process_tables(text)

        # Step 4: Process lists
        text = self._process_lists(text)

        # Step 5: Process markdown headers (###)
        text = self._process_markdown_headers(text)

        # Step 6: Process markdown formatting (bold, italic)
        text = self._process_markdown_formatting(text)

        # Step 7: Extract cross-references to placeholders (before escaping)
        text = self._extract_cross_references(text)

        # Step 8: Escape LaTeX special characters (but preserve our @ markers)
        text = self._escape_latex_content(text)

        # Step 9: Restore markdown formatting (must be before boxes that contain bold/italic)
        text = self._restore_markdown_formatting(text)

        # Step 10: Restore lists (must be before boxes that contain lists)
        text = self._restore_lists(text)

        # Step 11: Restore markdown headers
        text = self._restore_markdown_headers(text)

        # Step 12: Restore tables
        text = self._restore_tables(text)

        # Step 13: Restore boxes (after lists/formatting since boxes can contain them)
        text = self._restore_boxes(text)

        # Step 14: Restore images
        text = self._restore_images(text, image_map)

        # Step 15: Restore cross-references (after all content is in place)
        text = self._restore_cross_references(text)

        return text

    def _extract_images(self, text: str) -> Tuple[str, Dict]:
        """Extract [IMAGE:path:caption:width] tags and replace with placeholders"""
        # Use global counter and map to ensure unique placeholders across all sections
        image_map = {}

        def replace_image(match):
            self.image_counter += 1
            placeholder = f"@IMAGE{self.image_counter}@"

            groups = match.groups()
            image_data = {
                'path': groups[0] if len(groups) > 0 else '',
                'caption': groups[1] if len(groups) > 1 and groups[1] else '',
                'width': groups[2] if len(groups) > 2 and groups[2] else '0.8'
            }
            image_map[placeholder] = image_data
            # Also store in global map for restoration phase
            self.global_image_map[placeholder] = image_data
            return placeholder

        pattern = r'\[IMAGE:([^:]+):([^:]*):?([^\]]*)\]'
        text = re.sub(pattern, replace_image, text)

        return text, image_map

    def _process_highlight_boxes(self, text: str) -> str:
        """Process [KPI:], [FEATURE:], [BOX:] tags"""
        # KPI boxes: [KPI:color|title|value]
        kpi_pattern = r'\[KPI:([^|]+)\|([^|]+)\|([^\]]+)\]'

        def replace_kpi(match):
            color, title, value = match.groups()
            kpi_id = abs(hash(f"{color}{title}{value}")) % 100000
            return f"@KPIBOX:{color}:{kpi_id}@{title}|{value}@KPIBOXEND:{kpi_id}@"

        text = re.sub(kpi_pattern, replace_kpi, text)

        # FEATURE boxes: [FEATURE:color|title]content[/FEATURE]
        feature_pattern = r'\[FEATURE:([^|]+)\|([^\]]+)\](.*?)\[/FEATURE\]'

        def replace_feature(match):
            color, title, content = match.groups()
            feature_id = abs(hash(f"{color}{title}")) % 100000
            return f"@FEATUREBOX:{color}:{feature_id}@{title}|{content.strip()}@FEATUREBOXEND:{feature_id}@"

        text = re.sub(feature_pattern, replace_feature, text, flags=re.DOTALL)

        # Standard BOX: [BOX:type]content[/BOX]
        box_pattern = r'\[BOX:([^\]]+)\](.*?)\[/BOX\]'

        def replace_box(match):
            box_type, content = match.groups()
            box_id = abs(hash(f"{box_type}{content}")) % 100000
            return f"@BOX:{box_type}:{box_id}@{content.strip()}@BOXEND:{box_id}@"

        text = re.sub(box_pattern, replace_box, text, flags=re.DOTALL)

        # BADGE: [BADGE:color|text]
        badge_pattern = r'\[BADGE:([^|]+)\|([^\]]+)\]'

        def replace_badge(match):
            color, badge_text = match.groups()
            badge_id = abs(hash(f"{color}{badge_text}")) % 100000
            return f"@BADGE:{color}:{badge_id}@{badge_text}@BADGEEND:{badge_id}@"

        text = re.sub(badge_pattern, replace_badge, text)

        return text

    def _process_tables(self, text: str) -> str:
        """Process markdown tables with global counter for labeling"""
        # Convert \\n to actual newlines for regex
        text = text.replace('\\n', '\n')

        # Only process explicitly wrapped tables: [TABLE:style:caption]...table...[/TABLE]
        # Unwrapped markdown tables will render as inline tables without numbering
        table_pattern = r'\[TABLE:([^:]+):([^\]]+)\](.*?)\[/TABLE\]'

        def replace_table(match):
            self.table_counter += 1
            style, caption, table_md = match.groups()
            table_id = abs(hash(f"{style}{caption}{table_md}")) % 100000
            # Include table number in placeholder for labeling
            return f"@TABLE:{style}:{caption}:{table_id}:{self.table_counter}@{table_md.strip()}@TABLEEND:{table_id}@"

        text = re.sub(table_pattern, replace_table, text, flags=re.DOTALL)

        return text

    def _process_lists(self, text: str) -> str:
        """
        Extract markdown list blocks and protect with placeholders
        Actual LaTeX generation happens in _restore_lists after escaping
        """
        # Convert \\n to newlines
        text = text.replace('\\n', '\n')

        lines = text.split('\n')
        result = []
        i = 0
        list_counter = 0

        while i < len(lines):
            line = lines[i]

            # Check if this line starts a list
            if re.match(r'^(\s*)[•\-*]\s+', line) or re.match(r'^(\s*)\d+\.\s+', line):
                # Extract raw list lines (not LaTeX yet)
                list_lines, end_i = self._extract_list_lines(lines, i)
                # Store raw markdown with special separator
                list_content = '\x00'.join(list_lines)  # Use null char as separator
                placeholder = f'@LIST:{list_counter}@{list_content}@LISTEND:{list_counter}@'
                result.append(placeholder)
                list_counter += 1
                i = end_i
            else:
                result.append(line)
                i += 1

        return '\n'.join(result)

    def _extract_list_lines(self, lines: List[str], start_i: int) -> Tuple[List[str], int]:
        """Extract raw list lines without converting to LaTeX"""
        list_lines = []
        i = start_i
        base_indent = self._get_indent_level(lines[i])

        while i < len(lines):
            line = lines[i]

            if not line.strip():
                i += 1
                continue

            indent = self._get_indent_level(line)

            # Check if still part of list (list items or deeper indentation)
            if indent < base_indent:
                break

            # Check if it's a list item or continuation
            if re.match(r'^(\s*)(?:[•\-*]|\d+\.)\s+', line) or indent >= base_indent:
                list_lines.append(line)
                i += 1
            else:
                break

        return list_lines, i

    def _parse_list_block(self, lines: List[str], start_i: int) -> Tuple[str, int]:
        """Parse a complete list block with nesting"""
        list_items = []
        i = start_i
        base_indent = self._get_indent_level(lines[i])

        # Determine list type from first item
        is_numbered = bool(re.match(r'^(\s*)\d+\.\s+', lines[i]))
        env = 'enumerate' if is_numbered else 'itemize'

        while i < len(lines):
            line = lines[i]
            indent = self._get_indent_level(line)

            # Check if still part of this list
            if not line.strip():
                i += 1
                continue

            if indent < base_indent:
                break  # End of this list level

            # Parse item at current level
            if indent == base_indent:
                item_match = re.match(r'^(\s*)(?:[•\-*]|\d+\.)\s+(.+)$', line)
                if item_match:
                    item_text = item_match.group(2)

                    # Check if next lines are continuation or nested list
                    item_content = [item_text]
                    i += 1

                    # Gather continuation and nested lists
                    while i < len(lines) and lines[i].strip():
                        next_indent = self._get_indent_level(lines[i])

                        if next_indent > base_indent:
                            # Nested list
                            if re.match(r'^(\s*)(?:[•\-*]|\d+\.)\s+', lines[i]):
                                nested_block, i = self._parse_list_block(lines, i)
                                item_content.append(nested_block)
                            else:
                                # Continuation text
                                item_content.append(lines[i].strip())
                                i += 1
                        else:
                            break

                    list_items.append(f"\\item {' '.join(item_content)}")
                else:
                    i += 1
            else:
                i += 1

        # Build LaTeX list
        latex = [f'\\begin{{{env}}}']
        latex.extend(list_items)
        latex.append(f'\\end{{{env}}}')

        return '\n'.join(latex), i

    def _get_indent_level(self, line: str) -> int:
        """Get indentation level (number of leading spaces)"""
        return len(line) - len(line.lstrip())

    def _process_markdown_headers(self, text: str) -> str:
        """Process ### headers as subsections"""
        def replace_subsection(match):
            title = match.group(1)
            # Strip numbering like "2.3.1" or "B.1"
            title = re.sub(r'^[A-Z]?\d+(?:\.\d+)*\s+', '', title)
            title = re.sub(r'^[A-Z]\.\d+\s*—\s*', '', title)
            header_id = abs(hash(title)) % 100000
            return f'@SUBSEC:{header_id}@{title}@SUBSECEND:{header_id}@'

        text = re.sub(r'###\s+(.+?)(?:\n|$)', replace_subsection, text, flags=re.MULTILINE)
        return text

    def _process_markdown_formatting(self, text: str) -> str:
        """Process **bold** and *italic*"""
        # Bold: **text**
        text = re.sub(r'\*\*(.+?)\*\*', r'@BOLD@\1@BOLDEND@', text)
        # Italic: *text*
        text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'@ITALIC@\1@ITALICEND@', text)
        return text

    def _process_cross_references(self, text: str) -> str:
        """Process cross-references like 'Section 2.1' or 'Figure 3'"""
        # For now, just pass through - full implementation would create hyperlinks
        return text

    def _escape_latex(self, text: str) -> str:
        """Escape LaTeX special characters - for simple strings"""
        if not text or not isinstance(text, str):
            return ""

        # CRITICAL: Backslash MUST be escaped first!
        result = text.replace('\\', r'\textbackslash{}')

        # Then escape other special characters
        replacements = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
        }

        for char, escaped in replacements.items():
            result = result.replace(char, escaped)

        return result

    def _escape_latex_content(self, text: str) -> str:
        """Escape LaTeX special characters but preserve @ markers"""
        if not text or not isinstance(text, str):
            return ""

        # Split on @ markers to preserve them (match full marker syntax with multiple colons)
        parts = re.split(r'(@[A-Z]+:[^@]+@|@[A-Z]+END:[^@]+@)', text)

        result = []
        for part in parts:
            if part.startswith('@') and part.endswith('@'):
                # This is a marker, preserve it
                result.append(part)
            else:
                # Escape this part
                escaped = part
                replacements = {
                    '\\': r'\textbackslash{}',
                    '{': r'\{',
                    '}': r'\}',
                    '&': r'\&',
                    '%': r'\%',
                    '$': r'\$',
                    '#': r'\#',
                    '_': r'\_',
                    '~': r'\textasciitilde{}',
                    '^': r'\textasciicircum{}',
                }
                for char, repl in replacements.items():
                    escaped = escaped.replace(char, repl)
                result.append(escaped)

        return ''.join(result)

    def _restore_boxes(self, text: str) -> str:
        """Restore box placeholders to LaTeX"""
        # KPI boxes (may contain @ markers, use .*? non-greedy)
        kpi_pattern = r'@KPIBOX:([^:]+):(\d+)@(.*?)\|(.*?)@KPIBOXEND:\2@'

        def restore_kpi(match):
            color, box_id, title, value = match.groups()
            color_map = {'navy': 'snapNavy', 'blue': 'snapBlue', 'jade': 'snapJade', 'orange': 'snapOrange'}
            latex_color = color_map.get(color, 'snapBlue')

            return f"\\kpibox{{{latex_color}}}{{{title}}}{{{value}}}"

        text = re.sub(kpi_pattern, restore_kpi, text, flags=re.DOTALL)

        # FEATURE boxes (may contain @ markers, use .*? non-greedy)
        feature_pattern = r'@FEATUREBOX:([^:]+):(\d+)@(.*?)\|(.*?)@FEATUREBOXEND:\2@'

        def restore_feature(match):
            color, box_id, title, content = match.groups()
            color_map = {'navy': 'snapNavy', 'blue': 'snapBlue', 'jade': 'snapJade', 'orange': 'snapOrange'}
            latex_color = color_map.get(color, 'snapBlue')

            return f"\\featurebox{{{latex_color}}}{{{title}}}{{{content}}}"

        text = re.sub(feature_pattern, restore_feature, text, flags=re.DOTALL)

        # Standard BOX (use .*? non-greedy to match content that may contain other @ markers)
        box_pattern = r'@BOX:([^:]+):(\d+)@(.*?)@BOXEND:\2@'

        def restore_box(match):
            box_type, box_id, content = match.groups()
            box_map = {
                'info': 'infobox',
                'success': 'successbox',
                'warning': 'warningbox',
                'note': 'notebox'
            }
            box_cmd = box_map.get(box_type, 'infobox')
            return f"\\{box_cmd}{{{content}}}"

        text = re.sub(box_pattern, restore_box, text, flags=re.DOTALL)

        # BADGE boxes (may contain @ markers, use .*? non-greedy)
        badge_pattern = r'@BADGE:([^:]+):(\d+)@(.*?)@BADGEEND:\2@'

        def restore_badge(match):
            color, badge_id, badge_text = match.groups()
            color_map = {'navy': 'snapNavy', 'blue': 'snapBlue', 'jade': 'snapJade', 'orange': 'snapOrange'}
            latex_color = color_map.get(color, 'snapBlue')

            return f"\\badgebox{{{latex_color}}}{{{badge_text}}}"

        text = re.sub(badge_pattern, restore_badge, text, flags=re.DOTALL)

        return text

    def _restore_tables(self, text: str) -> str:
        """Restore table placeholders to LaTeX tables with labels"""
        # Updated pattern to capture table number
        table_pattern = r'@TABLE:([^:]+):([^:]+):(\d+):(\d+)@(.*?)@TABLEEND:\3@'

        def restore_table(match):
            style, caption, table_id, table_num, table_md = match.groups()

            # Parse markdown table
            lines = [l.strip() for l in table_md.strip().split('\n') if l.strip()]
            if len(lines) < 2:
                return ""

            # Extract headers
            header_line = lines[0]
            headers = [h.strip() for h in header_line.split('|') if h.strip()]

            # Skip separator line
            data_lines = lines[2:] if len(lines) > 2 else []
            rows = []
            for line in data_lines:
                cells = [c.strip() for c in line.split('|') if c.strip()]
                if cells:
                    rows.append(cells)

            # Generate LaTeX table based on style
            num_cols = len(headers)

            # Column specification (same for all styles)
            if num_cols > 0:
                col_width = f'\\dimexpr\\linewidth/{num_cols}-2\\tabcolsep\\relax'
                col_spec = ''.join([f'>{{\\setlength{{\\parindent}}{{0pt}}}}p{{{col_width}}}' for _ in range(num_cols)])
            else:
                col_spec = 'l'

            latex = []
            latex.append('\\begin{table}[h]')
            latex.append('\\centering')

            # Caption and label
            if caption and caption != '_':
                latex.append(f'\\caption{{{caption}}}')
            else:
                latex.append(f'\\caption{{}}')
            latex.append(f'\\label{{tab:{table_num}}}')
            latex.append('\\renewcommand{\\arraystretch}{1.2}')

            # Style-specific rendering
            if style == 'minimal':
                # Minimal: No colors, horizontal rules only (booktabs style)
                latex.append(f'\\begin{{tabular}}{{{col_spec}}}')
                latex.append('\\toprule')
                bold_headers = [f'\\textbf{{{h}}}' for h in headers]
                latex.append(f'{" & ".join(bold_headers)} \\\\')
                latex.append('\\midrule')
                for row in rows:
                    latex.append(f'{" & ".join(row)} \\\\')
                latex.append('\\bottomrule')

            elif style.startswith('accent-'):
                # Accent: Colored header (blue/jade/orange), white rows, single rule
                accent_color = style.split('-')[1] if '-' in style else 'blue'
                color_map = {'blue': 'snapBlue', 'jade': 'snapJade', 'orange': 'snapOrange', 'navy': 'snapNavy'}
                latex_color = color_map.get(accent_color, 'snapBlue')

                latex.append(f'\\begin{{tabular}}{{{col_spec}}}')
                white_headers = [f'\\textcolor{{white}}{{\\textbf{{{h}}}}}' for h in headers]
                latex.append(f'\\rowcolor{{{latex_color}}}{" & ".join(white_headers)} \\\\')
                latex.append('\\arrayrulecolor{' + latex_color + '!30}\\midrule')
                for row in rows:
                    latex.append(f'{" & ".join(row)} \\\\')

            elif style == 'bordered':
                # Bordered: Light gray header, all cells have borders
                latex.append(f'\\begin{{tabular}}{{|{"|".join(["p{" + col_width + "}" for _ in range(num_cols)])}|}}')
                latex.append('\\hline')
                gray_headers = [f'\\textcolor{{snapNavy}}{{\\textbf{{{h}}}}}' for h in headers]
                latex.append(f'\\rowcolor{{snapLightGray}}{" & ".join(gray_headers)} \\\\')
                latex.append('\\hline')
                for row in rows:
                    latex.append(f'{" & ".join(row)} \\\\')
                    latex.append('\\hline')

            elif style.startswith('status-'):
                # Status: Row colors indicate semantic meaning
                # Extract row colors from style (e.g., status-jade,orange,blue)
                colors_str = style.split('-', 1)[1] if '-' in style else ''
                row_colors = colors_str.split(',') if colors_str else []
                color_map = {'blue': 'snapBlue!20', 'jade': 'snapJade!20', 'orange': 'snapOrange!20',
                            'gray': 'snapLightGray', 'navy': 'snapNavy!20', 'white': 'white'}

                latex.append(f'\\begin{{tabular}}{{{col_spec}}}')
                # White header with navy text
                navy_headers = [f'\\textcolor{{snapNavy}}{{\\textbf{{{h}}}}}' for h in headers]
                latex.append(f'{" & ".join(navy_headers)} \\\\')
                latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')

                for i, row in enumerate(rows):
                    # First column bold for row labels
                    row_formatted = [f'\\textbf{{{row[0]}}}'] + row[1:] if row else row
                    # Apply color if specified
                    if i < len(row_colors):
                        latex_color = color_map.get(row_colors[i], 'white')
                        latex.append(f'\\rowcolor{{{latex_color}}}{" & ".join(row_formatted)} \\\\')
                    else:
                        latex.append(f'{" & ".join(row_formatted)} \\\\')

            else:  # 'simple' (default)
                # Simple: Navy header, alternating rows (white/light gray)
                latex.append(f'\\begin{{tabular}}{{{col_spec}}}')
                white_headers = [f'\\textcolor{{white}}{{\\textbf{{{h}}}}}' for h in headers]
                latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers)} \\\\')
                latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')
                for i, row in enumerate(rows):
                    if i % 2 == 1:
                        latex.append(f'\\rowcolor{{snapLightGray}}{" & ".join(row)} \\\\')
                    else:
                        latex.append(f'{" & ".join(row)} \\\\')

            latex.append('\\end{tabular}')
            latex.append('\\end{table}')

            return '\n'.join(latex)

        text = re.sub(table_pattern, restore_table, text, flags=re.DOTALL)
        return text

    def _restore_markdown_headers(self, text: str) -> str:
        """Restore subsection headers"""
        pattern = r'@SUBSEC:(\d+)@(.+?)@SUBSECEND:\1@'
        text = re.sub(pattern, r'\\subsection{\2}', text)
        return text

    def _restore_markdown_formatting(self, text: str) -> str:
        """Restore bold and italic"""
        text = re.sub(r'@BOLD@(.+?)@BOLDEND@', r'\\textbf{\1}', text)
        text = re.sub(r'@ITALIC@(.+?)@ITALICEND@', r'\\textit{\1}', text)
        return text

    def _restore_lists(self, text: str) -> str:
        """Restore list placeholders by converting markdown to LaTeX"""
        list_pattern = r'@LIST:(\d+)@(.+?)@LISTEND:\1@'

        def restore_list(match):
            list_id, list_content = match.groups()
            # Split back into lines using null char separator
            lines = list_content.split('\x00')
            # Now parse and convert to LaTeX
            list_latex, _ = self._parse_list_block(lines, 0)
            return list_latex

        text = re.sub(list_pattern, restore_list, text, flags=re.DOTALL)
        return text

    def _restore_images(self, text: str, image_map: Dict) -> str:
        """Restore image placeholders with labels for cross-referencing"""
        # Create bidirectional mapping between JSON order and document order:
        # - Text says "Figure X" referring to JSON image #X
        # - But images appear in document at different positions
        # - So we need: text "Figure X" -> label fig:X -> but label fig:X is on the image at its JSON position

        # Find all placeholders in document order
        placeholder_positions = []
        for placeholder in image_map.keys():
            pos = text.find(placeholder)
            if pos != -1:
                placeholder_num = int(placeholder.replace('@IMAGE', '').replace('@', ''))
                placeholder_positions.append((pos, placeholder, placeholder_num))

        # Sort by position in document
        placeholder_positions.sort()

        # Create mapping from JSON order to document order
        # json_to_doc[json_num] = document_order_num
        json_to_doc = {}
        for doc_order, (pos, placeholder, json_num) in enumerate(placeholder_positions, start=1):
            json_to_doc[json_num] = doc_order

        # Replace all placeholders
        for placeholder, image_data in image_map.items():
            path = image_data['path']
            caption = image_data.get('caption', '')
            width = image_data.get('width', '0.8')

            # Sanitize path - replace spaces with underscores to match copied files
            sanitized_path = path.replace(' ', '_')

            latex = f"""
\\begin{{figure}}[H]
\\centering
\\includegraphics[width={width}\\textwidth]{{{sanitized_path}}}
"""
            if caption and caption != '_':
                # Get JSON number and document order for this placeholder
                json_num = int(placeholder.replace('@IMAGE', '').replace('@', ''))
                doc_order = json_to_doc.get(json_num, json_num)

                # Use JSON number for label so text references match
                # BUT: LaTeX will auto-number based on document order
                # So we need label to match what text says (JSON number)
                latex += f"\\caption{{{caption}}}\\label{{fig:{json_num}}}\n"
            latex += "\\end{figure}\n"

            text = text.replace(placeholder, latex)

        return text

    def _copy_assets(self, work_dir: str, structure: Dict[str, Any]):
        """Copy logo and other assets to working directory"""
        # Copy SnapLogic logos (both blue and white for different title page styles)
        logo_blue = self.assets_dir / "logos" / "snaplogic-logo-blue.png"
        logo_white = self.assets_dir / "logos" / "snaplogic-logo-white.png"
        if logo_blue.exists():
            shutil.copy(logo_blue, work_dir)
        if logo_white.exists():
            shutil.copy(logo_white, work_dir)

        # Copy customer logo if specified
        customer_logo = structure.get('customer_logo', '')
        if customer_logo and os.path.exists(customer_logo):
            dest = Path(work_dir) / Path(customer_logo).name
            shutil.copy(customer_logo, dest)

        # Find and copy all content images referenced with [IMAGE:path:caption:width]
        image_pattern = r'\[IMAGE:([^:]+):'
        content_to_search = json.dumps(structure)  # Search entire structure

        for match in re.finditer(image_pattern, content_to_search):
            image_path = match.group(1)

            # Handle both relative and absolute paths
            if os.path.isabs(image_path):
                source_path = Path(image_path)
            else:
                # Relative paths are relative to the skill directory
                source_path = self.assets_dir.parent / image_path

            if source_path.exists():
                # Preserve directory structure in work_dir
                # e.g., assets/citizen-integrator/image.png -> work_dir/assets/citizen-integrator/image.png
                if not os.path.isabs(image_path):
                    # Replace spaces with underscores for LaTeX compatibility
                    sanitized_path = image_path.replace(' ', '_')
                    dest_path = Path(work_dir) / sanitized_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # For absolute paths, sanitize just the filename
                    sanitized_name = source_path.name.replace(' ', '_')
                    dest_path = Path(work_dir) / sanitized_name

                shutil.copy(source_path, dest_path)

    def _extract_cross_references(self, text: str) -> str:
        """Extract cross-references to placeholders before LaTeX escaping"""
        # Figure references: "Figure X" where X is a number
        # Replace with placeholder @FIGREF:X@
        def extract_figure_ref(match):
            fig_num = match.group(1)
            return f"@FIGREF:{fig_num}@"

        text = re.sub(r'\bFigure\s+(\d+)\b', extract_figure_ref, text)

        # Table references: "Table X" where X is a number
        # Replace with placeholder @TABREF:X@
        def extract_table_ref(match):
            tab_num = match.group(1)
            return f"@TABREF:{tab_num}@"

        text = re.sub(r'\bTable\s+(\d+)\b', extract_table_ref, text)

        # Section references: "Section X", "Section X.Y", "Section X.Y.Z"
        # Replace with placeholder @SECREF:X.Y.Z@
        def extract_section_ref(match):
            section_num = match.group(1)
            return f"@SECREF:{section_num}@"

        text = re.sub(r'\bSection\s+([\d\.]+)\b', extract_section_ref, text)

        return text

    def _restore_cross_references(self, text: str) -> str:
        """Restore cross-reference placeholders to proper LaTeX \ref commands"""
        # Figure references: @FIGREF:X@ -> Figure~\ref{fig:X}
        # LaTeX will auto-number based on figure order and hyperref makes it clickable
        # Using ~ for non-breaking space (standard LaTeX practice)
        def restore_figure_ref(match):
            fig_num = match.group(1)
            return f"Figure~\\ref{{fig:{fig_num}}}"

        text = re.sub(r'@FIGREF:(\d+)@', restore_figure_ref, text)

        # Table references: @TABREF:X@ -> Table~\ref{tab:X}
        # LaTeX will auto-number based on table order and hyperref makes it clickable
        def restore_table_ref(match):
            tab_num = match.group(1)
            return f"Table~\\ref{{tab:{tab_num}}}"

        text = re.sub(r'@TABREF:(\d+)@', restore_table_ref, text)

        # Section references: @SECREF:X.Y@ -> Section~\ref{sec:X.Y}
        # Sections get auto-labeled by our section generation code
        def restore_section_ref(match):
            section_num = match.group(1)
            return f"Section~\\ref{{sec:{section_num}}}"

        text = re.sub(r'@SECREF:([\d\.]+)@', restore_section_ref, text)

        return text

    def _compile_latex(self, work_dir: str) -> Path:
        """Run pdflatex to compile document"""
        tex_file = Path(work_dir) / "document.tex"

        # Run pdflatex twice (for TOC and cross-references)
        for run in range(2):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 'document.tex'],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                log_file = Path(work_dir) / "document.log"
                # Print relevant error lines
                if log_file.exists():
                    with open(log_file, 'r') as f:
                        log_content = f.read()
                        # Find error lines
                        for line in log_content.split('\n'):
                            if 'Error' in line or '!' in line[:2]:
                                print(line, file=sys.stderr)
                raise Exception(f"LaTeX compilation failed. Check {log_file}")

        pdf_file = Path(work_dir) / "document.pdf"
        if not pdf_file.exists():
            raise Exception("PDF was not generated")

        return pdf_file

    def _get_page_count(self, pdf_file: str) -> int:
        """Get number of pages in PDF"""
        try:
            result = subprocess.run(
                ['pdfinfo', pdf_file],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if line.startswith('Pages:'):
                    return int(line.split(':')[1].strip())
        except:
            pass
        return 0


def main():
    """Command line interface"""
    if len(sys.argv) < 4:
        print("Usage: compile_document.py <input.json> <output.pdf> <doc_type>")
        sys.exit(1)

    input_json = sys.argv[1]
    output_pdf = sys.argv[2]
    doc_type = sys.argv[3]

    # Optional arguments
    font_size = sys.argv[4] if len(sys.argv) > 4 else "11pt"
    paper_size = sys.argv[5] if len(sys.argv) > 5 else "letterpaper"
    color_scheme = sys.argv[6] if len(sys.argv) > 6 else "default"

    compiler = SnapLogicDocumentCompiler()
    result = compiler.compile(input_json, output_pdf, doc_type,
                             font_size, paper_size, color_scheme)

    print(json.dumps(result, indent=2))

    if result['status'] != 'success':
        sys.exit(1)


if __name__ == '__main__':
    main()
