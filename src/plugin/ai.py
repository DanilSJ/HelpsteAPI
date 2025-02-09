import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def ChatGPT(model: str, prompt: str, history: list) -> str:
    try:
        if not isinstance(model, str) or not model.strip():
            raise ValueError("Model must be a non-empty string.")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string.")
        if not isinstance(history, list):
            raise ValueError("History must be a list.")

        messages = [{"role": "system", "content": "You are a helpful assistant, speak Russian."}]
        messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        response = await client.chat.completions.create(
            model=model,
            messages=messages
        )

        if not response or not response.choices or not response.choices[0].message:
            raise ValueError("The response from ChatGPT is empty or invalid.")

        return response.choices[0].message.content
    except Exception as e:
        raise ValueError(f"Error in ChatGPT: {str(e)}")


async def Dalle(prompt: str, n: int):
    try:
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string.")

        response = await client.images.generate(
            prompt=prompt,
            n=n,
            size="1024x1024"
        )

        if not response:
            raise ValueError("The response from Dalle is empty or invalid.")

        return response
    except Exception as e:
        raise ValueError(f"Error in Dalle: {str(e)}")
