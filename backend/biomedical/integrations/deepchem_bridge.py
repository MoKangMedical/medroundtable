"""
DeepChem Integration — MediPharma Virtual Screening Enhancement
Adapted from DeepChem (Apache 2.0) for molecular featurization and prediction
"""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class DeepChemBridge:
    """Bridge to DeepChem for molecular ML capabilities."""

    def __init__(self):
        self._dc = None
        self._available = False
        try:
            import deepchem as dc
            self._dc = dc
            self._available = True
            logger.info("DeepChem bridge initialized successfully")
        except ImportError:
            logger.warning("DeepChem not available. Install with: pip install deepchem")

    @property
    def available(self) -> bool:
        return self._available

    def featurize_smiles(self, smiles_list: List[str], featurizer: str = "morgan") -> Optional[Any]:
        """Convert SMILES to molecular fingerprints/descriptors."""
        if not self._available:
            return None

        dc = self._dc
        featurizers = {
            "morgan": dc.feat.CircularFingerprint(size=2048),
            "rdkit": dc.feat.RDKitDescriptors(),
            "mol2vec": dc.feat.Mol2VecFingerprint(),
            "onehot": dc.feat.OneHotFeaturizer(),
        }
        feat = featurizers.get(featurizer, dc.feat.CircularFingerprint(size=2048))

        try:
            features = feat.featurize(smiles_list)
            return {
                "featurizer": featurizer,
                "shape": list(features.shape),
                "features": features.tolist(),
                "count": len(smiles_list),
            }
        except Exception as e:
            logger.error(f"Featurization failed: {e}")
            return None

    def compute_molecular_properties(self, smiles: str) -> Dict[str, Any]:
        """Compute basic molecular properties."""
        if not self._available:
            return {"error": "DeepChem not available"}

        dc = self._dc
        try:
            from rdkit import Chem
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return {"error": f"Invalid SMILES: {smiles}"}

            return {
                "smiles": smiles,
                "molecular_weight": dc.feat.RDKitDescriptors()._featurize(mol).tolist()[:5],
                "atom_count": mol.GetNumAtoms(),
                "heavy_atom_count": mol.GetNumHeavyAtoms(),
                "ring_count": mol.GetRingInfo().NumRings(),
            }
        except Exception as e:
            return {"error": str(e)}

    def similarity_search(self, query_smiles: str, library_smiles: List[str], top_k: int = 10) -> List[Dict[str, Any]]:
        """Tanimoto similarity search against a compound library."""
        if not self._available:
            return []

        dc = self._dc
        try:
            import numpy as np
            feat = dc.feat.CircularFingerprint(size=2048)
            query_fp = feat.featurize([query_smiles])[0]
            lib_fps = feat.featurize(library_smiles)

            # Tanimoto similarity
            similarities = []
            for i, fp in enumerate(lib_fps):
                intersection = np.sum(query_fp * fp)
                union = np.sum(query_fp) + np.sum(fp) - intersection
                sim = float(intersection / union) if union > 0 else 0.0
                similarities.append({"index": i, "smiles": library_smiles[i], "similarity": round(sim, 4)})

            similarities.sort(key=lambda x: x["similarity"], reverse=True)
            return similarities[:top_k]
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return []


# Global instance
deepchem_bridge = DeepChemBridge()
