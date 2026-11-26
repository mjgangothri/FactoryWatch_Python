"""FactoryWatch core sliding-window DSA engine.

The core path intentionally avoids collections.deque, heapq, max, min, and
sorted. Extrema are maintained with two custom circular monotonic deques.
"""


class CustomCircularDeque:
    def __init__(self, capacity):
        if capacity < 1:
            raise ValueError("Deque capacity must be positive")
        self._data = [None] * capacity
        self._capacity = capacity
        self._front = 0
        self._size = 0

    def is_empty(self):
        return self._size == 0

    def insert_rear(self, value):
        if self._size >= self._capacity:
            raise OverflowError("Deque is full")
        rear = (self._front + self._size) % self._capacity
        self._data[rear] = value
        self._size += 1

    def delete_front(self):
        if self.is_empty():
            raise IndexError("Cannot delete from an empty deque")
        value = self._data[self._front]
        self._data[self._front] = None
        self._front = (self._front + 1) % self._capacity
        self._size -= 1
        return value

    def delete_rear(self):
        if self.is_empty():
            raise IndexError("Cannot delete from an empty deque")
        rear = (self._front + self._size - 1) % self._capacity
        value = self._data[rear]
        self._data[rear] = None
        self._size -= 1
        return value

    def get_front(self):
        if self.is_empty():
            raise IndexError("Deque is empty")
        return self._data[self._front]

    def get_rear(self):
        if self.is_empty():
            raise IndexError("Deque is empty")
        rear = (self._front + self._size - 1) % self._capacity
        return self._data[rear]

    def to_list(self):
        return [self._data[(self._front + offset) % self._capacity] for offset in range(self._size)]


def validate_input(readings, window_size, high_threshold, low_threshold):
    if not isinstance(readings, list) or not readings:
        raise ValueError("Readings must be a non-empty list")
    if not isinstance(window_size, int) or isinstance(window_size, bool):
        raise ValueError("Window size K must be an integer")
    if window_size < 1 or window_size > len(readings):
        raise ValueError("Window size K must be between 1 and the number of readings")
    clean = []
    for reading in readings:
        if isinstance(reading, bool) or not isinstance(reading, (int, float)):
            raise ValueError("Every reading must be numeric")
        clean.append(float(reading))
    if not isinstance(high_threshold, (int, float)) or not isinstance(low_threshold, (int, float)):
        raise ValueError("Thresholds must be numeric")
    if low_threshold >= high_threshold:
        raise ValueError("Low threshold must be less than high threshold")
    return clean


def analyze_readings(readings, window_size, high_threshold, low_threshold):
    readings = validate_input(readings, window_size, high_threshold, low_threshold)
    maximum = CustomCircularDeque(window_size)
    minimum = CustomCircularDeque(window_size)
    windows = []
    operations = []

    for index, value in enumerate(readings):
        expired = index - window_size
        if not maximum.is_empty() and maximum.get_front() <= expired:
            removed = maximum.delete_front()
            operations.append({"type": "front-delete", "deque": "max", "index": removed})
        if not minimum.is_empty() and minimum.get_front() <= expired:
            removed = minimum.delete_front()
            operations.append({"type": "front-delete", "deque": "min", "index": removed})

        while not maximum.is_empty() and readings[maximum.get_rear()] <= value:
            removed = maximum.delete_rear()
            operations.append({"type": "rear-delete", "deque": "max", "index": removed})
        maximum.insert_rear(index)
        operations.append({"type": "rear-insert", "deque": "max", "index": index})

        while not minimum.is_empty() and readings[minimum.get_rear()] >= value:
            removed = minimum.delete_rear()
            operations.append({"type": "rear-delete", "deque": "min", "index": removed})
        minimum.insert_rear(index)
        operations.append({"type": "rear-insert", "deque": "min", "index": index})

        if index >= window_size - 1:
            window_start = index - window_size + 1
            window_values = readings[window_start:index + 1]
            current_max = readings[maximum.get_front()]
            current_min = readings[minimum.get_front()]
            high_alert = current_max > high_threshold
            low_alert = current_min < low_threshold
            status = "HIGH ALERT" if high_alert else "LOW ALERT" if low_alert else "NORMAL"
            windows.append({
                "window": len(windows) + 1,
                "readings": window_values,
                "maximum": current_max,
                "minimum": current_min,
                "high_alert": high_alert,
                "low_alert": low_alert,
                "status": status,
                "end_index": index,
            })

    return {
        "readings": readings,
        "window_size": window_size,
        "high_threshold": high_threshold,
        "low_threshold": low_threshold,
        "windows": windows,
        "operations": operations[-18:],
        "complexity": {"optimized": "O(N)", "reference": "O(N*K)", "space": "O(K)"},
        "deque_state": {
            "max": maximum.to_list(),
            "min": minimum.to_list(),
            "current_index": len(readings) - 1,
        },
    }


def reference_analyze(readings, window_size, high_threshold, low_threshold):
    readings = validate_input(readings, window_size, high_threshold, low_threshold)
    windows = []
    for start in range(len(readings) - window_size + 1):
        end = start + window_size
        current_max = readings[start]
        current_min = readings[start]
        for index in range(start + 1, end):
            if readings[index] > current_max:
                current_max = readings[index]
            if readings[index] < current_min:
                current_min = readings[index]
        windows.append((current_max, current_min))
    return windows
