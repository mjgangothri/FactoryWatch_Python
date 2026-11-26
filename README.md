# FactoryWatch

FactoryWatch is a premium industrial sensor monitoring dashboard for demonstrating an O(N) sliding-window extrema algorithm. It is intentionally a standard local project: open the folder in VS Code, run the Python standard-library server, and edit the HTML/CSS/JavaScript directly.

## Run in VS Code

1. Install Python 3.9+ and VS Code.
2. Open the `FactoryWatch` folder in VS Code.
3. Open the VS Code terminal.
4. Run `python backend/server.py`.
5. Open `http://127.0.0.1:8000` in your browser.
6. Run tests with `python -m unittest discover -s backend -p "test_*.py" -v`.

No Flask, Django, Node, build step, or Antigravity dependency is required.

## DSA approach

`backend/sensor_engine.py` implements a custom circular deque with `is_empty`, `insert_rear`, `delete_front`, `delete_rear`, `get_front`, and `get_rear`. Two index-based monotonic deques maintain decreasing maxima and increasing minima. Expired indices are removed from the front and dominated indices from the rear. The optimized algorithm is O(N) time and O(K) auxiliary space. A manually implemented O(N*K) reference path is included for comparison.

The chart is visualization only; it never calculates extrema.

## Project structure

- `backend/sensor_engine.py` — custom deque, monotonic sliding-window algorithm, validation, reference algorithm.
- `backend/server.py` — standard-library HTTP server, JSON APIs, static frontend, CSV download.
- `backend/test_sensor_engine.py` — increasing, decreasing, duplicate, negative, single-element, invalid-window, alert, and reference-match tests.
- `frontend/index.html` — dashboard structure.
- `frontend/style.css` — industrial visual system and responsive layout.
- `frontend/animations.css` — motion, glow, entrance, and reduced-motion rules.
- `frontend/script.js` — chart canvas, replay controls, configuration, alerts, and table rendering.
- `data/sample_readings.csv` — ready-to-load sample dataset.

## Team contributions

- **Member 1:** Custom Circular Deque and DSA implementation.
- **Member 2:** Sliding-window testing, edge cases, and complexity analysis.
- **Member 3:** Frontend dashboard, charts, CSS, and animations.
- **Member 4:** Python backend, API integration, CSV handling, and system testing.

## Demo flow

Load sample data, set K to 3, high threshold to 8, and low threshold to 2. Click Analyze to see the alert windows, then use Start Replay to watch readings arrive one at a time. CSV upload accepts a file containing numeric readings separated by commas or line breaks.
