from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline

# Cargar modelo una sola vez al iniciar la API
best_model_path = "./best_model"
tokenizer = AutoTokenizer.from_pretrained(best_model_path)
model = AutoModelForSequenceClassification.from_pretrained(best_model_path)

classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

app = FastAPI()

# Estructura del JSON de entrada
class datos_entrada(BaseModel):
    session_id: str
    timestamp_id: str
    text: str
    completed: bool

# Endpoint
@app.post("/sentiment-analysis/")
async def sentiment_analysis(data: datos_entrada):

    # Ignorar si el texto no está completo
    if not data.completed:
        return {"message": "Texto incompleto"}

    resultado = classifier(data.text)

    return {
        "session_id": data.session_id,
        "timestamp_id": data.timestamp_id,
        "lexical_score": resultado[0]['score'],
        "lexical_label": resultado[0]['label']
    }


