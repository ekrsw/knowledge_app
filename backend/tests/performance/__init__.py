"""
Performance Tests Package

This package contains performance and load testing for the Knowledge Revision System.

Test categories:
- API Performance: Response time and throughput testing
- Database Performance: Query performance and bulk operations
- Memory Performance: Memory usage and leak testing
- Concurrent Users: Multi-user simulation testing

Usage:
    # Run all performance tests
    pytest tests/performance/ -m performance -v

    # Run specific performance test categories
    pytest tests/performance/test_performance.py::TestPerformanceAPI -v
    pytest tests/performance/test_performance.py::TestPerformanceDatabase -v
    
Requirements:
- All tests must pass within specified time limits
- Memory usage should remain within acceptable bounds
- Concurrent user tests simulate real-world usage patterns
"""