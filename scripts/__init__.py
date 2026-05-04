"""
LaTeX Content Processor

This module provides content processing functionality for LaTeX document generation.
It handles conversion of markdown-like syntax with special tags ([TABLE:...], [IMAGE:...], [BOX:...])
into proper LaTeX commands.
"""

from .content_processor import ContentProcessor, ProcessingContext, ProcessingResult

__all__ = ['ContentProcessor', 'ProcessingContext', 'ProcessingResult']
