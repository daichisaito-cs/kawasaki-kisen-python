from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import whisper
import uvicorn

app = FastAPI()

# CORS設定（v0でローカルから叩けるように）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じて絞ってOK
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Whisperモデル読み込み（初期化は時間がかかるため一度だけ）
# ~/.cache/whisperにモデルが保存される
model = whisper.load_model("large-v3-turbo")
# available models = ['tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large', 'large-v3-turbo', 'turbo']

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    try:
        # 一時ファイルとして保存
        temp_file_path = f"/tmp/{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())

        # Whisperで文字起こし
        result = model.transcribe(temp_file_path, language="ja")
        return {"text": result["text"]}

    except Exception as e:
        return {"error": str(e)}
    
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# モデル（多言語対応、日英混在に強い）
embed_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# テンプレート一覧（IDと文）
templates = [
    {"id": 1, "en": "Oil leakage observed around the engine compartment."},
    {"id": 2, "en": "Surface rust observed on the hull."},
    {"id": 3, "en": "Cargo is properly secured with lashings."},
    {"id": 4, "en": "Minor dents detected on the starboard side."},
    {"id": 5, "en": "Paint damage found near the bow area."},
    {"id": 6, "en": "No visible damage to the cargo."},
    {"id": 7, "en": "Vehicles loaded in accordance with the manifest."},
    {"id": 8, "en": "Inspection completed without incident."},
    {"id": 9, "en": "High ambient temperature recorded during inspection."},
    {"id": 10, "en": "Anomaly detected; further inspection recommended."}
]

# ベクトル化（英語テンプレートは事前計算して保持）
template_embeddings = embed_model.encode([t["en"] for t in templates])

@app.post("/api/template")
async def get_template(text: str = Form(...)):
    try:
        # 入力テキストをベクトル化（日本語対応OK）
        query_vec = embed_model.encode([text])

        # 類似度計算（コサイン類似度）
        similarities = cosine_similarity(query_vec, template_embeddings)[0]
        best_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_idx])

        matched_template = templates[best_idx]["en"]

        return {
            "input": text,
            "matched": matched_template,
            "similarity": round(best_score, 3)
        }

    except Exception as e:
        return {"error": str(e)}

# if __name__ == "__main__":
#     import os
#     port = int(os.environ.get("PORT", 8000))
#     uvicorn.run(app, host="0.0.0.0", port=port)