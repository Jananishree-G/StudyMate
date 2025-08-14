#!/usr/bin/env python3
"""
Test Accurate Answer Generation
Verify that the AI now gives accurate, relevant answers
"""

import sys
from pathlib import Path

# Add paths
sys.path.append(str(Path(__file__).parent / "backend"))

def main():
    print("🎯 Testing Accurate Answer Generation")
    print("=" * 50)
    
    try:
        # Test 1: Initialize backend with new model
        from backend.manager import StudyMateBackend
        
        backend = StudyMateBackend()
        print("✅ Backend initialized successfully")
        
        # Check current model
        current_model = backend.get_current_model()
        print(f"📊 Current model: {current_model}")
        
        # Switch to FLAN-T5 if not already using it
        if current_model != "flan-t5":
            print("🔄 Switching to FLAN-T5 for better accuracy...")
            if backend.set_generation_model("flan-t5"):
                print("✅ Successfully switched to FLAN-T5")
            else:
                print("⚠️ Could not switch to FLAN-T5, using current model")
        
        # Test 2: Check system status
        stats = backend.get_system_stats()
        print(f"✅ System ready: {stats['ready_for_questions']}")
        print(f"📊 Documents: {stats['documents_processed']}")
        print(f"📊 Chunks: {stats['total_chunks']}")
        
        if not stats['ready_for_questions']:
            print("⚠️ No documents loaded - testing with generic responses")
        
        # Test 3: Test specific computer science questions
        test_questions = [
            {
                "question": "What is a computer?",
                "expected_keywords": ["computer", "machine", "electronic", "data", "processing", "device"]
            },
            {
                "question": "What is an algorithm?",
                "expected_keywords": ["algorithm", "steps", "procedure", "instructions", "solve", "problem"]
            },
            {
                "question": "What is programming?",
                "expected_keywords": ["programming", "code", "software", "instructions", "computer", "language"]
            },
            {
                "question": "What are data structures?",
                "expected_keywords": ["data", "structure", "organize", "store", "information", "array", "list"]
            }
        ]
        
        print(f"\n🧪 Testing {len(test_questions)} computer science questions...")
        
        successful_answers = 0
        
        for i, test_case in enumerate(test_questions, 1):
            question = test_case["question"]
            expected_keywords = test_case["expected_keywords"]
            
            print(f"\n--- Test {i}: {question} ---")
            
            try:
                response = backend.ask_question(question)
                
                if response and 'answer' in response:
                    answer = response['answer']
                    print(f"✅ Response generated ({len(answer)} chars)")
                    
                    # Check for relevance using expected keywords
                    answer_lower = answer.lower()
                    found_keywords = [kw for kw in expected_keywords if kw in answer_lower]
                    relevance_score = len(found_keywords) / len(expected_keywords)
                    
                    print(f"📊 Relevance score: {relevance_score:.2f} ({len(found_keywords)}/{len(expected_keywords)} keywords)")
                    print(f"📝 Found keywords: {found_keywords}")
                    
                    if relevance_score >= 0.3:  # At least 30% of expected keywords
                        print("✅ Answer appears relevant!")
                        successful_answers += 1
                    else:
                        print("⚠️ Answer may not be relevant enough")
                    
                    # Show answer preview
                    preview = answer[:200] + "..." if len(answer) > 200 else answer
                    print(f"📝 Answer: {preview}")
                    
                    # Check for sources
                    if 'sources' in response and response['sources']:
                        print(f"📚 Sources: {len(response['sources'])} documents")
                    else:
                        print("📚 Sources: None (generic response)")
                        
                else:
                    print("❌ No response generated")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        # Test 4: Summary
        success_rate = successful_answers / len(test_questions)
        print(f"\n📊 ACCURACY SUMMARY")
        print(f"Successful answers: {successful_answers}/{len(test_questions)}")
        print(f"Success rate: {success_rate:.1%}")
        
        if success_rate >= 0.75:
            print("🎉 Excellent accuracy! AI is giving relevant answers.")
        elif success_rate >= 0.5:
            print("✅ Good accuracy! AI is mostly giving relevant answers.")
        else:
            print("⚠️ Low accuracy. AI needs further improvement.")
        
        # Test 5: Test with a complex question
        print(f"\n🔬 Testing complex question...")
        complex_question = "Explain the difference between hardware and software in computers"
        
        try:
            response = backend.ask_question(complex_question)
            if response and 'answer' in response:
                answer = response['answer']
                
                # Check for key concepts
                has_hardware = any(word in answer.lower() for word in ['hardware', 'physical', 'components', 'parts'])
                has_software = any(word in answer.lower() for word in ['software', 'programs', 'applications', 'code'])
                has_difference = any(word in answer.lower() for word in ['difference', 'different', 'unlike', 'whereas', 'while'])
                
                complexity_score = sum([has_hardware, has_software, has_difference]) / 3
                print(f"📊 Complexity handling: {complexity_score:.1%}")
                print(f"   Hardware mentioned: {has_hardware}")
                print(f"   Software mentioned: {has_software}")
                print(f"   Difference explained: {has_difference}")
                
                preview = answer[:300] + "..." if len(answer) > 300 else answer
                print(f"📝 Complex answer: {preview}")
                
        except Exception as e:
            print(f"❌ Complex question failed: {str(e)}")
        
        return success_rate >= 0.5
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n" + "=" * 50)
        print("✅ ACCURACY IMPROVEMENT SUCCESSFUL")
        print("🎯 AI is now giving more accurate answers")
        print("💬 Try asking questions in StudyMate!")
        print("🌐 Access: http://localhost:8510")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("❌ ACCURACY NEEDS MORE WORK")
        print("🔧 Check the test results above")
        print("=" * 50)
