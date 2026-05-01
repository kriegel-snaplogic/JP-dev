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
        self.table_registry = {}  # Maps table caption to (table_num, label)

    def compile(self, input_json: str, output_pdf: str, doc_type: str = "general",
                font_size: str = "10pt", paper_size: str = "a4paper",
                color_scheme: str = "default", title_page_style: str = "navy") -> Dict[str, Any]:
        """
        Compile JSON to PDF

        Args:
            input_json: Path to input JSON file (monolithic JSON or manifest)
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
            raw_structure = json.load(f)

        # Detect and resolve manifest
        if self._is_manifest(raw_structure):
            structure = self._resolve_manifest(input_json, raw_structure)
        else:
            structure = raw_structure

        # Create temp working directory
        work_dir = tempfile.mkdtemp(prefix='snaplogic_doc_')

        try:
            # Reset global state for new compilation
            self.image_counter = 0
            self.global_image_map = {}
            self.table_counter = 0
            self.table_registry = {}

            # Pre-scan document to build table registry (for cross-references)
            self._build_table_registry(structure)

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

    def _is_manifest(self, structure: Dict[str, Any]) -> bool:
        """Check if JSON structure is a manifest (vs monolithic document)"""
        return "structure" in structure and isinstance(structure.get("structure"), list)

    def _resolve_manifest(self, manifest_path: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve manifest by loading all referenced content blocks and merging into monolithic structure

        Args:
            manifest_path: Path to manifest file (for resolving relative paths)
            manifest: Manifest structure with metadata, variables, and structure array

        Returns:
            Monolithic document structure ready for LaTeX compilation
        """
        manifest_dir = Path(manifest_path).parent
        content_library_root = manifest_dir.parent.parent  # documents/airbus -> content_library

        # Start with manifest metadata
        resolved = {
            "title": manifest.get("metadata", {}).get("title", "Untitled"),
            "author": manifest.get("metadata", {}).get("author", ""),
            "date": manifest.get("metadata", {}).get("date", ""),
            "version": manifest.get("metadata", {}).get("version", "1.0"),
            "sections": []
        }

        # Get variables for substitution
        variables = manifest.get("variables", {})

        # Process structure array
        for section_ref in manifest.get("structure", []):
            section_type = section_ref.get("section_type")

            if section_type == "title_page":
                # Title page - load from library and add to metadata
                resolved["title_page"] = self._load_and_substitute(
                    content_library_root, section_ref, variables
                )
            elif section_type == "management_summary":
                # Management summary - becomes abstract
                content = self._load_and_substitute(
                    content_library_root, section_ref, variables
                )
                resolved["abstract"] = content.get("content", {}).get("content", "")
            elif section_type == "section":
                # Regular section - may have subsections
                if "path" in section_ref:
                    # Single content block as section
                    section_content = self._load_and_substitute(
                        content_library_root, section_ref, variables
                    )
                    resolved["sections"].append(self._convert_to_section(section_content))
                else:
                    # Section with subsections
                    section = {
                        "title": section_ref.get("title", "Untitled Section"),
                        "subsections": []
                    }
                    for subsection_ref in section_ref.get("subsections", []):
                        subsection_content = self._load_and_substitute(
                            content_library_root, subsection_ref, variables
                        )
                        section["subsections"].append(self._convert_to_subsection(subsection_content))
                    resolved["sections"].append(section)
            elif section_type == "appendix":
                # Appendix - load and add to sections as appendix
                appendix_content = self._load_and_substitute(
                    content_library_root, section_ref, variables
                )
                if "appendices" not in resolved:
                    resolved["appendices"] = []
                resolved["appendices"].append(self._convert_to_section(appendix_content))

        return resolved

    def _load_and_substitute(self, content_library_root: Path,
                            section_ref: Dict[str, Any],
                            variables: Dict[str, str]) -> Dict[str, Any]:
        """
        Load content block from library and perform variable substitution

        Args:
            content_library_root: Root of content library
            section_ref: Section reference with path
            variables: Variables for substitution

        Returns:
            Content block with variables substituted
        """
        if section_ref.get("source") != "library":
            raise ValueError(f"Only 'library' source supported, got: {section_ref.get('source')}")

        block_path = content_library_root / section_ref["path"]
        with open(block_path, 'r') as f:
            block = json.load(f)

        # Perform variable substitution on content
        block_str = json.dumps(block)
        for var_name, var_value in variables.items():
            block_str = block_str.replace(f"{{{{{var_name}}}}}", var_value)

        return json.loads(block_str)

    def _convert_to_section(self, content_block: Dict[str, Any]) -> Dict[str, Any]:
        """Convert content block to section format expected by compiler"""
        content = content_block.get("content", {})
        return {
            "title": content.get("title", "Untitled"),
            "content": content.get("content", ""),
            "subsections": content.get("subsections", [])
        }

    def _convert_to_subsection(self, content_block: Dict[str, Any]) -> Dict[str, Any]:
        """Convert content block to subsection format expected by compiler"""
        content = content_block.get("content", {})
        return {
            "title": content.get("title", "Untitled"),
            "content": content.get("content", "")
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
        customer_logo = structure.get('customer_logo', '')

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
                content.append(f"{{\\large Prepared for: {customer_name}}}\\\\[0.5cm]")
                # Add customer logo if provided
                if customer_logo:
                    logo_filename = os.path.basename(customer_logo)
                    content.append(f"\\includegraphics[height=1.5cm]{{{logo_filename}}}\\\\[1cm]")

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
                content.append(f"{{\\large Prepared for: {customer_name}}}\\\\[0.5cm]")
                # Add customer logo if provided
                if customer_logo:
                    logo_filename = os.path.basename(customer_logo)
                    content.append(f"\\includegraphics[height=1.5cm]{{{logo_filename}}}\\\\[1cm]")

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

    def _build_table_registry(self, structure: Dict[str, Any]) -> None:
        """Pre-scan document to build table caption → label registry for cross-references"""
        content_str = json.dumps(structure)

        # Find all [TABLE:...] tags
        table_pattern = r'\[TABLE:([^\]]+)\]'

        table_num = 0
        for match in re.finditer(table_pattern, content_str):
            table_def = match.group(1)
            parts = table_def.split(':')

            # Parse: style:caption:emphasis:label or style:caption::label
            # Caption can contain colons, so we need to be smart
            if len(parts) < 2:
                continue

            style = parts[0]

            # Find the label (last non-empty part that looks like a label with dashes)
            label = None
            label_idx = -1
            for i in range(len(parts) - 1, 0, -1):
                part = parts[i].strip()
                if part and ',' not in part and ' ' not in part and ('-' in part or part.isdigit()):
                    # Looks like a label (has dashes, no spaces, no commas)
                    label = part
                    label_idx = i
                    break

            # Caption is everything between style and label (or style and end if no label)
            if label_idx > 1:
                # We found a label, caption is parts[1] to parts[label_idx-1 or label_idx-2 if empty]
                # Check if there's an empty part before label (:: syntax)
                if label_idx >= 2 and parts[label_idx - 1] == '':
                    caption_parts = parts[1:label_idx-1]
                else:
                    caption_parts = parts[1:label_idx]
            else:
                # No label, caption is everything after style
                caption_parts = parts[1:]

            caption = ':'.join(caption_parts).strip()

            # Skip if caption is empty or _
            if not caption or caption == '_':
                continue

            table_num += 1
            actual_label = label if label else str(table_num)

            # Register caption → (table_num, label)
            self.table_registry[caption] = (table_num, actual_label)

    def _generate_abstract(self, structure: Dict[str, Any]) -> str:
        """Generate management summary or abstract"""
        summary = structure.get('management_summary') or structure.get('abstract')

        if not summary:
            return ""

        # Process content through markdown pipeline
        content = self._process_content(summary)

        return f"""
\\phantomsection
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
            # Check if this is the "Appendices" section
            is_appendices_section = (section.get('title') == 'Appendices')
            # Check if this is Management Summary (should be unnumbered)
            is_mgmt_summary = (section.get('title') == 'Management Summary')

            if is_mgmt_summary:
                # Management Summary - unnumbered but with TOC link and label
                title = self._escape_latex(section.get('title', ''))
                content.append('\\phantomsection')
                content.append(f'\\section*{{{title}}}')
                content.append('\\addcontentsline{toc}{section}{Management Summary}')
                content.append('\\label{sec:mgmt-summary}')

                # Add content
                if section.get('content'):
                    content.append(self._process_content(section['content']))

                # Process subsections if any
                for subsection in section.get('subsections', []):
                    content.append(self._process_section(subsection, level=2))

                content.append("\\newpage")
            elif is_appendices_section:
                # Start appendix mode (switches to letter numbering: A, B, C...)
                content.append('\\appendix')

                # Add "Appendices" as an unnumbered TOC section header
                # This creates visual separation in the TOC without rendering a page header
                content.append('\\addtocontents{toc}{\\protect\\vspace{0.3cm}}')  # Add spacing before appendices
                content.append('\\addtocontents{toc}{\\protect\\textbf{Appendices}}')  # Bold "Appendices" header
                content.append('\\addtocontents{toc}{\\protect\\vspace{0.1cm}}')  # Small spacing after header

                appendix_started = True

                # Process subsections directly as top-level appendix sections
                # Skip rendering the "Appendices" header itself
                for appendix in section.get('subsections', []):
                    content.append("\\newpage")
                    # Process as top-level section (level=1) so it gets letter numbering
                    content.append(self._process_section(appendix, level=1))
            else:
                section_counter += 1

                # Page break before each section (except first)
                if section_counter > 1:
                    content.append("\\newpage")

                # Process section recursively (handles subsections)
                content.append(self._process_section(section, level=1, section_num=section_counter))

        return '\n\n'.join(content)

    def _process_section(self, section: Dict[str, Any], level: int = 1, section_num: int = None, parent_is_appendices: bool = False) -> str:
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

        title_raw = section.get('title', '')
        title = self._escape_latex(title_raw)

        # Special handling: if parent section is "Appendices", promote subsections to \section level
        # This allows LaTeX's \appendix command to apply letter numbering properly
        if parent_is_appendices and level == 2:
            # Promote from subsection to section for appendices
            cmd = 'section'
        else:
            cmd = latex_commands.get(level, 'subparagraph')

        # Add label for top-level sections
        if level == 1 and section_num:
            parts.append(f"\\{cmd}{{{title}}}\\label{{sec:{section_num}}}")
        else:
            parts.append(f"\\{cmd}{{{title}}}")

        # Section content
        if section.get('content'):
            parts.append(self._process_content(section['content']))

        # Check if this section is "Appendices" to pass down to children
        is_appendices_section = (level == 1 and 'Appendices' == title_raw)

        # Recursive subsections
        for subsection in section.get('subsections', []):
            parts.append(self._process_section(subsection, level=level+1, parent_is_appendices=is_appendices_section))

        # Handle subsubsections
        for subsubsection in section.get('subsubsections', []):
            parts.append(self._process_section(subsubsection, level=level+1, parent_is_appendices=is_appendices_section))

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
        0. Clean HTML/markdown artifacts
        1. Extract images and boxes (preserve them)
        2. Process markdown
        3. Escape LaTeX special characters
        4. Restore boxes and images
        """
        if not text:
            return ""

        # Step 0: Clean HTML/markdown artifacts before processing
        text = self._clean_html_artifacts(text)

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

    def _clean_html_artifacts(self, text: str) -> str:
        """
        Clean HTML/markdown artifacts that don't translate to LaTeX.

        Converts:
        - <br/> tags to LaTeX line breaks (\\)
        - <br> tags (without slash) to LaTeX line breaks
        - Multiple consecutive line breaks to single LaTeX breaks
        """
        if not text:
            return text

        # Convert HTML line breaks to LaTeX line breaks
        # Handle both <br/> and <br> variants
        text = re.sub(r'<br\s*/?\s*>', r'\\\\', text, flags=re.IGNORECASE)

        # Clean up multiple consecutive line breaks (max 2)
        # This prevents things like \\\\\\\\ from <br/><br/><br/>
        text = re.sub(r'(\\\\){3,}', r'\\\\', text)

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
                'width': groups[2] if len(groups) > 2 and groups[2] else '1.0',
                'label': groups[3] if len(groups) > 3 and groups[3] else None  # Optional semantic label
            }
            image_map[placeholder] = image_data
            # Also store in global map for restoration phase
            self.global_image_map[placeholder] = image_data
            return placeholder

        # Pattern: [IMAGE:path:caption:width:label] where width and label are optional
        # Captions can contain colons! Use .+? for caption to match minimally up to :: or :]
        # Groups: (path, rest_of_params)
        pattern = r'\[IMAGE:([^:]+):(.+?)\]'

        def extract_image_params(match):
            self.image_counter += 1
            placeholder = f"@IMAGE{self.image_counter}@"

            path = match.group(1)
            rest = match.group(2)

            # Parse rest: could be "caption", "caption:width", "caption:width:label", "caption::label"
            parts = rest.split(':')

            caption = None
            width = '1.0'
            label = None

            if len(parts) == 1:
                # Just caption
                caption = parts[0]
            elif len(parts) == 2:
                # caption:X where X is width or label
                caption = parts[0]
                second = parts[1]
                # Check if it looks like a width (number) or label (has dashes)
                try:
                    float(second)
                    width = second
                except:
                    if '-' in second or '_' in second:
                        label = second
                    else:
                        # Could be part of caption
                        caption = rest
            else:
                # 3+ parts: could be "caption:with:colons:width:label"
                # Look for patterns
                last = parts[-1]
                second_last = parts[-2] if len(parts) >= 2 else None

                # Check if last part is label (has dashes)
                if last and ('-' in last or '_' in last):
                    label = last
                    # Check if second-last is width
                    if second_last:
                        try:
                            float(second_last)
                            width = second_last
                            caption = ':'.join(parts[:-2])
                        except:
                            # Second-last is part of caption
                            caption = ':'.join(parts[:-1])
                    else:
                        caption = ':'.join(parts[:-1])
                else:
                    # Last part might be width
                    try:
                        float(last)
                        width = last
                        caption = ':'.join(parts[:-1])
                    except:
                        # All is caption
                        caption = rest

            image_data = {
                'path': path,
                'caption': caption if caption else '',
                'width': width,
                'label': label
            }
            image_map[placeholder] = image_data
            self.global_image_map[placeholder] = image_data
            return placeholder

        text = re.sub(pattern, extract_image_params, text)

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

        # Only process explicitly wrapped tables: [TABLE:style:caption:emphasis:label]
        # Captions can contain colons! Format is: [TABLE:style:caption::label] or [TABLE:style:caption:emphasis:label]
        # The :: separates caption from label when there's no emphasis
        # Match: [TABLE:style:<ANYTHING_INCLUDING_COLONS>:optional_more_parts]
        # We'll parse caption vs emphasis vs label in the replace_table function
        table_pattern = r'\[TABLE:([^:]+):(.+?)\](.*?)\[/TABLE\]'

        def replace_table(match):
            self.table_counter += 1
            style, rest, table_md = match.groups()

            # Parse rest which is: "caption" or "caption:emphasis" or "caption::label" or "caption:emphasis:label"
            # Captions can contain colons, so we need to find where caption ends
            # Caption ends at :: (empty emphasis before label) or at the LAST single : before a label-like string

            # Split by : and work backwards to find label and emphasis
            parts = rest.split(':')
            caption = None
            emphasis = None
            label = None

            if len(parts) == 1:
                # Just caption
                caption = parts[0]
            elif len(parts) == 2:
                # caption:X where X is either emphasis or label
                # Check if second part looks like a label (has hyphens) or emphasis (has commas/equals)
                if '=' in parts[1] or ',' in parts[1]:
                    caption, emphasis = parts
                elif parts[1] and ('-' in parts[1] or '_' in parts[1]):
                    caption, label = parts
                else:
                    # Ambiguous or empty - if empty, it's "caption:" which means just caption
                    caption = parts[0]
                    if parts[1]:
                        emphasis = parts[1]
            else:
                # 3+ parts: could be "caption:with:colons::label" or "caption:emphasis:label" etc.
                # Look for :: pattern (empty string in parts)
                if '' in parts:
                    # Found :: - split at that point
                    empty_idx = parts.index('')
                    caption = ':'.join(parts[:empty_idx])
                    # After :: is the label
                    label = ':'.join(parts[empty_idx+1:]) if empty_idx+1 < len(parts) else None
                else:
                    # No :: - assume last part is label, second-to-last is emphasis (if it looks like emphasis)
                    # Otherwise last part is emphasis and everything else is caption
                    last = parts[-1]
                    if last and ('-' in last or '_' in last):
                        # Last part looks like label
                        label = last
                        if len(parts) >= 3:
                            second_last = parts[-2]
                            if '=' in second_last or ',' in second_last:
                                emphasis = second_last
                                caption = ':'.join(parts[:-2])
                            else:
                                # Second-last is part of caption
                                caption = ':'.join(parts[:-1])
                        else:
                            caption = parts[0]
                    else:
                        # Last part might be emphasis or part of caption
                        if '=' in last or ',' in last:
                            emphasis = last
                            caption = ':'.join(parts[:-1])
                        else:
                            # All is caption
                            caption = rest

            # Combine style and emphasis if present
            if emphasis:
                full_style = f"{style}:{emphasis}"
            else:
                full_style = style

            table_id = abs(hash(f"{style}{caption}{table_md}")) % 100000
            # Include table number AND label in placeholder
            # Use || as delimiter between style and caption to avoid colon conflicts
            label_part = f":{label}" if label else ""
            return f"@TABLE:{full_style}||{caption}:{table_id}:{self.table_counter}{label_part}@{table_md.strip()}@TABLEEND:{table_id}@"

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
        header_counter = 0

        while i < len(lines):
            line = lines[i]

            # Check if this line is a paragraph header
            # Pattern: short standalone line (< 80 chars), followed by blank line(s)
            # This catches section headers like "Certifications & Compliance", "Support Model" etc.
            stripped = line.strip()
            if stripped and len(stripped) < 80 and not re.match(r'^(\s*)[•\-*]\s+', line) and not re.match(r'^(\s*)\d+\.\s+', line):
                # Check if this looks like a header (not starting with lowercase, not a long sentence)
                # Headers typically: Title Case or ALL CAPS, and end without punctuation (except :)
                if stripped[0].isupper() and (not stripped.endswith('.') or stripped.endswith(':')):
                    # Look ahead: is this followed by blank line(s)?
                    j = i + 1
                    has_blank_after = False
                    while j < len(lines) and not lines[j].strip():
                        has_blank_after = True
                        j += 1

                    # If followed by blank line, treat as header
                    if has_blank_after and j < len(lines):
                        # This is a paragraph header! Use placeholder to protect it
                        placeholder = f'@PARAHEADER:{header_counter}@{stripped}@PARAHEADEREND:{header_counter}@'
                        result.append(placeholder)
                        header_counter += 1
                        i += 1
                        continue

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

            # Handle blank lines: only continue if next non-blank is a list item
            if not line.strip():
                # Look ahead to see if the next non-blank line is a list item
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1

                if j < len(lines) and re.match(r'^(\s*)(?:[•\-*]|\d+\.)\s+', lines[j]):
                    # Next item is a list item, include the blank line and continue
                    list_lines.append(line)
                    i += 1
                    continue
                else:
                    # Next item is NOT a list item, stop here
                    break

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
        """Escape LaTeX special characters (but not @ which we use for placeholders)"""
        if not text or not isinstance(text, str):
            return ""

        # Protect LaTeX line breaks (\\) from being escaped
        # Replace them with a placeholder first
        LINE_BREAK_PLACEHOLDER = '@@@LINEBREAK@@@'
        text = text.replace('\\\\', LINE_BREAK_PLACEHOLDER)

        # Escape LaTeX special characters but NOT @
        # @ is safe in LaTeX and we use it for placeholder markers
        escaped = text
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

        # Restore LaTeX line breaks
        escaped = escaped.replace(LINE_BREAK_PLACEHOLDER, '\\\\')

        return escaped

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
        # First pass: convert FEATURE placeholders to LaTeX, then add row breaks
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
        # Pattern: @TABLE:style:caption:id:num:label@content@TABLEEND:id@
        # Both style and caption can contain colons!
        # Strategy: Match from the END backwards - id and num are always \d+
        # Pattern breakdown:
        #   @TABLE: - literal start
        #   (.+?) - style (non-greedy, can have colons)
        #   : - separator
        #   (.+?) - caption (non-greedy, can have colons)
        #   :(\d+):(\d+) - :id:num (digits mark the boundary!)
        #   (?::([^@]+))? - optional :label
        #   @ - boundary before content
        #   (.*?) - table content
        #   @TABLEEND:\3@ - end marker with id reference
        # Pattern: @TABLE:style||caption:id:num:label@content@TABLEEND:id@
        # Using || as delimiter between style and caption to handle colons in both
        table_pattern = r'@TABLE:(.+?)\|\|(.+?):(\d+):(\d+)(?::([^@]+))?@(.*?)@TABLEEND:\3@'

        def restore_table(match):
            style, caption, table_id, table_num, label, table_md = match.groups()

            # Check for landscape prefix
            is_landscape = style.startswith('landscape-')
            if is_landscape:
                style = style.replace('landscape-', '', 1)

            # Check for multipage prefix (enables longtable for page-spanning tables)
            is_multipage = style.startswith('multipage-')
            if is_multipage:
                style = style.replace('multipage-', '', 1)

            # Parse style and emphasis options
            # Format: "simple:first-bold,last-jade,total-row,widths=1,2,4,1.5" or just "simple"
            style_parts = style.split(':')
            base_style = style_parts[0]
            emphasis_opts = style_parts[1].split(',') if len(style_parts) > 1 else []

            # Parse emphasis options
            first_bold = 'first-bold' in emphasis_opts
            last_color = None
            manual_widths = None
            for opt in emphasis_opts:
                if opt.startswith('last-'):
                    last_color = opt.split('-')[1]  # jade, orange, blue, navy
                elif opt.startswith('widths='):
                    # Parse manual column widths: widths=1,2,4,1.5
                    width_str = opt.split('=')[1]
                    manual_widths = [float(w.strip()) for w in width_str.split(',')]
            total_row = 'total-row' in emphasis_opts

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
                # Split by | but keep empty cells (don't filter with if c.strip())
                all_cells = [c.strip() for c in line.split('|')]
                # Remove leading/trailing empty cells from split artifacts
                cells = all_cells[1:-1] if len(all_cells) > 2 and all_cells[0] == '' and all_cells[-1] == '' else all_cells
                cells = [c if c else ' ' for c in cells]  # Replace empty cells with space
                if cells:
                    rows.append(cells)

            # Generate LaTeX table based on style
            num_cols = len(headers)

            # Validate table constraints
            if is_landscape:
                if num_cols > 8:
                    return f"ERROR: Landscape table has {num_cols} columns (max 8 allowed)"
                if len(rows) > 25:
                    return f"ERROR: Landscape table has {len(rows)} rows (max 25 allowed)"
            else:
                # Portrait mode column limit
                if num_cols > 6:
                    return f"ERROR: Portrait table has {num_cols} columns (max 6 allowed)"

            # Column specification - use full available width
            if num_cols > 0:
                if is_landscape:
                    # Landscape: tabularx with full \linewidth and smart column widths
                    use_tabularx = True
                    table_width = '\\linewidth'

                    # Check for manual width override
                    if manual_widths and len(manual_widths) == num_cols:
                        # Use manually specified widths
                        widths = manual_widths
                    else:
                        # Auto-calculate widths based on TOTAL content volume per column
                        widths = []
                        for col_idx in range(num_cols):
                            # Sum total characters across header + all cells in this column
                            header_len = len(headers[col_idx]) if col_idx < len(headers) else 0
                            total_cell_chars = sum([len(row[col_idx]) if col_idx < len(row) else 0 for row in rows])
                            total_chars = header_len + total_cell_chars

                            # Also consider the max single cell
                            cell_lengths = [len(row[col_idx]) if col_idx < len(row) else 0 for row in rows]
                            max_cell_len = max(cell_lengths) if cell_lengths else 0
                            max_len = max(header_len, max_cell_len)

                            # Weight: 70% total volume, 30% max single cell
                            weighted_score = (total_chars * 0.7) + (max_len * 0.3)

                            # Convert score to relative width (landscape has more space, so tighter thresholds)
                            if weighted_score < 80:
                                widths.append(0.5)  # Tiny columns
                            elif weighted_score < 150:
                                widths.append(0.7)  # Short columns
                            elif weighted_score < 300:
                                widths.append(1.0)  # Medium columns
                            elif weighted_score < 600:
                                widths.append(1.3)  # Long columns
                            elif weighted_score < 1000:
                                widths.append(1.6)  # Very long columns
                            else:
                                widths.append(2.0)  # Massive columns

                    total_width = sum(widths)
                    # Normalize so they sum to num_cols (required by tabularx)
                    normalized = [w * num_cols / total_width for w in widths]

                    # Build column spec with proportional X columns + raggedright to prevent hyphenation
                    col_spec = ''.join([f'>{{\\hsize={n:.2f}\\hsize\\raggedright\\arraybackslash\\setlength{{\\parindent}}{{0pt}}}}X' for n in normalized])
                else:
                    # Portrait: use proportional column widths based on content
                    use_tabularx = True  # Enable tabularx for smart column sizing
                    table_width = '\\linewidth'

                    # Check for manual width override
                    if manual_widths and len(manual_widths) == num_cols:
                        # Use manually specified widths
                        widths = manual_widths
                    else:
                        # Auto-calculate widths based on TOTAL content volume per column
                        # (not just max single cell - that misses columns with lots of text across many cells)
                        widths = []
                        for col_idx in range(num_cols):
                            # Sum total characters across header + all cells in this column
                            header_len = len(headers[col_idx]) if col_idx < len(headers) else 0
                            total_cell_chars = sum([len(row[col_idx]) for row in rows if col_idx < len(row)])
                            total_chars = header_len + total_cell_chars

                            # Also consider the max single cell (for cells with line breaks or long words)
                            max_cell_len = max([len(row[col_idx]) for row in rows if col_idx < len(row)], default=0)
                            max_len = max(header_len, max_cell_len)

                            # Weight: 70% total volume, 30% max single cell
                            # This balances "this column has tons of text" vs "this column has one huge cell"
                            weighted_score = (total_chars * 0.7) + (max_len * 0.3)

                            # Convert score to relative width
                            # Scale is roughly: 0-200 = small, 200-500 = medium, 500-1000 = large, 1000+ = huge
                            if weighted_score < 100:
                                widths.append(0.6)  # Tiny columns (IDs, percentages)
                            elif weighted_score < 200:
                                widths.append(0.8)  # Short columns
                            elif weighted_score < 400:
                                widths.append(1.0)  # Medium columns
                            elif weighted_score < 700:
                                widths.append(1.5)  # Long columns
                            elif weighted_score < 1200:
                                widths.append(2.0)  # Very long columns
                            else:
                                widths.append(2.8)  # Massive text-heavy columns

                    total_width = sum(widths)
                    # Normalize so they sum to num_cols (required by tabularx)
                    normalized = [w * num_cols / total_width for w in widths]

                    # Build column spec with proportional X columns
                    col_spec = ''.join([f'>{{\\hsize={n:.2f}\\hsize\\raggedright\\arraybackslash\\setlength{{\\parindent}}{{0pt}}}}X' for n in normalized])
            else:
                use_tabularx = False
                col_spec = 'l'

            latex = []

            # Start landscape environment if needed
            if is_landscape:
                latex.append('\\begin{landscape}')

            # For multipage tables, use longtable instead of table float
            if is_multipage:
                # longtable doesn't use \begin{table}, caption goes after \begin{longtable}
                latex.append('\\renewcommand{\\arraystretch}{1.2}')
                # Caption will be added after longtable begins
            else:
                # Regular table float
                if is_landscape:
                    # For landscape, use full page width with minimal margins
                    latex.append('\\begin{table}[H]')
                    # No centering for landscape - use full width
                else:
                    latex.append('\\begin{table}[H]')
                    latex.append('\\centering')

                # Caption and label for regular tables
                if caption and caption != '_':
                    latex.append(f'\\caption{{{caption}}}')
                else:
                    latex.append(f'\\caption{{}}')

                # Always add numeric label first, then semantic label if provided
                latex.append(f'\\label{{tab:{table_num}}}')
                if label:
                    latex.append(f'\\label{{tab:{label}}}')
                    # Register caption → label mapping for cross-references
                    if caption and caption != '_':
                        self.table_registry[caption] = (table_num, label)
                else:
                    # Register caption → table number mapping
                    if caption and caption != '_':
                        self.table_registry[caption] = (table_num, str(table_num))

                latex.append('\\renewcommand{\\arraystretch}{1.2}')

            # Helper function to format cell with emphasis
            def format_cell(cell_text, is_first_col=False, is_last_col=False, is_total_row=False):
                formatted = cell_text
                # First column bold
                if is_first_col and first_bold:
                    formatted = f'\\textbf{{{formatted}}}'
                # Last column with color background (applied at row level)
                # Total row makes everything bold
                if is_total_row:
                    formatted = f'\\textbf{{{formatted}}}'
                return formatted

            # Style-specific rendering
            if base_style == 'minimal':
                # Minimal: No colors, horizontal rules only (booktabs style)
                if use_tabularx:
                    latex.append(f'\\begin{{tabularx}}{{{table_width}}}{{{col_spec}}}')
                else:
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

                if is_multipage:
                    # Use longtable for multi-page tables
                    # longtable needs p{width} columns, not tabularx X columns
                    # Calculate proper column widths for longtable
                    if manual_widths and len(manual_widths) == num_cols:
                        widths = manual_widths
                    # else: widths already calculated above

                    # Convert relative widths to actual cm widths (portrait: ~16cm usable width, landscape: ~25cm)
                    total_width_cm = 25.0 if is_landscape else 16.0
                    total_relative = sum(widths)
                    actual_widths = [w * total_width_cm / total_relative for w in widths]

                    # Build longtable column spec with left-aligned p{width} columns
                    longtable_col_spec = ''.join([f'>{{\\raggedright\\arraybackslash}}p{{{w:.1f}cm}}' for w in actual_widths])

                    latex.append(f'\\begin{{longtable}}{{{longtable_col_spec}}}')
                    # Caption for longtable goes AFTER \begin{longtable}
                    if caption and caption != '_':
                        latex.append(f'\\caption{{{caption}}}')
                        # Always add numeric label first
                        latex.append(f'\\label{{tab:{table_num}}}')
                        # Then semantic label if provided
                        if label:
                            latex.append(f'\\label{{tab:{label}}} \\\\')
                            # Register caption → label mapping for cross-references
                            self.table_registry[caption] = (table_num, label)
                        else:
                            latex.append(' \\\\')
                            # Register caption → table number mapping
                            self.table_registry[caption] = (table_num, str(table_num))
                    # Header row (always use navy for consistency)
                    white_headers = [f'\\textcolor{{white}}{{\\textbf{{{h}}}}}' for h in headers]
                    latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers)} \\\\')
                    latex.append('\\arrayrulecolor{snapNavy!30}\\midrule')
                    latex.append('\\endfirsthead')  # End of first page header
                    # Repeated header on continuation pages
                    latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers)} \\\\')
                    latex.append('\\arrayrulecolor{snapNavy!30}\\midrule')
                    latex.append('\\endhead')  # End of continuation header
                    # Data rows with zebra striping (but skip category headers in zebra count)
                    zebra_counter = 0
                    for i, row in enumerate(rows):
                        is_total = (i == len(rows) - 1 and total_row)

                        # Check if this is a category header row (ALL CAPS first cell, empty others)
                        is_category_header = False
                        if len(row) > 0 and row[0].strip():
                            first_cell = row[0].strip()
                            # Check if ALL CAPS and other cells are empty/whitespace
                            if first_cell.isupper() and all(not cell.strip() for cell in row[1:]):
                                is_category_header = True

                        # Format cells with emphasis
                        formatted_cells = []
                        for j, cell in enumerate(row):
                            is_first = (j == 0)
                            is_last = (j == len(row) - 1)
                            formatted = format_cell(cell, is_first, is_last, is_total)

                            # Add cellcolor for last column if specified
                            if is_last and last_color and not is_total and not is_category_header:
                                latex_color = last_col_colors.get(last_color, 'snapBlue!20')
                                formatted = f'\\cellcolor{{{latex_color}}}{formatted}'

                            formatted_cells.append(formatted)

                        # Row rendering with appropriate background
                        if is_total:
                            # Total row: Navy background with white text
                            white_cells = [f'\\textcolor{{white}}{{{c}}}' for c in formatted_cells]
                            latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_cells)} \\\\')
                        elif is_category_header:
                            # Category header: Lighter gray background with bold text
                            bold_cells = [f'\\textbf{{{c}}}' if c.strip() else c for c in formatted_cells]
                            latex.append(f'\\rowcolor{{snapBlue!10}}{" & ".join(bold_cells)} \\\\')
                        else:
                            # Regular rows with zebra striping
                            if zebra_counter % 2 == 1:
                                latex.append(f'\\rowcolor{{snapLightGray}}{" & ".join(formatted_cells)} \\\\')
                            else:
                                latex.append(f'{" & ".join(formatted_cells)} \\\\')
                            zebra_counter += 1
                else:
                    # Regular table
                    if use_tabularx:
                        latex.append(f'\\begin{{tabularx}}{{{table_width}}}{{{col_spec}}}')
                    else:
                        latex.append(f'\\begin{{tabular}}{{{col_spec}}}')
                    white_headers = [f'\\textcolor{{white}}{{\\textbf{{{h}}}}}' for h in headers]
                    latex.append(f'\\rowcolor{{{latex_color}}}{" & ".join(white_headers)} \\\\')
                    latex.append('\\arrayrulecolor{' + latex_color + '!30}\\midrule')
                    for row in rows:
                        latex.append(f'{" & ".join(row)} \\\\')

            elif style == 'bordered':
                # Bordered: Light gray header, all cells have borders
                if use_tabularx:
                    # For tabularx with borders, we need a different approach
                    latex.append(f'\\begin{{tabularx}}{{{table_width}}}{{|{"||".join(["X" for _ in range(num_cols)])}|}}')
                else:
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

                if use_tabularx:
                    latex.append(f'\\begin{{tabularx}}{{{table_width}}}{{{col_spec}}}')
                else:
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
                # Simple: Navy header, alternating rows (white/light gray) with optional emphasis
                if is_multipage:
                    # Use longtable for multi-page tables
                    # Calculate proper column widths for longtable
                    if manual_widths and len(manual_widths) == num_cols:
                        widths = manual_widths
                    # else: widths already calculated above

                    # Convert relative widths to actual cm widths
                    total_width_cm = 25.0 if is_landscape else 16.0
                    total_relative = sum(widths)
                    actual_widths = [w * total_width_cm / total_relative for w in widths]

                    # Build longtable column spec with left-aligned p{width} columns
                    longtable_col_spec = ''.join([f'>{{\\raggedright\\arraybackslash}}p{{{w:.1f}cm}}' for w in actual_widths])

                    latex.append(f'\\begin{{longtable}}{{{longtable_col_spec}}}')
                    # Caption for longtable goes AFTER \begin{longtable}
                    if caption and caption != '_':
                        latex.append(f'\\caption{{{caption}}}')
                        latex.append(f'\\label{{tab:{table_num}}}')
                        if label:
                            latex.append(f'\\label{{tab:{label}}} \\\\')
                            self.table_registry[caption] = (table_num, label)
                        else:
                            latex.append(' \\\\')
                            self.table_registry[caption] = (table_num, str(table_num))
                    # Header row
                    white_headers = [f'\\textcolor{{white}}{{\\textbf{{{h}}}}}' for h in headers]
                    latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers)} \\\\')
                    latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')
                    latex.append('\\endfirsthead')
                    # Repeated header on continuation pages
                    latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers)} \\\\')
                    latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')
                    latex.append('\\endhead')
                else:
                    # Regular table (not multipage)
                    if use_tabularx:
                        latex.append(f'\\begin{{tabularx}}{{{table_width}}}{{{col_spec}}}')
                    else:
                        latex.append(f'\\begin{{tabular}}{{{col_spec}}}')
                    white_headers = [f'\\textcolor{{white}}{{\\textbf{{{h}}}}}' for h in headers]
                    latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers)} \\\\')
                    latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')

                # Color map for last column emphasis
                last_col_colors = {
                    'jade': 'snapJade!20',
                    'orange': 'snapOrange!20',
                    'blue': 'snapBlue!20',
                    'navy': 'snapNavy!20'
                }

                # Track zebra striping (skip category headers in count)
                zebra_counter = 0
                for i, row in enumerate(rows):
                    is_last_row = (i == len(rows) - 1)
                    is_total = is_last_row and total_row

                    # Check if this is a category header row (ALL CAPS first cell, empty others)
                    is_category_header = False
                    if len(row) > 0 and row[0].strip():
                        first_cell = row[0].strip()
                        # Check if ALL CAPS and other cells are empty/whitespace
                        if first_cell.isupper() and all(not cell.strip() for cell in row[1:]):
                            is_category_header = True

                    # Format cells with emphasis
                    formatted_cells = []
                    for j, cell in enumerate(row):
                        is_first = (j == 0)
                        is_last = (j == len(row) - 1)
                        formatted = format_cell(cell, is_first, is_last, is_total)

                        # Add cellcolor for last column if specified
                        if is_last and last_color and not is_total and not is_category_header:
                            latex_color = last_col_colors.get(last_color, 'snapBlue!20')
                            formatted = f'\\cellcolor{{{latex_color}}}{formatted}'

                        formatted_cells.append(formatted)

                    # Row rendering with appropriate background
                    if is_total:
                        # Total row: Navy background with white text
                        white_cells = [f'\\textcolor{{white}}{{{c}}}' for c in formatted_cells]
                        latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_cells)} \\\\')
                    elif is_category_header:
                        # Category header: Lighter gray background with bold text
                        bold_cells = [f'\\textbf{{{c}}}' if c.strip() else c for c in formatted_cells]
                        latex.append(f'\\rowcolor{{snapBlue!10}}{" & ".join(bold_cells)} \\\\')
                    else:
                        # Regular rows with zebra striping
                        if zebra_counter % 2 == 1:
                            latex.append(f'\\rowcolor{{snapLightGray}}{" & ".join(formatted_cells)} \\\\')
                        else:
                            latex.append(f'{" & ".join(formatted_cells)} \\\\')
                        zebra_counter += 1

            # Close table environment
            if is_multipage:
                latex.append('\\end{longtable}')
            else:
                if use_tabularx:
                    latex.append('\\end{tabularx}')
                else:
                    latex.append('\\end{tabular}')
                latex.append('\\end{table}')

            # End landscape environment if needed
            if is_landscape:
                latex.append('\\end{landscape}')

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

        # Restore paragraph headers (bold text before lists)
        header_pattern = r'@PARAHEADER:(\d+)@(.+?)@PARAHEADEREND:\1@'

        def restore_header(match):
            header_id, header_text = match.groups()
            return f'\\textbf{{{header_text}}}\n'

        text = re.sub(header_pattern, restore_header, text)

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
            width = image_data.get('width', '1.0')

            # Sanitize path - replace spaces with underscores to match copied files
            sanitized_path = path.replace(' ', '_')

            latex = f"""
\\begin{{figure}}[H]
\\centering
\\includegraphics[width={width}\\textwidth]{{{sanitized_path}}}
"""
            if caption and caption != '_':
                # Get semantic label if provided, otherwise use numeric label
                semantic_label = image_data.get('label')

                if semantic_label:
                    # Use semantic label (e.g., "citizen-designer")
                    # This is robust - text can say Figure~\ref{fig:citizen-designer}
                    # and LaTeX will resolve to correct number regardless of position
                    latex += f"\\caption{{{caption}}}\\label{{fig:{semantic_label}}}\n"
                else:
                    # Fallback to numeric label for backward compatibility
                    json_num = int(placeholder.replace('@IMAGE', '').replace('@', ''))
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
                # Try multiple locations for relative paths
                # 1. content_library (where most assets live)
                source_path = self.assets_dir.parent / 'content_library' / image_path
                if not source_path.exists():
                    # 2. Skill root directory
                    source_path = self.assets_dir.parent / image_path
                if not source_path.exists():
                    # 3. Already relative to assets_dir
                    source_path = self.assets_dir / image_path

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
        # Figure references with semantic labels: "Figure~\ref{fig:label}"
        # Replace with placeholder @FIGREF:label@
        def extract_semantic_figure_ref(match):
            fig_label = match.group(1)
            return f"@FIGREF:{fig_label}@"

        text = re.sub(r'Figure~\\ref\{fig:([^}]+)\}', extract_semantic_figure_ref, text)

        # Figure references: "Figure X" where X is a number (numeric fallback)
        # Replace with placeholder @FIGREF:X@
        def extract_figure_ref(match):
            fig_num = match.group(1)
            return f"@FIGREF:{fig_num}@"

        text = re.sub(r'\bFigure\s+(\d+)\b', extract_figure_ref, text)

        # Table references with semantic labels: "Table~\ref{tab:label}"
        # Replace with placeholder @TABREF:label@
        def extract_semantic_table_ref(match):
            tab_label = match.group(1)
            return f"@TABREF:{tab_label}@"

        text = re.sub(r'Table~\\ref\{tab:([^}]+)\}', extract_semantic_table_ref, text)

        # Table references by caption: "Table (Caption)" or "Table⁠(Caption)" (thin space U+2009)
        # Look up caption in table_registry and replace with @TABREF:label@
        def extract_table_caption_ref(match):
            caption = match.group(1)
            if caption in self.table_registry:
                table_num, ref_label = self.table_registry[caption]
                return f"@TABREF:{ref_label}@"
            # If caption not found, keep as-is (user might have typo)
            return match.group(0)

        # Match both regular space and thin space (U+2009)
        text = re.sub(r'Table[\s ]+\(([^)]+)\)', extract_table_caption_ref, text)

        # Table references: "Table X" where X is a number (numeric fallback)
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
        # Figure references: @FIGREF:X@ or @FIGREF:semantic-label@ -> Figure~\ref{fig:X}
        # Handles both numeric (backward compat) and semantic labels
        # LaTeX will auto-number based on figure order and hyperref makes it clickable
        # Using ~ for non-breaking space (standard LaTeX practice)
        def restore_figure_ref(match):
            fig_ref = match.group(1)  # Can be number or semantic label
            return f"Figure~\\ref{{fig:{fig_ref}}}"

        text = re.sub(r'@FIGREF:([^@]+)@', restore_figure_ref, text)

        # Table references: @TABREF:X@ or @TABREF:semantic-label@ -> Table~\ref{tab:X}
        # Handles both numeric (backward compat) and semantic labels
        # LaTeX will auto-number based on table order and hyperref makes it clickable
        def restore_table_ref(match):
            tab_ref = match.group(1)  # Can be number or semantic label
            return f"Table~\\ref{{tab:{tab_ref}}}"

        text = re.sub(r'@TABREF:([^@]+)@', restore_table_ref, text)

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
        log_file = Path(work_dir) / "document.log"

        # Run pdflatex three times (for TOC, cross-references, and page numbers)
        for run in range(3):
            result = subprocess.run(
                ['pdflatex', '-interaction=nonstopmode', 'document.tex'],
                cwd=work_dir,
                capture_output=True,
                text=True
            )

            # pdflatex returns non-zero even for warnings
            # Only fail if PDF doesn't exist (fatal errors)
            pdf_file = Path(work_dir) / "document.pdf"
            if result.returncode != 0 and not pdf_file.exists():
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

        # Print warnings to stderr for user awareness
        if log_file.exists():
            with open(log_file, 'r') as f:
                log_content = f.read()
                warnings = [line for line in log_content.split('\n')
                           if 'Warning' in line or ('Error' in line and '!' not in line[:2])]
                if warnings:
                    print("LaTeX warnings:", file=sys.stderr)
                    for warning in warnings[:10]:  # Show first 10 warnings
                        print(f"  {warning}", file=sys.stderr)

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
    font_size = sys.argv[4] if len(sys.argv) > 4 else "10pt"
    paper_size = sys.argv[5] if len(sys.argv) > 5 else "a4paper"
    color_scheme = sys.argv[6] if len(sys.argv) > 6 else "default"

    compiler = SnapLogicDocumentCompiler()
    result = compiler.compile(input_json, output_pdf, doc_type,
                             font_size, paper_size, color_scheme)

    print(json.dumps(result, indent=2))

    if result['status'] != 'success':
        sys.exit(1)


if __name__ == '__main__':
    main()
