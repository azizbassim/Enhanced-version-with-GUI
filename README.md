# Enhanced-version-with-GUI
System Stress Tester - A tool for testing system stability and performance with GUI
# System Stress Tester

A powerful cross-platform system stress testing tool written in Python. Test your system's stability by stressing CPU cores and RAM simultaneously while monitoring performance metrics.

## ⚠️ Disclaimer

**Use this tool responsibly!** This software is designed for:
- Testing system stability under load
- Benchmarking cooling solutions
- Validating overclocking stability
- Testing thermal management
- Educational purposes

**Do not use on production systems without proper precautions.**

## Features

- 🚀 Multi-core CPU stress testing
- 💾 RAM allocation and stress testing
- 📊 Real-time resource monitoring
- 📈 Detailed performance metrics
- 💾 JSON result export
- 🎛️ Configurable parameters via CLI
- 🛡️ Graceful interruption handling
- 📱 Cross-platform (Windows, Linux, macOS)

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/system-stress-tester.git
cd system-stress-tester

# Install dependencies
pip install -r requirements.txt

# Run the tool
python src/stress_tester.py

Command Line Options

Option	Description	Default
-c, --cores	Number of CPU cores to stress	All available cores
-r, --ram	RAM to allocate in GB	2 GB
-d, --duration	Test duration in seconds	10 seconds
-o, --output	Save results to JSON file	False
-q, --quiet	Suppress detailed output	False
-h, --help	Show help message	-
