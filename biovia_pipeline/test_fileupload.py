import logging
import os
from pathlib import Path
from typing import Optional, Union, Dict, Any

from .notebook_connection import (
    NotebookConnectionObject,
    notebook_connection
)
from .experiment_query import experiment_query

logger = logging.getLogger("biovia_pipeline.experiment_attachment")




conn = notebook_connection(
    server_url="https://notebook.unilever.com",
    authentication_method=
        "Use Username and Password Parameters",
    username="arun.khuntia",
    password="Pogoanaisha321!",)

print(conn.session_token)
print(conn.api_endpoint)

experiments = experiment_query(
    connection=conn,
    filter_by="Experiment Number",
    filter_type="Equals",
    filter_value="EXP-26-BP7567"
)

print(experiments)
ids = experiments[0]["ID"]
print(ids)
########### PAYLOAD to create a section with given title##########
payload = {
    "sectiontypeid": 20,
    "title": "AI PLP fileattach"
}

response = conn.session.post(
    f"{conn.api_endpoint}/sections?documentid={ids}",
    json=payload,
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
)
import re
print(response.status_code)
print(response.text)
print(response.headers)
print(50*'=')
print(response)
location = response.headers["Location"]
section_id = int(re.search(r'/sections/(\d+)', location).group(1))
print(section_id)
####################################################
# r = conn.session.get(
#     f"{conn.api_endpoint}/sections/3614931/data",
#     headers={"Accept": "application/json"}
# )
# import json
# print(json.dumps(r.json(), indent=2))
# section_id = 3613786

# from pathlib import Path
####################################################
pdf_file = Path(__file__).parent / "Scinet-new.pptx"
#C:\Users\akhuntia\OneDrive - Capgemini\Desktop\Certification\PLP-Migration\PLP\biovia_pipeline\Unique-standard_UDA_Size_Report.xlsx
###################################
import base64

with open(pdf_file, "rb") as f:
    xlsx_b64 = base64.b64encode(f.read()).decode("utf-8")
    
import pandas as pd
#####################################
# xlsx = pd.ExcelFile(pdf_file)

# parts = []

# for sheet in xlsx.sheet_names:
#     parts.append(f"Sheet: {sheet}")

#     df = pd.read_excel(
#         pdf_file,
#         sheet_name=sheet,
#         dtype=str
#     ).fillna("")

#     for _, row in df.iterrows():
#         parts.append("\t".join(row.astype(str)))

# ascii_text = "\n".join(parts)
################################################
##### EXCEL
# import pandas as pd
# import matplotlib.pyplot as plt
# import io
# import base64

# df = pd.read_excel(
#     pdf_file,
#     nrows=20
# )

# fig, ax = plt.subplots(figsize=(10, 5))
# ax.axis("off")

# table = ax.table(
#     cellText=df.values,
#     colLabels=df.columns,
#     loc="center"
# )

# buffer = io.BytesIO()

# plt.savefig(
#     buffer,
#     format="png",
#     bbox_inches="tight"
# )

# buffer.seek(0)

# png_b64 = base64.b64encode(
#     buffer.read()
# ).decode("utf-8")

# plt.close(fig)
###########################################
## PPTX
from pptx import Presentation
import matplotlib.pyplot as plt
import io
import base64

prs = Presentation(pdf_file)

slide_text = []

for i in range(min(5, len(prs.slides))):
    slide = prs.slides[i]
    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text.strip():
            slide_text.append(shape.text)

text = "\n".join(slide_text[:30])

fig, ax = plt.subplots(figsize=(12, 8))
ax.axis("off")
ax.text(
    0.01,
    0.99,
    text,
    va="top",
    wrap=True,
    fontsize=10
)

buffer = io.BytesIO()

plt.savefig(
    buffer,
    format="png",
    bbox_inches="tight"
)

buffer.seek(0)

png_b64 = base64.b64encode(
    buffer.read()
).decode("utf-8")

plt.close(fig)

filename = os.path.basename(pdf_file)

with open(pdf_file, "rb") as f:
    file_b64 = base64.b64encode(
        f.read()
    ).decode("utf-8")
# # .xls application/vnd.ms-excel
## application/vnd.ms-powerpoint
payload = {
    "datatypeid": 20,
    "Properties": {
        "Height": 15,
        "Width": 617,
        "Tag": 0,
        "FailedLoading": False,
        "XPosition": 0,
        "YPosition": 0
    },
    "Formats": [
        {
            "Mimetype": "text/plain",
            "Content": f"FileName: {filename}"
        },
        {
            "Mimetype": "",
            "Content": {
                "__type": "FileAttachment",
                "Filename": filename
            }
        },
        {
            "Mimetype": "text/plain",
            "Content": file_b64
        }
    ]
}

response = conn.session.post(
    f"{conn.api_endpoint}/sections/{section_id}/data",
    json=payload,
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
)

print(response.status_code)
print(response.text)
print(response.headers)


