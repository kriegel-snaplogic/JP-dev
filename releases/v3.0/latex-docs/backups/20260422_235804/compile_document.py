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

    def compile(self, input_json: str, output_pdf: str, doc_type: str = "general",
                font_size: str = "11pt", paper_size: str = "letterpaper",
                color_scheme: str = "default") -> Dict[str, Any]:
        """
        Compile JSON to PDF

        Args:
            input_json: Path to input JSON file
            output_pdf: Path for output PDF file
            doc_type: Document type (general, technical, internal)
            font_size: LaTeX font size (10pt, 11pt, 12pt)
            paper_size: Paper size (letterpaper, a4paper)
            color_scheme: Color scheme (default, monochrome, high_contrast)

        Returns:
            Dict with status, output_path, pages, version
        """
        # Load JSON
        with open(input_json, 'r') as f:
            structure = json.load(f)

        # Create temp working directory
        work_dir = tempfile.mkdtemp(prefix='snaplogic_doc_')

        try:
            # Generate LaTeX content
            latex_content = self._generate_latex(structure, doc_type, font_size,
                                                 paper_size, color_scheme)

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
                       font_size: str, paper_size: str, color_scheme: str) -> str:
        """Generate complete LaTeX document"""

        # Load template
        template_file = self.templates_dir / "snaplogic_document.tex"
        with open(template_file, 'r', encoding='utf-8') as f:
            template = f.read()

        # Define color scheme
        if color_scheme == "default":
            color_defs = r"""
\definecolor{snapNavy}{RGB}{0,25,52}
\definecolor{snapBlue}{RGB}{64,115,255}
\definecolor{snapJade}{RGB}{66,165,210}
\definecolor{snapOrange}{RGB}{255,125,63}
\definecolor{snapLightGray}{RGB}{245,245,245}
"""
            primary_color = "snapBlue"
            accent_color = "snapJade"
            link_color = "snapBlue"
        else:
            color_defs = r"""
\definecolor{snapNavy}{RGB}{0,0,0}
\definecolor{snapBlue}{RGB}{0,0,0}
\definecolor{snapJade}{RGB}{100,100,100}
\definecolor{snapOrange}{RGB}{100,100,100}
\definecolor{snapLightGray}{RGB}{200,200,200}
"""
            primary_color = "black"
            accent_color = "black"
            link_color = "black"

        # Conditional packages
        conditional_packages = ""
        if doc_type == "technical":
            conditional_packages = r"\usepackage[backend=biber,style=numeric]{biblatex}"

        # Generate document parts
        title_page = self._generate_title_page(structure, doc_type)
        abstract = self._generate_abstract(structure)

        # TOC only if 3+ sections
        num_sections = len(structure.get('sections', []))
        toc = "\\tableofcontents\\newpage" if num_sections >= 3 else ""

        main_content = self._generate_main_content(structure)
        next_steps = self._generate_next_steps(structure)
        contacts = self._generate_contacts(structure)

        # Replace all template placeholders
        title = self._escape_latex(structure.get('title', 'Untitled'))
        author = self._escape_latex(structure.get('author', ''))
        date = self._escape_latex(structure.get('date', ''))
        version = structure.get('version', '1.0')

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
            '{{HEADER_CONTENT}}': '',
            '{{FOOTER_CONTENT}}': '',
            '{{HEADER_LEFT}}': title,
            '{{FOOTER_RIGHT}}': f'Page \\thepage\\ of \\pageref{{LastPage}}',
            '{{TITLE_PAGE_CONTENT}}': '',
            '{{TITLE_PAGE}}': title_page,
            '{{TOC_SECTION}}': toc,
            '{{LOF_SECTION}}': '',  # List of figures - add if needed
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

    def _generate_title_page(self, structure: Dict[str, Any], doc_type: str) -> str:
        """Generate title page"""
        title = self._escape_latex(structure.get('title', 'Untitled'))
        subtitle = self._escape_latex(structure.get('subtitle', ''))
        author = self._escape_latex(structure.get('author', ''))
        date = self._escape_latex(structure.get('date', ''))
        version = self._escape_latex(structure.get('version', '1.0'))
        customer_name = self._escape_latex(structure.get('customer_name', ''))

        content = [
            "\\begin{titlepage}",
            "\\centering",
            "\\vspace*{2cm}",
        ]

        # Add logo if available
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
        """Generate main document content from sections"""
        content = []
        section_counter = 0
        appendix_started = False

        for section in structure.get('sections', []):
            section_counter += 1
            section_title = self._escape_latex(section['title'])

            # Check for appendix
            if not appendix_started and 'Appendix' in section['title']:
                content.append('\\appendix')
                appendix_started = True

            # Page break before each section (except first)
            if section_counter > 1:
                content.append("\\newpage")

            # Section header
            content.append(f"\\section{{{section_title}}}\\label{{sec:{section_counter}}}")

            # Process section content
            section_content = self._process_content(section['content'])
            content.append(section_content)

        return '\n\n'.join(content)

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

        # Step 7: Process cross-references (Section X, Figure Y)
        text = self._process_cross_references(text)

        # Step 8: Escape LaTeX special characters (but preserve our @ markers)
        text = self._escape_latex_content(text)

        # Step 9: Restore boxes
        text = self._restore_boxes(text)

        # Step 10: Restore tables
        text = self._restore_tables(text)

        # Step 11: Restore markdown headers
        text = self._restore_markdown_headers(text)

        # Step 12: Restore markdown formatting
        text = self._restore_markdown_formatting(text)

        # Step 13: Restore images
        text = self._restore_images(text, image_map)

        return text

    def _extract_images(self, text: str) -> Tuple[str, Dict]:
        """Extract [IMAGE:path:caption:width] tags and replace with placeholders"""
        image_map = {}
        counter = 0

        def replace_image(match):
            nonlocal counter
            counter += 1
            placeholder = f"@IMAGE{counter}@"

            groups = match.groups()
            image_map[placeholder] = {
                'path': groups[0] if len(groups) > 0 else '',
                'caption': groups[1] if len(groups) > 1 and groups[1] else '',
                'width': groups[2] if len(groups) > 2 and groups[2] else '0.8'
            }
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
        """Process markdown tables"""
        # Convert \\n to actual newlines for regex
        text = text.replace('\\n', '\n')

        # Auto-wrap unwrapped markdown tables
        unwrapped_pattern = r'(\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+)'

        def wrap_table(match):
            table_content = match.group(1).strip()
            table_id = abs(hash(table_content)) % 100000
            return f'@TABLE:simple:_:{table_id}@\n{table_content}\n@TABLEEND:{table_id}@'

        text = re.sub(unwrapped_pattern, wrap_table, text, flags=re.MULTILINE)

        # Process wrapped tables: [TABLE:style:caption]...table...[/TABLE]
        table_pattern = r'\[TABLE:([^:]+):([^\]]+)\](.*?)\[/TABLE\]'

        def replace_table(match):
            style, caption, table_md = match.groups()
            table_id = abs(hash(f"{style}{caption}{table_md}")) % 100000
            return f"@TABLE:{style}:{caption}:{table_id}@{table_md.strip()}@TABLEEND:{table_id}@"

        text = re.sub(table_pattern, replace_table, text, flags=re.DOTALL)

        return text

    def _process_lists(self, text: str) -> str:
        """Process markdown lists with proper LaTeX environments"""
        # Convert \\n to newlines
        text = text.replace('\\n', '\n')

        lines = text.split('\n')
        result = []
        in_bullet_list = False
        in_numbered_list = False

        for i, line in enumerate(lines):
            # Check if this is a bullet list item
            if re.match(r'^-\s+', line):
                if not in_bullet_list:
                    result.append('\\begin{itemize}')
                    in_bullet_list = True
                # Convert bullet item
                item_text = re.sub(r'^-\s+', '', line)
                result.append(f'\\item {item_text}')
            # Check if this is a numbered list item
            elif re.match(r'^\d+\.\s+', line):
                if not in_numbered_list:
                    result.append('\\begin{enumerate}')
                    in_numbered_list = True
                # Convert numbered item
                item_text = re.sub(r'^\d+\.\s+', '', line)
                result.append(f'\\item {item_text}')
            else:
                # Not a list item - close any open lists
                if in_bullet_list:
                    result.append('\\end{itemize}')
                    in_bullet_list = False
                if in_numbered_list:
                    result.append('\\end{enumerate}')
                    in_numbered_list = False
                result.append(line)

        # Close any remaining open lists
        if in_bullet_list:
            result.append('\\end{itemize}')
        if in_numbered_list:
            result.append('\\end{enumerate}')

        return '\n'.join(result)

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

        # Split on @ markers to preserve them
        parts = re.split(r'(@[A-Z]+(?::\d+)?@|@[A-Z]+END(?::\d+)?@)', text)

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
        # KPI boxes
        kpi_pattern = r'@KPIBOX:([^:]+):(\d+)@([^|]+)\|([^@]+)@KPIBOXEND:\2@'

        def restore_kpi(match):
            color, box_id, title, value = match.groups()
            color_map = {'navy': 'snapNavy', 'blue': 'snapBlue', 'jade': 'snapJade', 'orange': 'snapOrange'}
            latex_color = color_map.get(color, 'snapBlue')

            return f"\\kpibox{{{latex_color}}}{{{title}}}{{{value}}}"

        text = re.sub(kpi_pattern, restore_kpi, text)

        # FEATURE boxes
        feature_pattern = r'@FEATUREBOX:([^:]+):(\d+)@([^|]+)\|([^@]+)@FEATUREBOXEND:\2@'

        def restore_feature(match):
            color, box_id, title, content = match.groups()
            color_map = {'navy': 'snapNavy', 'blue': 'snapBlue', 'jade': 'snapJade', 'orange': 'snapOrange'}
            latex_color = color_map.get(color, 'snapBlue')

            return f"\\featurebox{{{latex_color}}}{{{title}}}{{{content}}}"

        text = re.sub(feature_pattern, restore_feature, text)

        # Standard BOX
        box_pattern = r'@BOX:([^:]+):(\d+)@([^@]+)@BOXEND:\2@'

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

        text = re.sub(box_pattern, restore_box, text)

        # BADGE boxes
        badge_pattern = r'@BADGE:([^:]+):(\d+)@([^@]+)@BADGEEND:\2@'

        def restore_badge(match):
            color, badge_id, badge_text = match.groups()
            color_map = {'navy': 'snapNavy', 'blue': 'snapBlue', 'jade': 'snapJade', 'orange': 'snapOrange'}
            latex_color = color_map.get(color, 'snapBlue')

            return f"\\badgebox{{{latex_color}}}{{{badge_text}}}"

        text = re.sub(badge_pattern, restore_badge, text)

        return text

    def _restore_tables(self, text: str) -> str:
        """Restore table placeholders to LaTeX tables"""
        table_pattern = r'@TABLE:([^:]+):([^:]+):(\d+)@(.*?)@TABLEEND:\3@'

        def restore_table(match):
            style, caption, table_id, table_md = match.groups()

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

            # Generate LaTeX table
            num_cols = len(headers)

            # Use wrapping p columns with equal widths
            if num_cols > 0:
                col_width = f'\\dimexpr\\linewidth/{num_cols}-2\\tabcolsep\\relax'
                col_spec = ''.join([f'p{{{col_width}}}' for _ in range(num_cols)])
            else:
                col_spec = 'l'

            latex = []
            latex.append('\\begin{table}[h]')
            latex.append('\\centering')
            if caption and caption != '_':
                latex.append(f'\\caption{{{caption}}}')
            latex.append('\\renewcommand{\\arraystretch}{1.2}')
            latex.append(f'\\begin{{tabular}}{{@{{}}>{{\\ }}>{{\\ }}{col_spec}<{{\\ }}<{{\\ }}@{{}}}}')

            # Headers with navy background
            white_headers = ['\\textcolor{white}{\\textbf{' + h + '}}' for h in headers]
            latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers)} \\\\')
            latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')

            # Data rows with alternating colors
            for i, row in enumerate(rows):
                if i % 2 == 1:
                    latex.append(f'\\rowcolor{{snapLightGray}} {" & ".join(row)} \\\\')
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

    def _restore_images(self, text: str, image_map: Dict) -> str:
        """Restore image placeholders"""
        for placeholder, image_data in image_map.items():
            path = image_data['path']
            caption = image_data.get('caption', '')
            width = image_data.get('width', '0.8')

            latex = f"""
\\begin{{figure}}[h]
\\centering
\\includegraphics[width={width}\\textwidth]{{{path}}}
"""
            if caption and caption != '_':
                latex += f"\\caption{{{caption}}}\n"
            latex += "\\end{figure}\n"

            text = text.replace(placeholder, latex)

        return text

    def _copy_assets(self, work_dir: str, structure: Dict[str, Any]):
        """Copy logo and other assets to working directory"""
        # Copy SnapLogic logo
        logo_src = self.assets_dir / "logos" / "snaplogic-logo-blue.png"
        if logo_src.exists():
            shutil.copy(logo_src, work_dir)

        # Copy customer logo if specified
        customer_logo = structure.get('customer_logo', '')
        if customer_logo and os.path.exists(customer_logo):
            dest = Path(work_dir) / Path(customer_logo).name
            shutil.copy(customer_logo, dest)

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
