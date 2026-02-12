from fastapi import FastAPI, File, UploadFile, HTTPException
from google import genai
from google.genai import types
import PIL.Image
import io
import os

app = FastAPI()

# Pega a chave das Variáveis de Ambiente (Segurança!)
API_KEY = os.environ.get("GEMINI_API_KEY")

@app.get("/")
def home():
    return {"status": "Online", "msg": "API de Notas Fiscais rodando!"}

@app.post("/analisar")
async def analisar_nota(file: UploadFile = File(...)):
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key não configurada no Vercel")


    try:
        contents = await file.read()
        image = PIL.Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Arquivo inválido. Envie uma imagem.")


    client = genai.Client(api_key=API_KEY)

    prompt = """
    Analise esta nota fiscal. Extraia: Estabelecimento, CNPJ, Data, Valor Total e Itens.
    Retorne APENAS um JSON válido.
    """

   
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        # Retorna o JSON direto
        return {"sucesso": True, "dados": response.text}
        
    except Exception as e:
        return {"sucesso": False, "erro": str(e)}