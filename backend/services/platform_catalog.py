"""
平台目录加载器

统一读取静态站和 API 共用的平台数据库与能力目录。
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List


CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "platform-catalog.json"


@lru_cache(maxsize=1)
def load_platform_catalog() -> Dict[str, Any]:
    with CATALOG_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def get_platform_databases() -> List[Dict[str, Any]]:
    return load_platform_catalog()["databases"]


def get_platform_capability_lanes() -> List[Dict[str, Any]]:
    return load_platform_catalog()["capability_lanes"]


def get_platform_source_packages() -> List[Dict[str, Any]]:
    return load_platform_catalog()["source_packages"]


def get_platform_database_index() -> Dict[str, Dict[str, Any]]:
    return {database["id"]: database for database in get_platform_databases()}


def get_platform_stats() -> Dict[str, Any]:
    catalog = load_platform_catalog()
    databases = catalog["databases"]
    categories = sorted({database["category"] for database in databases})
    stats = catalog["stats"].copy()
    stats.update(
        {
            "database_total": len(databases),
            "database_categories_total": len(categories),
            "database_categories": categories,
            "capability_total": len(catalog["capability_lanes"]),
        }
    )
    return stats
