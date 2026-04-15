"""
Biotite Integration — PDB parsing, sequence analysis, structure comparison
Adapted from Biotite (BSD 3-Clause)
"""

from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BiotiteBridge:
    """Bridge to Biotite for structural bioinformatics."""

    def __init__(self):
        self._available = False
        try:
            import biotite
            self._available = True
            logger.info("Biotite bridge initialized")
        except ImportError:
            logger.warning("Biotite not available")

    @property
    def available(self) -> bool:
        return self._available

    def parse_pdb(self, pdb_text: str) -> Dict[str, Any]:
        """Parse PDB structure and extract key features."""
        if not self._available:
            return {"error": "Biotite not available"}

        try:
            import biotite.structure as struc
            import biotite.structure.io.pdb as pdb
            import tempfile, os

            # Write to temp file for parsing
            with tempfile.NamedTemporaryFile(mode="w", suffix=".pdb", delete=False) as f:
                f.write(pdb_text)
                tmp_path = f.name

            try:
                pdb_file = pdb.PDBFile.read(tmp_path)
                atom_array = pdb_file.get_structure(model=1)

                # Extract chains
                chains = list(set(atom_array.chain_id))

                # Extract residues
                residues = []
                for res_id, res_name in zip(atom_array.res_id, atom_array.res_name):
                    if (res_id, res_name) not in residues:
                        residues.append((int(res_id), res_name))

                # Secondary structure summary
                try:
                    from biotite.structure import annotate_sse
                    sse = annotate_sse(atom_array)
                    ss_counts = {"helix": int((sse == "a").sum()), "sheet": int((sse == "b").sum()), "coil": int((sse == "c").sum())}
                except:
                    ss_counts = {"helix": 0, "sheet": 0, "coil": 0}

                return {
                    "atom_count": len(atom_array),
                    "chains": chains,
                    "residue_count": len(residues),
                    "residues": residues[:20],
                    "secondary_structure": ss_counts,
                    "bounding_box": {
                        "min": [float(atom_array.coord[:, i].min()) for i in range(3)],
                        "max": [float(atom_array.coord[:, i].max()) for i in range(3)],
                    },
                }
            finally:
                os.unlink(tmp_path)

        except Exception as e:
            logger.error(f"PDB parsing failed: {e}")
            return {"error": str(e)}

    def extract_sequence(self, pdb_text: str) -> Dict[str, str]:
        """Extract amino acid sequences per chain."""
        if not self._available:
            return {}

        try:
            import biotite.structure as struc
            import biotite.structure.io.pdb as pdb
            import biotite.sequence as seq
            import tempfile, os

            with tempfile.NamedTemporaryFile(mode="w", suffix=".pdb", delete=False) as f:
                f.write(pdb_text)
                tmp_path = f.name

            try:
                pdb_file = pdb.PDBFile.read(tmp_path)
                atom_array = pdb_file.get_structure(model=1)

                sequences = {}
                for chain in set(atom_array.chain_id):
                    chain_atoms = atom_array[atom_array.chain_id == chain]
                    try:
                        protein = chain_atoms[struc.filter_amino_acids(chain_atoms)]
                        res_names = []
                        seen = set()
                        for res_id, res_name in zip(protein.res_id, protein.res_name):
                            if res_id not in seen:
                                seen.add(res_id)
                                res_names.append(res_name)
                        three_to_one = {
                            "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C",
                            "GLN": "Q", "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I",
                            "LEU": "L", "LYS": "K", "MET": "M", "PHE": "F", "PRO": "P",
                            "SER": "S", "THR": "T", "TRP": "W", "TYR": "Y", "VAL": "V",
                        }
                        sequences[chain] = "".join(three_to_one.get(r, "X") for r in res_names)
                    except:
                        pass
                return sequences
            finally:
                os.unlink(tmp_path)
        except Exception as e:
            return {"error": str(e)}


biotite_bridge = BiotiteBridge()
