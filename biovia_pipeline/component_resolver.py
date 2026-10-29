# component_resolver.py

BACKEND_COMPONENTS = {

    "Notebook Connection":
        "biovia_pipeline.notebook_connection",

    "Experiment Query":
        "biovia_pipeline.experiment_query",

    "Custom Filter":
        "biovia_pipeline.custom_filter",

    "Custom Manipulator":
        "biovia_pipeline.custom_manipulator",

    "Add Excel Section":
        "biovia_pipeline.add_excel_section",

    "Add PDF Section":
        "biovia_pipeline.add_pdf_section",

    "Add Word Section":
        "biovia_pipeline.add_word_section",

    "Add Image Section":
        "biovia_pipeline.add_image_section",

    "Add PowerPoint Section":
        "biovia_pipeline.add_powerpoint_section",

    "Extract Sections":
        "biovia_pipeline.extract_sections",

    "Section Dispatcher":
        "biovia_pipeline.section_dispatcher",

    "Directory Watcher":
        "biovia_pipeline.directory_watcher",

    "Azure Downloader":
        "biovia_pipeline.azure_downloader",

    "Delete File":
        "biovia_pipeline.delete_file"
}


def resolve_backend_component(name: str):

    for key, value in BACKEND_COMPONENTS.items():

        if key.lower() in name.lower():
            return value

    return None