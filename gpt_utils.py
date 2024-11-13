import config
import google.generativeai as genai

genai.configure(api_key=config.GPT_KEY)


def make_raquest(text: str) -> str:
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(
        "You are helpful and assistant. Your name is Ola." + text,
        generation_config=genai.types.GenerationConfig(
            max_output_tokens=100,
            temperature=0.9,
        ),
    )

    return response.text
