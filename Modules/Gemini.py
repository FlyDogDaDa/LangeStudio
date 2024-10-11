import google.generativeai as genai
from Modules.load_config import config_dict

genai.configure(api_key=config_dict["Google_AI_Studio_API_key"])
model = genai.GenerativeModel(
    model_name=config_dict["LLM_model"],
    system_instruction=config_dict["LLM_system_instruction"],
    safety_settings=config_dict["gemini_safety_settings"],
    generation_config=config_dict["gemini_generation_config"],
)

# TODO:視覺+音訊，多語者ASR，with Gemini-Tools
