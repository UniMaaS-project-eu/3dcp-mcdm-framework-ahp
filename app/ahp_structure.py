#
#

class AHPElement:

    def __init__(self, i_d, name, kpi, pid, weight, hb, kpi_type, criterion_id):
        self.id = int(i_d)
        self.name = name

        # True if this node is a KPI, False if it is an attribute
        self.kpi = bool(int(kpi))

        # Parent attribute id (to group sibling KPIs or attributes in the rrn calculations)
        self.pid = int(pid)

        # Local weight under its parent
        self.weight = float(weight)

        # High better flag, mainly useful for numeric KPIs
        self.high_better = bool(int(hb))

        # Examples: attribute, numeric, set, ling
        self.kpi_type = kpi_type

        self.criterion_id = criterion_id

        # Raw KPI values. For non-KPI attributes, this usually remains None.
        self.values = None

        # Relative ranking vector calculated by AHP
        self.rrv = []

    @classmethod
    def from_dict(cls, data):

        """
        Builds an AHPElement from one item in hierarchy.json.
        """

        return cls(
            i_d=data["i_d"],
            name=data["name"],
            kpi=data["kpi"],
            pid=data["pid"],
            weight=data["weight"],
            hb=data["hb"],
            kpi_type=data["kpi_type"],
            criterion_id=data["criterion_id"]
        )

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name,
            "kpi": self.kpi,
            "pid": self.pid,
            "weight": self.weight,
            "high_better": self.high_better,
            "kpi_type": self.kpi_type,
            "criterion_id": self.criterion_id,
            "values": self.values,
            "rrv": self.rrv
        }