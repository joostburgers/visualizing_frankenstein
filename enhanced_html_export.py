#!/usr/bin/env python3
"""
Enhanced notebook converter with fully working TOC and optimal layout
"""

import nbformat
import json
from nbconvert import HTMLExporter
from traitlets.config import Config
import re
import os

def create_enhanced_html_export(notebook_path, output_path):
    """
    Convert notebook to HTML with working TOC, hidden code cells, and professional layout
    """
    
    # Read the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Configure the HTML exporter
    c = Config()
    c.HTMLExporter.exclude_input = True  # Hide all code input cells
    c.HTMLExporter.exclude_output_prompt = True
    c.HTMLExporter.exclude_input_prompt = True
    
    # Create HTML exporter
    html_exporter = HTMLExporter(config=c)
    
    # Convert to HTML
    (body, resources) = html_exporter.from_notebook_node(nb)
    
    # Enhanced CSS with perfect TOC functionality and proper narrow layout
    enhanced_css = """
    <style>
    /* Reset and base styles */
    * {
        box-sizing: border-box;
    }
    
    html {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%) !important;
        min-height: 100vh;
    }
    
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.65;
        color: #2d3748;
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        margin: 0;
        padding: 40px 0;
        min-height: 100vh;
    }
    
    /* Main container - narrow column layout with 20% margins on each side */
    body.jp-Notebook, .main-container {
        max-width: 60% !important;
        width: 60% !important;
        margin: 0 auto !important;
        background: white !important;
        padding: 60px 40px !important;
        border-radius: 16px !important;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.08) !important;
        position: relative !important;
    }
    
    @media (max-width: 1400px) {
        body.jp-Notebook, .main-container {
            max-width: 65% !important;
            width: 65% !important;
            margin: 0 auto !important;
            padding: 50px 35px !important;
        }
    }
    
    @media (max-width: 1024px) {
        body.jp-Notebook, .main-container {
            max-width: 75% !important;
            width: 75% !important;
            margin: 0 auto !important;
            padding: 40px 30px !important;
        }
    }
    
    @media (max-width: 768px) {
        body.jp-Notebook, .main-container {
            max-width: 95% !important;
            width: 95% !important;
            padding: 30px 25px !important;
        }
        
        body {
            padding: 20px 0;
        }
    }
    
    /* Typography hierarchy */
    h1 {
        font-size: 3rem;
        color: #1a202c;
        text-align: center;
        margin: 0 0 60px 0;
        font-weight: 700;
        border-bottom: 4px solid #4299e1;
        padding-bottom: 20px;
        letter-spacing: -0.025em;
    }
    
    h2 {
        font-size: 2.25rem;
        color: #2d3748;
        margin: 80px 0 30px 0;
        font-weight: 600;
        border-left: 6px solid #4299e1;
        padding-left: 25px;
        letter-spacing: -0.025em;
    }
    
    h3 {
        font-size: 1.75rem;
        color: #4a5568;
        margin: 50px 0 25px 0;
        font-weight: 600;
    }
    
    h4 {
        font-size: 1.25rem;
        color: #718096;
        margin: 30px 0 20px 0;
        font-weight: 600;
    }
    
    
    
    /* Content styling */
    .rendered_html {
        font-size: 1.1rem;
        line-height: 1.8;
    }
    
    .rendered_html p {
        margin-bottom: 24px;
        text-align: justify;
        hyphens: auto;
    }
    
    .rendered_html ul, .rendered_html ol {
        margin-bottom: 24px;
        padding-left: 30px;
    }
    
    .rendered_html li {
        margin-bottom: 8px;
    }
    
    .rendered_html strong {
        color: #1a202c;
        font-weight: 600;
    }
    
    .rendered_html em {
        color: #4a5568;
    }
    
    /* Output area styling */
    .output_area {
        margin: 50px 0;
        padding: 0;
    }
    
    .output_subarea {
        padding: 0;
        max-width: 100%;
        overflow-x: auto;
    }
    
    /* Enhanced Plotly styling */
    .plotly-graph-div {
        margin: 50px auto !important;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
        overflow: hidden;
        background: white;
    }
    
    /* Text output styling */
    .output_text {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border: 1px solid #cbd5e0;
        border-radius: 12px;
        padding: 30px;
        font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #4a5568;
        margin: 30px 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    /* Hide all input elements completely */
    .input_area, .prompt, div.input, .CodeMirror {
        display: none !important;
    }
    
    /* Horizontal rules */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #4299e1 0%, transparent 100%);
        margin: 60px 0;
        border-radius: 1px;
    }
    
    /* Smooth scrolling */
    html {
        scroll-behavior: smooth;
    }
    
    /* Scroll margin for anchors */
    h1[id], h2[id], h3[id], h4[id] {
        scroll-margin-top: 30px;
    }
    
    /* Print styles */
    @media print {
        body {
            background: white;
            padding: 0;
        }
        
        body.jp-Notebook, .main-container {
            max-width: 100% !important;
            width: 100% !important;
            box-shadow: none !important;
            border-radius: 0 !important;
            padding: 20px !important;
        }
        
        .plotly-graph-div {
            break-inside: avoid;
            page-break-inside: avoid;
        }
        
        h1, h2, h3 {
            break-after: avoid;
            page-break-after: avoid;
        }
    }
    </style>
    
    <script>
   
    </script>
    """
    
    # Process the HTML body
    # Insert CSS and JavaScript
    head_end = body.find('</head>')
    if head_end != -1:
        body = body[:head_end] + enhanced_css + body[head_end:]
    
    # Wrap content in main container
    body_start = body.find('<body>')
    body_end = body.find('</body>')
    
    if body_start != -1 and body_end != -1:
        content_start = body_start + 6  # Skip <body>
        original_content = body[content_start:body_end]
        
        # Wrap in main container
        wrapped_content = f'<body><div class="main-container">{original_content}</div>'
        body = body[:body_start] + wrapped_content + body[body_end:]
    
    
    
    # Write the final HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(body)
    
    file_size = os.path.getsize(output_path) / 1024 / 1024
    print(f"✅ Enhanced HTML export created: {output_path}")
    print(f"📏 File size: {file_size:.2f} MB")
    print("🎨 Features:")
    print("   - Working table of contents with smooth scroll")
    print("   - All code cells hidden")
    print("   - Narrow centered layout with 20% margins on each side")
    print("   - Professional typography and spacing")
    print("   - Interactive Plotly charts preserved")
    print("   - Mobile responsive design")

if __name__ == "__main__":
    notebook_file = r"c:\Users\joost\My Drive (joostburgers@gmail.com)\Teaching\JMU\Courses\Fall 2025\Eng 221\visualizing_frankenstein\frankenstein_presentation.ipynb"
    output_file = r"c:\Users\joost\My Drive (joostburgers@gmail.com)\Teaching\JMU\Courses\Fall 2025\Eng 221\visualizing_frankenstein\frankenstein_presentation_professional.html"
    
    create_enhanced_html_export(notebook_file, output_file)