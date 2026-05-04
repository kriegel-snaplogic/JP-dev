#!/usr/bin/env python3
"""
Document Quality Validator
Analyzes document structure for professional quality based on industry best practices
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from collections import defaultdict


class DocumentValidator:
    """Validate document quality against professional standards"""

    # Best practice thresholds (from research)
    OPTIMAL_SECTION_LENGTH = (300, 500)  # words
    MIN_SECTION_LENGTH = 150
    MAX_SECTION_LENGTH = 800
    OPTIMAL_PARAGRAPH_LENGTH = (40, 125)  # words
    OPTIMAL_FIGURES_PER_PAGE = 0.33  # 1 figure per 2-3 pages
    MIN_FIGURES_PER_PAGE = 0.15
    MAX_FIGURES_PER_PAGE = 0.6
    MANAGEMENT_SUMMARY_RATIO = (0.05, 0.10)  # 5-10% of document
    MAX_TOC_DEPTH = 3
    OPTIMAL_SENTENCE_LENGTH = (15, 20)  # words

    def __init__(self):
        self.issues = {
            'critical': [],
            'warning': [],
            'suggestion': []
        }
        self.stats = {}
        self.score = 100

    def validate(self, doc_path: str) -> Dict[str, Any]:
        """Main validation entry point"""
        doc = self._load_document(doc_path)

        # Calculate document statistics
        self._calculate_stats(doc)

        # Run all validation checks
        self._check_visual_content_balance(doc)
        self._check_content_type_diversity(doc)
        self._check_cross_references(doc)
        self._check_document_structure(doc)
        self._check_readability(doc)
        self._check_technical_quality(doc)

        # Calculate final score
        self._calculate_score()

        return self._generate_report()

    def _load_document(self, doc_path: str) -> Dict:
        """Load and parse document JSON"""
        with open(doc_path, 'r') as f:
            return json.load(f)

    def _calculate_stats(self, doc: Dict):
        """Calculate document-wide statistics"""
        stats = {
            'total_words': 0,
            'total_sections': 0,
            'total_subsections': 0,
            'total_subsubsections': 0,
            'total_paragraphs': 0,
            'total_figures': 0,
            'total_tables': 0,
            'total_lists': 0,
            'section_words': {},
            'figure_references': set(),
            'section_references': set(),
            'max_depth': 1,
            'estimated_pages': 0
        }

        # Count from management summary
        if doc.get('management_summary'):
            stats['total_words'] += len(doc['management_summary'].split())
            stats['total_paragraphs'] += doc['management_summary'].count('\\n\\n') + 1

        # Count from sections
        for i, section in enumerate(doc.get('sections', []), 1):
            stats['total_sections'] += 1
            section_words = self._count_section_words(section)
            stats['section_words'][f"Section {i}: {section['title']}"] = section_words
            stats['total_words'] += section_words

            # Count content elements in section
            content = section.get('content', '')
            stats['total_paragraphs'] += content.count('\\n\\n') + 1
            stats['total_figures'] += content.count('[IMAGE:')
            stats['total_tables'] += content.count('[TABLE:')  # Proper table detection
            stats['total_lists'] += content.count('\\n- ') + content.count('\\n* ')

            # Find references (both numeric and semantic)
            # Numeric: "Figure 1", "Figure 3"
            stats['figure_references'].update(re.findall(r'Figure\s+(\d+)', content))
            # Semantic: "Figure~\ref{fig:label}"
            stats['figure_references'].update(re.findall(r'Figure~\\ref\{fig:([^}]+)\}', content))
            # Table references (numeric and semantic)
            stats['figure_references'].update(re.findall(r'Table\s+(\d+)', content))
            stats['figure_references'].update(re.findall(r'Table~\\ref\{tab:([^}]+)\}', content))
            stats['section_references'].update(re.findall(r'Section\s+([\d\.]+)', content))

            # Count subsections
            for subsection in section.get('subsections', []):
                stats['total_subsections'] += 1
                stats['max_depth'] = max(stats['max_depth'], 2)
                sub_content = subsection.get('content', '')
                stats['total_words'] += len(sub_content.split())
                stats['total_paragraphs'] += sub_content.count('\\n\\n') + 1
                stats['total_figures'] += sub_content.count('[IMAGE:')
                stats['total_tables'] += sub_content.count('[TABLE:')
                stats['figure_references'].update(re.findall(r'Figure\s+(\d+)', sub_content))
                stats['figure_references'].update(re.findall(r'Figure~\\ref\{fig:([^}]+)\}', sub_content))
                stats['figure_references'].update(re.findall(r'Table\s+(\d+)', sub_content))
                stats['figure_references'].update(re.findall(r'Table~\\ref\{tab:([^}]+)\}', sub_content))
                stats['section_references'].update(re.findall(r'Section\s+([\d\.]+)', sub_content))

                # Count subsubsections
                for subsubsection in subsection.get('subsubsections', []):
                    stats['total_subsubsections'] += 1
                    stats['max_depth'] = max(stats['max_depth'], 3)
                    subsub_content = subsubsection.get('content', '')
                    stats['total_words'] += len(subsub_content.split())
                    stats['total_figures'] += subsub_content.count('[IMAGE:')
                    stats['total_tables'] += subsub_content.count('[TABLE:')
                    stats['figure_references'].update(re.findall(r'Figure\s+(\d+)', subsub_content))
                    stats['figure_references'].update(re.findall(r'Figure~\\ref\{fig:([^}]+)\}', subsub_content))
                    stats['figure_references'].update(re.findall(r'Table\s+(\d+)', subsub_content))
                    stats['figure_references'].update(re.findall(r'Table~\\ref\{tab:([^}]+)\}', subsub_content))

        # Count next steps
        if doc.get('next_steps'):
            for step in doc['next_steps']:
                stats['total_words'] += len(step.split())
                stats['figure_references'].update(re.findall(r'Figure\s+(\d+)', step))
                stats['figure_references'].update(re.findall(r'Figure~\\ref\{fig:([^}]+)\}', step))
                stats['figure_references'].update(re.findall(r'Table\s+(\d+)', step))
                stats['figure_references'].update(re.findall(r'Table~\\ref\{tab:([^}]+)\}', step))
                stats['section_references'].update(re.findall(r'Section\s+([\d\.]+)', step))

        # Estimate pages (roughly 300-400 words per page with figures)
        words_per_page = 350
        stats['estimated_pages'] = max(1, stats['total_words'] // words_per_page)

        # Convert sets to lists for JSON serialization
        stats['figure_references'] = sorted(list(stats['figure_references']))
        stats['section_references'] = sorted(list(stats['section_references']))

        self.stats = stats

    def _count_section_words(self, section: Dict) -> int:
        """Recursively count words in a section and all subsections"""
        count = len(section.get('content', '').split())
        for sub in section.get('subsections', []):
            count += self._count_section_words(sub)
        return count

    def _check_visual_content_balance(self, doc: Dict):
        """Check figure/image density and distribution"""
        figures = self.stats['total_figures']
        pages = self.stats['estimated_pages']

        if pages == 0:
            return

        figures_per_page = figures / pages

        # Overall document balance
        if figures_per_page < self.MIN_FIGURES_PER_PAGE:
            self.issues['warning'].append({
                'category': 'Visual Content',
                'message': f'Document has too few visuals ({figures} figures across ~{pages} pages = {figures_per_page:.2f} per page)',
                'recommendation': 'Add diagrams, charts, or screenshots to break up text. Target: 1 figure per 2-3 pages.',
                'location': 'Document-wide'
            })
        elif figures_per_page > self.MAX_FIGURES_PER_PAGE:
            self.issues['warning'].append({
                'category': 'Visual Content',
                'message': f'Document is too visual-heavy ({figures} figures across ~{pages} pages = {figures_per_page:.2f} per page)',
                'recommendation': 'Consider if all figures are necessary. Some might work better as tables or text.',
                'location': 'Document-wide'
            })

        # Check for unreferenced figures
        referenced_figures = {int(ref) for ref in self.stats['figure_references']}
        total_figures_numbered = self.stats['total_figures']

        for i in range(1, total_figures_numbered + 1):
            if i not in referenced_figures:
                self.issues['warning'].append({
                    'category': 'Cross-Reference',
                    'message': f'Figure {i} is never referenced in the text',
                    'recommendation': f'Add "See Figure {i}" or "Figure {i} shows..." in the relevant section.',
                    'location': f'Figure {i}'
                })

        # Check section-level distribution
        sections_without_visuals = []
        for section in doc.get('sections', []):
            if '[IMAGE:' not in section.get('content', ''):
                # Check subsections too
                has_visual = any('[IMAGE:' in sub.get('content', '')
                               for sub in section.get('subsections', []))
                if not has_visual:
                    sections_without_visuals.append(section['title'])

        if len(sections_without_visuals) > len(doc.get('sections', [])) // 2:
            self.issues['suggestion'].append({
                'category': 'Visual Content',
                'message': f'{len(sections_without_visuals)} sections have no visuals',
                'recommendation': f'Consider adding diagrams to: {", ".join(sections_without_visuals[:3])}',
                'location': 'Multiple sections'
            })

    def _check_content_type_diversity(self, doc: Dict):
        """Check for appropriate mix of content types"""
        # Check if document is all prose (no lists, no tables)
        if self.stats['total_lists'] == 0 and self.stats['total_words'] > 500:
            self.issues['warning'].append({
                'category': 'Content Diversity',
                'message': 'Document contains no bullet lists or numbered lists',
                'recommendation': 'Use lists for: steps, requirements, features, or any items that can be scanned.',
                'location': 'Document-wide'
            })

        if self.stats['total_tables'] == 0 and self.stats['total_words'] > 1000:
            self.issues['suggestion'].append({
                'category': 'Content Diversity',
                'message': 'Document contains no tables',
                'recommendation': 'Consider tables for: comparisons, specifications, timelines, or structured data.',
                'location': 'Document-wide'
            })

        # Check for sections that are entirely lists (no prose)
        for section in doc.get('sections', []):
            content = section.get('content', '')
            list_chars = content.count('\\n- ') + content.count('\\n* ')
            words = len(content.split())

            if list_chars > 5 and words < 50:
                self.issues['suggestion'].append({
                    'category': 'Content Diversity',
                    'message': f'Section "{section["title"]}" is mostly bullet points with little prose',
                    'recommendation': 'Add 2-3 sentences to introduce or summarize the list items.',
                    'location': f'Section: {section["title"]}'
                })

    def _check_cross_references(self, doc: Dict):
        """Check quality and consistency of cross-references"""
        # Check for forward references to non-existent sections
        section_count = len(doc.get('sections', []))
        for ref in self.stats['section_references']:
            # Parse section number (e.g., "2.1.3")
            parts = ref.split('.')
            try:
                main_section = int(parts[0])
                if main_section > section_count:
                    self.issues['critical'].append({
                        'category': 'Cross-Reference',
                        'message': f'Reference to non-existent Section {ref}',
                        'recommendation': f'Fix section number. Document has {section_count} main sections.',
                        'location': 'Cross-reference error'
                    })
            except (ValueError, IndexError):
                pass

        # Check for vague references (qualitative check based on patterns)
        for section in doc.get('sections', []):
            content = section.get('content', '')
            vague_patterns = [
                (r'as mentioned (above|earlier|previously)', 'Use specific section reference: "as mentioned in Section X"'),
                (r'see (above|below|earlier)', 'Use specific reference: "see Section X" or "see Figure Y"'),
                (r'the (following|next) (section|figure)', 'Use specific reference with number')
            ]

            for pattern, recommendation in vague_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    self.issues['suggestion'].append({
                        'category': 'Cross-Reference',
                        'message': f'Vague reference in "{section["title"]}": {pattern}',
                        'recommendation': recommendation,
                        'location': f'Section: {section["title"]}'
                    })

    def _check_document_structure(self, doc: Dict):
        """Check section lengths, hierarchy, and organization"""
        # Check management summary length
        if doc.get('management_summary'):
            summary_words = len(doc['management_summary'].split())
            total_words = self.stats['total_words']
            summary_ratio = summary_words / total_words if total_words > 0 else 0

            min_ratio, max_ratio = self.MANAGEMENT_SUMMARY_RATIO
            if summary_ratio < min_ratio:
                self.issues['warning'].append({
                    'category': 'Document Structure',
                    'message': f'Management summary is too short ({summary_words} words, {summary_ratio*100:.1f}% of document)',
                    'recommendation': f'Expand to 5-10% of document length (target: {int(total_words * 0.075)} words)',
                    'location': 'Management Summary'
                })
            elif summary_ratio > max_ratio:
                self.issues['warning'].append({
                    'category': 'Document Structure',
                    'message': f'Management summary is too long ({summary_words} words, {summary_ratio*100:.1f}% of document)',
                    'recommendation': f'Condense to 5-10% of document length (target: {int(total_words * 0.075)} words)',
                    'location': 'Management Summary'
                })
        else:
            if self.stats['total_words'] > 500:
                self.issues['critical'].append({
                    'category': 'Document Structure',
                    'message': 'Document lacks a management summary',
                    'recommendation': 'Add a management_summary field with 5-10% of document length summarizing key points.',
                    'location': 'Document root'
                })

        # Check section lengths
        for section_name, word_count in self.stats['section_words'].items():
            if word_count < self.MIN_SECTION_LENGTH:
                self.issues['suggestion'].append({
                    'category': 'Document Structure',
                    'message': f'{section_name} is very short ({word_count} words)',
                    'recommendation': 'Expand with more detail or merge with another section. Target: 300-500 words.',
                    'location': section_name
                })
            elif word_count > self.MAX_SECTION_LENGTH:
                self.issues['warning'].append({
                    'category': 'Document Structure',
                    'message': f'{section_name} is very long ({word_count} words)',
                    'recommendation': 'Break into subsections or split into multiple sections. Target: 300-500 words per section.',
                    'location': section_name
                })

        # Check hierarchy depth
        if self.stats['max_depth'] > self.MAX_TOC_DEPTH:
            self.issues['suggestion'].append({
                'category': 'Document Structure',
                'message': f'Document hierarchy is {self.stats["max_depth"]} levels deep',
                'recommendation': 'Consider flattening structure. Optimal: 3 levels max for readability.',
                'location': 'Document structure'
            })

        # Check for next steps
        if not doc.get('next_steps') and self.stats['total_words'] > 500:
            self.issues['warning'].append({
                'category': 'Document Structure',
                'message': 'Document lacks "Next Steps" section',
                'recommendation': 'Add actionable next steps to guide the reader.',
                'location': 'Document end'
            })

    def _check_readability(self, doc: Dict):
        """Check paragraph length, sentence structure, and flow"""
        # Sample a few sections for paragraph analysis
        sampled_sections = doc.get('sections', [])[:3]  # First 3 sections

        for section in sampled_sections:
            content = section.get('content', '')
            paragraphs = [p.strip() for p in content.split('\\n\\n') if p.strip()]

            for i, para in enumerate(paragraphs):
                words = para.split()
                word_count = len(words)

                # Check paragraph length
                min_optimal, max_optimal = self.OPTIMAL_PARAGRAPH_LENGTH
                if word_count < min_optimal and not para.startswith('[IMAGE:'):
                    self.issues['suggestion'].append({
                        'category': 'Readability',
                        'message': f'Very short paragraph in "{section["title"]}" ({word_count} words)',
                        'recommendation': 'Expand with more detail or merge with adjacent paragraph.',
                        'location': f'{section["title"]}, paragraph {i+1}'
                    })
                elif word_count > max_optimal * 2:  # More than double optimal
                    self.issues['warning'].append({
                        'category': 'Readability',
                        'message': f'Very long paragraph in "{section["title"]}" ({word_count} words)',
                        'recommendation': 'Break into 2-3 paragraphs, each covering one main idea.',
                        'location': f'{section["title"]}, paragraph {i+1}'
                    })

        # Check for visual breaks (every 2-3 paragraphs should have a break)
        for section in doc.get('sections', []):
            content = section.get('content', '')
            paragraphs = content.split('\\n\\n')
            visual_elements = content.count('[IMAGE:') + content.count('\\n- ') + content.count('|')

            para_count = len([p for p in paragraphs if p.strip() and not p.startswith('[IMAGE:')])
            if para_count > 6 and visual_elements == 0:
                self.issues['suggestion'].append({
                    'category': 'Readability',
                    'message': f'Section "{section["title"]}" has {para_count} paragraphs with no visual breaks',
                    'recommendation': 'Add a figure, table, or bullet list every 2-3 paragraphs for scannability.',
                    'location': f'Section: {section["title"]}'
                })

    def _check_technical_quality(self, doc: Dict):
        """Check technical document specific best practices"""
        # Check if architecture/technical doc has diagrams
        title = doc.get('title', '').lower()
        is_technical = any(keyword in title for keyword in
                          ['architecture', 'technical', 'design', 'implementation', 'api'])

        if is_technical and self.stats['total_figures'] < self.stats['total_sections']:
            self.issues['warning'].append({
                'category': 'Technical Quality',
                'message': f'Technical document has fewer diagrams ({self.stats["total_figures"]}) than sections ({self.stats["total_sections"]})',
                'recommendation': 'Architecture docs should have ~1 diagram per major section.',
                'location': 'Document-wide'
            })

        # Check next steps are actionable (have verbs)
        if doc.get('next_steps'):
            action_verbs = {'create', 'implement', 'review', 'update', 'test', 'deploy',
                          'verify', 'configure', 'develop', 'design', 'complete', 'finalize'}

            non_actionable = []
            for i, step in enumerate(doc['next_steps'], 1):
                words = step.lower().split()
                if not any(verb in words for verb in action_verbs):
                    non_actionable.append(i)

            if len(non_actionable) > len(doc['next_steps']) // 2:
                self.issues['warning'].append({
                    'category': 'Technical Quality',
                    'message': f'{len(non_actionable)} next steps lack clear action verbs',
                    'recommendation': 'Start each step with an action verb: "Review", "Implement", "Verify", etc.',
                    'location': 'Next Steps section'
                })

    def _calculate_score(self):
        """Calculate overall quality score based on issues"""
        # Start at 100, deduct points for issues
        deductions = {
            'critical': 15,
            'warning': 5,
            'suggestion': 2
        }

        for severity, penalty in deductions.items():
            self.score -= len(self.issues[severity]) * penalty

        self.score = max(0, self.score)

    def _generate_report(self) -> Dict[str, Any]:
        """Generate final validation report"""
        # Categorize issues by category
        by_category = defaultdict(list)
        for severity in ['critical', 'warning', 'suggestion']:
            for issue in self.issues[severity]:
                by_category[issue['category']].append({
                    'severity': severity,
                    **issue
                })

        # Identify quick wins (easy fixes)
        quick_wins = []
        for issue in self.issues['warning'] + self.issues['suggestion']:
            if any(keyword in issue['message'].lower()
                   for keyword in ['unreferenced', 'lacks', 'missing', 'no ']):
                quick_wins.append(issue)

        # Identify strengths
        strengths = []
        if self.stats['total_figures'] > 0:
            strengths.append(f"Document includes {self.stats['total_figures']} visual elements")
        if self.stats['total_lists'] > 0:
            strengths.append(f"Uses {self.stats['total_lists']} lists for scannability")
        if len(self.issues['critical']) == 0:
            strengths.append("No critical structural issues")
        if self.stats.get('management_summary'):
            strengths.append("Includes management summary")

        return {
            'score': self.score,
            'grade': self._get_grade(),
            'statistics': self.stats,
            'issues': {
                'critical': self.issues['critical'],
                'warnings': self.issues['warning'],
                'suggestions': self.issues['suggestion']
            },
            'by_category': dict(by_category),
            'quick_wins': quick_wins[:5],  # Top 5
            'strengths': strengths,
            'summary': self._generate_summary()
        }

    def _get_grade(self) -> str:
        """Convert score to letter grade"""
        if self.score >= 95:
            return 'A+ (Excellent)'
        elif self.score >= 90:
            return 'A (Very Good)'
        elif self.score >= 85:
            return 'B+ (Good)'
        elif self.score >= 80:
            return 'B (Acceptable)'
        elif self.score >= 70:
            return 'C (Needs Improvement)'
        else:
            return 'D (Requires Significant Revision)'

    def _generate_summary(self) -> str:
        """Generate human-readable summary"""
        critical_count = len(self.issues['critical'])
        warning_count = len(self.issues['warning'])
        suggestion_count = len(self.issues['suggestion'])

        if critical_count > 0:
            return f"Document requires immediate attention: {critical_count} critical issues must be fixed."
        elif warning_count > 3:
            return f"Document needs improvement: {warning_count} warnings should be addressed for professional quality."
        elif warning_count > 0:
            return f"Document is good with minor issues: {warning_count} warnings to address."
        elif suggestion_count > 0:
            return f"Document is very good: {suggestion_count} optional suggestions for enhancement."
        else:
            return "Document meets professional quality standards."


def main():
    if len(sys.argv) < 2:
        print("Usage: validator.py <document.json>")
        sys.exit(1)

    doc_path = sys.argv[1]

    if not Path(doc_path).exists():
        print(f"Error: File not found: {doc_path}")
        sys.exit(1)

    validator = DocumentValidator()
    report = validator.validate(doc_path)

    # Output JSON report
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
