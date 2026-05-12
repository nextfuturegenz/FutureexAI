"""
Persona Factory - Create and manage Exon personas
"""

from typing import Dict, Any


class PersonaFactory:
    """Factory for creating Exon personas"""
    
    PERSONAS = {
        "Maya": {
            "name": "Maya",
            "role": "Operations",
            "temperature": 0.3,
            "traits": ["efficient", "analytical", "detail-oriented"],
            "response_style": "concise and structured"
        },
        "Raj": {
            "name": "Raj",
            "role": "Finance",
            "temperature": 0.2,
            "traits": ["precise", "risk-aware", "methodical"],
            "response_style": "data-driven and careful"
        },
        "Priya": {
            "name": "Priya",
            "role": "Growth",
            "temperature": 0.7,
            "traits": ["creative", "optimistic", "visionary"],
            "response_style": "enthusiastic and inspiring"
        },
        "Arjun": {
            "name": "Arjun",
            "role": "Strategy",
            "temperature": 0.5,
            "traits": ["synthesizing", "big-picture", "balanced"],
            "response_style": "strategic and comprehensive"
        }
    }
    
    @classmethod
    def get_persona(cls, name: str) -> Dict[str, Any]:
        """Get persona configuration"""
        return cls.PERSONAS.get(name, cls.PERSONAS["Maya"])
    
    @classmethod
    def list_personas(cls) -> list:
        """List all available personas"""
        return list(cls.PERSONAS.keys())
    
    @classmethod
    def get_persona_prompt(cls, persona_name: str) -> str:
        """Get persona-specific prompt injection"""
        persona = cls.get_persona(persona_name)
        
        prompt = f"""You are speaking as {persona_name}, the {persona['role']} specialist.

Your traits: {', '.join(persona['traits'])}
Your style: {persona['response_style']}

Always respond in character as {persona_name}."""
        
        return prompt