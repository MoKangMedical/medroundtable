"""
PubChem Integration — Direct compound lookup and bioactivity data
Uses PubChemPy (MIT license)
"""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class PubChemBridge:
    """Bridge to PubChem for compound data retrieval."""

    def __init__(self):
        self._pcp = None
        self._available = False
        try:
            import pubchempy as pcp
            self._pcp = pcp
            self._available = True
        except ImportError:
            logger.warning("PubChemPy not available")

    @property
    def available(self) -> bool:
        return self._available

    def get_compound(self, identifier: str, identifier_type: str = "name") -> Optional[Dict[str, Any]]:
        """Get compound data from PubChem."""
        if not self._available:
            return None

        pcp = self._pcp
        try:
            if identifier_type == "name":
                results = pcp.get_compounds(identifier, "name")
            elif identifier_type == "smiles":
                results = pcp.get_compounds(identifier, "smiles")
            elif identifier_type == "cid":
                results = pcp.get_compounds(identifier, "cid")
            else:
                results = pcp.get_compounds(identifier, "name")

            if not results:
                return None

            c = results[0]
            return {
                "cid": c.cid,
                "name": c.iupac_name or identifier,
                "molecular_formula": c.molecular_formula,
                "molecular_weight": float(c.molecular_weight) if c.molecular_weight else None,
                "canonical_smiles": c.canonical_smiles,
                "isomeric_smiles": c.isomeric_smiles,
                "xlogp": c.xlogp,
                "tpsa": c.tpsa,
                "h_bond_donors": c.h_bond_donor_count,
                "h_bond_acceptors": c.h_bond_acceptor_count,
                "rotatable_bonds": c.rotatable_bond_count,
                "synonyms": (c.synonyms or [])[:5],
            }
        except Exception as e:
            logger.error(f"PubChem lookup failed: {e}")
            return None

    def search_similar(self, smiles: str, threshold: int = 90, max_results: int = 20) -> List[Dict[str, Any]]:
        """Search for structurally similar compounds."""
        if not self._available:
            return []

        pcp = self._pcp
        try:
            results = pcp.get_compounds(smiles, "smiles", searchtype="similarity", Threshold=threshold)
            output = []
            for c in results[:max_results]:
                output.append({
                    "cid": c.cid,
                    "name": c.iupac_name or f"CID_{c.cid}",
                    "molecular_formula": c.molecular_formula,
                    "molecular_weight": float(c.molecular_weight) if c.molecular_weight else None,
                    "canonical_smiles": c.canonical_smiles,
                })
            return output
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []

    def get_bioassays(self, cid: int, max_results: int = 10) -> List[Dict[str, Any]]:
        """Get bioassay results for a compound."""
        if not self._available:
            return []

        pcp = self._pcp
        try:
            assays = pcp.get_assays(cid)
            output = []
            for a in assays[:max_results]:
                output.append({
                    "aid": a.aid,
                    "name": a.name,
                    "description": (a.description or "")[:200],
                })
            return output
        except Exception as e:
            logger.error(f"Bioassay lookup failed: {e}")
            return []


pubchem_bridge = PubChemBridge()
