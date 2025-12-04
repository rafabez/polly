"""
PDF handling utilities for reading and writing PDFs
"""

import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from .i18n import get_text

# Configure console with legacy_windows=False to enable better Unicode support on Windows
console = Console(legacy_windows=False)

# Check if PDF libraries are available
try:
    from pypdf import PdfReader
    PDF_READ_AVAILABLE = True
except ImportError:
    PDF_READ_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
    PDF_WRITE_AVAILABLE = True
except ImportError:
    PDF_WRITE_AVAILABLE = False


def read_pdf(file_path: str) -> Optional[str]:
    """
    Extract text from a PDF file
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Extracted text or None if failed
    """
    if not PDF_READ_AVAILABLE:
        console.print(f"[yellow]{get_text('label.warning')} {get_text('pdf.pypdf_missing')}[/yellow]")
        return None

    try:
        reader = PdfReader(file_path)
        text_parts = []

        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            if text.strip():
                text_parts.append(f"--- Page {page_num} ---\n{text}")

        if not text_parts:
            console.print(f"[yellow]{get_text('label.warning')} {get_text('pdf.no_text')}[/yellow]")
            return None

        return "\n\n".join(text_parts)

    except Exception as e:
        console.print(f"[red]{get_text('pdf.read_error', e=str(e))}[/red]")
        return None


def write_pdf(content: str, output_path: str, title: str = "Polly Output") -> bool:
    """
    Write text content to a PDF file
    
    Args:
        content: Text content to write
        output_path: Path for output PDF file
        title: Document title
        
    Returns:
        True if successful, False otherwise
    """
    if not PDF_WRITE_AVAILABLE:
        console.print(f"[yellow]{get_text('label.warning')} {get_text('pdf.reportlab_missing')}[/yellow]")
        return False

    try:
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )

        # Container for the 'Flowable' objects
        story = []

        # Define styles
        styles = getSampleStyleSheet()

        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor='#00ff00',
            spaceAfter=30,
        )

        # Body style
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=10,
            leading=14,
            alignment=TA_LEFT,
            spaceAfter=12,
        )

        # Code style
        code_style = ParagraphStyle(
            'Code',
            parent=styles['Code'],
            fontSize=9,
            leading=12,
            leftIndent=20,
            fontName='Courier',
            spaceAfter=12,
        )

        # Add title
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 12))

        # Process content
        # Split by code blocks (```...```)
        parts = content.split('```')

        for i, part in enumerate(parts):
            if i % 2 == 0:
                # Regular text
                # Split into paragraphs
                paragraphs = part.split('\n\n')
                for para in paragraphs:
                    if para.strip():
                        # Escape special characters for reportlab
                        para = para.replace('&', '&amp;')
                        para = para.replace('<', '&lt;')
                        para = para.replace('>', '&gt;')
                        para = para.replace('\n', '<br/>')
                        story.append(Paragraph(para, body_style))
            else:
                # Code block
                lines = part.strip().split('\n')
                # Skip language identifier if present
                if lines and not lines[0].strip().startswith('#'):
                    lines = lines[1:] if len(lines) > 1 else lines

                code_text = '\n'.join(lines)
                code_text = code_text.replace('&', '&amp;')
                code_text = code_text.replace('<', '&lt;')
                code_text = code_text.replace('>', '&gt;')
                code_text = code_text.replace('\n', '<br/>')
                story.append(Paragraph(code_text, code_style))

        # Build PDF
        doc.build(story)

        console.print(f"[green]{get_text('label.success')} {get_text('pdf.saved', output_path=output_path)}[/green]")
        return True

    except Exception as e:
        console.print(f"[red]{get_text('pdf.write_error', e=str(e))}[/red]")
        return False


def is_pdf_file(file_path: str) -> bool:
    """Check if file is a PDF based on extension"""
    return Path(file_path).suffix.lower() == '.pdf'
