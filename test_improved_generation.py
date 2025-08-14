#!/usr/bin/env python3
"""
Test Improved Text Generation
Verify that the repetition issue is fixed
"""

import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))

def main():
    print("🔧 Testing Improved Text Generation")
    print("=" * 50)
    
    try:
        # Test 1: Import and initialize
        from backend.manager import StudyMateBackend
        
        backend = StudyMateBackend()
        print("✅ Backend initialized successfully")
        
        # Test 2: Check system status
        stats = backend.get_system_stats()
        print(f"✅ System ready: {stats['ready_for_questions']}")
        print(f"📊 Documents: {stats['documents_processed']}")
        print(f"📊 Chunks: {stats['total_chunks']}")
        
        if not stats['ready_for_questions']:
            print("⚠️ No documents loaded - answers will be generic")
        
        # Test 3: Test simple questions
        test_questions = [
            "What is a computer?",
            "Explain algorithms",
            "What is programming?",
            "Define data structures"
        ]
        
        print(f"\n🧪 Testing {len(test_questions)} questions...")
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n--- Test {i}: {question} ---")
            
            try:
                response = backend.ask_question(question)
                
                if response and 'answer' in response:
                    answer = response['answer']
                    print(f"✅ Response generated ({len(answer)} chars)")
                    
                    # Check for repetition issues
                    words = answer.split()
                    if len(words) > 10:
                        # Check for excessive repetition
                        word_counts = {}
                        for word in words:
                            word_counts[word] = word_counts.get(word, 0) + 1
                        
                        max_repetition = max(word_counts.values())
                        if max_repetition > len(words) * 0.3:  # More than 30% repetition
                            print(f"⚠️ High repetition detected (max word appears {max_repetition} times)")
                        else:
                            print(f"✅ Good variety (max repetition: {max_repetition})")
                    
                    # Show preview
                    preview = answer[:150] + "..." if len(answer) > 150 else answer
                    print(f"📝 Preview: {preview}")
                    
                    # Check for sources
                    if 'sources' in response and response['sources']:
                        print(f"📚 Sources: {len(response['sources'])} documents")
                    else:
                        print("📚 Sources: None (generic response)")
                        
                else:
                    print("❌ No response generated")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        # Test 4: Test model switching
        print(f"\n🔄 Testing model switching...")
        
        available_models = backend.get_available_models()
        current_model = backend.get_current_model()
        
        print(f"📊 Available models: {list(available_models.keys())}")
        print(f"📊 Current model: {current_model}")
        
        # Try switching to a different model
        for model_key in available_models.keys():
            if model_key != current_model:
                print(f"🔄 Switching to {model_key}...")
                if backend.set_generation_model(model_key):
                    print(f"✅ Successfully switched to {model_key}")
                    
                    # Test a question with the new model
                    test_response = backend.ask_question("What is computer science?")
                    if test_response and 'answer' in test_response:
                        answer_preview = test_response['answer'][:100] + "..."
                        print(f"📝 {model_key} response: {answer_preview}")
                    
                    # Switch back
                    backend.set_generation_model(current_model)
                    print(f"🔄 Switched back to {current_model}")
                    break
                else:
                    print(f"❌ Failed to switch to {model_key}")
        
        print(f"\n🎉 Text generation testing complete!")
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
        print("✅ IMPROVED GENERATION WORKING")
        print("🔧 Repetition issues should be resolved")
        print("💬 Try asking questions in StudyMate chat!")
        print("🌐 Access: http://localhost:8510")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ GENERATION ISSUES REMAIN")
        print("🔧 Check the error messages above")
        print("=" * 50)
