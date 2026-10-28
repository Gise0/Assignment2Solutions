# 问题/错误报告 Bug Report

该报告记录了在有错误程序中发现的问题（bugs），包括失败的测试用例、根本原因分析（root cause analysis）以及已应用的修复方案。

---

## 问题/错误报告 1：Problem 4 - 背靠背会议被错误拒绝

### 1. 测试程序 Program Under Test
- **File:** `problem4.py`
- **Class / Function:** `MeetingRoom.book()`

### 2. 失败的测试用例 Failing Test Case

```python
def test_back_to_back_meetings_allowed(self):
    room = MeetingRoom("TestRoom", capacity=10)
    room.book("B1", "Meeting 1", 9, 10, 5)
    # 以下调用应成功但实际抛出 ValueError
    room.book("B2", "Meeting 2", 10, 12, 5)
```

**测试输出 / 错误信息：**
```
ValueError: Time slot [10, 12] conflicts with booking 'B1' [9, 10]
```

### 3. 根本原因分析 Root Cause Analysis
- **预期行为：** 背靠背会议（如 9-10 和 10-12）不应冲突，应允许预订。
- **实际行为：** 代码将背靠背会议错误地识别为时间重叠，抛出 ValueError。
- **根本原因：** 冲突检测逻辑使用了严格不等式（`<` 和 `>`），导致结束时间等于开始时间的情况被误判为重叠。

```python
# 原始代码（有 bug）
if not (end_time < b["start_time"] or start_time > b["end_time"]):
    raise ValueError(...)
```

当新预订为 [10, 12]、已有预订为 [9, 10] 时：
- `end_time (10) < b["start_time"] (10)` → `10 < 10` → `False`
- `start_time (10) > b["end_time"] (10)` → `10 > 10` → `False`
- `not (False or False)` → `True` → 错误地抛出异常

### 4. 代码修复与差异 Code Fix & Diff

```diff
-        if not (end_time < b["start_time"] or start_time > b["end_time"]):
+        if not (end_time <= b["start_time"] or start_time >= b["end_time"]):
```

将 `<` 改为 `<=`，将 `>` 改为 `>=`，使背靠背会议（结束时间 = 开始时间）不被视为冲突。

---

## 问题/错误报告 2：Problem 5 - min/max 聚合函数互换

### 1. 测试程序 Program Under Test
- **File:** `problem5.py`
- **Class / Function:** `clean_and_aggregate()`

### 2. 失败的测试用例 Failing Test Case

```python
def test_aggregate_min_and_max(self):
    min_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="min")
    max_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="max")

    self.assertAlmostEqual(min_result["North"], 100.0)  # 期望最小值
    self.assertAlmostEqual(max_result["North"], 200.0)   # 期望最大值
```

**测试输出 / 错误信息：**
```
AssertionError: 200.0 != 100.0 within 7 places (100.0 difference)
```

### 3. 根本原因分析 Root Cause Analysis
- **预期行为：** `aggregation="min"` 应返回每组的最小值，`aggregation="max"` 应返回每组的最大值。
- **实际行为：** `min` 聚合返回了最大值，`max` 聚合返回了最小值——两个函数体被互换了。
- **根本原因：** 代码中 `min` 和 `max` 对应的内置函数写反了。

```python
# 原始代码（有 bug）
elif agg_op == "min":
    val = max(values)   # Bug: 应该调用 min()
elif agg_op == "max":
    val = min(values)   # Bug: 应该调用 max()
```

### 4. 代码修复与差异 Code Fix & Diff

```diff
-        elif agg_op == "min":
-            val = max(values)
+        elif agg_op == "min":
+            val = min(values)
-        elif agg_op == "max":
-            val = min(values)
+        elif agg_op == "max":
+            val = max(values)
```

---

## 问题/错误报告 3：Problem 5 - 空数据集未抛出异常

### 1. 测试程序 Program Under Test
- **File:** `problem5.py`
- **Class / Function:** `clean_and_aggregate()`

### 2. 失败的测试用例 Failing Test Case

```python
def test_empty_dataset_raises_value_error(self):
    with self.assertRaises(ValueError):
        clean_and_aggregate([], group_by="region", metric="sales")
```

**测试输出 / 错误信息：**
```
AssertionError: ValueError not raised
```

### 3. 根本原因分析 Root Cause Analysis
- **预期行为：** 当传入空列表 `[]` 时，函数应抛出 `ValueError`。
- **实际行为：** 函数静默返回空字典 `{}`，未抛出任何异常。
- **根本原因：** 函数缺少对空输入列表的显式检查。

### 4. 代码修复与差异 Code Fix & Diff

```diff
     valid_aggregations = {"sum", "mean", "min", "max", "count"}
     agg_op = aggregation.lower()
     if agg_op not in valid_aggregations:
         raise ValueError(f"Invalid aggregation '{aggregation}'. Must be one of {valid_aggregations}")

+    if not records:
+        raise ValueError("records cannot be empty")
+
     # 分组数据 Group data
```

在聚合逻辑之前添加空列表检查，当 `records` 为空时立即抛出 `ValueError`。

---

## 问题/错误报告 4：（无其他发现）

在 Problem 2（BankAccount）和 Problem 3（Order）的源代码中未发现逻辑错误。所有测试用例均基于源代码的实际行为编写，用于验证功能的正确性和边界情况的处理。
