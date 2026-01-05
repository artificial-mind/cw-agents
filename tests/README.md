# Testing Strategy

## Single Comprehensive Test Suite

This project uses a **single comprehensive E2E test suite** approach to ensure:
- All features are tested in one place
- New features don't break existing functionality
- Easy regression testing
- Clear test coverage visibility

## Test Files

### Primary Test Suite
- **`test_complete_e2e.py`** - The single source of truth for all E2E testing
  - Tests ALL features across the entire stack
  - Append new test scenarios here when adding features
  - Run this before every commit to ensure no regressions

### Deprecated Tests
- `tests/deprecated/` - Old individual test files (kept for reference)
  - These are no longer actively maintained
  - Refer to them only if you need to understand specific test patterns

## Running Tests

### Prerequisites
Ensure all services are running:
```bash
# Terminal 1: Analytics Engine
cd cw-analytics-engine
python start_server.py

# Terminal 2: MCP Server
cd cw-ai-server
python src/server_fastmcp.py

# Terminal 3: A2A Agent Server
cd cw-agents
python src/a2a_server/main.py

# Terminal 4: Brain Server
cd cw-brain
python run_server.py
```

### Run Complete Test Suite
```bash
cd cw-agents
python test_complete_e2e.py
```

### Expected Output
```
======================================================================
       CW LOGISTICS PLATFORM - COMPLETE E2E TEST SUITE              
           All Features - Regression Prevention                     
======================================================================

Starting comprehensive test suite...
Date: 2026-01-05 21:00:00

======================================================================
                    TEST SUITE 1: SERVICE HEALTH CHECKS             
======================================================================

▶ Testing: A2A Agent Server Health Check
✓ PASS: A2A Agent Server is healthy
▶ Testing: MCP Server Health Check
✓ PASS: MCP Server is healthy
...

======================================================================
                         FINAL TEST SUMMARY                          
======================================================================

Total Tests: 25
✓ Passed: 25
✗ Failed: 0
Pass Rate: 100.0%

======================================================================
                    🎉 ALL TESTS PASSED! 🎉                        
======================================================================
```

## Adding New Test Scenarios

When you add a new feature, **append a new test** to `test_complete_e2e.py`:

### Example: Adding a new feature test

```python
# ========================================================================
# TEST SUITE 8: NEW FEATURE NAME (Day X)
# ========================================================================

async def test_suite_8_new_feature(self):
    """Test new feature description"""
    self.print_header("TEST SUITE 8: NEW FEATURE NAME")
    
    # Test 8.1: First test case
    def validate_feature(result):
        if result.get("expected_field"):
            self.print_success(f"Feature works: {result['expected_field']}")
        else:
            self.print_failure("Feature validation failed")
    
    await self.test_a2a_skill(
        "new-skill-name",
        {"param1": "value1"},
        validate_feature
    )
```

Then add the test suite to the main execution in `main()`:
```python
await suite.test_suite_8_new_feature()  # Add this line
```

## Test Suites Covered

Current test suites (as of Day 5):

1. **Service Health Checks** - Verify all services are running
2. **Basic Shipment Operations** - CRUD operations, search, track
3. **Advanced Analytics** - Delays, routes, KPIs
4. **Document Generation** - BOL, Invoice, Packing List (Day 5)
5. **ML Predictions** - Delay prediction (placeholder for future)
6. **Database Integrity** - Data structure validation
7. **Error Handling** - Edge cases and invalid inputs

## CI/CD Integration

This test suite is designed to be run in CI/CD pipelines:

```yaml
# Example: .github/workflows/test.yml
name: E2E Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start all services
        run: ./start_all_services.sh
      - name: Run E2E tests
        run: cd cw-agents && python test_complete_e2e.py
```

## Benefits of Single Test Suite Approach

✅ **Regression Prevention** - Every test runs on every change
✅ **Clear Coverage** - One file shows all features tested
✅ **Easy Maintenance** - Update tests in one place
✅ **Fast Debugging** - Quickly see which feature broke
✅ **Documentation** - Test suite serves as feature documentation
✅ **Confidence** - Know exactly what's tested before deploying

## Migration from Old Tests

Old test files have been moved to `tests/deprecated/` for reference.
All their test scenarios have been integrated into `test_complete_e2e.py`.

If you find a test scenario missing, extract it from the deprecated files
and add it as a new test suite in the comprehensive test.
