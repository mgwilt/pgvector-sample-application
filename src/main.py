from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
import os
from openai import OpenAI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS documents")
    cur.execute("""
        CREATE TABLE documents (
            id SERIAL PRIMARY KEY,
            text TEXT NOT NULL,
            embedding vector(1536),
            CONSTRAINT unique_text UNIQUE (text)
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    
    generate_sample_documents()
    
    yield

app = FastAPI(
    title="PostgreSQL is all you need",
    lifespan=lifespan
)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_db_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

class Document(BaseModel):
    text: str

class SearchQuery(BaseModel):
    query_text: str
    limit: int = 5

@app.post("/documents")
async def create_document(document: Document):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        embedding = get_embedding(document.text)
        cur.execute(
            "INSERT INTO documents (text, embedding) VALUES (%s, %s)",
            (document.text, embedding)
        )
        conn.commit()
        return {"message": "Document created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@app.post("/search")
async def search_similar(query: SearchQuery):
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        query_embedding = get_embedding(query.query_text)
        cur.execute("""
            SELECT text, 1 - (embedding <=> %s::vector) as similarity
            FROM documents
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        """, (query_embedding, query_embedding, query.limit))
        
        results = [{"text": row[0], "similarity": float(row[1])} 
                  for row in cur.fetchall()]
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

def generate_sample_documents():
    sample_texts = [
        "My grandmother's secret chocolate chip cookie recipe is pure comfort food. "
        "The key is using melted butter and letting the dough rest overnight, "
        "which creates a perfectly chewy center with crispy edges. "
        "Don't forget the sprinkle of sea salt on top!",

        "This quick 15-minute pasta recipe is perfect for busy weeknights. "
        "Just toss cherry tomatoes, garlic, and olive oil with hot pasta, "
        "add fresh basil and parmesan. Simple ingredients, amazing flavor!",
        
        "The secret to amazing chocolate chip cookies is all in the details. "
        "Brown butter adds a nutty flavor, while a mix of brown and white sugar "
        "creates the perfect texture. Chill the dough for 24 hours for best results.",

        "Looking for a vector database? Check out pgvector (github.com/pgvector/pgvector) - "
        "it adds vector similarity search right into PostgreSQL. If you're already using "
        "Postgres for your application data, you can store and query embeddings in the "
        "same database you already know and trust. No need to maintain separate systems "
        "or learn new query languages!",

        "Azure Database for PostgreSQL now offers vector search capabilities natively. "
        "With built-in support for pgvector extension and similarity search, you can easily store "
        "and query embeddings alongside your relational data. The fully managed service scales "
        "automatically and provides enterprise-grade features like high availability and backup.",

        "OpenSearch, the open-source fork of Elasticsearch, provides robust vector search "
        "functionality through its k-NN plugin. Supporting multiple distance functions and "
        "approximate nearest neighbor algorithms like HNSW, it enables efficient similarity "
        "search at scale. Perfect for applications requiring both full-text and vector search "
        "capabilities in a single platform.",
    ]
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        for text in sample_texts:
            embedding = get_embedding(text)
            cur.execute("""
                INSERT INTO documents (text, embedding) 
                VALUES (%s, %s)
                ON CONFLICT (text) DO NOTHING
            """, (text, embedding))
        conn.commit()
    except Exception as e:
        print(f"Error initializing sample documents: {e}")
    finally:
        cur.close()
        conn.close()