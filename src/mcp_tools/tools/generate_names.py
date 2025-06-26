"""
Generate Names MCP Tool

AI-powered BEM name generation for PDF form fields.
Uses training data patterns and context analysis for intelligent naming.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class GenerateNamesTool:
    """MCP tool for generating BEM-style field names."""
    
    def __init__(self):
        """Initialize the generate names tool."""
        self.training_data_path = Path(__file__).parent.parent.parent.parent / "training_data" / "Clean Field Data - Sheet1.csv"
        self.bem_patterns = self._load_bem_patterns()
    
    def _load_bem_patterns(self) -> Dict[str, Any]:
        """Load BEM naming patterns from training data."""
        # Placeholder - will be enhanced in Phase 2.2
        return {
            "blocks": {
                "personal-information": ["name", "address", "phone", "email", "ssn"],
                "contingent-benficiary": ["name", "address", "dob", "percentage"],
                "sign-here": ["signature", "date"],
                "payment-information": ["method", "amount", "frequency"],
                "employer-information": ["name", "address", "contact"]
            },
            "modifiers": {
                "frequency": ["monthly", "quarterly", "annually"],
                "person": ["primary", "secondary", "joint"],
                "contact": ["home", "work", "mobile"]
            },
            "radio_group_suffix": "--group"
        }
    
    async def execute(
        self,
        field_data: Dict[str, Any],
        use_training_data: bool = True,
        confidence_threshold: float = 0.7,
        naming_strategy: str = "context_aware"
    ) -> Dict[str, Any]:
        """
        Generate BEM-style API names for extracted fields.
        
        Args:
            field_data: Extracted field data from extract_fields tool
            use_training_data: Whether to use training data patterns
            confidence_threshold: Minimum confidence for auto-accept
            naming_strategy: Strategy for name generation
            
        Returns:
            Dictionary containing generated names with confidence scores
        """
        try:
            logger.info("Generating BEM-style field names")
            
            if not field_data.get("success"):
                return {
                    "success": False,
                    "error": "Invalid field data provided",
                    "error_type": "InvalidInputError"
                }
            
            fields = field_data.get("fields", [])
            generated_names = []
            
            for field in fields:
                generated_name = self._generate_field_name(field, naming_strategy)
                generated_names.append(generated_name)
            
            # Analyze results
            high_confidence_count = len([
                name for name in generated_names 
                if name["confidence"] >= confidence_threshold
            ])
            
            result = {
                "success": True,
                "generation_metadata": {
                    "total_fields": len(fields),
                    "generated_count": len(generated_names),
                    "high_confidence_count": high_confidence_count,
                    "confidence_threshold": confidence_threshold,
                    "naming_strategy": naming_strategy,
                    "used_training_data": use_training_data
                },
                "generated_names": generated_names,
                "generation_summary": {
                    "ready_for_review": high_confidence_count,
                    "needs_manual_review": len(generated_names) - high_confidence_count,
                    "field_type_distribution": self._analyze_generated_types(generated_names)
                }
            }
            
            logger.info(f"Generated {len(generated_names)} field names")
            return result
            
        except Exception as e:
            logger.error(f"Error in generate_names: {str(e)}")
            return {
                "success": False,
                "error": f"Name generation error: {str(e)}",
                "error_type": type(e).__name__
            }
    
    def _generate_field_name(
        self, 
        field: Dict[str, Any], 
        strategy: str = "context_aware"
    ) -> Dict[str, Any]:
        """Generate a BEM-style name for a single field."""
        
        # Extract field information
        field_id = field.get("UUID", "unknown")
        original_name = field.get("Api name", "")
        field_type = field.get("Type", "TextField")
        label = field.get("Label", "")
        section_id = field.get("Section ID", "")
        
        # Context information
        context_data = field.get("_context_data", {})
        surrounding_text = context_data.get("surrounding_text", "")
        section_header = context_data.get("section_header", "")
        
        # Generate BEM name based on strategy
        if strategy == "context_aware":
            bem_name = self._generate_context_aware_name(
                original_name, field_type, label, surrounding_text, section_header
            )
        else:
            bem_name = self._generate_pattern_based_name(original_name, field_type, label)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(
            bem_name, field_type, label, original_name
        )
        
        return {
            "field_id": field_id,
            "original_name": original_name,
            "suggested_name": bem_name,
            "field_type": field_type,
            "label": label,
            "confidence": confidence,
            "reasoning": self._generate_reasoning(bem_name, field_type, strategy),
            "alternatives": self._generate_alternatives(bem_name, field_type)
        }
    
    def _generate_context_aware_name(
        self,
        original_name: str,
        field_type: str, 
        label: str,
        surrounding_text: str,
        section_header: str
    ) -> str:
        """Generate name using context analysis."""
        
        # Determine block (section) from various sources
        block = self._determine_block(original_name, label, section_header, surrounding_text)
        
        # Determine element (field purpose)
        element = self._determine_element(original_name, label, field_type)
        
        # Determine modifier if applicable
        modifier = self._determine_modifier(original_name, label, surrounding_text)
        
        # Handle RadioGroup special case
        if field_type == "RadioGroup":
            if modifier:
                return f"{block}_{element}__{modifier}--group"
            else:
                return f"{block}_{element}--group"
        
        # Build BEM name: block_element__modifier
        if modifier:
            return f"{block}_{element}__{modifier}"
        else:
            return f"{block}_{element}"
    
    def _determine_block(self, original_name: str, label: str, section_header: str, context: str) -> str:
        """Determine the BEM block (section) name."""
        
        # Check if original name already has a good block
        if "_" in original_name:
            potential_block = original_name.split("_")[0]
            if potential_block in self.bem_patterns["blocks"]:
                return potential_block
        
        # Analyze context for block hints
        context_lower = (section_header + " " + context + " " + label).lower()
        
        if any(word in context_lower for word in ["personal", "name", "address", "ssn"]):
            return "personal-information"
        elif any(word in context_lower for word in ["beneficiary", "contingent"]):
            return "contingent-benficiary"  # Match training data spelling
        elif any(word in context_lower for word in ["signature", "sign", "date"]):
            return "sign-here"
        elif any(word in context_lower for word in ["payment", "amount", "method"]):
            return "payment-information"
        elif any(word in context_lower for word in ["employer", "company"]):
            return "employer-information"
        else:
            return "general-information"
    
    def _determine_element(self, original_name: str, label: str, field_type: str) -> str:
        """Determine the BEM element (field purpose) name."""
        
        # Extract from original name if available
        if "_" in original_name:
            element_part = original_name.split("_")[1] if len(original_name.split("_")) > 1 else ""
            if element_part:
                return element_part.lower().replace(" ", "-")
        
        # Analyze label for element hints
        label_lower = label.lower()
        
        if "first" in label_lower and "name" in label_lower:
            return "first-name"
        elif "last" in label_lower and "name" in label_lower:
            return "last-name"
        elif "name" in label_lower:
            return "name"
        elif "address" in label_lower:
            return "address"
        elif "city" in label_lower:
            return "city"
        elif "state" in label_lower:
            return "state"
        elif "zip" in label_lower:
            return "zip"
        elif "phone" in label_lower:
            return "phone"
        elif "email" in label_lower:
            return "email"
        elif "ssn" in label_lower or "social" in label_lower:
            return "ssn"
        elif "signature" in label_lower:
            return "signature"
        elif "date" in label_lower:
            return "date"
        else:
            # Fallback: use original name or generic
            return original_name.lower().replace("_", "-").replace(" ", "-") or "field"
    
    def _determine_modifier(self, original_name: str, label: str, context: str) -> Optional[str]:
        """Determine the BEM modifier if applicable."""
        
        combined_text = (original_name + " " + label + " " + context).lower()
        
        # Check for common modifiers
        if "monthly" in combined_text:
            return "monthly"
        elif "quarterly" in combined_text:
            return "quarterly"
        elif "annually" in combined_text or "annual" in combined_text:
            return "annually"
        elif "primary" in combined_text:
            return "primary"
        elif "secondary" in combined_text:
            return "secondary"
        elif "joint" in combined_text:
            return "joint"
        
        return None
    
    def _generate_pattern_based_name(self, original_name: str, field_type: str, label: str) -> str:
        """Generate name using simple pattern matching."""
        
        # Basic pattern: convert existing name to BEM format
        if not original_name:
            return f"field-{field_type.lower()}"
        
        # Clean and format the name
        clean_name = original_name.lower().replace("_", "-").replace(" ", "-")
        
        if field_type == "RadioGroup" and not clean_name.endswith("--group"):
            clean_name += "--group"
        
        return clean_name
    
    def _calculate_confidence(
        self,
        bem_name: str,
        field_type: str,
        label: str,
        original_name: str
    ) -> float:
        """Calculate confidence score for generated name."""
        
        confidence = 0.5  # Base confidence
        
        # Boost confidence for well-formed BEM names
        if "_" in bem_name and not bem_name.startswith("_"):
            confidence += 0.2
        
        # Boost for RadioGroup handling
        if field_type == "RadioGroup" and bem_name.endswith("--group"):
            confidence += 0.2
        
        # Boost if we have meaningful label information
        if label and len(label) > 2:
            confidence += 0.1
        
        # Reduce confidence for generic names
        if "field" in bem_name or "unknown" in bem_name:
            confidence -= 0.3
        
        return min(1.0, max(0.1, confidence))
    
    def _generate_reasoning(self, bem_name: str, field_type: str, strategy: str) -> str:
        """Generate human-readable reasoning for the name choice."""
        
        if field_type == "RadioGroup":
            return f"Applied RadioGroup pattern with --group suffix using {strategy} strategy"
        elif "_" in bem_name:
            parts = bem_name.split("_")
            if len(parts) >= 2:
                block = parts[0]
                element = parts[1].split("__")[0] if "__" in parts[1] else parts[1]
                return f"Applied BEM pattern: block='{block}', element='{element}' using {strategy} strategy"
        
        return f"Applied {strategy} strategy for {field_type}"
    
    def _generate_alternatives(self, bem_name: str, field_type: str) -> List[str]:
        """Generate alternative name suggestions."""
        
        alternatives = []
        
        # Provide variations
        if "_" in bem_name:
            # Try different separator styles
            alternatives.append(bem_name.replace("_", "-"))
            
            # Try shortened version
            parts = bem_name.split("_")
            if len(parts) >= 2:
                alternatives.append(f"{parts[0][0:3]}_{parts[1]}")
        
        # Add generic fallback
        alternatives.append(f"custom-{field_type.lower()}")
        
        return alternatives[:3]  # Limit to 3 alternatives
    
    def _analyze_generated_types(self, generated_names: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze the distribution of generated field types."""
        
        type_counts = {}
        for name_entry in generated_names:
            field_type = name_entry.get("field_type", "Unknown")
            type_counts[field_type] = type_counts.get(field_type, 0) + 1
        
        return type_counts