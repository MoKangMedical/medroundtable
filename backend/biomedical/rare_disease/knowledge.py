"""
Rare Disease Knowledge Graph
Symptom-disease-gene-treatment relationships
"""
from typing import Any, Dict, List


class RareDiseaseKnowledgeGraph:
    """Knowledge graph for rare disease relationships."""

    def __init__(self):
        self.nodes = {}  # id -> {type, name, properties}
        self.edges = []  # (source, target, relation, properties)

    def add_node(self, node_id: str, node_type: str, name: str, **properties):
        self.nodes[node_id] = {"type": node_type, "name": name, "properties": properties}

    def add_edge(self, source: str, target: str, relation: str, **properties):
        self.edges.append({"source": source, "target": target, "relation": relation, "properties": properties})

    def get_related(self, node_id: str, relation: str = None) -> List[Dict[str, Any]]:
        """Get nodes related to a given node."""
        results = []
        for edge in self.edges:
            if edge["source"] == node_id and (relation is None or edge["relation"] == relation):
                target = self.nodes.get(edge["target"], {})
                results.append({"node": target, "relation": edge["relation"]})
            elif edge["target"] == node_id and (relation is None or edge["relation"] == relation):
                source = self.nodes.get(edge["source"], {})
                results.append({"node": source, "relation": edge["relation"]})
        return results

    def get_gene_disease_path(self, gene: str) -> List[Dict[str, Any]]:
        """Find diseases linked to a gene."""
        gene_id = f"gene:{gene}"
        return self.get_related(gene_id, "causes")

    def get_drug_targets(self, disease_id: str) -> List[Dict[str, Any]]:
        """Find drug targets for a disease."""
        return self.get_related(disease_id, "treated_by")


rare_disease_kg = RareDiseaseKnowledgeGraph()
