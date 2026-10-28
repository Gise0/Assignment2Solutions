"""
问题 5 单元测试: clean_and_aggregate

该测试套件作为完整参考套件提供。
学生可以运行此测试套件来验证回归测试，并用它验证他们在其他作业中的持续集成 (CI) 配置。

运行测试：
    python -m unittest test_problem5.py -v
"""
import unittest
from problem5 import clean_and_aggregate


class TestDataAggregator(unittest.TestCase):

    def setUp(self):
        """
        为测试准备样例数据集。
        """
        self.sample_sales = [
            {"region": "North", "rep": "Alice", "sales": 100.0, "active": True},
            {"region": "North", "rep": "Bob", "sales": 200.0, "active": True},
            {"region": "South", "rep": "Charlie", "sales": 150.0, "active": False},
            {"region": "South", "rep": "Diana", "sales": 350.0, "active": True},
            {"region": "East", "rep": "Evan", "sales": 500.0, "active": True},
            {"region": "East", "rep": "Fiona", "sales": None, "active": True},  # Null value to test cleaning
            # 空值用于测试清理
        ]

    def test_aggregate_mean_by_region(self):
        """
        测试按地区计算平均销售额。
        """
        result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="mean")
        expected = {
            "North": 150.0,  # (100 + 200) / 2
            "South": 250.0,  # (150 + 350) / 2
            "East": 500.0    # 500 / 1 (ignoring None)
            # 500 / 1（忽略 None）
        }
        self.assertDictEqual(result, expected)

    def test_aggregate_sum_by_region(self):
        """
        测试按地区计算销售额总和。
        """
        result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="sum")
        expected = {
            "North": 300.0,
            "South": 500.0,
            "East": 500.0
        }
        self.assertDictEqual(result, expected)

    def test_aggregate_min_and_max(self):
        """
        测试最小值和最大值聚合操作。
        """
        min_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="min")
        max_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="max")

        self.assertAlmostEqual(min_result["North"], 100.0)
        self.assertAlmostEqual(max_result["North"], 200.0)
        self.assertAlmostEqual(min_result["South"], 150.0)
        self.assertAlmostEqual(max_result["South"], 350.0)

    def test_aggregate_count(self):
        """
        测试统计非空指标值的记录数。
        """
        count_result = clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="count")
        self.assertAlmostEqual(count_result["North"], 2.0)
        self.assertAlmostEqual(count_result["South"], 2.0)
        self.assertAlmostEqual(count_result["East"], 1.0)  # Fiona 的 None sales 会被跳过

    def test_filter_function(self):
        """
        测试在聚合前筛选活跃代表。
        """
        result = clean_and_aggregate(
            self.sample_sales,
            group_by="region",
            metric="sales",
            aggregation="sum",
            filter_fn=lambda r: r.get("active") is True
        )
        # Charlie（South, 150）应被排除
        self.assertAlmostEqual(result["South"], 350.0)
        self.assertAlmostEqual(result["North"], 300.0)

    def test_empty_dataset_raises_value_error(self):
        """
        测试传入空列表时抛出 ValueError。
        """
        with self.assertRaises(ValueError):
            clean_and_aggregate([], group_by="region", metric="sales")

    def test_invalid_input_types_raise_type_error(self):
        """
        测试无效类型会抛出 TypeError。
        """
        with self.assertRaises(TypeError):
            clean_and_aggregate("not a list", group_by="region", metric="sales")

        invalid_data = [{"region": "North", "sales": "one hundred"}]  # 字符串代替数字
        with self.assertRaises(TypeError):
            clean_and_aggregate(invalid_data, group_by="region", metric="sales")

    def test_missing_keys_raise_value_error(self):
        """
        测试缺失字典键时抛出 ValueError。
        """
        invalid_data = [{"country": "USA", "revenue": 100}]
        with self.assertRaises(ValueError):
            clean_and_aggregate(invalid_data, group_by="region", metric="sales")

    def test_invalid_aggregation_operator_raises_value_error(self):
        """
        测试未知聚合名称会抛出 ValueError。
        """
        with self.assertRaises(ValueError):
            clean_and_aggregate(self.sample_sales, group_by="region", metric="sales", aggregation="variance")


if __name__ == "__main__":
    unittest.main()
