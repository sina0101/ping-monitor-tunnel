# Ping Monitor

A simple and powerful Python-based ping monitor that tracks the status of multiple IP addresses over time, calculates minimum and maximum ping values for the last hour, and displays live information in a rich terminal interface.

## Features
- Monitor multiple IP addresses in real-time.
- Display packet loss, minimum, maximum, and last ping times.
- Show a graphical representation of recent ping history.
- Display status based on ping performance:
  - 🟢 **OK**: Connection is healthy.
  - 🟡 **Slow**: High latency or packet loss.
  - 🔴 **DOWN**: Host is unreachable.

## Requirements
- Python 3.6+
- `rich` library: Install using `pip install rich`.

## How to Run
1. Clone this repository or download the `monitor.py` file.
2. Install the required library:
   
   pip install rich
