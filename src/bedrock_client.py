"""AWS Bedrock client for AI model inference."""
import json
import time
import logging
from typing import Optional
import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)


class BedrockClient:
    """Client for invoking AWS Bedrock AI models."""
    
    def __init__(
        self,
        region: str = "eu-north-1",
        primary_model_id: str = "anthropic.claude-3-5-sonnet-20241022-v2:0",
        fallback_model_id: str = "anthropic.claude-3-haiku-20240307-v1:0",
        timeout: float = 0.8
    ):
        """
        Initialize Bedrock client.
        
        Args:
            region: AWS region
            primary_model_id: Primary AI model to use
            fallback_model_id: Fallback model if primary fails
            timeout: Timeout for AI calls in seconds
        """
        self.region = region
        self.primary_model_id = primary_model_id
        self.fallback_model_id = fallback_model_id
        self.timeout = timeout
        
        try:
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=region
            )
            logger.info(f"Bedrock client initialized for region {region}")
        except Exception as e:
            logger.error(f"Failed to initialize Bedrock client: {e}")
            self.client = None
    
    def invoke_model(self, prompt: str, model_id: Optional[str] = None) -> Optional[str]:
        """
        Invoke a Bedrock model with the given prompt.
        
        Args:
            prompt: The prompt to send to the model
            model_id: Model ID to use (defaults to primary_model_id)
        
        Returns:
            Model response text, or None if invocation fails
        """
        if not self.client:
            logger.error("Bedrock client not initialized")
            return None
        
        model_id = model_id or self.primary_model_id
        
        try:
            # Construct request body for Claude models
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 2000,
                "temperature": 0.7,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            logger.info(f"Invoking model {model_id}")
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract text from Claude response
            if 'content' in response_body and len(response_body['content']) > 0:
                text = response_body['content'][0].get('text', '')
                logger.info(f"Model response received ({len(text)} chars)")
                return text
            
            logger.warning("No content in model response")
            return None
            
        except ClientError as e:
            logger.error(f"AWS ClientError invoking model: {e}")
            return None
        except BotoCoreError as e:
            logger.error(f"BotoCoreError invoking model: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error invoking model: {e}")
            return None
    
    def invoke_model_with_retry(
        self,
        prompt: str,
        max_retries: int = 2
    ) -> Optional[str]:
        """
        Invoke model with retry logic and fallback.
        
        Strategy:
        1. Try primary model
        2. If fails, try primary model again (1 retry)
        3. If still fails, try fallback model
        
        Args:
            prompt: The prompt to send
            max_retries: Maximum retry attempts per model
        
        Returns:
            Model response text, or None if all attempts fail
        """
        # Try primary model
        for attempt in range(max_retries):
            response = self.invoke_model(prompt, self.primary_model_id)
            if response:
                return response
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying primary model (attempt {attempt + 2}/{max_retries})")
                time.sleep(0.1)  # Brief delay before retry
        
        # Try fallback model
        logger.info("Primary model failed, trying fallback model")
        response = self.invoke_model(prompt, self.fallback_model_id)
        if response:
            return response
        
        logger.error("All model invocation attempts failed")
        return None
