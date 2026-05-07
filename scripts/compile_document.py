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

# Phase 3 Migration: ContentProcessor now required (old methods removed)
# Content processing is handled by latex-content-processor skill


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
            self.doc_type = doc_type  # Store for ContentProcessor access

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
            import traceback
            print(f"Error: {str(e)}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
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
        # Require a separator row (|---|) to avoid false positives from code blocks / config examples
        has_unwrapped = bool(re.search(r'\|[-: ]+\|', content_str))
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

                # Add "Appendices" as an unnumbered TOC section header with explicit line break.
                # \par\noindent...\par ensures it occupies its own line, not flowing into next entry.
                content.append('\\addtocontents{toc}{\\protect\\vspace{0.3cm}}')
                content.append('\\addtocontents{toc}{\\protect\\par\\noindent\\protect\\textbf{Appendices}\\protect\\par}')
                content.append('\\addtocontents{toc}{\\protect\\vspace{0.1cm}}')

                appendix_started = True

                # Strip redundant "Appendix X: " prefix from subsection titles.
                # After \appendix, LaTeX auto-numbers sections with letters (A, B, C...).
                # Keeping "Appendix A:" in the title causes double-letter collision in heading and TOC.
                import re as _re
                for appendix in section.get('subsections', []):
                    content.append("\\newpage")
                    appendix = dict(appendix)
                    appendix['title'] = _re.sub(r'^Appendix\s+[A-Z][.:]\s*', '', appendix.get('title', ''))
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
        Process content through complete markdown/LaTeX pipeline using ContentProcessor.

        Delegates to latex-content-processor skill which handles:
        - Table rendering (simple style, with emphasis options)
        - Image extraction and figure generation
        - Highlight boxes (info, success, warning, note, KPI, feature)
        - List processing (bullet/numbered, 4 levels deep)
        - Markdown formatting (**bold**, *italic*)
        - Cross-reference extraction and restoration
        - LaTeX special character escaping
        """
        if not text:
            return ""

        # Use external ContentProcessor for all content processing
        sys.path.insert(0, str(self.skill_dir.parent / 'latex-content-processor' / 'scripts'))
        from content_processor import ContentProcessor, ProcessingContext
        from brand_config import LATEX_COLORS

        processor = ContentProcessor()
        context = ProcessingContext(
            content=text,
            doc_type=self.doc_type if hasattr(self, 'doc_type') else 'general',
            brand_colors=LATEX_COLORS,
            image_counter=self.image_counter,
            table_counter=self.table_counter,
            global_image_map=self.global_image_map,
            table_registry=self.table_registry
        )
        result = processor.process_content(context)

        # Update state from result
        self.image_counter = result.updated_image_counter
        self.table_counter = result.updated_table_counter
        self.global_image_map.update(result.image_map)

        return result.processed_content

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
        if customer_logo:
            logo_path = Path(customer_logo)
            if not logo_path.is_absolute() or not logo_path.exists():
                logo_path = self.skill_dir / customer_logo
            if logo_path.exists():
                dest = Path(work_dir) / logo_path.name
                shutil.copy(str(logo_path), dest)

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
                if not source_path.exists():
                    # 4. Recursive search in assets/images subdirectories (e.g. assets/images/airbus_rfp/)
                    filename = Path(image_path).name
                    found = list((self.assets_dir / 'images').rglob(filename)) if (self.assets_dir / 'images').exists() else []
                    if found:
                        source_path = found[0]

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
                text=True,
                encoding='utf-8',
                errors='replace'
            )

            # pdflatex returns non-zero even for warnings
            # Only fail if PDF doesn't exist (fatal errors)
            pdf_file = Path(work_dir) / "document.pdf"
            if result.returncode != 0 and not pdf_file.exists():
                # Print relevant error lines
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
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
            with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
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
