from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os, json
from dotenv import load_dotenv

# Load .env file
load_dotenv()

app = FastAPI()

# Now it will pick from .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class IngredientsRequest(BaseModel):
    ingredients: list[str]

@app.post("/get_recipes")
async def get_recipes(request: IngredientsRequest):
    prompt = f"""
    Suggest 3 recipes I can cook using these ingredients: {', '.join(request.ingredients)}.
    Return valid JSON list with fields: name, ingredients, steps, cooking_time.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    content = response.choices[0].message.content

    try:
        recipes = json.loads(content)
    except:
        recipes = {"error": "Invalid JSON from AI", "raw": content}
    
    return {"recipes": recipes}
