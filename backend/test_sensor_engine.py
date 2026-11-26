import unittest
from sensor_engine import analyze_readings, reference_analyze


class SensorEngineTests(unittest.TestCase):
    def test_increasing(self):
        result = analyze_readings([1, 2, 3, 4], 2, 99, -99)
        self.assertEqual([row["maximum"] for row in result["windows"]], [2, 3, 4])

    def test_decreasing(self):
        result = analyze_readings([4, 3, 2, 1], 2, 99, -99)
        self.assertEqual([row["minimum"] for row in result["windows"]], [3, 2, 1])

    def test_duplicates(self):
        result = analyze_readings([5, 5, 5], 2, 6, 4)
        self.assertEqual(len(result["windows"]), 2)
        self.assertTrue(all(row["status"] == "NORMAL" for row in result["windows"]))

    def test_negative_values(self):
        result = analyze_readings([-5, -2, -8], 2, 0, -10)
        self.assertEqual(result["windows"][0]["maximum"], -2)

    def test_single_element(self):
        result = analyze_readings([7], 1, 8, 2)
        self.assertEqual(result["windows"][0]["maximum"], 7)

    def test_invalid_window(self):
        with self.assertRaises(ValueError):
            analyze_readings([1, 2], 3, 9, 0)

    def test_alerts(self):
        result = analyze_readings([4, 1, 7, 3, 6], 3, 8, 2)
        self.assertEqual(result["windows"][0]["status"], "LOW ALERT")
        self.assertEqual(result["windows"][2]["status"], "NORMAL")

    def test_reference_matches_optimized(self):
        readings = [4, 1, 7, 3, 6, 11]
        result = analyze_readings(readings, 3, 8, 2)
        reference = reference_analyze(readings, 3, 8, 2)
        self.assertEqual([(r["maximum"], r["minimum"]) for r in result["windows"]], reference)


if __name__ == "__main__":
    unittest.main()
