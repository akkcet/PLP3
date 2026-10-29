from biovia_pipeline.notebook_connection import notebook_connection
from biovia_pipeline.experiment_query import experiment_query

conn = notebook_connection(
    server_url="https://notebook.unilever.com",
    authentication_method="Use Username and Password Parameters",
    username="arun.khuntia",
    password="Pogoanaisha321!",
)

results = experiment_query(
    connection=conn,
    filter_by="Experiment Number",
    filter_type="Equals",
    filter_value="EXP-26-BP7567",
    mock_data_fallback=False
)

print(results)
