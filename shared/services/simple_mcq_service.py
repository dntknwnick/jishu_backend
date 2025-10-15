"""
Simple MCQ Generation Service - Fallback when RAG fails
"""

import random
from typing import List, Dict

class SimpleMCQService:
    """Simple MCQ generation service with predefined question banks"""
    
    def __init__(self):
        self.question_banks = {
            'physics': [
                {
                    'question': 'What is the SI unit of force?',
                    'option_a': 'Newton',
                    'option_b': 'Joule',
                    'option_c': 'Watt',
                    'option_d': 'Pascal',
                    'correct_answer': 'A',
                    'explanation': 'The SI unit of force is Newton (N), named after Sir Isaac Newton.'
                },
                {
                    'question': 'What is the speed of light in vacuum?',
                    'option_a': '3 × 10⁸ m/s',
                    'option_b': '3 × 10⁶ m/s',
                    'option_c': '3 × 10¹⁰ m/s',
                    'option_d': '3 × 10⁴ m/s',
                    'correct_answer': 'A',
                    'explanation': 'The speed of light in vacuum is approximately 3 × 10⁸ meters per second.'
                },
                {
                    'question': 'What is the formula for kinetic energy?',
                    'option_a': '½mv²',
                    'option_b': 'mgh',
                    'option_c': 'F = ma',
                    'option_d': 'E = mc²',
                    'correct_answer': 'A',
                    'explanation': 'Kinetic energy is given by KE = ½mv², where m is mass and v is velocity.'
                },
                {
                    'question': 'What is the acceleration due to gravity on Earth?',
                    'option_a': '9.8 m/s²',
                    'option_b': '10 m/s²',
                    'option_c': '8.9 m/s²',
                    'option_d': '11 m/s²',
                    'correct_answer': 'A',
                    'explanation': 'The acceleration due to gravity on Earth is approximately 9.8 m/s².'
                },
                {
                    'question': 'What is Ohm\'s Law?',
                    'option_a': 'V = IR',
                    'option_b': 'P = IV',
                    'option_c': 'F = ma',
                    'option_d': 'E = hf',
                    'correct_answer': 'A',
                    'explanation': 'Ohm\'s Law states that voltage (V) equals current (I) times resistance (R).'
                }
            ],
            'chemistry': [
                {
                    'question': 'What is the atomic number of carbon?',
                    'option_a': '6',
                    'option_b': '12',
                    'option_c': '14',
                    'option_d': '8',
                    'correct_answer': 'A',
                    'explanation': 'Carbon has an atomic number of 6, meaning it has 6 protons in its nucleus.'
                },
                {
                    'question': 'What is the chemical formula for water?',
                    'option_a': 'H₂O',
                    'option_b': 'CO₂',
                    'option_c': 'NaCl',
                    'option_d': 'CH₄',
                    'correct_answer': 'A',
                    'explanation': 'Water has the chemical formula H₂O, consisting of two hydrogen atoms and one oxygen atom.'
                },
                {
                    'question': 'What is the pH of pure water?',
                    'option_a': '7',
                    'option_b': '0',
                    'option_c': '14',
                    'option_d': '1',
                    'correct_answer': 'A',
                    'explanation': 'Pure water has a pH of 7, which is neutral on the pH scale.'
                },
                {
                    'question': 'What is the most abundant gas in Earth\'s atmosphere?',
                    'option_a': 'Nitrogen',
                    'option_b': 'Oxygen',
                    'option_c': 'Carbon dioxide',
                    'option_d': 'Argon',
                    'correct_answer': 'A',
                    'explanation': 'Nitrogen makes up about 78% of Earth\'s atmosphere.'
                },
                {
                    'question': 'What is the chemical symbol for gold?',
                    'option_a': 'Au',
                    'option_b': 'Ag',
                    'option_c': 'Go',
                    'option_d': 'Gd',
                    'correct_answer': 'A',
                    'explanation': 'Gold has the chemical symbol Au, from the Latin word "aurum".'
                }
            ],
            'biology': [
                {
                    'question': 'What is the powerhouse of the cell?',
                    'option_a': 'Mitochondria',
                    'option_b': 'Nucleus',
                    'option_c': 'Ribosome',
                    'option_d': 'Endoplasmic reticulum',
                    'correct_answer': 'A',
                    'explanation': 'Mitochondria are called the powerhouse of the cell because they produce ATP energy.'
                },
                {
                    'question': 'What is the basic unit of life?',
                    'option_a': 'Cell',
                    'option_b': 'Tissue',
                    'option_c': 'Organ',
                    'option_d': 'Organism',
                    'correct_answer': 'A',
                    'explanation': 'The cell is the basic structural and functional unit of all living organisms.'
                },
                {
                    'question': 'What process do plants use to make food?',
                    'option_a': 'Photosynthesis',
                    'option_b': 'Respiration',
                    'option_c': 'Digestion',
                    'option_d': 'Fermentation',
                    'correct_answer': 'A',
                    'explanation': 'Plants use photosynthesis to convert sunlight, water, and carbon dioxide into glucose.'
                },
                {
                    'question': 'How many chambers does a human heart have?',
                    'option_a': '4',
                    'option_b': '2',
                    'option_c': '3',
                    'option_d': '5',
                    'correct_answer': 'A',
                    'explanation': 'The human heart has four chambers: two atria and two ventricles.'
                },
                {
                    'question': 'What is DNA?',
                    'option_a': 'Deoxyribonucleic acid',
                    'option_b': 'Ribonucleic acid',
                    'option_c': 'Amino acid',
                    'option_d': 'Fatty acid',
                    'correct_answer': 'A',
                    'explanation': 'DNA stands for deoxyribonucleic acid, which carries genetic information.'
                }
            ],
            'mathematics': [
                {
                    'question': 'What is the value of π (pi) approximately?',
                    'option_a': '3.14159',
                    'option_b': '2.71828',
                    'option_c': '1.41421',
                    'option_d': '2.30259',
                    'correct_answer': 'A',
                    'explanation': 'π (pi) is approximately 3.14159, representing the ratio of circumference to diameter of a circle.'
                },
                {
                    'question': 'What is the square root of 144?',
                    'option_a': '12',
                    'option_b': '14',
                    'option_c': '10',
                    'option_d': '16',
                    'correct_answer': 'A',
                    'explanation': 'The square root of 144 is 12, because 12 × 12 = 144.'
                },
                {
                    'question': 'What is 2³ (2 to the power of 3)?',
                    'option_a': '8',
                    'option_b': '6',
                    'option_c': '9',
                    'option_d': '4',
                    'correct_answer': 'A',
                    'explanation': '2³ = 2 × 2 × 2 = 8.'
                },
                {
                    'question': 'What is the sum of angles in a triangle?',
                    'option_a': '180°',
                    'option_b': '360°',
                    'option_c': '90°',
                    'option_d': '270°',
                    'correct_answer': 'A',
                    'explanation': 'The sum of all angles in any triangle is always 180 degrees.'
                },
                {
                    'question': 'What is the derivative of x²?',
                    'option_a': '2x',
                    'option_b': 'x',
                    'option_c': '2',
                    'option_d': 'x²',
                    'correct_answer': 'A',
                    'explanation': 'The derivative of x² with respect to x is 2x.'
                }
            ]
        }
    
    def generate_questions(self, subject: str, num_questions: int = 50) -> Dict:
        """Generate questions for a subject"""
        try:
            subject_lower = subject.lower()
            
            # Get question bank for subject (default to physics if not found)
            question_bank = self.question_banks.get(subject_lower, self.question_banks['physics'])
            
            # Generate questions by cycling through the bank and adding variations
            questions = []
            for i in range(num_questions):
                base_index = i % len(question_bank)
                base_question = question_bank[base_index].copy()
                
                # Add question number for variation
                if i >= len(question_bank):
                    variation_num = (i // len(question_bank)) + 1
                    base_question['question'] = f"[Variation {variation_num}] {base_question['question']}"
                
                questions.append(base_question)
            
            return {
                'success': True,
                'questions': questions,
                'total_generated': len(questions),
                'subject': subject,
                'method': 'simple_fallback',
                'source': 'predefined_question_bank'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Simple MCQ generation failed: {str(e)}',
                'questions': []
            }

# Singleton instance
_simple_mcq_service = None

def get_simple_mcq_service() -> SimpleMCQService:
    """Get singleton instance of SimpleMCQService"""
    global _simple_mcq_service
    if _simple_mcq_service is None:
        _simple_mcq_service = SimpleMCQService()
    return _simple_mcq_service
