import json
import os
from flask import request
from flask_restx import Resource
from app import mcdm_api
from app.ahp_structure import AHPElement
from app.ahp.methods import qahp_rrv_kpi_calc, attr_rrv

BASE_DIR = os.path.dirname(__file__)
HIERARCHY_PATH = os.path.join(BASE_DIR, "static", "hierarchy.json")

PREFERENCES = []
ALTERNATIVES = []
CRITERION_VECTORS = {}

# Here start writting functionalities for the API -----------
def read_hierarchy_json():
    """
    Reads the static hierarchy.json file.
    """
    if not os.path.exists(HIERARCHY_PATH):
        raise FileNotFoundError(f"hierarchy.json was not found: {HIERARCHY_PATH}")

    with open(HIERARCHY_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

def load_ahp_structure():
     """
     Load the hierarchy into the AHP elements class, separate attributes and kpis
     """
     ahp_hierarchy = read_hierarchy_json()

     hierarchy = [ AHPElement.from_dict(item) for item in ahp_hierarchy]
     attributes = [item for item in hierarchy if not item.kpi]
     kpis = [item for item in hierarchy if item.kpi]
     
     return hierarchy, attributes, kpis


def prepare_criterion_vectors(alternatives, kpis):
    """
    Creates one vector of values per criterion.
    Example:
        C1 -> [12, 12, 12, 20]
        C2 -> [3, 3, 3, 7]
    The criterion IDs are read from the AHP KPI elements,
    using each KPI's criterion_id field.
    """
    criterion_vectors = {}

    for kpi in kpis:
        criterion_id = kpi.criterion_id

        if not criterion_id:
            raise ValueError(f"KPI '{kpi.name}' does not have a criterion_id.")

        values = []

        for alternative in alternatives:
            if criterion_id not in alternative:
                raise ValueError(
                    f"Alternative with materialID '{alternative.get('materialID')}' "
                    f"and supplierID '{alternative.get('supplierID')}' "
                    f"is missing criterion '{criterion_id}'."
                )
            values.append(alternative[criterion_id])
        criterion_vectors[criterion_id] = values

        # Also store the vector inside the corresponding KPI object
        kpi.values = values
    return criterion_vectors


def read_alternatives_input(body, kpis):
    """
    Reads the request body, and prepares criterion vectors.
    """

    preferences = body["preferences"]
    preferences = [float(value) for value in preferences]
    alternatives = body["alternatives"] 

    if len(preferences) != 4: # Depending on the MCDM scenario!!!!!
        raise ValueError("'preferences' must contain exactly 4 values.")
   
    criterion_vectors = prepare_criterion_vectors(
        alternatives=alternatives,
        kpis=kpis
    )

    return preferences, alternatives, criterion_vectors

def anv_preferences(preferences, attributes, kpis):
    """
    Update weight values for the respective criteria for ANV pilot
    """
    top_attr = next(attr for attr in attributes if attr.pid == 0)
    children = []

    # Find child attributes of the overall/top-level atribute
    for attr in attributes:
        if attr.pid == top_attr.id:
            children.append(attr)

    # Find child KPIs of the overall/top-level atribute
    for kpi in kpis:
        if kpi.pid == top_attr.id:
            children.append(kpi)

    # children stores the same object references
    children = sorted(children, key=lambda x: x.id)

    for index, child in enumerate(children):
        child.weight = float(preferences[index])

    return attributes, kpis


# Here start writting the routes for the API -----------
@mcdm_api.route("/ahp/kpis") # read the KPIs for the AHP
class GetKPIs(Resource):
    @staticmethod
    def get():
        """
        Returns only KPI elements.
        """
        try:
            _, _, kpis = load_ahp_structure()
            return {
                "kpis_count": len(kpis),
                "kpis": [item.to_dict() for item in kpis]
            }, 200

        except Exception as exc:
            return {
                "error": "Could not retrieve KPIs.",
                "details": str(exc)
            }, 500



@mcdm_api.route("/ahp/attributes") # read the attributes for the AHP
class GetAttributes(Resource):
    @staticmethod
    def get():
        """
        Returns only attribute elements.
        """
        try:
            _, attributes, _ = load_ahp_structure()
            return {
                "attributes_count": len(attributes),
                "attributes": [item.to_dict() for item in attributes]
            }, 200

        except Exception as exc:
            return {
                "error": "Could not retrieve attributes.",
                "details": str(exc)
            }, 500

@mcdm_api.route("/alternatives")
class Alternatives(Resource):
    @staticmethod
    def post():
        """
        Receives preferences and concrete alternatives.
        Prepares one vector of values per criterion.
        """

        global PREFERENCES, ALTERNATIVES, CRITERION_VECTORS

        try:
            hierachy, attributes, kpis = load_ahp_structure()
            body = request.get_json()
            preferences, alternatives, criterion_vectors = read_alternatives_input(
                body=body,
                kpis=kpis
            )

            # Here apply preferences to root children
            attributes, kpis = anv_preferences(
            preferences=preferences,
            attributes=attributes,
            kpis=kpis
            )

            PREFERENCES = preferences
            ALTERNATIVES = alternatives
            CRITERION_VECTORS = criterion_vectors

            # TODO: When the calculations are ready
            # return ahp_result, overall_rrv, _, _

            # Calculate rrv for the KPIs 
            for kpi in kpis:
                kpi.rrv = qahp_rrv_kpi_calc(kpi.values, kpi.high_better)
                # print(kpi.rrv)

            # Calculate rrv for the Attributes
            attributes = attr_rrv(attributes, kpis)

            # Find best and prepare output
            overall_rank = next(attr for attr in attributes if attr.pid == 0)
            best_index = overall_rank.rrv.index(max(overall_rank.rrv))

            best_alternative = alternatives[best_index]
            print(best_alternative)

            return {"overall_rank": overall_rank.to_dict(),
                    "best_index": best_index,
                    "best_alternative": best_alternative,
                    "attributes": [attr.to_dict() for attr in attributes],
                    "kpis":[kpi.to_dict() for kpi in kpis]}, 200

        except KeyError as exc:
            return {
                "error": f"Missing required field: {str(exc)}"
            }, 400