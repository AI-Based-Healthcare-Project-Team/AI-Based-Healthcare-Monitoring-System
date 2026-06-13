"""
Mental Health / Stress Screening Engine
Rule-based stress assessment system using questionnaire scoring
"""

class MentalHealthScreeningEngine:
    """Expert system for stress and mental health assessment"""
    
    def __init__(self):
        self.questions = [
            'Feeling stressed or overwhelmed',
            'Difficulty relaxing',
            'Trouble sleeping',
            'Excessive worrying',
            'Difficulty concentrating',
            'Irritability',
            'Fatigue or low energy',
            'Feeling anxious in daily activities',
            'Loss of motivation',
            'Feeling emotionally exhausted'
        ]
        
        self.score_labels = {
            0: 'Never',
            1: 'Sometimes',
            2: 'Often',
            3: 'Almost Always'
        }
    
    def assess_stress(self, responses):
        """
        Assess stress level based on questionnaire responses
        
        Parameters:
        -----------
        responses : dict or list
            Either a dictionary with question keys and scores (0-3)
            or a list of 10 scores (0-3)
        
        Returns:
        --------
        dict: Assessment results with stress score, level, and recommendations
        """
        # Handle both dict and list inputs
        if isinstance(responses, dict):
            scores = [responses.get(f'q{i+1}', 0) for i in range(10)]
        elif isinstance(responses, list):
            scores = responses[:10]  # Take first 10 scores
        else:
            raise ValueError("Responses must be dict or list")
        
        # Validate scores
        for score in scores:
            if not isinstance(score, (int, float)) or score < 0 or score > 3:
                raise ValueError("All scores must be between 0 and 3")
        
        # Calculate total stress score
        stress_score = sum(scores)
        
        # Determine stress level
        if stress_score <= 7:
            stress_level = 'Low'
            severity = 'minimal'
            recommendation = 'Your stress levels appear to be within normal range. Continue maintaining healthy lifestyle habits including regular exercise, adequate sleep, and social connections.'
            action = 'Continue current wellness practices'
            urgency = 'routine'
        elif stress_score <= 15:
            stress_level = 'Mild'
            severity = 'mild'
            recommendation = 'You are experiencing mild stress. Consider incorporating stress management techniques such as mindfulness, deep breathing exercises, regular physical activity, and ensuring adequate rest.'
            action = 'Implement stress management techniques'
            urgency = 'routine'
        elif stress_score <= 22:
            stress_level = 'Moderate'
            severity = 'moderate'
            recommendation = 'You are experiencing moderate stress levels. Consider consulting with a mental health professional for guidance. Stress management techniques, lifestyle modifications, and possibly counseling may be beneficial.'
            action = 'Consider professional consultation'
            urgency = 'soon'
        else:
            stress_level = 'High'
            severity = 'significant'
            recommendation = 'You are experiencing high stress levels that may be impacting your daily functioning. Professional consultation with a mental health provider is strongly recommended. They can provide appropriate support, coping strategies, and treatment if needed.'
            action = 'Seek professional help'
            urgency = 'important'
        
        # Identify high-concern areas
        high_concern_areas = []
        for i, score in enumerate(scores):
            if score >= 2:  # Often or Almost Always
                high_concern_areas.append(self.questions[i])
        
        # Build detailed explanation
        explanation = self._build_explanation(stress_score, stress_level, high_concern_areas)
        
        # Generate coping strategies
        coping_strategies = self._get_coping_strategies(stress_level)
        
        return {
            'stress_score': stress_score,
            'max_score': 30,
            'stress_level': stress_level,
            'severity': severity,
            'recommendation': recommendation,
            'action': action,
            'urgency': urgency,
            'high_concern_areas': high_concern_areas,
            'coping_strategies': coping_strategies,
            'explanation': explanation,
            'assessment_type': 'Rule-Based Stress Screening',
            'model_type': 'Questionnaire-Based Assessment',
            'disclaimer': 'This is a preliminary stress assessment tool and should not be used as a substitute for professional mental health diagnosis. If you are experiencing severe distress or having thoughts of self-harm, please seek immediate professional help or contact a crisis helpline.'
        }
    
    def _build_explanation(self, stress_score, stress_level, high_concern_areas):
        """Build detailed explanation of the assessment"""
        explanation = f"Your total stress score is {stress_score} out of 30, indicating {stress_level.lower()} stress levels.\n\n"
        
        if high_concern_areas:
            explanation += f"Areas of concern (reported as 'Often' or 'Almost Always'):\n"
            for i, area in enumerate(high_concern_areas, 1):
                explanation += f"{i}. {area}\n"
            explanation += "\n"
        
        if stress_level == 'High':
            explanation += "High stress levels can significantly impact your physical and mental health, relationships, and daily functioning. "
            explanation += "Professional support can help you develop effective coping strategies and address underlying issues."
        elif stress_level == 'Moderate':
            explanation += "Moderate stress, if left unmanaged, can escalate and affect your well-being. "
            explanation += "Taking proactive steps now can prevent more serious issues."
        elif stress_level == 'Mild':
            explanation += "Mild stress is common and manageable with appropriate self-care strategies. "
            explanation += "Regular practice of stress management techniques can help maintain your well-being."
        else:
            explanation += "Your stress levels appear to be well-managed. "
            explanation += "Continue your current healthy practices to maintain your mental wellness."
        
        return explanation
    
    def _get_coping_strategies(self, stress_level):
        """Get appropriate coping strategies based on stress level"""
        base_strategies = [
            'Practice deep breathing exercises (4-7-8 technique)',
            'Engage in regular physical activity (30 minutes daily)',
            'Maintain consistent sleep schedule (7-9 hours)',
            'Practice mindfulness or meditation',
            'Connect with supportive friends and family'
        ]
        
        if stress_level in ['Moderate', 'High']:
            additional_strategies = [
                'Consider professional counseling or therapy',
                'Explore stress management workshops or programs',
                'Evaluate and adjust work-life balance',
                'Practice progressive muscle relaxation',
                'Keep a stress journal to identify triggers'
            ]
            return base_strategies + additional_strategies
        
        return base_strategies


def create_mental_health_assessment(responses):
    """
    Convenience function to create mental health assessment
    
    Parameters:
    -----------
    responses : dict or list
        Questionnaire responses (0-3 for each question)
    
    Returns:
    --------
    dict: Assessment results
    """
    engine = MentalHealthScreeningEngine()
    return engine.assess_stress(responses)


# Example usage
if __name__ == "__main__":
    # Test case 1: High stress
    test_responses_high = {
        'q1': 3,  # Feeling stressed or overwhelmed
        'q2': 3,  # Difficulty relaxing
        'q3': 3,  # Trouble sleeping
        'q4': 2,  # Excessive worrying
        'q5': 2,  # Difficulty concentrating
        'q6': 3,  # Irritability
        'q7': 3,  # Fatigue or low energy
        'q8': 2,  # Feeling anxious
        'q9': 2,  # Loss of motivation
        'q10': 3  # Feeling emotionally exhausted
    }
    
    result = create_mental_health_assessment(test_responses_high)
    print("High Stress Test:")
    print(f"Stress Score: {result['stress_score']}/30")
    print(f"Stress Level: {result['stress_level']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"High Concern Areas: {len(result['high_concern_areas'])}")
    print()
    
    # Test case 2: Low stress
    test_responses_low = [0, 1, 0, 1, 0, 1, 1, 0, 0, 1]  # List format
    
    result = create_mental_health_assessment(test_responses_low)
    print("Low Stress Test:")
    print(f"Stress Score: {result['stress_score']}/30")
    print(f"Stress Level: {result['stress_level']}")
    print(f"Recommendation: {result['recommendation']}")
    print()
    
    # Test case 3: Moderate stress
    test_responses_moderate = {
        'q1': 2, 'q2': 2, 'q3': 1, 'q4': 2, 'q5': 1,
        'q6': 2, 'q7': 2, 'q8': 1, 'q9': 1, 'q10': 2
    }
    
    result = create_mental_health_assessment(test_responses_moderate)
    print("Moderate Stress Test:")
    print(f"Stress Score: {result['stress_score']}/30")
    print(f"Stress Level: {result['stress_level']}")
    print(f"Recommendation: {result['recommendation']}")

# Made with Bob
