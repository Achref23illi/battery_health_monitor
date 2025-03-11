import unittest
from src.battery_repport import parse_battery_report

class TestBatteryReportParsing(unittest.TestCase):
    def test_parse_battery_report(self):
        # Sample HTML content for testing
        sample_html = """
        <html>
        <body>
            <table>
                <tr><td>Design Capacity</td><td>56999 mWh</td></tr>
                <tr><td>Full Charge Capacity</td><td>21466 mWh</td></tr>
                <tr><td>Cycle Count</td><td>300</td></tr>
            </table>
        </body>
        </html>
        """
        with open("sample_battery_report.html", "w", encoding="utf-8") as f:
            f.write(sample_html)
        
        expected_metrics = {
            "Design Capacity": "56999 mWh",
            "Full Charge Capacity": "21466 mWh",
            "Cycle Count": "300"
        }
        
        parsed_metrics = parse_battery_report("sample_battery_report.html")
        self.assertEqual(parsed_metrics, expected_metrics)

if __name__ == "__main__":
    unittest.main()
