#!/usr/bin/env python3
"""
Generate PDF from Markdown documentation.
Converts BENCHMARK_COMPREHENSIVE_GUIDE.md to PDF format.
"""

import os
import sys
from pathlib import Path

def generate_pdf_with_weasyprint(md_file: str, output_pdf: str):
    """Generate PDF using weasyprint (requires weasyprint)."""
    try:
        import markdown
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        # Read markdown file
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            md_content,
            extensions=['extra', 'codehilite', 'tables', 'toc']
        )
        
        # Add CSS styling
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: 'Georgia', 'Times New Roman', serif;
                    line-height: 1.6;
                    color: #333;
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    page-break-after: avoid;
                }}
                h2 {{
                    color: #34495e;
                    border-bottom: 2px solid #95a5a6;
                    padding-bottom: 8px;
                    margin-top: 30px;
                    page-break-after: avoid;
                }}
                h3 {{
                    color: #555;
                    margin-top: 25px;
                    page-break-after: avoid;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 15px;
                    border-left: 4px solid #3498db;
                    overflow-x: auto;
                    page-break-inside: avoid;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                    page-break-inside: avoid;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #3498db;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f2f2f2;
                }}
                blockquote {{
                    border-left: 4px solid #3498db;
                    margin: 20px 0;
                    padding-left: 20px;
                    color: #555;
                    font-style: italic;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                .toc {{
                    background-color: #f9f9f9;
                    padding: 20px;
                    margin: 20px 0;
                    border: 1px solid #ddd;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Generate PDF
        HTML(string=html_template).write_pdf(output_pdf)
        print(f"✓ PDF generated successfully: {output_pdf}")
        return True
        
    except ImportError as e:
        print(f"✗ Missing dependency: {e}")
        print("\nInstall required packages:")
        print("  pip install markdown weasyprint")
        return False
    except Exception as e:
        print(f"✗ Error generating PDF: {e}")
        return False


def generate_pdf_with_pypandoc(md_file: str, output_pdf: str):
    """Generate PDF using pypandoc (requires pandoc and LaTeX)."""
    try:
        import pypandoc
        
        # Convert markdown to PDF
        pypandoc.convert_file(
            md_file,
            'pdf',
            outputfile=output_pdf,
            extra_args=[
                '--pdf-engine=xelatex',
                '--variable=mainfont:Georgia',
                '--variable=fontsize:11pt',
                '--variable=geometry:margin=2cm',
                '--toc',
                '--toc-depth=3'
            ]
        )
        print(f"✓ PDF generated successfully: {output_pdf}")
        return True
        
    except ImportError:
        print("✗ pypandoc not installed")
        print("\nInstall required packages:")
        print("  pip install pypandoc")
        print("  # Also install pandoc: https://pandoc.org/installing.html")
        print("  # And LaTeX: https://www.latex-project.org/get/")
        return False
    except Exception as e:
        print(f"✗ Error generating PDF: {e}")
        return False


def main():
    """Main function to generate PDF from markdown."""
    # Get script directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Input markdown file
    md_file = project_root / "docs" / "BENCHMARK_COMPREHENSIVE_GUIDE.md"
    
    # Output PDF file
    output_pdf = project_root / "docs" / "BENCHMARK_COMPREHENSIVE_GUIDE.pdf"
    
    if not md_file.exists():
        print(f"✗ Markdown file not found: {md_file}")
        print("\nPlease create BENCHMARK_COMPREHENSIVE_GUIDE.md first.")
        return 1
    
    print(f"Converting: {md_file}")
    print(f"Output: {output_pdf}")
    print()
    
    # Try weasyprint first (easier to install)
    if generate_pdf_with_weasyprint(str(md_file), str(output_pdf)):
        return 0
    
    # Fallback to pypandoc
    print("\nTrying pypandoc...")
    if generate_pdf_with_pypandoc(str(md_file), str(output_pdf)):
        return 0
    
    print("\n✗ Could not generate PDF. Please install one of:")
    print("  1. weasyprint: pip install markdown weasyprint")
    print("  2. pypandoc: pip install pypandoc (also requires pandoc and LaTeX)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
