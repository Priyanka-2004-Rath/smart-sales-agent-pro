# enhanced_mood_detector.py
from transformers import pipeline
import torch
import re
from typing import Dict, List, Tuple

class MoodDetector:
    def __init__(self):
        """Initialize the mood detection pipeline with error handling"""
        self.emotion_pipeline = None
        self._initialize_pipeline()
        
        # Enhanced mood mapping with more emotions
        self.mood_mapping = {
            "joy": "😊 Happy",
            "happiness": "😊 Happy", 
            "sadness": "😢 Sad",
            "anger": "😠 Angry",
            "fear": "😨 Fearful",
            "surprise": "😲 Surprised",
            "disgust": "🤢 Disgusted",
            "love": "❤️ Loving",
            "excitement": "🤩 Excited",
            "optimism": "🌟 Optimistic",
            "annoyance": "😤 Annoyed",
            "disappointment": "😞 Disappointed",
            "neutral": "😐 Neutral",
            "admiration": "👏 Admiring",
            "approval": "👍 Approving",
            "caring": "🤗 Caring",
            "confusion": "😕 Confused",
            "curiosity": "🤔 Curious",
            "desire": "😍 Interested",
            "embarrassment": "😳 Embarrassed",
            "gratitude": "🙏 Grateful",
            "grief": "😭 Grieving",
            "nervousness": "😰 Nervous",
            "pride": "😤 Proud",
            "realization": "💡 Realizing",
            "relief": "😌 Relieved",
            "remorse": "😔 Remorseful"
        }
        
        # Enhanced emotion categories for better reply generation
        self.emotion_categories = {
            "happy": ["joy", "happiness", "love", "excitement", "optimism", "admiration", 
                     "approval", "gratitude", "pride", "relief"],
            "excited": ["excitement", "joy", "love", "admiration", "desire", "curiosity"],
            "sad": ["sadness", "grief", "disappointment", "remorse", "embarrassment"],
            "angry": ["anger", "annoyance", "disgust"],
            "frustrated": ["annoyance", "disappointment", "confusion", "nervousness"],
            "neutral": ["neutral", "realization", "surprise", "caring", "fear"]
        }
    
    def _initialize_pipeline(self):
        """Initialize the emotion detection pipeline with fallback options"""
        models_to_try = [
            "j-hartmann/emotion-english-distilroberta-base",
            "cardiffnlp/twitter-roberta-base-emotion-multilabel-latest",
            "microsoft/DialoGPT-medium"  # Fallback option
        ]
        
        for model_name in models_to_try:
            try:
                self.emotion_pipeline = pipeline(
                    "text-classification",
                    model=model_name,
                    device=0 if torch.cuda.is_available() else -1,
                    return_all_scores=True
                )
                print(f"Successfully loaded model: {model_name}")
                break
            except Exception as e:
                print(f"Failed to load {model_name}: {e}")
                continue
        
        if self.emotion_pipeline is None:
            print("Warning: Using rule-based fallback for emotion detection")
    
    def detect_mood(self, text: str) -> Dict:
        """
        Detect the mood/emotion of the given text with enhanced error handling
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            dict: Dictionary containing mood, confidence, and raw scores
        """
        if not text or text.strip() == "":
            return {
                "mood": "😐 Neutral",
                "confidence": 0.0,
                "raw_scores": {},
                "label": "neutral"
            }
        
        text = text.strip()
        
        # If pipeline failed to load, use rule-based detection
        if self.emotion_pipeline is None:
            return self._rule_based_detection(text)
        
        try:
            # Get emotion predictions
            results = self.emotion_pipeline(text)
            
            # Handle different result formats
            if isinstance(results[0], list):
                results = results[0]
            
            # Sort results by score
            sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
            top_result = sorted_results[0]
            
            # Get the emotion label and confidence
            label = top_result['label'].lower()
            confidence = round(top_result['score'] * 100, 2)
            
            # Map to display format
            mood = self.mood_mapping.get(label, f"🧠 {label.capitalize()}")
            
            # Create raw scores dictionary
            raw_scores = {r['label']: round(r['score'] * 100, 2) for r in results}
            
            return {
                "mood": mood,
                "confidence": confidence,
                "raw_scores": raw_scores,
                "label": label
            }
            
        except Exception as e:
            print(f"Error in mood detection: {e}")
            return self._rule_based_detection(text)
    
    def _rule_based_detection(self, text: str) -> Dict:
        """Fallback rule-based emotion detection"""
        text_lower = text.lower()
        
        # Define keyword patterns
        emotion_keywords = {
            "happy": ["happy", "great", "awesome", "amazing", "fantastic", "wonderful", 
                     "excellent", "love", "excited", "thrilled", "joy", "pleased"],
            "angry": ["angry", "furious", "mad", "rage", "hate", "terrible", "awful",
                     "disgusting", "outraged", "livid"],
            "sad": ["sad", "depressed", "disappointed", "upset", "hurt", "crying",
                   "miserable", "heartbroken", "devastated"],
            "frustrated": ["frustrated", "annoyed", "irritated", "bothered", "stuck",
                          "confused", "overwhelmed", "stressed"],
            "excited": ["excited", "thrilled", "eager", "enthusiastic", "pumped",
                       "stoked", "psyched"],
            "neutral": ["okay", "fine", "alright", "normal", "average"]
        }
        
        # Score each emotion based on keyword matches
        emotion_scores = {}
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                emotion_scores[emotion] = score
        
        # Determine primary emotion
        if emotion_scores:
            primary_emotion = max(emotion_scores.keys(), key=lambda x: emotion_scores[x])
            confidence = min(emotion_scores[primary_emotion] * 20, 100)  # Simple confidence calc
        else:
            primary_emotion = "neutral"
            confidence = 50.0
        
        mood = self.mood_mapping.get(primary_emotion, f"🧠 {primary_emotion.capitalize()}")
        
        return {
            "mood": mood,
            "confidence": confidence,
            "raw_scores": {k: v*10 for k, v in emotion_scores.items()},
            "label": primary_emotion
        }
    
    def get_mood_category(self, emotion_label: str) -> str:
        """
        Categorize emotions into broader mood categories for reply generation
        
        Args:
            emotion_label (str): Raw emotion label from the model
            
        Returns:
            str: Categorized mood
        """
        emotion_lower = emotion_label.lower()
        
        for category, emotions in self.emotion_categories.items():
            if emotion_lower in emotions:
                return category
        
        return "neutral"
    
    def analyze_sentiment_intensity(self, text: str) -> str:
        """Analyze the intensity of the sentiment"""
        text_lower = text.lower()
        
        # High intensity indicators
        high_intensity = ["!!", "!!!", "absolutely", "extremely", "really", "very", 
                         "so", "totally", "completely", "utterly"]
        
        # Check for caps (indicates strong emotion)
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if text else 0
        
        # Check for high intensity words
        intensity_score = sum(1 for word in high_intensity if word in text_lower)
        
        if caps_ratio > 0.3 or intensity_score >= 2:
            return "high"
        elif intensity_score >= 1 or "!" in text:
            return "medium"
        else:
            return "low"


class ReplyGenerator:
    def __init__(self):
        """Initialize the reply generator with enhanced templates"""
        self.mood_responses = {
            "angry": {
                "high": "I completely understand your frustration, and I sincerely apologize for this experience. Let me personally ensure we resolve this for you right away.",
                "medium": "I understand your frustration and want to help resolve this issue for you.",
                "low": "I apologize for any inconvenience. Let me help you with this."
            },
            "frustrated": {
                "high": "I can see this has been really challenging for you. Let's work together to find a solution that works.",
                "medium": "I understand this has been frustrating. Let me help you through this step by step.",
                "low": "I can see this might be confusing. Let me clarify this for you."
            },
            "happy": {
                "high": "I absolutely love your enthusiasm! I'm thrilled to help you with this.",
                "medium": "That's wonderful to hear! I'm excited to assist you today.",
                "low": "Great to hear from you! How can I help you today?"
            },
            "excited": {
                "high": "Your excitement is contagious! I'm just as excited to help you achieve your goals.",
                "medium": "I love your energy! Let's explore how we can help you.",
                "low": "That's great to hear! What can I help you with today?"
            },
            "sad": {
                "high": "I'm really sorry to hear you're going through this. I'm here to support you in any way I can.",
                "medium": "I'm sorry to hear that. Let me see how I can help improve this situation.",
                "low": "I understand this might be disappointing. How can I assist you?"
            },
            "neutral": {
                "high": "Thank you for reaching out. I'm here to help with whatever you need.",
                "medium": "Thanks for your message. How can I assist you today?",
                "low": "Hello! How can I help you today?"
            }
        }
        
        # Context-specific responses
        self.context_patterns = {
            "pricing": ["price", "cost", "expensive", "cheap", "budget", "affordable"],
            "support": ["help", "support", "problem", "issue", "broken", "not working", "crash", "crashing", "bug", "glitch", "reinstall", "freeze", "lag", "slow"],
            "product": ["product", "feature", "service", "offer", "solution"],
            "greeting": ["hi", "hello", "hey", "greetings", "good morning", "good afternoon"]
        }
    
    def generate_reply(self, user_input: str, mood: str, intensity: str = "medium") -> str:
        """
        Generate a contextually appropriate reply based on mood and intensity
        
        Args:
            user_input (str): The user's message
            mood (str): Detected mood category
            intensity (str): Intensity level (high/medium/low)
            
        Returns:
            str: Generated reply
        """
        if not user_input or user_input.strip() == "":
            return "I'd be happy to help! Could you please share more details about what you're looking for?"
        
        # Detect context
        context = self._detect_context(user_input.lower())
        
        # Get base response based on mood and intensity
        base_response = self.mood_responses.get(mood, self.mood_responses["neutral"])
        response = base_response.get(intensity, base_response["medium"])
        
        # Add context-specific follow-up
        context_followup = self._get_context_followup(context, mood)
        if context_followup:
            response += f" {context_followup}"
        
        return response
    
    def _detect_context(self, text: str) -> str:
        """Detect the context of the user's message"""
        for context, keywords in self.context_patterns.items():
            if any(keyword in text for keyword in keywords):
                return context
        return "general"
    
    def _get_context_followup(self, context: str, mood: str) -> str:
        """Get context-specific follow-up based on detected context and mood"""
        followups = {
            "pricing": "Would you like to discuss our pricing options and find something that fits your budget?",
            "support": "What specific issue are you experiencing? I'm here to help resolve it.",
            "product": "What particular aspect of our product/service interests you most?",
            "greeting": "What brings you here today? I'm ready to assist!",
            "general": "What can I help you with today?"
        }
        
        return followups.get(context, "How can I assist you further?")


# Test function
def test_enhanced_system():
    """Test the enhanced mood detection and reply system"""
    detector = MoodDetector()
    generator = ReplyGenerator()
    
    test_messages = [
        "Hey! I'm really excited about your new product launch!",
        "This is absolutely terrible service, I'm furious right now!!!",
        "I've been trying to reach someone for hours and no one is responding",
        "This looks amazing! I love what you guys are doing",
        "I'm really disappointed with my recent experience",
        "Can you tell me about your pricing plans?",
        "HELP! Nothing is working and I'm so frustrated!",
        "Hi there, just wanted to say your product is fantastic!"
    ]
    
    print("Testing Enhanced Mood Detection & Reply System:")
    print("=" * 60)
    
    for message in test_messages:
        # Detect mood
        result = detector.detect_mood(message)
        category = detector.get_mood_category(result['label'])
        intensity = detector.analyze_sentiment_intensity(message)
        
        # Generate reply
        reply = generator.generate_reply(message, category, intensity)
        
        print(f"Message: {message}")
        print(f"Mood: {result['mood']}")
        print(f"Confidence: {result['confidence']}%")
        print(f"Category: {category}")
        print(f"Intensity: {intensity}")
        print(f"Reply: {reply}")
        print("-" * 60)


if __name__ == "__main__":
    test_enhanced_system()