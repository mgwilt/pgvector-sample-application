# PGVector Sample Application - PostgreSQL is all you need

This repository is inspired by one of many reddit posts with users asking which vector database to use. The answer is to use the solution that adds to your entire application and not to focus on new infrastructure for a single feature. If you're already using PostgresSQL, Redis, MongoDB, Cosmos, OpenSearch/ElasticSearch, or many other databases, chances are you don't need a new databse just for vector similarity search.

---

This is a sample application demonstrating how to use pgvector with PostgreSQL for vector similarity search. The application provides a REST API for storing and searching vector embeddings of text documents using OpenAI's text embeddings.

This sample uses OpenAI's `text-embedding-3-small` model for embeddings to keep things simple, but you could also use a local model or a different provider.

## Features

- Store text documents with automatically generated embeddings

- Perform semantic similarity search using cosine similarity


- Built-in sample documents for testing
- Containerized deployment with Docker Compose
- Uses OpenAI's text-embedding-3-small model for embeddings

## Prerequisites

- Docker
- Docker Compose
- OpenAI API Key

## Setup

1. Clone this repository
2. Set your OpenAI API key in the environment:
   ```bash
   # For Linux/macOS
   export OPENAI_API_KEY=your_api_key_here
   
   # For Windows PowerShell
   $env:OPENAI_API_KEY = "your_api_key_here"
   ```
3. Run the application:
   ```bash
   docker-compose up --build
   ```

The application will be available at:
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

- PostgreSQL: localhost:5432

## API Endpoints

### Store a Document
```bash
POST /documents
{
    "text": "Your document text"
}
```
The API will automatically generate embeddings using OpenAI's text-embedding-3-small model.

### Search Similar Documents
```bash
POST /search
{
    "query_text": "Your search text",
    "limit": 5
}
```
Returns the most similar documents based on cosine similarity of their embeddings.


## Example: 
### Search for `"Which vector database should I use with PostgreSQL?"`

Relevant results:
```json
[
    {
        "text": "Looking for a vector database? Check out pgvector (github.com/pgvector/pgvector) - it adds vector similarity search right into PostgreSQL. If you're already using Postgres for your application data, you can store and query embeddings in the same database you already know and trust. No need to maintain separate systems or learn new query languages!",
        "similarity": 0.7779749168172542
    },
    {
        "text": "Azure Database for PostgreSQL now offers vector search capabilities natively. With built-in support for pgvector extension and similarity search, you can easily store and query embeddings alongside your relational data. The fully managed service scales automatically and provides enterprise-grade features like high availability and backup.",
        "similarity": 0.6984344900587518
    }
]
```

Less relevant results:
```json
[
    {
        "text": "This quick 15-minute pasta recipe is perfect for busy weeknights. Just toss cherry tomatoes, garlic, and olive oil with hot pasta, add fresh basil and parmesan. Simple ingredients, amazing flavor!",
        "similarity": 0.011121310830556008
    },
    {
        "text": "My grandmother's secret chocolate chip cookie recipe is pure comfort food. The key is using melted butter and letting the dough rest overnight, which creates a perfectly chewy center with crispy edges.",
        "similarity": -0.0092456838193129
    }
]
```

