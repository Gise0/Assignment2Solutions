"""
问题 4 单元测试: MeetingRoom

说明：
使用 Python 的 unittest 框架补全下面的单元测试方法。
你的测试方法必须断言 MeetingRoom 对象上的多个属性
（例如 bookings 列表、total_hours_booked、free slots、utilization rate）
以验证会议室状态和冲突管理。

运行测试：
    python -m unittest test_problem4.py -v
"""
import unittest
from problem4 import MeetingRoom


class TestMeetingRoom(unittest.TestCase):

    def setUp(self):
        """
        在每个测试方法执行前设置测试夹具。
        """
        self.room = MeetingRoom("Conference-A", capacity=10)

    def test_initial_state_multi_attributes(self):
        """
        验证空会议室的初始状态。
        """
        self.assertEqual(self.room.room_id, "Conference-A")
        self.assertEqual(self.room.capacity, 10)
        self.assertEqual(self.room.bookings, [])
        self.assertEqual(self.room.total_hours_booked, 0)
        self.assertEqual(self.room.is_maintenance, False)

        # 验证 utilization rate
        rate = self.room.get_utilization_rate(total_available_hours=10)
        self.assertEqual(rate, 0.0)

        # 验证 free slots（无预订时应返回完整时间段）
        free = self.room.get_free_slots(day_start=8, day_end=18)
        self.assertEqual(free, [(8, 18)])

    def test_single_booking_multi_attributes(self):
        """
        测试创建一个有效预订。
        验证 bookings 列表、total_hours_booked、utilization rate 和 free slots。
        """
        # 预订会议 'B01'，时间为 10 到 12，参与人数为 5
        result = self.room.book("B01", "Team Standup", 10, 12, 5)
        self.assertTrue(result)

        # 验证 bookings 列表
        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.bookings[0]["booking_id"], "B01")
        self.assertEqual(self.room.bookings[0]["title"], "Team Standup")
        self.assertEqual(self.room.bookings[0]["start_time"], 10)
        self.assertEqual(self.room.bookings[0]["end_time"], 12)
        self.assertEqual(self.room.bookings[0]["attendees"], 5)

        # 验证 total_hours_booked
        self.assertEqual(self.room.total_hours_booked, 2)

        # 验证 utilization rate (2/10 = 0.2)
        rate = self.room.get_utilization_rate(total_available_hours=10)
        self.assertEqual(rate, 0.2)

        # 验证 free slots
        free = self.room.get_free_slots(day_start=8, day_end=18)
        self.assertEqual(free, [(8, 10), (12, 18)])

    def test_back_to_back_meetings_allowed(self):
        """
        测试有效的连续/背靠背会议 (例如 9-10 和 10-12) 不会引发冲突错误。
        验证两个预订成功后的多属性状态。
        """
        # 预订第一场会议 9-10
        result1 = self.room.book("B01", "Morning Meeting", 9, 10, 5)
        self.assertTrue(result1)

        # 预订背靠背会议 10-12（应该成功，不冲突）
        result2 = self.room.book("B02", "Afternoon Meeting", 10, 12, 5)
        self.assertTrue(result2)

        # 验证两个预订都存在
        self.assertEqual(len(self.room.bookings), 2)

        # 验证 total_hours_booked = 1 + 2 = 3
        self.assertEqual(self.room.total_hours_booked, 3)

        # 验证 free slots
        free = self.room.get_free_slots(day_start=8, day_end=18)
        self.assertEqual(free, [(8, 9), (12, 18)])

        # 验证 utilization rate (3/10 = 0.3)
        rate = self.room.get_utilization_rate(total_available_hours=10)
        self.assertEqual(rate, 0.3)

    def test_overlapping_booking_rejected(self):
        """
        测试重叠预订（例如 9-11 与 10-12, 或完全包含在 9-12 与 10-11 之间）
        应抛出 ValueError, 并保持会议室状态不变。
        """
        # 先预订一个会议
        self.room.book("B01", "First Meeting", 9, 11, 5)

        # 测试部分重叠（开始时间在已有预订中间）
        with self.assertRaises(ValueError):
            self.room.book("B02", "Overlapping Meeting", 10, 12, 5)

        # 测试完全包含（已有预订包含新预订）
        with self.assertRaises(ValueError):
            self.room.book("B03", "Contained Meeting", 9, 10, 5)

        # 测试完全包含（新预订包含已有预订）
        with self.assertRaises(ValueError):
            self.room.book("B04", "Containing Meeting", 8, 12, 5)

        # 验证会议室状态未改变
        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.total_hours_booked, 2)

    def test_cancel_booking_updates_all_attributes(self):
        """
        测试取消预订是否能正确从 bookings 中移除，
        减少 total_hours_booked, 并恢复 free slots。
        """
        # 预订两场会议
        self.room.book("B01", "Meeting 1", 9, 10, 5)
        self.room.book("B02", "Meeting 2", 11, 12, 5)

        # 验证状态
        self.assertEqual(len(self.room.bookings), 2)
        self.assertEqual(self.room.total_hours_booked, 2)

        # 取消第一场会议
        result = self.room.cancel("B01")
        self.assertTrue(result)

        # 验证取消后状态
        self.assertEqual(len(self.room.bookings), 1)
        self.assertEqual(self.room.bookings[0]["booking_id"], "B02")
        self.assertEqual(self.room.total_hours_booked, 1)

        # 验证 free slots 恢复
        free = self.room.get_free_slots(day_start=8, day_end=18)
        self.assertEqual(free, [(8, 11), (12, 18)])

        # 验证 utilization rate
        rate = self.room.get_utilization_rate(total_available_hours=10)
        self.assertEqual(rate, 0.1)

        # 测试取消不存在的预订
        with self.assertRaises(KeyError):
            self.room.cancel("Nonexistent")

    def test_capacity_and_validation_exceptions(self):
        """
        测试边界情况和异常：
        - 参与人数超过容量 (ValueError)
        - 开始时间 >= 结束时间 (ValueError)
        - 预订 ID 重复 (ValueError)
        - 会议室处于维护状态时预订 (RuntimeError)
        - 取消不存在的预订 (KeyError)
        """
        # 测试参与人数超过容量
        with self.assertRaises(ValueError):
            self.room.book("B01", "Too Many People", 9, 10, 11)

        # 测试零参与人数
        with self.assertRaises(ValueError):
            self.room.book("B02", "Zero People", 9, 10, 0)

        # 测试负数参与人数
        with self.assertRaises(ValueError):
            self.room.book("B03", "Negative People", 9, 10, -1)

        # 测试开始时间 >= 结束时间
        with self.assertRaises(ValueError):
            self.room.book("B04", "Invalid Time", 10, 10, 5)
        with self.assertRaises(ValueError):
            self.room.book("B05", "Invalid Time", 12, 10, 5)

        # 测试开始时间为负
        with self.assertRaises(ValueError):
            self.room.book("B06", "Negative Start", -1, 5, 5)

        # 测试重复预订 ID
        self.room.book("B07", "First Booking", 9, 10, 5)
        with self.assertRaises(ValueError):
            self.room.book("B07", "Duplicate ID", 11, 12, 5)

        # 测试会议室维护状态
        self.room.is_maintenance = True
        with self.assertRaises(RuntimeError):
            self.room.book("B08", "During Maintenance", 14, 15, 5)

        # 测试 get_free_slots 的无效参数
        self.room.is_maintenance = False  # 恢复
        with self.assertRaises(ValueError):
            self.room.get_free_slots(day_start=18, day_end=8)

        # 测试 get_utilization_rate 的无效参数
        with self.assertRaises(ValueError):
            self.room.get_utilization_rate(total_available_hours=0)
        with self.assertRaises(ValueError):
            self.room.get_utilization_rate(total_available_hours=-5)

        # 测试容量验证
        with self.assertRaises(ValueError):
            MeetingRoom("BadRoom", capacity=0)
        with self.assertRaises(ValueError):
            MeetingRoom("BadRoom", capacity=-5)


if __name__ == "__main__":
    unittest.main()
