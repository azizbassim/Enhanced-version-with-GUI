#!/usr/bin/env python3
"""
System Stress Tester - A tool for testing system stability and performance
"""

import multiprocessing
import psutil
import time
import threading
import argparse
import signal
import sys
from datetime import datetime
import json
import os

class StressTester:
    def __init__(self):
        self.running = False
        self.results = {
            'start_time': None,
            'end_time': None,
            'cpu_cores': 0,
            'ram_gb': 0,
            'duration': 0,
            'monitoring_data': []
        }
    
    def cpu_worker(self, duration):
        """CPU intensive worker process"""
        end_time = time.time() + duration
        operations = 0
        while time.time() < end_time and self.running:
            # Perform calculations
            x = sum(i*i for i in range(10000))
            operations += 1
        return operations
    
    def ram_worker(self, gb, duration):
        """RAM intensive worker thread"""
        chunks = []
        allocated_gb = 0
        try:
            # Allocate memory in 100MB chunks
            chunk_size = 100 * 1024 * 1024  # 100MB
            target_chunks = gb * 10  # 10 chunks per GB
            
            for _ in range(target_chunks):
                if not self.running:
                    break
                chunks.append(bytearray(chunk_size))
                allocated_gb += 0.1
                
                # Simulate some work
                time.sleep(0.1)
            
            # Hold the memory for the duration
            time.sleep(duration)
            
        except MemoryError:
            print(f"Warning: Could only allocate {allocated_gb:.1f} GB of RAM")
        except Exception as e:
            print(f"RAM worker error: {e}")
        finally:
            # Clean up
            del chunks
        return allocated_gb
    
    def monitor(self, duration):
        """Monitor system resources during test"""
        print("\n" + "="*60)
        print(f"{'Time':<8} {'CPU %':<10} {'RAM %':<10} {'RAM Used':<15}")
        print("="*60)
        
        start_time = time.time()
        while time.time() - start_time < duration and self.running:
            cpu_percent = psutil.cpu_percent(interval=1)
            ram = psutil.virtual_memory()
            ram_percent = ram.percent
            ram_used = ram.used / (1024**3)  # Convert to GB
            
            timestamp = time.time() - start_time
            
            # Store data
            self.results['monitoring_data'].append({
                'time': timestamp,
                'cpu': cpu_percent,
                'ram_percent': ram_percent,
                'ram_used_gb': ram_used
            })
            
            # Print live stats
            print(f"{timestamp:5.1f}s   {cpu_percent:8.1f}%   {ram_percent:8.1f}%   {ram_used:8.2f} GB")
            
            time.sleep(1)  # Monitor every second
    
    def run_stress_test(self, cpu_cores=None, ram_gb=2, duration=10, verbose=True):
        """Run the complete stress test"""
        
        # Auto-detect CPU cores if not specified
        if cpu_cores is None:
            cpu_cores = multiprocessing.cpu_count()
        
        # Validate parameters
        cpu_cores = min(cpu_cores, multiprocessing.cpu_count())
        ram_gb = min(ram_gb, psutil.virtual_memory().total / (1024**3) * 0.8)  # Use max 80% of RAM
        
        self.running = True
        self.results['start_time'] = datetime.now().isoformat()
        self.results['cpu_cores'] = cpu_cores
        self.results['ram_gb'] = ram_gb
        self.results['duration'] = duration
        
        if verbose:
            print(f"\n🚀 Starting Stress Test...")
            print(f"📊 System Info:")
            print(f"   - Total CPU Cores: {multiprocessing.cpu_count()}")
            print(f"   - Total RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB")
            print(f"   - Available RAM: {psutil.virtual_memory().available / (1024**3):.1f} GB")
            print(f"\n⚙️  Test Configuration:")
            print(f"   - CPU Cores to stress: {cpu_cores}")
            print(f"   - RAM to allocate: {ram_gb} GB")
            print(f"   - Duration: {duration} seconds\n")
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor, args=(duration,))
        monitor_thread.start()
        
        # Start CPU stress processes
        cpu_procs = []
        for i in range(cpu_cores):
            p = multiprocessing.Process(target=self.cpu_worker, args=(duration,))
            p.start()
            cpu_procs.append(p)
            if verbose:
                print(f"   Started CPU worker {i+1}/{cpu_cores}")
        
        # Start RAM stress thread
        ram_thread = threading.Thread(target=self.ram_worker, args=(ram_gb, duration))
        ram_thread.start()
        if verbose:
            print(f"   Started RAM worker (target: {ram_gb} GB)")
        
        # Wait for all processes to complete
        for p in cpu_procs:
            p.join()
        ram_thread.join()
        monitor_thread.join()
        
        self.running = False
        self.results['end_time'] = datetime.now().isoformat()
        
        if verbose:
            self.print_summary()
        
        return self.results
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📈 TEST SUMMARY")
        print("="*60)
        
        if self.results['monitoring_data']:
            max_cpu = max(data['cpu'] for data in self.results['monitoring_data'])
            avg_cpu = sum(data['cpu'] for data in self.results['monitoring_data']) / len(self.results['monitoring_data'])
            max_ram = max(data['ram_percent'] for data in self.results['monitoring_data'])
            avg_ram = sum(data['ram_percent'] for data in self.results['monitoring_data']) / len(self.results['monitoring_data'])
            
            print(f"📊 CPU Usage:")
            print(f"   - Peak: {max_cpu:.1f}%")
            print(f"   - Average: {avg_cpu:.1f}%")
            print(f"\n💾 RAM Usage:")
            print(f"   - Peak: {max_ram:.1f}%")
            print(f"   - Average: {avg_ram:.1f}%")
        
        print(f"\n✅ Test completed successfully!")
        print(f"   Duration: {self.results['duration']} seconds")
    
    def save_results(self, filename="stress_test_results.json"):
        """Save test results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")
    
    def stop(self):
        """Stop the stress test"""
        self.running = False
        print("\n🛑 Stopping stress test...")

def main():
    parser = argparse.ArgumentParser(
        description="System Stress Tester - Test your system's stability and performance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Run with auto-detected settings
  %(prog)s -c 4 -r 2 -d 30          # 4 cores, 2GB RAM, 30 seconds
  %(prog)s -c 8 -r 4 -d 60 -o       # 8 cores, 4GB RAM, 60 seconds, output results
  %(prog)s -c 2 -r 1 -d 10          # Light test
        """
    )
    
    parser.add_argument('-c', '--cores', type=int, default=None,
                       help=f'Number of CPU cores to stress (default: all {multiprocessing.cpu_count()} cores)')
    parser.add_argument('-r', '--ram', type=float, default=2,
                       help='RAM to allocate in GB (default: 2)')
    parser.add_argument('-d', '--duration', type=int, default=10,
                       help='Test duration in seconds (default: 10)')
    parser.add_argument('-o', '--output', action='store_true',
                       help='Save results to JSON file')
    parser.add_argument('-q', '--quiet', action='store_true',
                       help='Suppress detailed output')
    
    args = parser.parse_args()
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\n⚠️  Interrupted by user")
        if hasattr(stress_tester, 'stop'):
            stress_tester.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run stress test
    stress_tester = StressTester()
    
    try:
        results = stress_tester.run_stress_test(
            cpu_cores=args.cores,
            ram_gb=args.ram,
            duration=args.duration,
            verbose=not args.quiet
        )
        
        if args.output:
            stress_tester.save_results()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
