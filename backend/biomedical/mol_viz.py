"""
Molecular Visualization Data Converter — MedRoundTable Biomedical Hub
Atom/splat data conversion for 3D molecular visualization
Adapted from PharmaSpark
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Optional
import math


# CPK coloring + vdW radii
ELEMENTS = {
    "H":  {"color": [255, 255, 255], "vdw": 1.20, "mass": 1.008},
    "C":  {"color": [100, 100, 100], "vdw": 1.70, "mass": 12.011},
    "N":  {"color": [48,  80,  240], "vdw": 1.55, "mass": 14.007},
    "O":  {"color": [255, 13,  13],  "vdw": 1.52, "mass": 15.999},
    "P":  {"color": [255, 128, 0],   "vdw": 1.80, "mass": 30.974},
    "S":  {"color": [255, 255, 48],  "vdw": 1.80, "mass": 32.065},
    "F":  {"color": [144, 224, 80],  "vdw": 1.47, "mass": 18.998},
    "Cl": {"color": [31,  240, 31],  "vdw": 1.75, "mass": 35.453},
    "Br": {"color": [166, 41,  41],  "vdw": 1.85, "mass": 79.904},
    "DEFAULT": {"color": [255, 20, 147], "vdw": 1.70, "mass": 0},
}


def get_element(symbol: str) -> Dict[str, Any]:
    return ELEMENTS.get(symbol, ELEMENTS.get(symbol[0].upper(), ELEMENTS["DEFAULT"]))


@dataclass
class AtomData:
    x: float
    y: float
    z: float
    element: str
    color: List[int]
    vdw: float


@dataclass
class SplatData:
    """Gaussian splat data for 3D rendering."""
    positions: List[List[float]]  # [[x,y,z], ...]
    scales: List[List[float]]     # [[sx,sy,sz], ...]
    colors: List[List[float]]     # [[r,g,b,a], ...] normalized 0-1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "positions": self.positions,
            "scales": self.scales,
            "colors": self.colors,
            "count": len(self.positions),
        }


def atoms_to_splats(atoms: List[Dict[str, Any]], radius_scale: float = 0.5, opacity: float = 0.9) -> SplatData:
    """Convert atom list to splat data for 3D visualization."""
    positions, scales, colors = [], [], []
    for atom in atoms:
        elem = get_element(atom.get("element", "C"))
        r = elem["vdw"] * radius_scale
        positions.append([atom["x"], atom["y"], atom["z"]])
        scales.append([r, r, r])
        c = elem["color"]
        colors.append([c[0]/255, c[1]/255, c[2]/255, opacity])
    return SplatData(positions=positions, scales=scales, colors=colors)


def parse_pdb_atoms(pdb_text: str) -> List[Dict[str, Any]]:
    """Parse ATOM/HETATM records from PDB text."""
    atoms = []
    for line in pdb_text.split("\n"):
        if line[:6].strip() not in ("ATOM", "HETATM"):
            continue
        element = line[76:78].strip() if len(line) >= 78 else line[12:14].strip().replace("0-9", "")
        if not element:
            element = "C"
        atoms.append({
            "x": float(line[30:38]),
            "y": float(line[38:46]),
            "z": float(line[46:54]),
            "element": element,
            "residue": line[17:20].strip(),
            "chain": line[21],
            "res_seq": int(line[22:26].strip()),
            "b_factor": float(line[60:66].strip()) if len(line) >= 66 else 0.0,
        })
    return atoms


def molecular_to_viz(mol_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert molecular data to visualization-ready format.
    Input: {"atoms": [...], "bonds": [...], "center": [x,y,z]}
    Output: {"splat_data": {...}, "center": [...], "atom_count": N, "bond_count": N}
    """
    atoms = mol_data.get("atoms", [])
    splats = atoms_to_splats(atoms)

    # Compute center
    if atoms:
        cx = sum(a["x"] for a in atoms) / len(atoms)
        cy = sum(a["y"] for a in atoms) / len(atoms)
        cz = sum(a["z"] for a in atoms) / len(atoms)
    else:
        cx, cy, cz = 0, 0, 0

    return {
        "splat_data": splats.to_dict(),
        "center": [cx, cy, cz],
        "atom_count": len(atoms),
        "bond_count": len(mol_data.get("bonds", [])),
    }


mol_viz = type("MolViz", (), {
    "atoms_to_splats": staticmethod(atoms_to_splats),
    "parse_pdb_atoms": staticmethod(parse_pdb_atoms),
    "molecular_to_viz": staticmethod(molecular_to_viz),
})()
