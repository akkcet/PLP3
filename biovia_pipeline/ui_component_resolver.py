# ui_component_resolver.py

UI_COMPONENTS = {

    "File Chooser":
        "FileUpload",

    "Submit Button":
        "PrimaryButton",

    "Input Form":
        "FormContainer",

    "List Box":
        "DataGrid",

    "Text":
        "TextLabel",

    "HTML Template":
        "PageLayout",

    "Bootstrap Form Group":
        "FormGroup",

    "Tile Horizontal":
        "Row",

    "Tile Vertical":
        "Column",

    "Product Wizard Page":
        "WizardPage"
}


def resolve_ui_component(name: str):

    for key, value in UI_COMPONENTS.items():

        if key.lower() in name.lower():
            return value

    return None
