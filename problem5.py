"""
问题 5: 数据管道聚合器(AI 开发)
Problem 5: Data Pipeline Aggregator (Developped by AI)
"""
from typing import List, Dict, Any, Optional, Callable


def clean_and_aggregate(
    records: List[Dict[str, Any]],
    group_by: str,
    metric: str,
    aggregation: str = "mean",
    filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None
) -> Dict[str, float]:
    """
    Filter, clean, and aggregate a list of dictionary records by a grouping key.
    根据分组键过滤、清洗并聚合字典记录列表。

    Args:
    参数：
        records (List[Dict[str, Any]]): List of records (each record is a dict).
        records (List[Dict[str, Any]])：记录列表（每条记录都是一个字典）。
        group_by (str): The dictionary key to group records by.
        group_by (str)：用于分组的字典键。
        metric (str): The numeric dictionary key to aggregate.
        metric (str)：要聚合的数值字典键。
        aggregation (str): Aggregation function: "sum", "mean", "min", "max", or "count".
        aggregation (str)：聚合函数："sum"、"mean"、"min"、"max" 或 "count"。
        filter_fn (Optional[Callable]): Optional predicate function to filter records before aggregation.
        filter_fn (Optional[Callable])：在聚合前筛选记录的可选谓词函数。

    Returns:
    返回：
        Dict[str, float]: Aggregated dictionary mapping group names to calculated float metrics.
        Dict[str, float]：按分组名映射到计算结果浮点值的聚合字典。

    Raises:
    引发：
        ValueError: 如果 records 为空、聚合类型无效，或记录中缺少键。
        TypeError: 如果 records 不是列表，或者指标值不是数字。
    """

    valid_aggregations = {"sum", "mean", "min", "max", "count"}
    agg_op = aggregation.lower()
    if agg_op not in valid_aggregations:
        raise ValueError(f"Invalid aggregation '{aggregation}'. Must be one of {valid_aggregations}")

    if not records:
        raise ValueError("records cannot be empty")

    # 分组数据 Group data
    grouped_values: Dict[str, List[float]] = {}

    for i, record in enumerate(records):
        if not isinstance(record, dict):
            raise TypeError(f"Record at index {i} must be a dictionary")
        if group_by not in record:
            raise ValueError(f"Record at index {i} is missing group_by key: '{group_by}'")
        if metric not in record:
            raise ValueError(f"Record at index {i} is missing metric key: '{metric}'")

        # 应用可选过滤器 Apply optional filter
        if filter_fn is not None and not filter_fn(record):
            continue

        raw_val = record[metric]
        if raw_val is None:
            continue  # Skip None / missing values

        if not isinstance(raw_val, (int, float)) or isinstance(raw_val, bool):
            raise TypeError(f"Metric value '{raw_val}' in record {i} is not numeric")

        group_key = str(record[group_by])
        if group_key not in grouped_values:
            grouped_values[group_key] = []
        grouped_values[group_key].append(float(raw_val))

    # 计算聚合结果 Compute aggregations
    results: Dict[str, float] = {}
    for group_key, values in grouped_values.items():
        if not values:
            continue
        if agg_op == "sum":
            val = sum(values)
        elif agg_op == "mean":
            val = sum(values) / len(values)
        elif agg_op == "min":
            val = min(values)
        elif agg_op == "max":
            val = max(values)
        elif agg_op == "count":
            val = len(values)
        else:
            val = 0.0

        results[group_key] = round(val, 2)

    return results
