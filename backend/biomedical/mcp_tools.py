"""
MCP Tool Registry — MedRoundTable Biomedical Hub
Lightweight MCP tool integration for biomedical data sources
Adapted from OpenClaw-Medical-Harness
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import json


@dataclass
class MCPToolDefinition:
    name: str
    description: str
    category: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    endpoint: str = ""
    available: bool = True


class MCPToolRegistry:
    """Lightweight registry for biomedical MCP tools."""

    def __init__(self):
        self._tools: Dict[str, MCPToolDefinition] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Pre-register core biomedical tools."""
        defaults = [
            MCPToolDefinition(
                name="pubmed",
                description="PubMed literature search — query biomedical literature by keywords, authors, or MeSH terms",
                category="literature",
                parameters={"query": "string", "max_results": "int", "sort": "string"},
                endpoint="https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            ),
            MCPToolDefinition(
                name="chembl",
                description="ChEMBL drug compound database — search drug targets, compounds, and bioactivity data",
                category="drug_data",
                parameters={"target": "string", "compound": "string", "limit": "int"},
                endpoint="https://www.ebi.ac.uk/chembl/api/data",
            ),
            MCPToolDefinition(
                name="opentargets",
                description="OpenTargets drug target validation — disease-target associations, evidence scores",
                category="drug_data",
                parameters={"target_id": "string", "disease_id": "string"},
                endpoint="https://api.platform.opentargets.org/api/v1/graphql",
            ),
            MCPToolDefinition(
                name="omim",
                description="OMIM genetic disease database — Mendelian disorders, gene-phenotype relationships",
                category="genomics",
                parameters={"gene": "string", "phenotype": "string"},
                endpoint="https://api.omim.org/api",
            ),
            MCPToolDefinition(
                name="openfda",
                description="OpenFDA adverse events — drug safety signals, adverse event reports",
                category="drug_safety",
                parameters={"drug": "string", "reaction": "string", "limit": "int"},
                endpoint="https://api.fda.gov/drug/event.json",
            ),
            MCPToolDefinition(
                name="rdkit",
                description="RDKit cheminformatics — molecular descriptors, fingerprints, similarity search",
                category="cheminformatics",
                parameters={"smiles": "string", "operation": "string"},
                endpoint="local",
            ),
        ]
        for tool in defaults:
            self._tools[tool.name] = tool

    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available tools, optionally filtered by category."""
        tools = []
        for tool in self._tools.values():
            if category and tool.category != category:
                continue
            tools.append({
                "name": tool.name,
                "description": tool.description,
                "category": tool.category,
                "parameters": tool.parameters,
                "available": tool.available,
            })
        return tools

    def list_categories(self) -> List[str]:
        """List all tool categories."""
        return list(set(t.category for t in self._tools.values()))

    def get_tool(self, name: str) -> Optional[MCPToolDefinition]:
        """Get tool definition by name."""
        return self._tools.get(name)

    def register_handler(self, name: str, handler: Callable):
        """Register a handler function for a tool."""
        self._handlers[name] = handler

    async def call_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Call a registered tool with arguments."""
        tool = self.get_tool(name)
        if not tool:
            return {"error": f"Tool '{name}' not found", "available_tools": list(self._tools.keys())}
        if not tool.available:
            return {"error": f"Tool '{name}' is currently unavailable"}

        handler = self._handlers.get(name)
        if handler:
            try:
                result = await handler(args) if callable(handler) else handler(args)
                return {"tool": name, "result": result}
            except Exception as e:
                return {"tool": name, "error": str(e)}

        # Default: return tool info for external MCP integration
        return {
            "tool": name,
            "endpoint": tool.endpoint,
            "parameters": tool.parameters,
            "message": f"Tool '{name}' is registered but no local handler. Use MCP endpoint for external execution.",
        }


# Global registry instance
registry = MCPToolRegistry()
