"""
AI Strategy Generator Service

This module provides functionality to generate trading strategy code using
Google's Gemini AI with code execution capabilities.
"""

import google.generativeai as genai
import re
import json
import logging
from typing import Dict, Any, Optional
from django.conf import settings
import os

logger = logging.getLogger(__name__)


class StrategyGeneratorError(Exception):
    """Custom exception for strategy generation errors"""
    pass


class AIStrategyGenerator:
    """
    AI-powered trading strategy generator using Google Gemini API
    with code execution tool enabled.
    """
    
    def __init__(self):
        """Initialize the AI Strategy Generator with Gemini API"""
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise StrategyGeneratorError(
                "GEMINI_API_KEY not found in settings or environment variables"
            )
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model with code execution tool
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            tools='code_execution'
        )
    
    def generate_strategy_code(self, prompt: str) -> str:
        """
        Generate trading strategy code using Gemini AI with code execution.
        
        Args:
            prompt (str): User's text prompt describing the desired trading strategy
            
        Returns:
            str: Generated Python code for the trading strategy
            
        Raises:
            StrategyGeneratorError: If code generation fails or no executable code found
        """
        try:
            # Enhanced prompt for trading strategy generation
            enhanced_prompt = self._build_strategy_prompt(prompt)
            
            logger.info(f"Generating strategy code for prompt: {prompt[:100]}...")
            
            # Generate content with code execution tool
            response = self.model.generate_content(enhanced_prompt)
            
            # Extract executable code from response
            strategy_code = self._extract_executable_code(response)
            
            if not strategy_code:
                raise StrategyGeneratorError("No executable code found in AI response")
            
            logger.info("Strategy code generated successfully")
            return strategy_code
            
        except Exception as e:
            logger.error(f"Strategy generation failed: {str(e)}")
            raise StrategyGeneratorError(f"Failed to generate strategy code: {str(e)}")
    
    def _build_strategy_prompt(self, user_prompt: str) -> str:
        """
        Build an enhanced prompt for trading strategy generation.
        
        Args:
            user_prompt (str): Original user prompt
            
        Returns:
            str: Enhanced prompt with context and requirements
        """
        return f"""
You are an expert trading strategy developer. Generate a complete Python trading strategy based on this request:

USER REQUEST: {user_prompt}

REQUIREMENTS:
1. Create a complete trading strategy function that can be used in a trading bot
2. Include proper technical analysis using common indicators
3. Return clear buy/sell/hold signals
4. Add comprehensive comments explaining the logic
5. Include risk management features like stop-loss and take-profit
6. Use realistic parameters and thresholds
7. Handle edge cases and error conditions

STRATEGY TEMPLATE:
```python
def execute_strategy(market_data: dict, strategy_params: dict) -> dict:
    \"\"\"
    Trading strategy implementation
    
    Args:
        market_data (dict): Current market data including OHLCV
        strategy_params (dict): Strategy configuration parameters
        
    Returns:
        dict: Trading signal with action, confidence, and metadata
    \"\"\"
    # Your strategy implementation here
    pass
```

EXPECTED OUTPUT FORMAT:
- Return a complete, executable Python function
- Include all necessary imports at the top
- Add detailed docstrings and comments
- Ensure the code is production-ready

Please generate the complete strategy code with explanations:
"""
    
    def _extract_executable_code(self, response) -> Optional[str]:
        """
        Extract executable Python code from Gemini response.
        
        Args:
            response: Gemini API response object
            
        Returns:
            Optional[str]: Extracted Python code or None if not found
        """
        try:
            # First, try to extract from code execution parts
            if hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'executable_code') and part.executable_code:
                        if hasattr(part.executable_code, 'code'):
                            return part.executable_code.code
            
            # Alternative: extract from text using regex patterns
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            # Look for Python code blocks
            code_patterns = [
                r'```python\n(.*?)\n```',
                r'```\n(.*?)\n```',
                r'<code>(.*?)</code>',
                r'executableCode["\']?\s*:\s*["\']?(.*?)["\']?',
            ]
            
            for pattern in code_patterns:
                matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)
                if matches:
                    # Return the largest code block found
                    return max(matches, key=len).strip()
            
            # If no code blocks found, look for function definitions
            function_pattern = r'(def\s+\w+.*?(?=\n\S|\Z))'
            function_matches = re.findall(function_pattern, response_text, re.DOTALL)
            if function_matches:
                return '\n\n'.join(function_matches)
            
            logger.warning("No executable code patterns found in response")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting executable code: {str(e)}")
            return None
    
    def validate_strategy_code(self, code: str) -> Dict[str, Any]:
        """
        Validate the generated strategy code for syntax and structure.
        
        Args:
            code (str): Generated Python code
            
        Returns:
            Dict[str, Any]: Validation results with success status and details
        """
        validation_result = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'has_function': False,
            'has_imports': False
        }
        
        try:
            # Check for syntax errors
            compile(code, '<string>', 'exec')
            validation_result['syntax_valid'] = True
            
            # Check for required function
            if 'def ' in code:
                validation_result['has_function'] = True
            else:
                validation_result['warnings'].append("No function definition found")
            
            # Check for imports
            if 'import ' in code:
                validation_result['has_imports'] = True
            
            # Check for common trading strategy elements
            trading_keywords = ['signal', 'buy', 'sell', 'strategy', 'market_data']
            found_keywords = [kw for kw in trading_keywords if kw.lower() in code.lower()]
            validation_result['trading_keywords'] = found_keywords
            
            if len(found_keywords) >= 2:
                validation_result['valid'] = True
            else:
                validation_result['errors'].append("Code doesn't appear to be a trading strategy")
                
        except SyntaxError as e:
            validation_result['errors'].append(f"Syntax error: {str(e)}")
        except Exception as e:
            validation_result['errors'].append(f"Validation error: {str(e)}")
        
        return validation_result


def generate_strategy_code(prompt: str) -> str:
    """
    Convenience function to generate strategy code using AI.
    
    Args:
        prompt (str): User's text prompt describing the desired trading strategy
        
    Returns:
        str: Generated Python code for the trading strategy
        
    Raises:
        StrategyGeneratorError: If code generation fails
    """
    generator = AIStrategyGenerator()
    return generator.generate_strategy_code(prompt)


def validate_generated_strategy(code: str) -> Dict[str, Any]:
    """
    Convenience function to validate generated strategy code.
    
    Args:
        code (str): Generated Python code
        
    Returns:
        Dict[str, Any]: Validation results
    """
    generator = AIStrategyGenerator()
    return generator.validate_strategy_code(code)
