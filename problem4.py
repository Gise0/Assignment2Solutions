"""
问题 4: 会议室调度器(AI 开发)
Problem 4: Meeting Room Scheduler (Developed by AI)

该模块实现了一个 MeetingRoom 类，用于处理多属性调度、冲突检测、利用率跟踪和空闲时间段计算。
"""
from typing import List, Dict, Any, Tuple


class MeetingRoom:
    """
    一个会议室预订管理器，用于跟踪预订记录、容量、已预订总时长、利用率和可用时间段。

    属性(Attributes):
        room_id (str): 房间的唯一名称/编号。
        capacity (int): 允许的最大参与人数。
        bookings (List[Dict[str, Any]]): 按时间顺序排列的预订列表。
        total_hours_booked (int): 已预订的总小时数。
        is_maintenance (bool): 会议室是否因维护而关闭。
    """

    def __init__(self, room_id: str, capacity: int):
        if capacity <= 0:
            raise ValueError("Room capacity must be a positive integer")

        self.room_id = room_id
        self.capacity = int(capacity)
        self.bookings: List[Dict[str, Any]] = []
        self.total_hours_booked = 0
        self.is_maintenance = False

    def book(self, booking_id: str, title: str, start_time: int, end_time: int, attendees: int) -> bool:
        """
        为指定时间段 [start_time, end_time] 预订会议室。
        时间以整数小时表示(例如, 9 表示上午 9:00, 17 表示下午 5:00)。

        规则(Rules):
        1. start_time >= 0 且 end_time > start_time
        2. 参与人数必须 > 0 且 <= capacity。
        3. 若会议室处于维护状态，则无法预订。
        4. 预订 ID 必须唯一。
        5. 不能与现有预订重叠。背靠背会议(例如, 9-10 和 10-11)不会冲突并且允许。
        """
        if self.is_maintenance:
            raise RuntimeError("Cannot book a room that is under maintenance")
        if start_time < 0:
            raise ValueError("Start time cannot be negative")
        if end_time <= start_time:
            raise ValueError("End time must be strictly greater than start time")
        if attendees <= 0:
            raise ValueError("Attendees must be positive")
        if attendees > self.capacity:
            raise ValueError(f"Attendees ({attendees}) exceeds room capacity ({self.capacity})")
        if any(b["booking_id"] == booking_id for b in self.bookings):
            raise ValueError(f"Duplicate booking ID: {booking_id}")

        # 检查与现有预订的时间冲突
        for b in self.bookings:
            if not (end_time <= b["start_time"] or start_time >= b["end_time"]):
                raise ValueError(f"Time slot [{start_time}, {end_time}] conflicts with booking '{b['booking_id']}' [{b['start_time']}, {b['end_time']}]")

        new_booking = {
            "booking_id": booking_id,
            "title": title,
            "start_time": start_time,
            "end_time": end_time,
            "attendees": attendees
        }

        self.bookings.append(new_booking)
        self.bookings.sort(key=lambda x: x["start_time"])
        self.total_hours_booked += (end_time - start_time)
        return True

    def cancel(self, booking_id: str) -> bool:
        """根据 booking_id 取消现有预订"""
        for i, b in enumerate(self.bookings):
            if b["booking_id"] == booking_id:
                duration = b["end_time"] - b["start_time"]
                self.total_hours_booked -= duration
                del self.bookings[i]
                return True
        raise KeyError(f"Booking ID '{booking_id}' not found")

    def get_free_slots(self, day_start: int = 8, day_end: int = 18) -> List[Tuple[int, int]]:
        """
        返回 day_start 和 day_end 之间可用的空闲时间区间列表(start, end)
        """
        if day_start >= day_end:
            raise ValueError("day_start must be less than day_end")

        free_slots = []
        current_time = day_start

        for b in self.bookings:
            if b["end_time"] <= day_start:
                continue
            if b["start_time"] >= day_end:
                break

            b_start = max(day_start, b["start_time"])
            if b_start > current_time:
                free_slots.append((current_time, b_start))
            current_time = max(current_time, b["end_time"])

        if current_time < day_end:
            free_slots.append((current_time, day_end))

        return free_slots

    def get_utilization_rate(self, total_available_hours: int = 10) -> float:
        """
        计算会议室利用率(total_hours_booked / total_available_hours)
        """
        if total_available_hours <= 0:
            raise ValueError("Total available hours must be positive")
        return round(self.total_hours_booked / total_available_hours, 2)
