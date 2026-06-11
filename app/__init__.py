from flask import Flask
from flask_restx import Api, Namespace, fields

app = Flask(__name__)

api = Api(
    app,
    version="1.0",
    title="UniMaaS MCDM API",
    description="API for AHP-based selection"
)

mcdm_api = Namespace(
    "mcdm_api",
    description="MCDM - AHP-based structure and ranking"
)

api.add_namespace(mcdm_api, path="/mcdm_api")

weights_model = api.model(
    "WeightsInput",
    {
        "weights": fields.Raw(
            required=True,
            description="Dictionary with node names as keys and weights as values"
        )
    }
)

alternatives_model = api.model(
    "AlternativesInput",
    {
        "alternatives": fields.List(
            fields.Raw,
            required=True,
            description="List of alternatives with KPI values"
        )
    }
)

from app import routes
