# Custom nbconvert configuration to hide specific cells
c = get_config()

# Use the TagRemovePreprocessor to remove cells with specific tags
c.TagRemovePreprocessor.remove_cell_tags = {"hide_cell"}
c.TagRemovePreprocessor.remove_all_outputs_tags = {"hide_output"}
c.TagRemovePreprocessor.remove_input_tags = {"hide_input"}
c.TagRemovePreprocessor.enabled = True

# Add the preprocessor to the list
c.HTMLExporter.preprocessors = ['nbconvert.preprocessors.TagRemovePreprocessor']