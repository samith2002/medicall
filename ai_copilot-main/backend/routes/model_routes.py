from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

from config import STT_CONFIG, LLM_CONFIG, STT_MODELS, LLM_MODELS
from models.schemas import ModelUpdateRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/models", tags=["models"])

@router.get("/")
async def get_models() -> Dict[str, Any]:
    """Get available models and current configuration"""
    return {
        "stt_models": STT_MODELS,
        "llm_models": LLM_MODELS,
        "current_stt_config": STT_CONFIG,
        "current_llm_config": LLM_CONFIG
    }

@router.post("/update")
async def update_model(request: ModelUpdateRequest) -> Dict[str, Any]:
    """Update model configuration"""
    try:
        # Update STT model if provided
        if request.stt_model:
            if request.stt_model in STT_MODELS:
                STT_CONFIG["model"] = STT_MODELS[request.stt_model]
                logger.info(f"Updated STT model to {STT_CONFIG['model']}")
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unknown STT model: {request.stt_model}. Available options: {list(STT_MODELS.keys())}"
                )
                
        # Update LLM model if provided
        if request.llm_model:
            if request.llm_model in LLM_MODELS:
                LLM_CONFIG["model"] = LLM_MODELS[request.llm_model]
                logger.info(f"Updated LLM model to {LLM_CONFIG['model']}")
            else:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unknown LLM model: {request.llm_model}. Available options: {list(LLM_MODELS.keys())}"
                )
                
        # Update other configuration parameters
        if request.temperature is not None:
            LLM_CONFIG["temperature"] = float(request.temperature)
            logger.info(f"Updated temperature to {LLM_CONFIG['temperature']}")
            
        if request.max_tokens is not None:
            LLM_CONFIG["max_tokens"] = int(request.max_tokens)
            logger.info(f"Updated max_tokens to {LLM_CONFIG['max_tokens']}")
            
        if request.system_prompt:
            LLM_CONFIG["system_prompt"] = request.system_prompt
            logger.info(f"Updated system prompt")
            
        return {
            "status": "success", 
            "stt_config": STT_CONFIG, 
            "llm_config": LLM_CONFIG
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating model: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 