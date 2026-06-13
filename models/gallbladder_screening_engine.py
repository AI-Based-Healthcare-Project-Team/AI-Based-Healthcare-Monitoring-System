"""
Gallbladder Screening Engine
Rule-based clinical risk assessment system for gallbladder disease
"""

class GallbladderScreeningEngine:
    """Expert system for gallbladder disease risk assessment"""
    
    def __init__(self):
        self.risk_weights = {
            'upper_right_pain': 3,
            'pain_after_fatty_meals': 3,
            'nausea': 2,
            'vomiting': 2,
            'bloating': 1,
            'fever': 2,
            'jaundice': 4,
            'family_history': 2,
            'previous_issues': 3,
            'female': 1,
            'high_bmi': 1,
            'age_over_40': 1
        }
    
    def assess_risk(self, symptoms):
        """
        Assess gallbladder disease risk based on symptoms
        
        Parameters:
        -----------
        symptoms : dict
            Dictionary containing symptom information:
            - age: int
            - gender: str ('male' or 'female')
            - bmi: float (optional)
            - upper_right_pain: bool
            - pain_after_fatty_meals: bool
            - nausea: bool
            - vomiting: bool
            - bloating: bool
            - fever: bool
            - jaundice: bool
            - family_history: bool
            - previous_issues: bool
        
        Returns:
        --------
        dict: Assessment results with risk score, level, and recommendations
        """
        risk_score = 0
        risk_factors = []
        
        # Symptom-based scoring
        if symptoms.get('upper_right_pain', False):
            risk_score += self.risk_weights['upper_right_pain']
            risk_factors.append('Upper right abdominal pain')
        
        if symptoms.get('pain_after_fatty_meals', False):
            risk_score += self.risk_weights['pain_after_fatty_meals']
            risk_factors.append('Pain after fatty meals')
        
        if symptoms.get('nausea', False):
            risk_score += self.risk_weights['nausea']
            risk_factors.append('Nausea')
        
        if symptoms.get('vomiting', False):
            risk_score += self.risk_weights['vomiting']
            risk_factors.append('Vomiting')
        
        if symptoms.get('bloating', False):
            risk_score += self.risk_weights['bloating']
            risk_factors.append('Bloating/indigestion')
        
        if symptoms.get('fever', False):
            risk_score += self.risk_weights['fever']
            risk_factors.append('Fever')
        
        if symptoms.get('jaundice', False):
            risk_score += self.risk_weights['jaundice']
            risk_factors.append('Jaundice (yellowing of skin/eyes)')
        
        if symptoms.get('family_history', False):
            risk_score += self.risk_weights['family_history']
            risk_factors.append('Family history of gallstones')
        
        if symptoms.get('previous_issues', False):
            risk_score += self.risk_weights['previous_issues']
            risk_factors.append('Previous gallbladder issues')
        
        # Demographic factors
        if symptoms.get('gender', '').lower() == 'female':
            risk_score += self.risk_weights['female']
            risk_factors.append('Female gender (higher risk)')
        
        bmi = symptoms.get('bmi')
        if bmi and bmi > 30:
            risk_score += self.risk_weights['high_bmi']
            risk_factors.append('BMI > 30 (obesity)')
        
        age = symptoms.get('age')
        if age and age > 40:
            risk_score += self.risk_weights['age_over_40']
            risk_factors.append('Age over 40')
        
        # Determine risk level
        if risk_score <= 4:
            risk_level = 'Low'
            possible_condition = 'Low likelihood of gallbladder disease'
            recommendation = 'Monitor symptoms. Maintain healthy diet and weight. Consult doctor if symptoms worsen.'
            urgency = 'routine'
        elif risk_score <= 9:
            risk_level = 'Moderate'
            possible_condition = 'Moderate risk of gallbladder disease'
            recommendation = 'Schedule appointment with healthcare provider for evaluation. May need ultrasound examination.'
            urgency = 'soon'
        else:
            risk_level = 'High'
            possible_condition = 'High risk of gallbladder disease/gallstones'
            recommendation = 'Seek medical attention promptly. Ultrasound evaluation recommended. May require specialist consultation.'
            urgency = 'urgent'
        
        # Build detailed explanation
        explanation = self._build_explanation(risk_factors, risk_score, risk_level)
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'possible_condition': possible_condition,
            'recommendation': recommendation,
            'urgency': urgency,
            'risk_factors': risk_factors,
            'explanation': explanation,
            'assessment_type': 'Rule-Based Clinical Screening',
            'model_type': 'Expert System Logic',
            'disclaimer': 'This is a preliminary risk assessment tool and should not be used as a substitute for professional medical diagnosis. Please consult a healthcare provider for proper evaluation.'
        }
    
    def _build_explanation(self, risk_factors, risk_score, risk_level):
        """Build detailed explanation of the assessment"""
        if not risk_factors:
            return "No significant risk factors identified. Continue maintaining healthy lifestyle."
        
        explanation = f"Based on your responses, you have {len(risk_factors)} risk factor(s) for gallbladder disease:\n\n"
        
        for i, factor in enumerate(risk_factors, 1):
            explanation += f"{i}. {factor}\n"
        
        explanation += f"\nTotal Risk Score: {risk_score}\n"
        explanation += f"Risk Level: {risk_level}\n\n"
        
        if risk_level == 'High':
            explanation += "Your symptoms suggest a higher likelihood of gallbladder issues. "
            explanation += "Common gallbladder conditions include gallstones (cholelithiasis) and inflammation (cholecystitis). "
            explanation += "Prompt medical evaluation is recommended."
        elif risk_level == 'Moderate':
            explanation += "Your symptoms indicate moderate risk. "
            explanation += "While not immediately urgent, medical evaluation is advisable to rule out gallbladder disease."
        else:
            explanation += "Your risk appears low based on current symptoms. "
            explanation += "However, if symptoms persist or worsen, consult a healthcare provider."
        
        return explanation


def create_gallbladder_assessment(symptoms):
    """
    Convenience function to create gallbladder assessment
    
    Parameters:
    -----------
    symptoms : dict
        Symptom information
    
    Returns:
    --------
    dict: Assessment results
    """
    engine = GallbladderScreeningEngine()
    return engine.assess_risk(symptoms)


# Example usage
if __name__ == "__main__":
    # Test case 1: High risk
    test_symptoms_high = {
        'age': 45,
        'gender': 'female',
        'bmi': 32,
        'upper_right_pain': True,
        'pain_after_fatty_meals': True,
        'nausea': True,
        'vomiting': True,
        'bloating': True,
        'fever': False,
        'jaundice': False,
        'family_history': True,
        'previous_issues': False
    }
    
    result = create_gallbladder_assessment(test_symptoms_high)
    print("High Risk Test:")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendation: {result['recommendation']}")
    print()
    
    # Test case 2: Low risk
    test_symptoms_low = {
        'age': 25,
        'gender': 'male',
        'bmi': 22,
        'upper_right_pain': False,
        'pain_after_fatty_meals': False,
        'nausea': False,
        'vomiting': False,
        'bloating': True,
        'fever': False,
        'jaundice': False,
        'family_history': False,
        'previous_issues': False
    }
    
    result = create_gallbladder_assessment(test_symptoms_low)
    print("Low Risk Test:")
    print(f"Risk Score: {result['risk_score']}")
    print(f"Risk Level: {result['risk_level']}")
    print(f"Recommendation: {result['recommendation']}")

# Made with Bob
