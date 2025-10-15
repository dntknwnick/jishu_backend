#!/usr/bin/env python3
"""
Test script to debug validation logic in RAG service
"""

import json

# This is the exact response from the logs
questions_data = [
    {
        "question": "What is the definition of physics?",
        "option_a": "The study of energy",
        "option_b": "The study of matter",
        "option_c": "The study of space and time",
        "option_d": "The study of motion",
        "correct_answer": "The study of energy"
    },
    {
        "question": "What is the main difference between chemical and physical properties?",
        "option_a": "Chemical property depends on the amount of substance present",
        "option_b": "Physical property does not depend on the amount of substance present",
        "option_c": "Chemical reaction involves a change in the composition of a substance",
        "option_d": "Physical change is reversible and can be reversed by heating or cooling",
        "correct_answer": "Physical property does not depend on the amount of substance present"
    },
    {
        "question": "What are the two main branches of chemistry?",
        "option_a": "Inorganic and Organic chemistry",
        "option_b": "Physical and Chemical chemistry",
        "option_c": "Biochemistry and Environmental science",
        "option_d": "Theoretical and Applied chemistry",
        "correct_answer": "Inorganic and Organic chemistry"
    },
    {
        "question": "What is the principle of conservation of mass?",
        "option_a": "Mass cannot be created or destroyed in a chemical reaction",
        "option_b": "Matter can only change from one substance to another",
        "option_c": "Energy cannot be created or destroyed, only converted from one form to another",
        "option_d": "Temperature remains constant during a chemical reaction",
        "correct_answer": "Mass cannot be created or destroyed in a chemical reaction"
    },
    {
        "question": "What is the term for the amount of matter in an object?",
        "option_a": "Mole",
        "option_b": "Atom",
        "option_c": "Element",
        "option_d": "Compound",
        "correct_answer": "Mole"
    }
]

def test_validation_logic():
    """Test the exact validation logic from RAG service"""
    print("🧪 Testing Validation Logic")
    print("=" * 50)
    
    validated_questions = []
    
    for i, q in enumerate(questions_data):
        print(f"\n🔍 Validating question {i+1}:")
        print(f"  Question: {q['question'][:50]}...")
        
        # Check if all required fields are present
        required_fields = ['question', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_answer']
        if all(key in q for key in required_fields):
            print("  ✅ All required fields present")
            
            # Extract and validate correct_answer against options
            correct = q.get("correct_answer", "").strip()
            options = [q.get("option_a", "").strip(), q.get("option_b", "").strip(),
                     q.get("option_c", "").strip(), q.get("option_d", "").strip()]

            print(f"  Correct answer: '{correct}'")
            print(f"  Options: {options}")
            
            # Check each option individually
            for j, option in enumerate(options):
                match = correct == option
                print(f"    Option {chr(97+j)}: '{option}' - Match: {match}")
            
            # Ensure correct_answer matches one of the options exactly
            if correct and correct in options:
                validated_questions.append(q)
                print(f"  ✅ Question {i+1} validated successfully")
            else:
                print(f"  ❌ Question {i+1} FAILED validation")
                print(f"     Correct answer '{correct}' not found in options")
                
                # Check for close matches
                for option in options:
                    if correct.lower() == option.lower():
                        print(f"     🔍 Case-insensitive match found: '{option}'")
                    elif correct.strip() == option.strip():
                        print(f"     🔍 Whitespace difference found: '{option}'")
        else:
            missing_keys = [key for key in required_fields if key not in q]
            print(f"  ❌ Missing required fields: {missing_keys}")
    
    print(f"\n📊 Validation Results:")
    print(f"  Total questions: {len(questions_data)}")
    print(f"  Validated questions: {len(validated_questions)}")
    print(f"  Success rate: {len(validated_questions)/len(questions_data)*100:.1f}%")
    
    return len(validated_questions) == len(questions_data)

def test_option_matching():
    """Test specific option matching scenarios"""
    print("\n🧪 Testing Option Matching Scenarios")
    print("=" * 50)
    
    test_cases = [
        {
            "correct_answer": "The study of energy",
            "options": ["The study of energy", "The study of matter", "The study of space", "The study of motion"],
            "expected": True
        },
        {
            "correct_answer": "The study of energy ",  # trailing space
            "options": ["The study of energy", "The study of matter", "The study of space", "The study of motion"],
            "expected": False  # Should fail without strip()
        },
        {
            "correct_answer": "the study of energy",  # different case
            "options": ["The study of energy", "The study of matter", "The study of space", "The study of motion"],
            "expected": False  # Should fail - case sensitive
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest case {i+1}:")
        correct = test_case["correct_answer"].strip()
        options = [opt.strip() for opt in test_case["options"]]
        result = correct in options
        expected = test_case["expected"]
        
        print(f"  Correct: '{correct}'")
        print(f"  Options: {options}")
        print(f"  Result: {result} (Expected: {expected})")
        print(f"  Status: {'✅ PASS' if result == expected else '❌ FAIL'}")

def main():
    """Run all validation tests"""
    print("🚀 Validation Logic Debug Tests")
    print("=" * 60)
    
    success = test_validation_logic()
    test_option_matching()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if success:
        print("🎉 All questions should validate successfully!")
        print("The issue might be elsewhere in the processing pipeline.")
    else:
        print("⚠️ Some questions failed validation.")
        print("This explains why the chunked generation is failing.")
    
    print("\n💡 Recommendations:")
    print("1. Check for whitespace differences in AI responses")
    print("2. Consider case-insensitive matching")
    print("3. Add more robust option matching logic")
    print("4. Verify the AI is generating consistent format")

if __name__ == "__main__":
    main()
