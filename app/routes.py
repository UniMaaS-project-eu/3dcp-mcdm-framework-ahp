import json
import os
from flask_restx import Resource
from app import mcdm_api
from app.ahp_structure import AHPElement

BASE_DIR = os.path.dirname(__file__)
HIERARCHY_PATH = os.path.join(BASE_DIR, "static", "hierarchy.json")

# global
HIERARCHY = []
ATTRIBUTES = []
KPIS = []
INPUT_DATA = {}
ALTERNATIVES = []
KPI_VECTORS = {}

def load_ahp_structure():
     if not os.path.exists(HIERARCHY_PATH):
            return {
                "error": "hierarchy.json was not found",
                "path": HIERARCHY_PATH
            }, 404

     with open(HIERARCHY_PATH, "r", encoding="utf-8") as file:
        ahp_hierarchy = json.load(file)

     hierarchy = [ AHPElement.from_dict(item) for item in ahp_hierarchy]
     attributes = [item for item in HIERARCHY if not item.kpi]
     kpis = [item for item in HIERARCHY if item.kpi]
     
     return 

@mcdm_api.route("/ahp/load")
class LoadAHP(Resource):
    @staticmethod
    def get():
        """
        Reads AHP hierarchical structure from file: hierarchy.json from app/static/
        and converts every item into an AHPElement object.
        """
        global HIERARCHY, ATTRIBUTES, KPIS

        if not os.path.exists(HIERARCHY_PATH):
            return {
                "error": "hierarchy.json was not found",
                "path": HIERARCHY_PATH
            }, 404

        with open(HIERARCHY_PATH, "r", encoding="utf-8") as file:
            ahp_hierarchy = json.load(file)

        HIERARCHY = [ AHPElement.from_dict(item) for item in ahp_hierarchy]
        ATTRIBUTES = [item for item in HIERARCHY if not item.kpi]
        KPIS = [item for item in HIERARCHY if item.kpi]

        return {
            "message": "AHP hierarchy loaded successfully",
            "total_elements": len(HIERARCHY),
            "attributes": [item.to_dict() for item in ATTRIBUTES],
            "kpis": [item.to_dict() for item in KPIS]
        }, 200




# @mcdm_api.route("/health")
# class Health(Resource):
#     @staticmethod
#     def get():
#         return {
#             "status": "ok",
#             "message": "MCDM API is running"
#         }, 200