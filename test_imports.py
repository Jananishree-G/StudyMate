#!/usr/bin/env python3
"""
Test all imports to identify the issue
"""

import sys
from pathlib import Path

# Add backend to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def test_step(step_name, import_func):
    """Test a single import step"""
    try:
        print(f"Testing {step_name}...")
        import_func()
        print(f"✅ {step_name} - SUCCESS")
        return True
    except Exception as e:
        print(f"❌ {step_name} - FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config():
    from backend.config import config, logger
    print(f"   Config loaded: {config.APP_TITLE}")

def test_model_manager():
    from backend.model_manager import model_manager
    print(f"   Model manager device: {model_manager.device}")

def test_qa_engine():
    from backend.qa_engine_hf import qa_engine
    print(f"   QA engine loaded")

def test_backend_manager():
    from backend.manager import StudyMateBackend
    backend = StudyMateBackend()
    print(f"   Backend manager created")

def test_app_import():
    from app import main as run_app
    print(f"   App main function imported")

def main():
    print("=" * 60)
    print("🧪 StudyMate Import Test Suite")
    print("=" * 60)
    
    tests = [
        ("Config", test_config),
        ("Model Manager", test_model_manager),
        ("QA Engine", test_qa_engine),
        ("Backend Manager", test_backend_manager),
        ("App Import", test_app_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_step(test_name, test_func):
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application should work now.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
