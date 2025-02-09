from fastapi import APIRouter, HTTPException
from src.plugin.ai import ChatGPT, Dalle
from src.routers.sheme.AiModels import *

router = APIRouter()

@router.post("_gpt/")
async def gpt_request(request: GPTRequest):
    try:
        chat = await ChatGPT(request.model, request.prompt, request.history)
        if not chat:
            raise HTTPException(status_code=500, detail="The response from ChatGPT is empty.")
        return {"response": chat}
    except ValueError as ve:
        raise HTTPException(
            status_code=400,
            detail=("Error 400 check argument")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("_dalle/")
async def dalle_request(request: DalleRequest):
    try:
        chat = await Dalle(prompt=request.prompt, n=request.n)
        if not chat:
            raise HTTPException(status_code=500, detail="The response from Dalle is empty.")
        return {"response": chat}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

