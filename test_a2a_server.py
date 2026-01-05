"""
Test script for A2A server and crew execution.
Tests AgentCards, message routing, and crew execution.
"""
import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.a2a_server.agent_cards import (
    COMBINED_CARD,
    get_crew_by_skill,
    list_all_skills
)
from src.executors.crew_executor import (
    CrewExecutor,
    A2AMessage
)


async def test_agent_cards():
    """Test AgentCard definitions."""
    print("\n" + "="*80)
    print("TEST: AgentCards")
    print("="*80)
    
    print(f"\n✓ Combined card ID: {COMBINED_CARD['agent_id']}")
    print(f"✓ Total crews: {len(COMBINED_CARD['crews'])}")
    print(f"✓ Total skills: {len(COMBINED_CARD['all_skills'])}")
    print(f"✓ Total capabilities: {len(COMBINED_CARD['all_capabilities'])}")
    
    print("\nCrew Skills:")
    for crew in COMBINED_CARD['crews']:
        print(f"  - {crew['name']}: {len(crew['skills'])} skills")
    
    print("\nAll Skills:")
    for skill in list_all_skills():
        crew = get_crew_by_skill(skill)
        print(f"  - {skill} → {crew}")
    
    return True


async def test_skill_routing():
    """Test skill-based routing logic."""
    print("\n" + "="*80)
    print("TEST: Skill Routing")
    print("="*80)
    
    test_skills = [
        ("track-shipment", "tracking"),
        ("calculate-route", "routing"),
        ("handle-exception", "exception"),
        ("generate-report", "analytics"),
    ]
    
    for skill, expected_crew in test_skills:
        crew = get_crew_by_skill(skill)
        status = "✓" if crew == expected_crew else "✗"
        print(f"{status} {skill} → {crew} (expected: {expected_crew})")
        if crew != expected_crew:
            return False
    
    return True


async def test_message_creation():
    """Test A2A message creation."""
    print("\n" + "="*80)
    print("TEST: A2A Message Creation")
    print("="*80)
    
    message = A2AMessage(
        skill="track-shipment",
        content="Track shipment SH-12345",
        parameters={"shipment_id": "SH-12345"},
        context={"user_id": "test-user"},
        metadata={"source": "test"}
    )
    
    print(f"✓ Message ID: {message.message_id}")
    print(f"✓ Skill: {message.skill}")
    print(f"✓ Parameters: {message.parameters}")
    print(f"✓ Status: {message.status}")
    
    # Test to_dict
    message_dict = message.to_dict()
    print(f"✓ Serialized: {len(json.dumps(message_dict))} bytes")
    
    # Test from_dict
    restored = A2AMessage.from_dict(message_dict)
    print(f"✓ Restored ID: {restored.message_id}")
    
    return True


async def test_executor_initialization():
    """Test CrewExecutor initialization."""
    print("\n" + "="*80)
    print("TEST: CrewExecutor Initialization")
    print("="*80)
    
    executor = CrewExecutor()
    print("✓ Executor created")
    
    try:
        await executor.initialize()
        print("✓ Executor initialized")
        
        # Check crews
        crews = {
            "tracking": executor.tracking_crew,
            "routing": executor.routing_crew,
            "exception": executor.exception_crew,
            "analytics": executor.analytics_crew
        }
        
        for name, crew in crews.items():
            status = "✓" if crew is not None else "✗"
            print(f"{status} {name} crew: {type(crew).__name__ if crew else 'None'}")
        
        await executor.cleanup()
        print("✓ Executor cleaned up")
        
        return all(crew is not None for crew in crews.values())
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_message_routing():
    """Test message routing to crews."""
    print("\n" + "="*80)
    print("TEST: Message Routing")
    print("="*80)
    
    executor = CrewExecutor()
    
    test_cases = [
        ("track-shipment", "tracking"),
        ("calculate-route", "routing"),
        ("handle-exception", "exception"),
        ("generate-report", "analytics")
    ]
    
    for skill, expected_crew in test_cases:
        message = A2AMessage(skill=skill, parameters={})
        crew = executor.route_message(message)
        status = "✓" if crew == expected_crew else "✗"
        print(f"{status} {skill} → {crew} (expected: {expected_crew})")
        if crew != expected_crew:
            return False
    
    # Test unknown skill
    try:
        message = A2AMessage(skill="unknown-skill", parameters={})
        crew = executor.route_message(message)
        print(f"✗ Unknown skill should raise error")
        return False
    except ValueError as e:
        print(f"✓ Unknown skill raises error: {e}")
    
    return True


async def test_api_endpoints():
    """Test that FastAPI app can be imported."""
    print("\n" + "="*80)
    print("TEST: API Endpoints")
    print("="*80)
    
    try:
        from src.a2a_server.main import app
        print(f"✓ FastAPI app imported: {app.title}")
        
        # Check routes
        routes = [route.path for route in app.routes]
        required_routes = [
            "/.well-known/agent-card.json",
            "/message:send",
            "/message:stream",
            "/tasks",
            "/tasks/{task_id}",
            "/health"
        ]
        
        for route in required_routes:
            if any(route in r for r in routes):
                print(f"✓ Route exists: {route}")
            else:
                print(f"✗ Route missing: {route}")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Error importing app: {e}")
        return False


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("CW AGENTS - A2A SERVER TEST SUITE")
    print("="*80)
    
    tests = [
        ("AgentCards", test_agent_cards),
        ("Skill Routing", test_skill_routing),
        ("Message Creation", test_message_creation),
        ("Executor Init", test_executor_initialization),
        ("Message Routing", test_message_routing),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results[name] = result
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:.<40} {status}")
    
    total = len(results)
    passed = sum(1 for r in results.values() if r)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
