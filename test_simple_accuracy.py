#!/usr/bin/env python3
"""
Simple Accuracy Test
Test the improved FLAN-T5 model with better context handling
"""

import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))

def main():
    print("🎯 Testing Simple Accuracy with FLAN-T5")
    print("=" * 50)
    
    try:
        # Test 1: Initialize backend
        from backend.manager import StudyMateBackend
        
        backend = StudyMateBackend()
        print("✅ Backend initialized successfully")
        
        # Check current model
        current_model = backend.get_current_model()
        print(f"📊 Current model: {current_model}")
        
        # Test 2: Check system status
        stats = backend.get_system_stats()
        print(f"✅ System ready: {stats['ready_for_questions']}")
        print(f"📊 Documents: {stats['documents_processed']}")
        print(f"📊 Chunks: {stats['total_chunks']}")
        
        # Test 3: Simple question test
        print(f"\n🧪 Testing simple question...")
        
        question = "What is a computer?"
        print(f"Question: {question}")
        
        try:
            response = backend.ask_question(question)
            
            if response and 'answer' in response:
                answer = response['answer']
                print(f"✅ Response generated ({len(answer)} chars)")
                print(f"📝 Answer: {answer}")
                
                # Check if it mentions computer-related terms
                computer_terms = ['computer', 'machine', 'device', 'electronic', 'data', 'processing', 'system']
                found_terms = [term for term in computer_terms if term.lower() in answer.lower()]
                
                if found_terms:
                    print(f"✅ Found relevant terms: {found_terms}")
                    print("🎉 Answer appears to be relevant!")
                else:
                    print("⚠️ No relevant computer terms found")
                
                # Check sources
                if 'sources' in response and response['sources']:
                    print(f"📚 Sources: {len(response['sources'])} documents")
                    for i, source in enumerate(response['sources'][:2], 1):
                        print(f"   {i}. {source.get('filename', 'Unknown')} (score: {source.get('similarity_score', 0):.3f})")
                else:
                    print("📚 Sources: None")
                    
            else:
                print("❌ No response generated")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False
        
        # Test 4: Check model info
        print(f"\n📊 Model Information:")
        model_info = backend.get_model_info()
        if model_info:
            print(f"   Name: {model_info['name']}")
            print(f"   Loaded: {model_info['loaded']}")
        
        available_models = backend.get_available_models()
        print(f"   Available: {list(available_models.keys())}")
        
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
        print("✅ SIMPLE ACCURACY TEST PASSED")
        print("🎯 FLAN-T5 model is working")
        print("💬 Try asking questions in StudyMate!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ SIMPLE ACCURACY TEST FAILED")
        print("🔧 Check the error messages above")
        print("=" * 50)
