import aiohttp
import openai
from app.utils.logger import logger
from app.config.config import COST_1K_TOKENS, DS_API_KEY, GPT_API_KEY
from datetime import datetime
import traceback


def calculate_cost(response_json,model):
    """Calcula el costo en USD de cada accion del LLM"""
    for i in COST_1K_TOKENS:
        if i == model:
            cost_data = COST_1K_TOKENS.get(model, {"input": 0, "output": 0})
            break
        else: continue
    usage = response_json.get('usage', {})
    input_cost = cost_data["costo"]["input"] / 1000 * usage.get('prompt_tokens', 0)
    output_cost = cost_data["costo"]["output"] / 1000 * usage.get('completion_tokens', 0)
    total_cost = round(input_cost + output_cost,2)   
    return total_cost


async def llm_switch(prompt, 
                     message, 
                     max_tokens, 
                     temperature, 
                     deepseek_api_key=DS_API_KEY, 
                     ds_first_try = None, 
                     ds_second_try = None,
                     gpt_api_key=GPT_API_KEY, 
                     gpt_first_try = None):
    deepseek_url = "https://api.deepseek.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {deepseek_api_key}", "Content-Type": "application/json"}
    

    for model in [ds_first_try, ds_second_try]:
        data = {
            "model": model,
            "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": message}],
            "max_tokens": max_tokens,
            "temperature": temperature}
        try:
            logger.info(f"Calling DeepSeek API with model {model}...")
            async with aiohttp.ClientSession() as session:
                async with session.post(deepseek_url, headers=headers, json=data, timeout=40) as response:
                    logger.info(f"DeepSeek API response status (model {model}): {response.status}")
                    if response.status != 200:
                        try:
                            error_text = await response.text()
                        except Exception:
                            error_text = "<Unable to read error response>"
                        logger.warning(f"DeepSeek call with model {model} failed with status {response.status}: {error_text}")
                        continue 
                    response_json = await response.json()
                    created_at = response_json.get("created_at") or response_json.get("created")
                    created_at =  datetime.fromtimestamp(int(created_at))
                    response = response_json['choices'][0]['message']['content'].strip()
                    cost = calculate_cost(response_json,model)
                    logger.info(f"DeepSeek API responded successfully with model {model}.")
                    return response,created_at,model,cost
        except Exception as e:
                error_details = traceback.format_exc()
                logger.error(f"DeepSeek call with model {model} encountered an exception: {error_details}")
        logger.warning("Both DeepSeek calls failed. Falling back to GPT API.")

    try:
        logger.info("Calling GPT...")
        openai.api_key = gpt_api_key 
        response_json = await openai.ChatCompletion.acreate(
                                                model=gpt_first_try,
                                                messages=[{"role": "system", "content": prompt}, {"role": "user", "content": message}],
                                                max_tokens=max_tokens,
                                                temperature=temperature)
        
        model = gpt_first_try
        created_at = response_json.get("created_at") or response_json.get("created")
        created_at =  datetime.fromtimestamp(int(created_at))
        response = response_json['choices'][0]['message']['content'].strip()
        cost = calculate_cost(response_json,model)
        logger.info("GPT fallback succeeded.")
        return response,created_at,model,cost
    
    except Exception as e:
        logger.error(f"GPT fallback also failed: {e}")
        raise