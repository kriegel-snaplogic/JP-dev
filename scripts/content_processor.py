#!/usr/bin/env python3
"""
LaTeX Content Processor
Processes markdown-like content with special tags into LaTeX

Extracted from compile_document.py for modular, stateless processing.
"""

import re
from typing import Dict, Any, Tuple, List
from dataclasses import dataclass


@dataclass
class ProcessingContext:
    """Input context for content processing"""
    content: str
    doc_type: str
    brand_colors: Dict[str, str]
    image_counter: int
    table_counter: int
    global_image_map: Dict[str, Any]
    table_registry: Dict[str, Tuple[int, str]]


@dataclass
class ProcessingResult:
    """Output from content processing"""
    processed_content: str
    image_map: Dict[str, Any]
    updated_image_counter: int
    updated_table_counter: int


class ContentProcessor:
    """Processes markdown-like content with special tags into LaTeX"""

    def __init__(self):
        pass

    def process_content(self, context: ProcessingContext) -> ProcessingResult:
        """
        Process content through complete markdown/LaTeX pipeline

        Order matters:
        0. Clean HTML/markdown artifacts
        1. Extract images and boxes (preserve them)
        2. Process markdown
        3. Escape LaTeX special characters
        4. Restore boxes and images
        """
        text = context.content
        if not text:
            return ProcessingResult(
                processed_content="",
                image_map=context.global_image_map,
                updated_image_counter=context.image_counter,
                updated_table_counter=context.table_counter
            )

        # Track counters locally
        image_counter = context.image_counter
        table_counter = context.table_counter

        # Step 0: Clean HTML/markdown artifacts before processing
        text = self._clean_html_artifacts(text)

        # Step 1: Extract images
        text, image_map = self._extract_images(text, context)
        # Update local counter from extraction
        image_counter = max(image_counter, max([int(k.replace('@IMAGE', '').replace('@', ''))
                                                 for k in image_map.keys()], default=image_counter))

        # Step 2: Process highlight boxes (KPI, FEATURE, BOX)
        text = self._process_highlight_boxes(text)

        # Step 3: Process tables
        text, table_counter = self._process_tables(text, context)

        # Step 4: Process lists
        text = self._process_lists(text)

        # Step 5: Process markdown headers (###)
        text = self._process_markdown_headers(text)

        # Step 6: Process markdown formatting (bold, italic)
        text = self._process_markdown_formatting(text)

        # Step 7: Extract cross-references to placeholders (before escaping)
        text = self._extract_cross_references(text, context)

        # Step 8: Escape LaTeX special characters (but preserve our @ markers)
        text = self._escape_latex_content(text)

        # Step 9: Restore markdown formatting (must be before boxes that contain bold/italic)
        text = self._restore_markdown_formatting(text)

        # Step 10: Restore lists (must be before boxes that contain lists)
        text = self._restore_lists(text)

        # Step 11: Restore markdown headers
        text = self._restore_markdown_headers(text)

        # Step 12: Restore tables
        text = self._restore_tables(text, context)

        # Step 13: Restore boxes (after lists/formatting since boxes can contain them)
        text = self._restore_boxes(text)

        # Step 14: Restore images
        text = self._restore_images(text, image_map)

        # Step 15: Restore cross-references (after all content is in place)
        text = self._restore_cross_references(text)

        return ProcessingResult(
            processed_content=text,
            image_map=context.global_image_map,
            updated_image_counter=image_counter,
            updated_table_counter=table_counter
        )

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

    def _extract_images(self, text: str, context: ProcessingContext) -> Tuple[str, Dict]:
        """Extract [IMAGE:path:caption:width] tags and replace with placeholders"""
        # Use context's counter and map to ensure unique placeholders across all sections
        image_map = {}
        image_counter = context.image_counter

        def extract_image_params(match):
            nonlocal image_counter
            image_counter += 1
            placeholder = f"@IMAGE{image_counter}@"

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
            context.global_image_map[placeholder] = image_data
            return placeholder

        # Pattern: [IMAGE:path:caption:width:label] where width and label are optional
        pattern = r'\[IMAGE:([^:]+):(.+?)\]'
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

    def _process_tables(self, text: str, context: ProcessingContext) -> Tuple[str, int]:
        """Process markdown tables with global counter for labeling"""
        # Convert \\n to actual newlines for regex
        text = text.replace('\\n', '\n')

        table_counter = context.table_counter

        # Only process explicitly wrapped tables: [TABLE:style:caption:emphasis:label]
        table_pattern = r'\[TABLE:([^:]+):(.+?)\](.*?)\[/TABLE\]'

        def replace_table(match):
            nonlocal table_counter
            table_counter += 1
            style, rest, table_md = match.groups()

            # Parse rest which is: "caption" or "caption:emphasis" or "caption::label" or "caption:emphasis:label"
            parts = rest.split(':')
            caption = None
            emphasis = None
            label = None

            # Known emphasis tokens — never treat these as labels
            EMPHASIS_TOKENS = {'first-bold', 'total-row', 'last-jade', 'last-orange', 'last-blue', 'last-navy', 'status'}

            def _is_emphasis(val: str) -> bool:
                """Return True if val looks like an emphasis option, not a label."""
                import re as _re
                if not val:
                    return False
                # Contains = or , → definitely emphasis (e.g. widths=1,2,1.5 or first-bold,last-jade)
                if '=' in val or ',' in val:
                    return True
                # Matches a known emphasis token
                if val in EMPHASIS_TOKENS:
                    return True
                # colN-COLOR, colN-bold, or colN-status pattern e.g. col2-jade, col3-bold, col2-status
                if _re.match(r'^col\d+-[a-z]+$', val):
                    return True
                return False

            if len(parts) == 1:
                # Just caption
                caption = parts[0]
            elif len(parts) == 2:
                # caption:X where X is either emphasis or label
                if _is_emphasis(parts[1]):
                    caption, emphasis = parts
                elif parts[1] and ('-' in parts[1] or '_' in parts[1]):
                    caption, label = parts
                else:
                    caption = parts[0]
                    if parts[1]:
                        emphasis = parts[1]
            else:
                # 3+ parts: could be "caption:with:colons::label" or "caption:emphasis:label" etc.
                if '' in parts:
                    # Found :: - split at that point
                    empty_idx = parts.index('')
                    caption = ':'.join(parts[:empty_idx])
                    label = ':'.join(parts[empty_idx+1:]) if empty_idx+1 < len(parts) else None
                else:
                    # No :: - assume last part is label, second-to-last is emphasis
                    last = parts[-1]
                    if _is_emphasis(last):
                        emphasis = last
                        caption = ':'.join(parts[:-1])
                    elif last and ('-' in last or '_' in last):
                        label = last
                        if len(parts) >= 3:
                            second_last = parts[-2]
                            if _is_emphasis(second_last):
                                emphasis = second_last
                                caption = ':'.join(parts[:-2])
                            else:
                                caption = ':'.join(parts[:-1])
                        else:
                            caption = parts[0]
                    else:
                        caption = rest

            # Combine style and emphasis if present
            if emphasis:
                full_style = f"{style}:{emphasis}"
            else:
                full_style = style

            table_id = abs(hash(f"{style}{caption}{table_md}")) % 100000
            label_part = f":{label}" if label else ""
            return f"@TABLE:{full_style}||{caption}:{table_id}:{table_counter}{label_part}@{table_md.strip()}@TABLEEND:{table_id}@"

        text = re.sub(table_pattern, replace_table, text, flags=re.DOTALL)

        return text, table_counter

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
            stripped = line.strip()
            if stripped and len(stripped) < 80 and not re.match(r'^(\s*)[•\-*]\s+', line) and not re.match(r'^(\s*)\d+\.\s+', line):
                if stripped[0].isupper() and (not stripped.endswith('.') or stripped.endswith(':')):
                    # Look ahead: is this followed by blank line(s)?
                    j = i + 1
                    has_blank_after = False
                    while j < len(lines) and not lines[j].strip():
                        has_blank_after = True
                        j += 1

                    # If followed by blank line, treat as header
                    if has_blank_after and j < len(lines):
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

        # Grid layout for KPI (4 per row) and FEATURE (3 per row) boxes.
        # Collect consecutive runs of the same box type, chunk them into rows,
        # and emit each row as \noindent{box1}{box2}...{boxN}\par\vspace{6pt}
        def make_grid(text, pattern, per_row):
            box_re = re.compile(pattern)
            # Find all consecutive runs and replace them with chunked rows
            def replace_run(match):
                run = match.group(0)
                boxes = box_re.findall(run)
                chunks = [boxes[i:i + per_row] for i in range(0, len(boxes), per_row)]
                rows = []
                for idx, chunk in enumerate(chunks):
                    is_last = (idx == len(chunks) - 1)
                    # Use negative spacing to pull rows together and eliminate white space
                    tail = '\\par\\vspace{6pt}' if is_last else '\\\\[-6pt]'
                    rows.append('\\noindent' + '%\n'.join(chunk) + tail)
                return '\n'.join(rows)
            # Match a run of consecutive box commands (separated only by optional whitespace)
            run_re = re.compile(r'(?:' + pattern + r'\s*)+', re.DOTALL)
            return run_re.sub(replace_run, text)

        # kpibox: \kpibox{color}{title}{value}  — 3 brace groups, values contain no }
        kpi_pat = r'\\kpibox\{[^}]+\}\{[^}]+\}\{[^}]+\}'
        text = make_grid(text, kpi_pat, 4)

        # featurebox: \featurebox{color}{title}{content}  — content may be empty
        feat_pat = r'\\featurebox\{[^}]+\}\{[^}]+\}\{[^}]*\}'
        text = make_grid(text, feat_pat, 3)

        return text

    def _restore_tables(self, text: str, context: ProcessingContext) -> str:
        """Restore table placeholders to LaTeX tables with labels"""
        # Pattern: @TABLE:style||caption:id:num:label@content@TABLEEND:id@
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
            # status-colors is an alias for simple+status (backward compatibility)
            style_parts = style.split(':')
            base_style = style_parts[0]
            emphasis_opts = style_parts[1].split(',') if len(style_parts) > 1 else []
            if base_style == 'status-colors':
                base_style = 'simple'
                if 'status' not in emphasis_opts:
                    emphasis_opts.append('status')

            # Parse emphasis options
            # col_colors: dict of {0-based col index -> latex color string}
            # col_bold:   set of 0-based col indices that should be bolded
            col_colors = {}
            col_bold = set()
            manual_widths = None
            COLOR_MAP_EMPHASIS = {
                'jade': 'snapJade!20', 'orange': 'snapOrange!20',
                'blue': 'snapBlue!20', 'navy': 'snapNavy!20',
            }
            col_status = set()  # 0-based col indices with status auto-colouring; -2 sentinel = all columns
            for opt in emphasis_opts:
                if opt == 'first-bold':
                    col_bold.add(0)  # shorthand for col1-bold
                elif opt == 'status':
                    col_status.add(-2)  # -2 sentinel = all columns
                elif opt.startswith('last-'):
                    color_name = opt.split('-', 1)[1]
                    col_colors[-1] = COLOR_MAP_EMPHASIS.get(color_name, 'snapBlue!20')
                elif opt.startswith('col') and '-' in opt:
                    # colN-COLOR, colN-bold, or colN-status
                    rest = opt[3:]  # strip "col"
                    dash_idx = rest.index('-')
                    try:
                        col_1based = int(rest[:dash_idx])
                        attr = rest[dash_idx + 1:]
                        col_0based = col_1based - 1
                        if attr == 'bold':
                            col_bold.add(col_0based)
                        elif attr == 'status':
                            col_status.add(col_0based)
                        else:
                            col_colors[col_0based] = COLOR_MAP_EMPHASIS.get(attr, 'snapBlue!20')
                    except ValueError:
                        pass
                elif opt.startswith('widths='):
                    width_str = opt.split('=')[1]
                    manual_widths = [float(w.strip()) for w in width_str.split(',')]
            # -1 sentinel = last column (resolved at render time)
            total_row = 'total-row' in emphasis_opts
            # first-bold is now handled via col_bold, keep legacy flag for format_cell
            first_bold = 0 in col_bold

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
                # Split by | but keep empty cells
                all_cells = [c.strip() for c in line.split('|')]
                # Remove leading/trailing empty cells from split artifacts
                cells = all_cells[1:-1] if len(all_cells) > 2 and all_cells[0] == '' and all_cells[-1] == '' else all_cells
                cells = [c if c else ' ' for c in cells]
                if cells:
                    rows.append(cells)

            # Generate LaTeX table based on style
            num_cols = len(headers)

            # Auto-landscape: 7+ columns switch to landscape automatically
            if num_cols >= 7 and not is_landscape:
                is_landscape = True

            # Validate table constraints
            if is_landscape:
                if num_cols > 10:
                    return f"ERROR: Landscape table has {num_cols} columns (max 10 allowed)"
            else:
                if num_cols > 6:
                    return f"ERROR: Portrait table has {num_cols} columns (max 6 allowed)"

            # Column specification - use full available width
            if num_cols > 0:
                if is_landscape:
                    use_tabularx = True
                    table_width = '\\linewidth'

                    if manual_widths and len(manual_widths) == num_cols:
                        widths = manual_widths
                    else:
                        # Column width based on 90th-percentile cell length.
                        # This allocates space proportional to where content is densest,
                        # minimising total line breaks across the table without being
                        # distorted by single long outliers (max) or short typical values (avg).
                        widths = []
                        for col_idx in range(num_cols):
                            header_len = len(headers[col_idx]) if col_idx < len(headers) else 0
                            cell_lens = sorted([len(row[col_idx]) if col_idx < len(row) else 0 for row in rows])
                            if cell_lens:
                                p90_idx = max(0, int(len(cell_lens) * 0.9) - 1)
                                p90_len = cell_lens[p90_idx]
                            else:
                                p90_len = 0
                            widths.append(max(header_len, p90_len, 3))

                    total_width = sum(widths)
                    normalized = [w * num_cols / total_width for w in widths]
                    col_spec = ''.join([f'>{{\\hsize={n:.2f}\\hsize\\raggedright\\arraybackslash\\setlength{{\\parindent}}{{0pt}}}}X' for n in normalized])
                else:
                    # Portrait
                    use_tabularx = True
                    table_width = '\\linewidth'

                    if manual_widths and len(manual_widths) == num_cols:
                        widths = manual_widths
                    else:
                        # Column width based on 90th-percentile cell length.
                        # This allocates space proportional to where content is densest,
                        # minimising total line breaks across the table without being
                        # distorted by single long outliers (max) or short typical values (avg).
                        widths = []
                        for col_idx in range(num_cols):
                            header_len = len(headers[col_idx]) if col_idx < len(headers) else 0
                            cell_lens = sorted([len(row[col_idx]) if col_idx < len(row) else 0 for row in rows])
                            if cell_lens:
                                p90_idx = max(0, int(len(cell_lens) * 0.9) - 1)
                                p90_len = cell_lens[p90_idx]
                            else:
                                p90_len = 0
                            widths.append(max(header_len, p90_len, 3))

                    total_width = sum(widths)
                    normalized = [w * num_cols / total_width for w in widths]
                    col_spec = ''.join([f'>{{\\hsize={n:.2f}\\hsize\\raggedright\\arraybackslash\\setlength{{\\parindent}}{{0pt}}}}X' for n in normalized])
            else:
                use_tabularx = False
                col_spec = 'l'

            # All landscape tables use longtable (handles any row count, single or multi-page)
            landscape_longtable = is_landscape

            latex = []

            # Landscape opener:
            # - landscape_longtable (many rows): pdflscape directly — longtable handles page breaks
            # - landscape single page: afterpage defers until current portrait page is full
            if is_landscape:
                # Both landscape modes use afterpage to fill portrait page before switching
                # landscape_longtable: afterpage wraps the full landscape+longtable block
                latex.append('\\afterpage{')
                latex.append('\\begin{landscape}')
                latex.append('\\centering')

            # Helper function to format cell with emphasis
            def format_cell(cell_text, col_index=0, is_total_row=False):
                formatted = cell_text
                if col_index in col_bold:
                    formatted = f'\\textbf{{{formatted}}}'
                if is_total_row:
                    formatted = f'\\textbf{{{formatted}}}'
                return formatted

            # Status cell colour helper — used when col_status is set
            STATUS_JADE_KW = {'active', 'done', 'success', 'complete', 'completed', 'ok', 'stable', 'live', 'passed'}
            STATUS_AMBER_KW = {'pending', 'in progress', 'in-progress', 'review', 'partial', 'draft', 'scheduled', 'planned'}
            STATUS_ORANGE_KW = {'warning', 'degraded', 'delayed', 'at risk'}
            STATUS_RED_KW = {'error', 'failed', 'fail', 'critical', 'blocked', 'rejected', 'down', 'broken'}

            def _cell_status_color(cell_text):
                val = cell_text.strip().lower()
                if any(kw == val or kw in val for kw in STATUS_RED_KW): return 'snapOrange!35'
                if any(kw == val or kw in val for kw in STATUS_ORANGE_KW): return 'snapOrange!20'
                if any(kw == val or kw in val for kw in STATUS_AMBER_KW): return 'yellow!30'
                if any(kw == val or kw in val for kw in STATUS_JADE_KW): return 'snapJade!25'
                return None

            def _apply_status_color(cell_text, col_index, formatted):
                """Apply status cell colour if this column has status colouring enabled."""
                if -2 in col_status or col_index in col_status:
                    color = _cell_status_color(cell_text)
                    if color:
                        return f'\\cellcolor{{{color}}}{formatted}'
                return formatted

            # Auto-select longtable for portrait tables with >4 rows.
            # Landscape uses sidewaystable float (not longtable) — allows LaTeX to place it near the reference.
            use_longtable = is_landscape or is_multipage or (len(rows) > 4)

            # Best practice: set arraystretch before the environment, reset after
            latex.append('\\renewcommand{\\arraystretch}{1.2}')

            if use_longtable:
                pass  # longtable is inline — no float wrapper, caption handled separately
            else:
                if not is_landscape:
                    # Portrait small table: standard float with \caption
                    latex.append('\\begin{table}[H]')
                    latex.append('\\centering')
                    if caption and caption != '_':
                        latex.append(f'\\caption{{{caption}}}')
                    else:
                        latex.append(f'\\caption{{}}')
                    latex.append(f'\\label{{tab:{table_num}}}')
                    if label:
                        latex.append(f'\\label{{tab:{label}}}')
                        if caption and caption != '_':
                            context.table_registry[caption] = (int(table_num), label)
                    else:
                        if caption and caption != '_':
                            context.table_registry[caption] = (int(table_num), str(table_num))
                else:
                    # Landscape inline: \captionof registers in List of Tables without a float wrapper
                    if caption and caption != '_':
                        latex.append(f'\\captionof{{table}}{{{caption}}}')
                        latex.append(f'\\label{{tab:{table_num}}}')
                        if label:
                            latex.append(f'\\label{{tab:{label}}}')
                            context.table_registry[caption] = (int(table_num), label)
                        else:
                            context.table_registry[caption] = (int(table_num), str(table_num))

                latex.append('\\renewcommand{\\arraystretch}{1.2}')

            # Style-specific rendering
            if base_style == 'status-colors':
                # Auto-detect status keywords per cell and apply cellcolor only to that cell
                STATUS_JADE = {'active', 'done', 'success', 'complete', 'completed', 'ok', 'stable', 'live', 'passed'}
                STATUS_AMBER = {'pending', 'in progress', 'in-progress', 'review', 'partial', 'draft', 'scheduled', 'planned'}
                STATUS_ORANGE = {'warning', 'degraded', 'delayed', 'at risk'}
                STATUS_RED = {'error', 'failed', 'fail', 'critical', 'blocked', 'rejected', 'down', 'broken'}

                def _status_cell_color(cell_text):
                    val = cell_text.strip().lower()
                    if any(kw == val or kw in val for kw in STATUS_RED):
                        return 'snapOrange!35'
                    if any(kw == val or kw in val for kw in STATUS_ORANGE):
                        return 'snapOrange!20'
                    if any(kw == val or kw in val for kw in STATUS_AMBER):
                        return 'yellow!30'
                    if any(kw == val or kw in val for kw in STATUS_JADE):
                        return 'snapJade!25'
                    return None

                if use_longtable:
                    # Subtract tabcolsep: LaTeX adds 2*tabcolsep per column as padding (default 6pt=0.211cm)
                    # ltablex X columns: auto-fills linewidth, page-break safe
                    total_relative = sum(widths)
                    normalized = [w * num_cols / total_relative for w in widths]
                    longtable_col_spec = ''.join([f'>{{\\hsize={n:.2f}\\hsize\\raggedright\\arraybackslash\\setlength{{\\parindent}}{{0pt}}}}X' for n in normalized])

                    latex.append(f'\\begin{{tabularx}}{{\\linewidth}}{{{longtable_col_spec}}}')
                    if caption and caption != '_':

                        # longtable: \caption{} \\ then \label on next line (best practice)
                        latex.append(f'\\caption{{{caption}}} \\\\')
                        latex.append(f'\\label{{tab:{table_num}}}')
                        if label:
                            latex.append(f'\\label{{tab:{label}}}')
                            context.table_registry[caption] = (int(table_num), label)
                        else:
                            context.table_registry[caption] = (int(table_num), str(table_num))
                    white_headers_st = [f'\\textcolor{{white}}{{\\textbf{{{h}}}}}' for h in headers]
                    latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers_st)} \\\\')
                    latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')
                    latex.append('\\endfirsthead')
                    latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers_st)} \\\\')
                    latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')
                    latex.append('\\endhead')
                else:
                    if use_tabularx:
                        latex.append(f'\\begin{{tabularx}}{{{table_width}}}{{{col_spec}}}')
                    else:
                        latex.append(f'\\begin{{tabular}}{{{col_spec}}}')
                    white_headers_st = [f'\\textcolor{{white}}{{\\textbf{{{h}}}}}' for h in headers]
                    latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers_st)} \\\\')
                    latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')

                zebra_counter = 0
                for row in rows:
                    # Category header: ALL CAPS first cell, rest empty
                    is_category_header = (len(row) > 0 and row[0].strip().isupper() and
                                          all(not cell.strip() for cell in row[1:]))
                    formatted_cells = []
                    for j, cell in enumerate(row):
                        if is_category_header:
                            formatted = f'\\textbf{{{cell}}}' if cell.strip() else cell
                        else:
                            cell_color = _status_cell_color(cell)
                            formatted = f'\\textbf{{{cell}}}' if j == 0 else cell
                            if cell_color:
                                formatted = f'\\cellcolor{{{cell_color}}}{formatted}'
                        formatted_cells.append(formatted)
                    if is_category_header:
                        white_cells_cat = [f'\\textcolor{{white}}{{\\textbf{{{c}}}}}' if c.strip() else c for c in formatted_cells]
                        latex.append(f'\\rowcolor{{snapBlue}}{" & ".join(white_cells_cat)} \\\\')
                    elif zebra_counter % 2 == 1:
                        latex.append(f'\\rowcolor{{snapLightGray}}{" & ".join(formatted_cells)} \\\\')
                    else:
                        latex.append(f'{" & ".join(formatted_cells)} \\\\')
                    if not is_category_header:
                        zebra_counter += 1

            else:  # 'simple' (default)
                if use_longtable:
                    if manual_widths and len(manual_widths) == num_cols:
                        widths = manual_widths

                    # Subtract tabcolsep: LaTeX adds 2*tabcolsep per column as padding (default 6pt=0.211cm)
                    # ltablex X columns: auto-fills linewidth, page-break safe
                    total_relative = sum(widths)
                    normalized = [w * num_cols / total_relative for w in widths]
                    longtable_col_spec = ''.join([f'>{{\\hsize={n:.2f}\\hsize\\raggedright\\arraybackslash\\setlength{{\\parindent}}{{0pt}}}}X' for n in normalized])

                    # captionof registers in List of Tables without needing a table float
                    if caption and caption != '_':
                        latex.append(f'\\captionof{{table}}{{{caption}}}')
                        latex.append(f'\\label{{tab:{table_num}}}')
                        if label:
                            latex.append(f'\\label{{tab:{label}}}')
                            context.table_registry[caption] = (int(table_num), label)
                        else:
                            context.table_registry[caption] = (int(table_num), str(table_num))
                    latex.append(f'\\begin{{tabularx}}{{\\linewidth}}{{{longtable_col_spec}}}')
                    white_headers = [f'\\textcolor{{white}}{{\\textbf{{{h}}}}}' for h in headers]
                    latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers)} \\\\')
                    latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')
                    latex.append('\\endfirsthead')
                    latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers)} \\\\')
                    latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')
                    latex.append('\\endhead')
                else:
                    if use_tabularx:
                        latex.append(f'\\begin{{tabularx}}{{{table_width}}}{{{col_spec}}}')
                    else:
                        latex.append(f'\\begin{{tabular}}{{{col_spec}}}')
                    white_headers = [f'\\textcolor{{white}}{{\\textbf{{{h}}}}}' for h in headers]
                    latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_headers)} \\\\')
                    latex.append('\\arrayrulecolor{snapLightGray!30}\\midrule')

                # Resolve sentinel -1 (last column) to actual last col index
                resolved_col_colors = {}
                for col_idx, lc in col_colors.items():
                    resolved = (num_cols - 1) if col_idx == -1 else col_idx
                    resolved_col_colors[resolved] = lc

                zebra_counter = 0
                for i, row in enumerate(rows):
                    is_last_row = (i == len(rows) - 1)
                    is_total = is_last_row and total_row

                    is_category_header = False
                    if len(row) > 0 and row[0].strip():
                        first_cell = row[0].strip()
                        if first_cell.isupper() and all(not cell.strip() for cell in row[1:]):
                            is_category_header = True

                    formatted_cells = []
                    for j, cell in enumerate(row):
                        formatted = format_cell(cell, j, is_total)

                        if j in resolved_col_colors and not is_total and not is_category_header:
                            formatted = f'\\cellcolor{{{resolved_col_colors[j]}}}{formatted}'

                        if not is_total and not is_category_header and col_status:
                            formatted = _apply_status_color(cell, j, formatted)

                        formatted_cells.append(formatted)

                    if is_total:
                        white_cells = [f'\\textcolor{{white}}{{{c}}}' for c in formatted_cells]
                        latex.append(f'\\rowcolor{{snapNavy}}{" & ".join(white_cells)} \\\\')
                    elif is_category_header:
                        white_cells_cat = [f'\\textcolor{{white}}{{\\textbf{{{c}}}}}' if c.strip() else c for c in formatted_cells]
                        latex.append(f'\\rowcolor{{snapBlue}}{" & ".join(white_cells_cat)} \\\\')
                    else:
                        if zebra_counter % 2 == 1:
                            latex.append(f'\\rowcolor{{snapLightGray}}{" & ".join(formatted_cells)} \\\\')
                        else:
                            latex.append(f'{" & ".join(formatted_cells)} \\\\')
                        zebra_counter += 1

            # Close table environment — add bottomrule for clean termination (best practice)
            latex.append('\\noalign{\\global\\arrayrulecolor{black}}\\bottomrule')
            # Close the tabular/tabularx environment
            if use_longtable or use_tabularx or is_landscape:
                latex.append('\\end{tabularx}')
            else:
                latex.append('\\end{tabular}')

            # Close float wrapper
            if is_landscape:
                pass  # landscape closed below via afterpage
            elif not use_longtable:
                latex.append('\\end{table}')

            # Reset arraystretch to avoid affecting subsequent content
            latex.append('\\renewcommand{\\arraystretch}{1.0}')

            if is_landscape:
                latex.append('\\end{landscape}')
                latex.append('}')

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
                    latex += f"\\caption{{{caption}}}\\label{{fig:{semantic_label}}}\n"
                else:
                    # Fallback to numeric label
                    json_num = int(placeholder.replace('@IMAGE', '').replace('@', ''))
                    latex += f"\\caption{{{caption}}}\\label{{fig:{json_num}}}\n"
            latex += "\\end{figure}\n"

            text = text.replace(placeholder, latex)

        return text

    def _extract_cross_references(self, text: str, context: ProcessingContext) -> str:
        """Extract cross-references to placeholders before LaTeX escaping"""
        # Figure references with semantic labels
        def extract_semantic_figure_ref(match):
            fig_label = match.group(1)
            return f"@FIGREF:{fig_label}@"

        text = re.sub(r'Figure~\\ref\{fig:([^}]+)\}', extract_semantic_figure_ref, text)

        # Figure references: "Figure X" where X is a number
        def extract_figure_ref(match):
            fig_num = match.group(1)
            return f"@FIGREF:{fig_num}@"

        text = re.sub(r'\bFigure\s+(\d+)\b', extract_figure_ref, text)

        # Table references with semantic labels
        def extract_semantic_table_ref(match):
            tab_label = match.group(1)
            return f"@TABREF:{tab_label}@"

        text = re.sub(r'Table~\\ref\{tab:([^}]+)\}', extract_semantic_table_ref, text)

        # Table references by caption
        def extract_table_caption_ref(match):
            caption = match.group(1)
            if caption in context.table_registry:
                table_num, ref_label = context.table_registry[caption]
                return f"@TABREF:{ref_label}@"
            return match.group(0)

        text = re.sub(r'Table[\s ]+\(([^)]+)\)', extract_table_caption_ref, text)

        # Table references: "Table X" where X is a number
        def extract_table_ref(match):
            tab_num = match.group(1)
            return f"@TABREF:{tab_num}@"

        text = re.sub(r'\bTable\s+(\d+)\b', extract_table_ref, text)

        # Section references
        def extract_section_ref(match):
            section_num = match.group(1)
            return f"@SECREF:{section_num}@"

        text = re.sub(r'\bSection\s+([\d\.]+)\b', extract_section_ref, text)

        return text

    def _restore_cross_references(self, text: str) -> str:
        """Restore cross-reference placeholders to proper LaTeX \ref commands"""
        # Figure references
        def restore_figure_ref(match):
            fig_ref = match.group(1)
            return f"Figure~\\ref{{fig:{fig_ref}}}"

        text = re.sub(r'@FIGREF:([^@]+)@', restore_figure_ref, text)

        # Table references
        def restore_table_ref(match):
            tab_ref = match.group(1)
            return f"Table~\\ref{{tab:{tab_ref}}}"

        text = re.sub(r'@TABREF:([^@]+)@', restore_table_ref, text)

        # Section references
        def restore_section_ref(match):
            section_num = match.group(1)
            return f"Section~\\ref{{sec:{section_num}}}"

        text = re.sub(r'@SECREF:([\d\.]+)@', restore_section_ref, text)

        return text
