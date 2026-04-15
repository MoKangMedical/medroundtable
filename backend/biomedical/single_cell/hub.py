"""
Single-Cell Benchmarking Interface — MedRoundTable Biomedical Hub
Lightweight interface for single-cell model discovery and evaluation
Adapted from VirtualCell
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ModelInfo:
    id: str
    name: str
    description: str
    modality: str  # scRNA-seq, ATAC-seq, multi-omics
    task_types: List[str] = field(default_factory=list)
    reference: str = ""


@dataclass
class DatasetInfo:
    id: str
    name: str
    n_cells: int
    n_genes: int
    organism: str
    tissue: str
    task_types: List[str] = field(default_factory=list)


# Pre-registered models from VirtualCell benchmark
KNOWN_MODELS = [
    ModelInfo("scgpt", "scGPT", "Foundation model for single-cell biology", "scRNA-seq",
              ["cell_type_annotation", "perturbation_prediction", "gene_imputation"],
              "https://github.com/bowang-lab/scGPT"),
    ModelInfo("geneformer", "GeneFormer", "Context-aware transformer for single-cell", "scRNA-seq",
              ["cell_type_annotation", "gene_network_inference"],
              "https://huggingface.co/ctheodoris/Geneformer"),
    ModelInfo("scfoundation", "scFoundation", "Large-scale single-cell foundation model", "scRNA-seq",
              ["cell_type_annotation", "drug_response", "gene_expression"],
              "https://github.com/biomap-research/scFoundation"),
    ModelInfo("cell_lm", "CellLM", "Language model for cellular biology", "scRNA-seq",
              ["cell_type_annotation", "gene_program_discovery"],
              "https://github.com/sony/cell_lm"),
    ModelInfo("uce", "UCE", "Universal Cell Embedding", "scRNA-seq",
              ["cell_type_annotation", "cross_species_transfer"],
              "https://github.com/snap-stanford/UCE"),
    ModelInfo("scbert", "scBERT", "BERT for single-cell transcriptomics", "scRNA-seq",
              ["cell_type_annotation", "perturbation_prediction"],
              "https://github.com/TencentAILabHealthcare/scBERT"),
    ModelInfo("lingshu_cell", "Lingshu-Cell", "灵枢细胞 — 中医经络视角的细胞状态模型", "scRNA-seq",
              ["cell_type_annotation", "tcm_meridian_mapping"],
              ""),
]

KNOWN_DATASETS = [
    DatasetInfo("pbmc_10x", "PBMC 10X", 68579, 2000, "human", "blood", ["cell_type_annotation"]),
    DatasetInfo("lung_atlas", "Human Lung Cell Atlas", 584944, 2000, "human", "lung", ["cell_type_annotation"]),
    DatasetInfo("pancreas", "Human Pancreas", 14890, 2000, "human", "pancreas", ["cell_type_annotation"]),
    DatasetInfo("tabula_muris", "Tabula Muris", 100000, 2000, "mouse", "multi-tissue", ["cell_type_annotation"]),
    DatasetInfo("brain_allen", "Allen Brain Atlas", 120000, 2000, "mouse", "brain", ["cell_type_annotation"]),
    DatasetInfo("immune_cell", "Immune Cell Atlas", 350000, 2000, "human", "immune", ["cell_type_annotation"]),
]

TASK_TYPES = [
    {"id": "cell_type_annotation", "name": "细胞类型注释", "description": "根据基因表达谱预测细胞类型"},
    {"id": "perturbation_prediction", "name": "扰动预测", "description": "预测基因敲除/过表达后的表达变化"},
    {"id": "gene_imputation", "name": "基因补全", "description": "填充dropout导致的零值"},
    {"id": "drug_response", "name": "药物响应预测", "description": "预测细胞对药物的响应"},
    {"id": "gene_network_inference", "name": "基因网络推断", "description": "从表达数据推断基因调控网络"},
]


class SingleCellHub:
    """Lightweight single-cell model/dataset discovery interface."""

    def __init__(self):
        self.models = {m.id: m for m in KNOWN_MODELS}
        self.datasets = {d.id: d for d in KNOWN_DATASETS}

    def list_models(self, task: Optional[str] = None) -> List[Dict[str, Any]]:
        models = []
        for m in self.models.values():
            if task and task not in m.task_types:
                continue
            models.append({
                "id": m.id, "name": m.name, "description": m.description,
                "modality": m.modality, "task_types": m.task_types, "reference": m.reference,
            })
        return models

    def list_datasets(self, organism: Optional[str] = None) -> List[Dict[str, Any]]:
        datasets = []
        for d in self.datasets.values():
            if organism and d.organism != organism:
                continue
            datasets.append({
                "id": d.id, "name": d.name, "n_cells": d.n_cells, "n_genes": d.n_genes,
                "organism": d.organism, "tissue": d.tissue, "task_types": d.task_types,
            })
        return datasets

    def list_tasks(self) -> List[Dict[str, str]]:
        return TASK_TYPES

    def get_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        m = self.models.get(model_id)
        if not m:
            return None
        return {
            "id": m.id, "name": m.name, "description": m.description,
            "modality": m.modality, "task_types": m.task_types, "reference": m.reference,
        }


hub = SingleCellHub()
