#!/usr/bin/env python3
"""
Document Quality Advisor Skill Entry Point
"""

import sys
import json
import subprocess
from pathlib import Path


def main():
    """Run document quality validation and format results for Claude"""

    if len(sys.argv) < 2:
        print("❌ Usage: doc-quality-advisor <document.json>")
        print("\nAnalyzes document structure and content for professional quality.")
        print("Compatible with latex-docs JSON format.")
        sys.exit(1)

    doc_path = sys.argv[1]

    if not Path(doc_path).exists():
        print(f"❌ Error: Document not found: {doc_path}")
        sys.exit(1)

    # Run validator
    skill_dir = Path(__file__).parent
    validator_script = skill_dir / "validator.py"

    try:
        result = subprocess.run(
            [sys.executable, str(validator_script), doc_path],
            capture_output=True,
            text=True,
            check=True
        )

        report = json.loads(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"❌ Validation failed: {e.stderr}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse validation report: {e}")
        sys.exit(1)

    # Format report for readability
    print(f"\n{'='*80}")
    print(f"📊 DOCUMENT QUALITY REPORT")
    print(f"{'='*80}\n")

    # Overall score
    score = report['score']
    grade = report['grade']
    score_emoji = "🟢" if score >= 85 else "🟡" if score >= 70 else "🔴"
    print(f"{score_emoji} Overall Score: {score}/100 ({grade})")
    print(f"\n{report['summary']}\n")

    # Statistics
    stats = report['statistics']
    print(f"📈 Document Statistics:")
    print(f"   • Total Words: {stats['total_words']}")
    print(f"   • Estimated Pages: {stats['estimated_pages']}")
    print(f"   • Sections: {stats['total_sections']} main, {stats['total_subsections']} subsections")
    print(f"   • Visual Elements: {stats['total_figures']} figures, {stats['total_tables']} tables")
    print(f"   • Content Variety: {stats['total_lists']} lists, {stats['total_paragraphs']} paragraphs")
    print(f"   • Max Hierarchy Depth: {stats['max_depth']} levels")
    print()

    # Issues by severity
    issues = report['issues']

    if issues['critical']:
        print(f"🔴 CRITICAL ISSUES ({len(issues['critical'])})")
        print(f"   These MUST be fixed before finalizing the document:\n")
        for i, issue in enumerate(issues['critical'], 1):
            print(f"   {i}. {issue['message']}")
            print(f"      → {issue['recommendation']}")
            print(f"      📍 {issue['location']}\n")

    if issues['warnings']:
        print(f"🟡 WARNINGS ({len(issues['warnings'])})")
        print(f"   These SHOULD be addressed for professional quality:\n")
        for i, issue in enumerate(issues['warnings'][:5], 1):  # Top 5
            print(f"   {i}. {issue['message']}")
            print(f"      → {issue['recommendation']}")
            print(f"      📍 {issue['location']}\n")

        if len(issues['warnings']) > 5:
            print(f"   ... and {len(issues['warnings']) - 5} more warnings\n")

    if issues['suggestions']:
        print(f"🔵 SUGGESTIONS ({len(issues['suggestions'])})")
        print(f"   Optional improvements for enhancement:\n")
        for i, issue in enumerate(issues['suggestions'][:3], 1):  # Top 3
            print(f"   {i}. {issue['message']}")
            print(f"      → {issue['recommendation']}\n")

        if len(issues['suggestions']) > 3:
            print(f"   ... and {len(issues['suggestions']) - 3} more suggestions\n")

    # Quick wins
    if report['quick_wins']:
        print(f"⚡ QUICK WINS (Easy Fixes):")
        for i, issue in enumerate(report['quick_wins'], 1):
            print(f"   {i}. {issue['message']} → {issue['recommendation']}")
        print()

    # Strengths
    if report['strengths']:
        print(f"✅ STRENGTHS:")
        for strength in report['strengths']:
            print(f"   • {strength}")
        print()

    # Action items for agents
    print(f"{'='*80}")
    print(f"🤖 FOR AGENTS: Next Steps")
    print(f"{'='*80}\n")

    if issues['critical']:
        print(f"1. Address all {len(issues['critical'])} CRITICAL issues immediately")
    if issues['warnings']:
        print(f"2. Fix top {min(5, len(issues['warnings']))} WARNINGS for professional quality")
    if score < 85:
        print(f"3. Re-run validator after changes (target score: 85+)")
        print(f"4. Iterate until no CRITICAL issues remain")
    else:
        print(f"✅ Document quality is acceptable. Address remaining items if time allows.")

    print()

    # Output JSON for programmatic use
    json_output_path = Path(doc_path).with_suffix('.quality_report.json')
    with open(json_output_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"📄 Full report saved to: {json_output_path}")
    print()


if __name__ == '__main__':
    main()
