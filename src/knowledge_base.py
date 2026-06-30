"""
knowledge_base.py

Carrega e indexa o dataset de finanças pessoais do Hugging Face
(bilalRahib/fiqa-personal-finance-dataset) para uso em RAG
(Retrieval-Augmented Generation).

Na primeira execução, baixa o dataset e calcula os embeddings.
Em execuções seguintes, usa o cache local (pasta cache/).
"""

import os
import pickle
import numpy as np
from datasets import load_dataset
from sentence_transformers import SentenceTransformer

CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "fiqa_embeddings.pkl")

# Limite de exemplos do dataset a indexar (ajuste conforme sua máquina;
# o dataset completo tem milhares de pares pergunta-resposta)
MAX_DOCS = 2000


class KnowledgeBase:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")  # leve e roda bem em CPU
        self.questions = []
        self.answers = []
        self.embeddings = None
        self._load_or_build()

    def _load_or_build(self):
        os.makedirs(CACHE_DIR, exist_ok=True)

        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "rb") as f:
                data = pickle.load(f)
            self.questions = data["questions"]
            self.answers = data["answers"]
            self.embeddings = data["embeddings"]
            return

        # Baixa o dataset do Hugging Face
        dataset = load_dataset(
            "bilalRahib/fiqa-personal-finance-dataset", split="train"
        )
        dataset = dataset.select(range(min(MAX_DOCS, len(dataset))))

        # Schema real do dataset: colunas 'input' (pergunta) e 'output' (resposta)
        self.questions = list(dataset["input"])
        self.answers = list(dataset["output"])

        self.embeddings = self.model.encode(
            self.questions, show_progress_bar=True, convert_to_numpy=True
        )

        with open(CACHE_FILE, "wb") as f:
            pickle.dump(
                {
                    "questions": self.questions,
                    "answers": self.answers,
                    "embeddings": self.embeddings,
                },
                f,
            )

    def search(self, query: str, top_k: int = 3):
        """Retorna os top_k pares (pergunta, resposta) mais similares à query."""
        query_emb = self.model.encode([query], convert_to_numpy=True)[0]

        # similaridade do cosseno
        sims = self.embeddings @ query_emb / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_emb) + 1e-8
        )
        top_idx = np.argsort(sims)[::-1][:top_k]

        return [
            {
                "question": self.questions[i],
                "answer": self.answers[i],
                "score": float(sims[i]),
            }
            for i in top_idx
        ]

    def build_context(self, query: str, top_k: int = 2) -> str:
        """Monta um bloco de texto pronto para incluir no prompt."""
        results = self.search(query, top_k=top_k)
        blocos = []
        for r in results:
            blocos.append(f"P: {r['question']}\nR: {r['answer']}")
        return "\n\n".join(blocos)
