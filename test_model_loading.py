#!/usr/bin/env python3
"""
Test Model Loading Fix
Verify that AI models are loaded properly for question answering
"""

import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))

def main():
    print("🤖 Testing AI Model Loading Fix")
    print("=" * 50)
    
    try:
        # Test 1: Import model manager
        from backend.model_manager import model_manager
        print("✅ Model manager imported successfully")
        
        # Test 2: Check available models
        available_models = model_manager.get_available_models()
        print(f"✅ Available models: {list(available_models.keys())}")
        
        # Test 3: Import QA engine
        from backend.qa_engine_hf import qa_engine
        print("✅ QA engine imported successfully")
        
        # Test 4: Check if model is loaded after initialization
        if qa_engine.is_model_loaded():
            print("✅ Generation model loaded during initialization")
            current_model = qa_engine.get_current_model()
            print(f"   Current model: {current_model}")
        else:
            print("⚠️ No generation model loaded during initialization")
            print("   Attempting to load default model...")
            
            # Try to load default model
            default_model = qa_engine.current_model
            if qa_engine.set_model(default_model):
                print(f"✅ Successfully loaded default model: {default_model}")
            else:
                print(f"❌ Failed to load default model: {default_model}")
                
                # Try alternative models
                for model_key in available_models.keys():
                    if model_key != default_model:
                        print(f"   Trying alternative model: {model_key}")
                        if qa_engine.set_model(model_key):
                            print(f"✅ Successfully loaded alternative model: {model_key}")
                            break
                else:
                    print("❌ Failed to load any model")
                    return False
        
        # Test 5: Test model info
        model_info = model_manager.get_current_model_info()
        if model_info:
            print(f"✅ Model info available:")
            print(f"   Name: {model_info['name']}")
            print(f"   Description: {model_info['description']}")
            print(f"   Loaded: {model_info['loaded']}")
        else:
            print("⚠️ No model info available")
        
        # Test 6: Test text generation
        print("\n🔄 Testing text generation...")
        try:
            test_prompt = "Hello, this is a test prompt."
            response = model_manager.generate_text(test_prompt, max_new_tokens=50)
            if response:
                print("✅ Text generation successful!")
                print(f"   Response: {response[:100]}...")
            else:
                print("❌ Text generation returned empty response")
                return False
        except Exception as e:
            print(f"❌ Text generation failed: {str(e)}")
            if "No generation model loaded" in str(e):
                print("   This confirms the original issue - no model loaded")
            return False
        
        # Test 7: Test QA engine question answering (without documents)
        print("\n💬 Testing QA engine...")
        try:
            # This should handle the case where no documents are loaded
            test_question = "What is artificial intelligence?"
            response = qa_engine.ask_question(test_question)
            
            if response and 'answer' in response:
                print("✅ QA engine responding successfully!")
                print(f"   Answer: {response['answer'][:100]}...")
                print(f"   Model used: {response.get('model_used', 'Unknown')}")
            else:
                print("❌ QA engine not responding properly")
                return False
                
        except Exception as e:
            print(f"❌ QA engine test failed: {str(e)}")
            return False
        
        # Test 8: Test backend integration
        print("\n🔧 Testing backend integration...")
        try:
            from backend.manager import StudyMateBackend
            
            backend = StudyMateBackend()
            print("✅ Backend initialized successfully")
            
            # Test model switching
            available_models = backend.get_available_models()
            current_model = backend.get_current_model()
            
            print(f"   Available models: {list(available_models.keys())}")
            print(f"   Current model: {current_model}")
            
            # Test question with no documents
            response = backend.ask_question("Test question")
            if response and 'answer' in response:
                print("✅ Backend question answering working!")
                if "No documents have been processed" in response['answer']:
                    print("   Correctly handling no documents case")
                else:
                    print(f"   Response: {response['answer'][:100]}...")
            else:
                print("❌ Backend question answering failed")
                return False
                
        except Exception as e:
            print(f"❌ Backend integration test failed: {str(e)}")
            return False
        
        print("\n🎉 All tests passed!")
        print("✅ AI model loading is working correctly")
        print("✅ Text generation is functional")
        print("✅ QA engine is responding properly")
        print("✅ Backend integration is working")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ MODEL LOADING FIX SUCCESSFUL")
        print("🤖 AI models are now loading properly")
        print("💬 Question answering should work in StudyMate")
        print("🚀 Try asking questions in the chat!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ MODEL LOADING FIX FAILED")
        print("🔧 There are still issues with model loading")
        print("📋 Check the error messages above")
        print("=" * 50)
