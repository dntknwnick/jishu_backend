#!/usr/bin/env python3
"""
Test script to debug JSON parsing issue in RAG service
"""

import json

# This is the exact response from the logs
ai_response = '''[
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
]'''

def test_json_parsing():
    """Test JSON parsing with the actual response"""
    print("🧪 Testing JSON Parsing")
    print("=" * 50)
    
    print(f"Response length: {len(ai_response)}")
    print(f"Response starts with: {ai_response[:50]}")
    print(f"Response ends with: {ai_response[-50:]}")
    
    # Test direct parsing
    try:
        questions = json.loads(ai_response)
        print(f"✅ Direct parsing successful: {len(questions)} questions")
        for i, q in enumerate(questions):
            print(f"  Question {i+1}: {q['question'][:50]}...")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ Direct parsing failed: {str(e)}")
        print(f"❌ Error at position: {e.pos if hasattr(e, 'pos') else 'unknown'}")
        
        # Show the character at error position
        if hasattr(e, 'pos') and e.pos < len(ai_response):
            print(f"❌ Character at error position: '{ai_response[e.pos]}' (ord: {ord(ai_response[e.pos])})")
            print(f"❌ Context around error: '{ai_response[max(0, e.pos-10):e.pos+10]}'")
        
        return False

def test_extraction_logic():
    """Test the extraction logic used in RAG service"""
    print("\n🧪 Testing Extraction Logic")
    print("=" * 50)
    
    # Simulate the RAG service logic
    json_start = ai_response.find('[')
    json_end = ai_response.rfind(']') + 1
    
    print(f"JSON start position: {json_start}")
    print(f"JSON end position: {json_end}")
    
    if json_start != -1 and json_end > 0:
        json_str = ai_response[json_start:json_end]
        print(f"Extracted JSON length: {len(json_str)}")
        print(f"Extracted JSON starts with: {json_str[:50]}")
        print(f"Extracted JSON ends with: {json_str[-50:]}")
        
        # Clean up
        json_str = json_str.strip()
        
        try:
            questions = json.loads(json_str)
            print(f"✅ Extraction parsing successful: {len(questions)} questions")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ Extraction parsing failed: {str(e)}")
            return False
    else:
        print("❌ Could not find JSON array boundaries")
        return False

def test_character_analysis():
    """Analyze characters in the response"""
    print("\n🧪 Testing Character Analysis")
    print("=" * 50)
    
    # Check for non-printable characters
    non_printable = []
    for i, char in enumerate(ai_response):
        if ord(char) < 32 and char not in ['\n', '\r', '\t']:
            non_printable.append((i, char, ord(char)))
    
    if non_printable:
        print(f"❌ Found {len(non_printable)} non-printable characters:")
        for pos, char, code in non_printable[:10]:  # Show first 10
            print(f"  Position {pos}: '{char}' (ord: {code})")
    else:
        print("✅ No problematic non-printable characters found")
    
    # Check for common JSON issues
    issues = []
    if ',]' in ai_response:
        issues.append("Trailing comma before closing bracket")
    if ',}' in ai_response:
        issues.append("Trailing comma before closing brace")
    if ai_response.count('[') != ai_response.count(']'):
        issues.append("Mismatched square brackets")
    if ai_response.count('{') != ai_response.count('}'):
        issues.append("Mismatched curly braces")
    
    if issues:
        print(f"❌ Found JSON issues: {', '.join(issues)}")
    else:
        print("✅ No common JSON issues found")

def main():
    """Run all tests"""
    print("🚀 JSON Parsing Debug Tests")
    print("=" * 60)
    
    tests = [
        test_json_parsing,
        test_extraction_logic,
        test_character_analysis
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Test crashed: {str(e)}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("🎉 All tests passed! JSON should parse correctly.")
    else:
        print("⚠️ Some tests failed. There may be an issue with the JSON response.")

if __name__ == "__main__":
    main()
