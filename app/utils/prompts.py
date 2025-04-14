from app.gbq.reading import get_prompt
from app.utils.logger import logger
import json
##MEJORAR RUTA PARA NO TENER PROBLEMAS.


def creating_json():
    prompts = {
        "System_Prompt_Assistant" : {"prompt":"", "documento_oficial":"x" , "chat":""},
        "System_Prompt_Cop":{"prompt":"","documento_oficial":"x", "chat":""},
        "System_Prompt_Tag":{"prompt":"","chat":""}
        }
    
    documentacion = get_prompt("Documentacion")
    for i in prompts.keys():
        data = get_prompt(i)
        prompts[i]['prompt'] = data
        if prompts[i].get('documento_oficial'):
            prompts[i]['documento_oficial'] = documentacion
        else:
            None
    with open("app/utils/prompts.json", "w",encoding='utf-8') as file:
        json.dump(prompts, file, indent=4, ensure_ascii=False)
    file.close()


def enhancing_json(category,chat=None):
    with open("app/utils/prompts.json", "r",encoding='utf-8') as file:
        prompts = json.load(file)
    if chat:
        prompts[category]['chat'] = chat
    else:
        None
    file.close()
    return str(prompts[category])