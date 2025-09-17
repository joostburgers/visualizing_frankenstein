#!/usr/bin/env python3
"""
Custom notebook converter with proper TOC and styling
"""

import nbformat
import json
from nbconvert import HTMLExporter
from traitlets.config import Config
import re

def create_custom_html_export(notebook_path, output_path):
    """
    Convert notebook to HTML with proper TOC, hidden code cells, and custom styling
    """
    
    # Read the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Configure the HTML exporter to hide input cells
    c = Config()
    c.HTMLExporter.exclude_input = True  # Hide all code cells
    c.HTMLExporter.exclude_output_prompt = True  # Hide output prompts
    c.HTMLExporter.exclude_input_prompt = True  # Hide input prompts
    
    # Create HTML exporter
    html_exporter = HTMLExporter(config=c)
    
    # Convert to HTML
    (body, resources) = html_exporter.from_notebook_node(nb)
    
    # Custom CSS for better layout and working TOC
    custom_css = """
    <style>
    /* Main layout - centered with margins */
    body {
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', 'Helvetica Neue', Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        background-color: #fdfdfd;
        margin: 0;
        padding: 0;
    }
    
    .container {
        max-width: 80%;
        margin: 0 auto;
        padding: 40px 20px;
        background-color: white;
        box-shadow: 0 0 20px rgba(0,0,0,0.05);
        min-height: 100vh;
    }
    
    /* Typography */
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 15px;
        text-align: center;
        margin-bottom: 30px;
        font-size: 2.5em;
    }
    
    h2 {
        color: #34495e;
        border-left: 4px solid #3498db;
        padding-left: 20px;
        margin-top: 50px;
        margin-bottom: 25px;
        font-size: 2em;
    }
    
    h3 {
        color: #2980b9;
        margin-top: 35px;
        margin-bottom: 20px;
        font-size: 1.5em;
    }
    
    h4 {
        color: #7f8c8d;
        margin-top: 25px;
        margin-bottom: 15px;
        font-size: 1.2em;
    }
    
    /* Table of Contents styling */
    .toc-container {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 30px;
        margin: 30px 0 50px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .toc-container h2 {
        margin-top: 0;
        color: #495057;
        border-left: none;
        text-align: center;
        font-size: 1.8em;
        margin-bottom: 25px;
    }
    
    .toc-container ol {
        margin: 0;
        padding-left: 0;
        counter-reset: toc-counter;
        list-style: none;
    }
    
    .toc-container > ol > li {
        counter-increment: toc-counter;
        margin: 15px 0;
        position: relative;
        padding-left: 40px;
    }
    
    .toc-container > ol > li::before {
        content: counter(toc-counter) ".";
        position: absolute;
        left: 0;
        font-weight: bold;
        color: #3498db;
        font-size: 1.1em;
    }
    
    .toc-container ul {
        margin: 8px 0 0 0;
        padding-left: 20px;
        list-style-type: none;
    }
    
    .toc-container li {
        margin: 8px 0;
    }
    
    .toc-container a {
        color: #2980b9;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.2s ease;
        display: block;
        padding: 5px 0;
    }
    
    .toc-container a:hover {
        color: #3498db;
        text-decoration: underline;
        transform: translateX(5px);
    }
    
    /* Content styling */
    .rendered_html {
        font-size: 16px;
        line-height: 1.7;
    }
    
    .rendered_html p {
        margin-bottom: 20px;
        text-align: justify;
    }
    
    .rendered_html ul, .rendered_html ol {
        margin-bottom: 20px;
        padding-left: 30px;
    }
    
    .rendered_html li {
        margin-bottom: 8px;
    }
    
    /* Output styling */
    .output_area {
        margin: 30px 0;
        padding: 0;
    }
    
    .output_subarea {
        padding: 0;
    }
    
    /* Plotly chart styling */
    .plotly-graph-div {
        margin: 40px auto !important;
        border: 1px solid #e1e5e9;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        overflow: hidden;
    }
    
    /* Text output styling */
    .output_text {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 20px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 14px;
        margin: 20px 0;
        line-height: 1.4;
        color: #495057;
        overflow-x: auto;
    }
    
    /* Code styling (if any remains) */
    .input_area {
        display: none !important;
    }
    
    .prompt {
        display: none !important;
    }
    
    /* Strong and emphasis */
    strong {
        color: #2c3e50;
        font-weight: 600;
    }
    
    em {
        color: #6c757d;
        font-style: italic;
    }
    
    /* Horizontal rules */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(to right, #3498db, transparent);
        margin: 50px 0;
    }
    
    /* Responsive design */
    @media (max-width: 1200px) {
        .container {
            max-width: 90%;
        }
    }
    
    @media (max-width: 768px) {
        .container {
            max-width: 95%;
            padding: 20px 15px;
        }
        
        h1 {
            font-size: 2em;
        }
        
        h2 {
            font-size: 1.6em;
        }
        
        .toc-container {
            padding: 20px;
        }
        
        .plotly-graph-div {
            width: 100% !important;
        }
    }
    
    /* Print styles */
    @media print {
        .container {
            max-width: 100%;
            box-shadow: none;
        }
        
        .plotly-graph-div {
            break-inside: avoid;
        }
        
        h1, h2, h3 {
            break-after: avoid;
        }
    }
    
    /* Smooth scrolling for anchor links */
    html {
        scroll-behavior: smooth;
    }
    
    /* Anchor link offset for fixed headers */
    h1[id], h2[id], h3[id], h4[id] {
        scroll-margin-top: 20px;
    }
    </style>
    """
    
    # Inject the custom CSS and wrap content in container
    # Find the </head> tag and insert CSS before it
    head_end = body.find('</head>')
    if head_end != -1:
        body = body[:head_end] + custom_css + body[head_end:]
    
    # Wrap the main content in a container div
    # Find the body content and wrap it
    body_start = body.find('<body>')
    body_end = body.find('</body>')
    
    if body_start != -1 and body_end != -1:
        content_start = body.find('<div class="container">', body_start)
        if content_start == -1:  # If container doesn't exist, create it
            original_content = body[body_start + 6:body_end]  # +6 to skip <body>
            new_content = f'<body><div class="container">{original_content}</div>'
            body = body[:body_start] + new_content + body[body_end:]
    
    # Fix the table of contents to work properly
    # Make sure all heading IDs are properly formatted
    def fix_heading_ids(match):
        heading_tag = match.group(1)
        heading_text = match.group(2)
        # Create a proper ID from the heading text
        heading_id = re.sub(r'[^\w\s-]', '', heading_text.lower())
        heading_id = re.sub(r'[-\s]+', '-', heading_id).strip('-')
        return f'<{heading_tag} id="{heading_id}">{heading_text}</{heading_tag}>'
    
    # Fix heading IDs
    body = re.sub(r'<(h[1-6])>(.*?)</h[1-6]>', fix_heading_ids, body)
    
    # Also add the TOC container class
    body = body.replace('<h2>Table of Contents</h2>', '<div class="toc-container"><h2>Table of Contents</h2>')
    
    # Find the end of the TOC (look for the next h2 or the hr after TOC)
    toc_end = body.find('<hr>', body.find('Table of Contents'))
    if toc_end != -1:
        hr_end = body.find('>', toc_end) + 1
        body = body[:hr_end] + '</div>' + body[hr_end:]
    
    # Write the final HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(body)
    
    print(f"✅ Created custom HTML export: {output_path}")
    print(f"📏 File size: {len(body)/1024/1024:.2f} MB")
    print("🎨 Features: Working TOC, hidden code cells, centered layout, custom styling")

if __name__ == "__main__":
    notebook_file = r"c:\Users\joost\My Drive (joostburgers@gmail.com)\Teaching\JMU\Courses\Fall 2025\Eng 221\visualizing_frankenstein\frankenstein_presentation.ipynb"
    output_file = r"c:\Users\joost\My Drive (joostburgers@gmail.com)\Teaching\JMU\Courses\Fall 2025\Eng 221\visualizing_frankenstein\frankenstein_presentation_final.html"
    
    create_custom_html_export(notebook_file, output_file)