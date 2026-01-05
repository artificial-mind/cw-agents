"""
End-to-End Test: Document Generation through A2A → MCP → Analytics Engine
Tests the full document generation flow across all services.
"""

import asyncio
import httpx
import json
from datetime import datetime


# Service URLs
A2A_URL = "http://localhost:8001"
MCP_URL = "http://localhost:8000"
ANALYTICS_URL = "http://localhost:8002"


async def test_service_health():
    """Verify all services are running."""
    print("\n" + "="*70)
    print("🏥 Health Check: Verifying all services are running")
    print("="*70)
    
    services = {
        "A2A Server": (A2A_URL, "/health"),
        "MCP Server": (MCP_URL, "/"),  # MCP uses SSE, just check root
        "Analytics Engine": (ANALYTICS_URL, "/health")
    }
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        all_healthy = True
        for name, (url, endpoint) in services.items():
            try:
                response = await client.get(f"{url}{endpoint}")
                if response.status_code in [200, 404]:  # 404 is ok for MCP root
                    print(f"✅ {name} ({url}): Healthy")
                else:
                    print(f"⚠️  {name} ({url}): Responded but not healthy (status {response.status_code})")
                    all_healthy = False
            except Exception as e:
                print(f"❌ {name} ({url}): Not responding - {str(e)}")
                all_healthy = False
        
        return all_healthy


async def test_generate_bol_via_a2a(shipment_id: str = "job-2025-001"):
    """Test Bill of Lading generation through A2A."""
    print("\n" + "="*70)
    print(f"📄 Test 1: Generate BOL via A2A for {shipment_id}")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Call A2A's message endpoint (A2A Protocol)
            response = await client.post(
                f"{A2A_URL}/message:send",
                json={
                    "skill": "generate-bol",
                    "content": f"Generate bill of lading for shipment {shipment_id}",
                    "parameters": {
                        "shipment_id": shipment_id
                    }
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            print(f"\n📊 A2A Response Status: {response.status_code}")
            print(f"📦 Result Preview:")
            print(json.dumps(result, indent=2))
            
            # Extract the actual tool result from A2A artifact
            tool_result = result.get("artifact", {}).get("content", {}).get("result", {})
            
            # Validate result
            if tool_result.get("success"):
                print(f"\n✅ BOL Generated Successfully!")
                print(f"   Document Number: {tool_result.get('document_number')}")
                print(f"   Document URL: {tool_result.get('document_url')}")
                print(f"   File Size: {tool_result.get('file_size_kb')} KB")
                return True
            else:
                print(f"\n❌ BOL Generation Failed: {tool_result.get('error')}")
                return False
                
    except Exception as e:
        print(f"❌ Error during BOL generation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_generate_invoice_via_a2a(shipment_id: str = "job-2025-001"):
    """Test Commercial Invoice generation through A2A."""
    print("\n" + "="*70)
    print(f"💰 Test 2: Generate Commercial Invoice via A2A for {shipment_id}")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            invoice_number = f"INV-TEST-{datetime.now().strftime('%Y%m%d')}"
            response = await client.post(
                f"{A2A_URL}/message:send",
                json={
                    "skill": "generate-invoice",
                    "content": f"Generate commercial invoice for shipment {shipment_id}",
                    "parameters": {
                        "shipment_id": shipment_id,
                        "invoice_number": invoice_number
                    }
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            print(f"\n📊 A2A Response Status: {response.status_code}")
            print(f"📦 Result Preview:")
            print(json.dumps(result, indent=2))
            
            # Extract the actual tool result from A2A artifact
            tool_result = result.get("artifact", {}).get("content", {}).get("result", {})
            
            if tool_result.get("success"):
                print(f"\n✅ Invoice Generated Successfully!")
                print(f"   Invoice Number: {tool_result.get('invoice_number')}")
                print(f"   Document URL: {tool_result.get('document_url')}")
                print(f"   Total Amount: {tool_result.get('currency')} {tool_result.get('total_amount', 0):.2f}")
                print(f"   File Size: {tool_result.get('file_size_kb')} KB")
                return True
            else:
                print(f"\n❌ Invoice Generation Failed: {tool_result.get('error')}")
                return False
                
    except Exception as e:
        print(f"❌ Error during Invoice generation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_generate_packing_list_via_a2a(shipment_id: str = "job-2025-001"):
    """Test Packing List generation through A2A."""
    print("\n" + "="*70)
    print(f"📦 Test 3: Generate Packing List via A2A for {shipment_id}")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{A2A_URL}/message:send",
                json={
                    "skill": "generate-packing-list",
                    "content": f"Generate packing list for shipment {shipment_id}",
                    "parameters": {
                        "shipment_id": shipment_id
                    }
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            print(f"\n📊 A2A Response Status: {response.status_code}")
            print(f"📦 Result Preview:")
            print(json.dumps(result, indent=2))
            
            # Extract the actual tool result from A2A artifact
            tool_result = result.get("artifact", {}).get("content", {}).get("result", {})
            
            if tool_result.get("success"):
                print(f"\n✅ Packing List Generated Successfully!")
                print(f"   Packing List Number: {tool_result.get('packing_list_number')}")
                print(f"   Document URL: {tool_result.get('document_url')}")
                print(f"   Total Packages: {tool_result.get('total_packages')}")
                print(f"   Total Weight: {tool_result.get('total_weight_kg')} KG")
                print(f"   File Size: {tool_result.get('file_size_kb')} KB")
                return True
            else:
                print(f"\n❌ Packing List Generation Failed: {tool_result.get('error')}")
                return False
                
    except Exception as e:
        print(f"❌ Error during Packing List generation test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_direct_analytics_endpoint():
    """Test calling analytics engine directly (bypass A2A/MCP)."""
    print("\n" + "="*70)
    print("🔧 Test 4: Direct Analytics Engine Call (Bypass Test)")
    print("="*70)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Simple BOL test data
            response = await client.post(
                f"{ANALYTICS_URL}/generate-document",
                json={
                    "document_type": "BOL",
                    "data": {
                        "shipment_id": "test-direct",
                        "carrier_name": "TEST CARRIER",
                        "vessel_name": "TEST VESSEL",
                        "voyage_number": "TEST123",
                        "port_of_loading": "Test Port A",
                        "port_of_discharge": "Test Port B",
                        "shipper_name": "Test Shipper",
                        "shipper_address": "123 Test St",
                        "shipper_city": "Test City",
                        "shipper_country": "Test Country",
                        "consignee_name": "Test Consignee",
                        "consignee_address": "456 Test Ave",
                        "consignee_city": "Test City 2",
                        "consignee_country": "Test Country 2",
                        "containers": [
                            {
                                "number": "TEST1234567",
                                "seal_number": "SEAL001",
                                "type": "40HC",
                                "package_count": 100,
                                "package_type": "CARTONS",
                                "description": "Test Cargo",
                                "weight": 10000,
                                "volume": 50.0
                            }
                        ]
                    }
                }
            )
            
            response.raise_for_status()
            result = response.json()
            
            print(f"\n📊 Direct Analytics Response:")
            print(json.dumps(result, indent=2))
            
            if result.get("success"):
                print(f"\n✅ Direct Analytics Call Successful!")
                print(f"   This confirms the analytics engine is working properly.")
                return True
            else:
                print(f"\n❌ Direct Analytics Call Failed")
                return False
                
    except Exception as e:
        print(f"❌ Error during direct analytics test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all document generation tests."""
    print("\n" + "="*70)
    print("🚀 CW Logistics Platform - Document Generation E2E Tests")
    print("="*70)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Testing Services:")
    print(f"  - A2A Server: {A2A_URL}")
    print(f"  - MCP Server: {MCP_URL}")
    print(f"  - Analytics Engine: {ANALYTICS_URL}")
    
    # Health check
    services_healthy = await test_service_health()
    
    if not services_healthy:
        print("\n❌ Some services are not healthy. Please start all services:")
        print("   1. Analytics Engine: cd cw-analytics-engine && python start_server.py")
        print("   2. MCP Server: cd cw-ai-server && python server_fastmcp.py")
        print("   3. A2A Server: cd cw-agents && python start_server.py")
        return
    
    # Run all tests
    print("\n" + "="*70)
    print("🧪 Running Document Generation Tests")
    print("="*70)
    
    test_results = []
    
    # Test 1: BOL
    bol_result = await test_generate_bol_via_a2a()
    test_results.append(("Bill of Lading", bol_result))
    
    # Test 2: Invoice
    invoice_result = await test_generate_invoice_via_a2a()
    test_results.append(("Commercial Invoice", invoice_result))
    
    # Test 3: Packing List
    packing_result = await test_generate_packing_list_via_a2a()
    test_results.append(("Packing List", packing_result))
    
    # Test 4: Direct Analytics
    direct_result = await test_direct_analytics_endpoint()
    test_results.append(("Direct Analytics", direct_result))
    
    # Summary
    print("\n" + "="*70)
    print("📊 Test Summary")
    print("="*70)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{'='*70}")
    print(f"Tests Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All document generation tests PASSED!")
        print("\n✅ Day 5 Document Generation - COMPLETE!")
        print("\nGenerated documents are saved in:")
        print("  cw-analytics-engine/generated_documents/")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Please review errors above.")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
