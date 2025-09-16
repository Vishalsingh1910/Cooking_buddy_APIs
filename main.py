# todo: hit this in terminal $env:GEMINI_API_KEY="YOUR_API_KEY_HERE"


from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json

app = Flask(__name__)
CORS(app)

# Configure Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Use flash model (faster, higher free quota)
model = genai.GenerativeModel("gemini-1.5-flash")


@app.route("/generate_recipe", methods=["POST"])
def generate_recipe():
    try:
        data = request.json
        ingredients = data.get("ingredients", [])

        if not ingredients:
            return jsonify({"error": "No ingredients provided"}), 400

        prompt = f"""
        Generate a recipe in JSON format using these ingredients: {ingredients}.
        Structure it like this:
        {{
          "title": "Recipe Title",
          "ingredients": ["item1", "item2"],
          "steps": ["step1", "step2"]
        }}
        """

        # Call Gemini
        gemini_response = model.generate_content(prompt)

        # ✅ Correct way: use .text, not .response.text
        raw_text = gemini_response.text.strip()

        # Remove Markdown code fences if Gemini adds them
        if raw_text.startswith("```"):
            raw_text = raw_text.strip("`")
            if raw_text.startswith("json"):
                raw_text = raw_text[4:].strip()

        # Try to parse JSON
        try:
            recipe_json = json.loads(raw_text)
        except json.JSONDecodeError:
            recipe_json = {"raw": raw_text}

        return jsonify(recipe_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
