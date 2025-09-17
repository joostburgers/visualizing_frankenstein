#!/usr/bin/env python3
"""
Custom notebook converter to hide specific cells during HTML export
"""

import nbformat
import sys
from nbconvert import HTMLExporter
from nbconvert.preprocessors import TagRemovePreprocessor
from traitlets.config import Config
import os

def convert_notebook_hide_cells(notebook_path, output_path, cells_to_hide=None):
    """
    Convert notebook to HTML while hiding specified cells
    
    Args:
        notebook_path (str): Path to input notebook
        output_path (str): Path for output HTML file
        cells_to_hide (list): List of cell indices to hide (0-based)
    """
    
    # Read the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # If specific cells to hide are provided, remove them
    if cells_to_hide:
        # Remove cells in reverse order to maintain indices
        for cell_idx in sorted(cells_to_hide, reverse=True):
            if 0 <= cell_idx < len(nb.cells):
                print(f"Hiding cell {cell_idx}")
                del nb.cells[cell_idx]
    
    # Configure the HTML exporter
    c = Config()
    c.HTMLExporter.exclude_input = False  # Keep input cells visible (except hidden ones)
    c.HTMLExporter.exclude_output = False  # Keep outputs visible
    
    # Create HTML exporter
    html_exporter = HTMLExporter(config=c)
    
    # Convert to HTML
    (body, resources) = html_exporter.from_notebook_node(nb)
    
    # Write HTML file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(body)
    
    print(f"Converted notebook to HTML: {output_path}")
    print(f"File size: {len(body)/1024/1024:.2f} MB")

if __name__ == "__main__":
    notebook_file = r"c:\Users\joost\My Drive (joostburgers@gmail.com)\Teaching\JMU\Courses\Fall 2025\Eng 221\visualizing_frankenstein\frankenstein_presentation.ipynb"
    output_file = r"c:\Users\joost\My Drive (joostburgers@gmail.com)\Teaching\JMU\Courses\Fall 2025\Eng 221\visualizing_frankenstein\frankenstein_presentation_hidden.html"
    
    # Cell 2 is the data loading cell (0-based indexing: cell 0=title, cell 1=toc, cell 2=data loading)
    cells_to_hide = [2]  # Hide the data loading cell
    
    convert_notebook_hide_cells(notebook_file, output_file, cells_to_hide)