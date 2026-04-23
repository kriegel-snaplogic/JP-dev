"""
SnapLogic Brand Configuration
Extracted from official brand guidelines - 2026-04-14
"""

# Brand Colors (hex format)
BRAND_COLORS = {
    # Primary Colors
    'navy': '#003399',      # Primary navy - headers, main branding, dark backgrounds
    'blue': '#2F8DFE',      # Primary blue - buttons, primary actions

    # Accent Colors
    'jade': '#2CA392',      # Jade - accent stripe, highlights, modern docs
    'link_blue': '#003899', # Link blue - hyperlinks, interactive elements
    'orange': '#F97F6E',    # Orange - warm accent, stats

    # Neutrals
    'white': '#FFFFFF',     # White - text on dark backgrounds
    'light_gray': '#E7F5FF', # Backgrounds, zebra rows
    'dark_gray': '#0E1830',  # Body text, secondary text
}

# LaTeX Color Definitions
# Converts hex to RGB for LaTeX \definecolor commands
def hex_to_rgb(hex_color):
    """Convert hex color to RGB values (0-1 range for LaTeX)"""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"{r/255:.3f},{g/255:.3f},{b/255:.3f}"

LATEX_COLORS = {
    'snapNavy': hex_to_rgb(BRAND_COLORS['navy']),
    'snapBlue': hex_to_rgb(BRAND_COLORS['blue']),
    'snapJade': hex_to_rgb(BRAND_COLORS['jade']),
    'snapLinkBlue': hex_to_rgb(BRAND_COLORS['link_blue']),
    'snapOrange': hex_to_rgb(BRAND_COLORS['orange']),
    'snapWhite': hex_to_rgb(BRAND_COLORS['white']),
    'snapLightGray': hex_to_rgb(BRAND_COLORS['light_gray']),
    'snapDarkGray': hex_to_rgb(BRAND_COLORS['dark_gray']),
}

# Typography
TYPOGRAPHY = {
    'heading': 'Poppins, Arial, sans-serif',
    'body': 'Roboto, Arial, sans-serif',
    'monospace': 'Consolas, monospace'
}

# LaTeX Font Packages
# Since we can't bundle Poppins/Roboto directly, use similar professional alternatives
LATEX_FONTS = {
    'heading': 'helvet',  # Helvetica (similar to Arial/sans-serif)
    'body': 'helvet',     # Helvetica for body as well (clean, professional)
    'monospace': 'courier' # Courier (standard monospace)
}

# Logo Files
LOGO_FILES = {
    'blue': 'logos/snaplogic-logo-blue.png',
    'white': 'logos/snaplogic-logo-white.png',
    'mark_white': 'logos/snaplogic-logomark-white.png'
}

# Document Type Configurations
DOCUMENT_TYPES = {
    'technical': {
        'name': 'Technical Document',
        'primary_color': 'snapNavy',
        'accent_color': 'snapBlue',
        'title_color': 'snapNavy',
        'logo': 'blue',
        'cover_style': 'light',           # Simple white cover
        'include_toc': True,  # Conditional: >=3 sections
        'include_citations': True,
        'section_numbering': True,
        'page_numbers': True,
        'header_style': 'minimal',
        'font_size': '11pt',
    },
    'general': {
        'name': 'General/Customer-Facing Document',
        'primary_color': 'snapNavy',       # Navy for all headers
        'accent_color': 'snapNavy',        # Navy for all header levels
        'title_color': 'snapWhite',        # White text on dark cover
        'logo': 'white',                   # White logo for dark cover
        'cover_style': 'dark',             # Dark navy full-bleed cover
        'include_toc': True,
        'include_citations': False,
        'section_numbering': True,
        'page_numbers': True,
        'header_style': 'branded',
        'font_size': '11pt',
    },
    'internal': {
        'name': 'Internal Document',
        'primary_color': 'snapDarkGray',
        'accent_color': 'snapBlue',
        'title_color': 'snapDarkGray',
        'logo': 'blue',
        'cover_style': 'light',           # Simple white cover
        'include_toc': True,
        'include_citations': False,
        'section_numbering': True,
        'page_numbers': True,
        'header_style': 'simple',
        'font_size': '11pt',
    }
}

# Customization Options
CUSTOMIZATION_OPTIONS = {
    'font_size': ['10pt', '11pt', '12pt'],
    'page_layout': ['oneside', 'twoside'],
    'paper_size': ['letterpaper', 'a4paper'],
    'color_schemes': ['default', 'monochrome', 'high_contrast']
}
