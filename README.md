

# PDF Chat API

The PDF Chat API is a sophisticated backend application built using FastAPI that enables users to interact with PDF documents via a chat interface. This project leverages natural language processing (NLP) and advanced text extraction techniques to allow users to ask questions and receive answers based on the content of uploaded PDFs.

## Key Features

- **Retrieval-Augmented Generation (RAG) with Gemini**: This project utilizes the RAG approach combined with Gemini, which supports a 1 Million context size. RAG dynamically retrieves and incorporates relevant information from the PDFs, enhancing the accuracy and relevance of the responses while efficiently managing the context size.
- **ChromaDB**: The project integrates with ChromaDB, a high-performance vector database that facilitates efficient storage and retrieval of document embeddings, enabling rapid and accurate information retrieval.
- **LangChain**: LangChain is used to cache LLM responses and managing prompt templates.


## Installation

To set up and run the PDF Chat API locally, follow these steps:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/mertyatir/pdf-chat-api.git
   cd pdf-chat-api/
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Download and set up PostgreSQL**:
   - Download PostgreSQL from [here](https://www.postgresql.org/download/).
   - Set up PostgreSQL:
     ```bash
     sudo -i -u postgres
     psql
     CREATE USER myuser WITH PASSWORD 'mypassword';
     CREATE DATABASE pdf_chat_db OWNER myuser;
     GRANT ALL PRIVILEGES ON DATABASE pdf_chat_db TO myuser;
     \q
     exit
     ```

5. **Run the tests**:
   ```bash
   pytest
   ```

6. **Start the FastAPI development server**:
   ```bash
   fastapi dev app/main.py
   ```

7. **Access the API documentation**:
   - Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in your browser to view the API endpoint documentation.

## API Usage



### Upload a PDF

To upload a PDF, use the following `curl` command:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/v1/pdf/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@eg14_cats_and_people.pdf;type=application/pdf'
```

**Response**:

```json
{
  "pdf_id": "<pdf_id>"
}
```

### Query the PDF

To query the PDF you just uploaded, use the following `curl` command, replacing `<pdf_id>` with the actual PDF ID from the upload response:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/v1/chat/<pdf_id>/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "message": "Whats this PDF about?"
}'
```

**Response**:

```json
{
  "response": "This PDF is about how to care for a cat. It includes information on the following topics:\n\n* The basics of cat care, such as feeding, grooming, and housing\n* Common health problems in cats\n* How to socialize a cat\n* How to deal with feral cats\n* How to find a cat to adopt\n* How to get involved with Cats Protection, a UK-based cat welfare organization"
}
```


### Source PDF

The PDF used in this example can be found at: [EG14 Cats and People](https://www.cats.org.uk/media/1025/eg14_cats_and_people.pdf)






## Environment Variables

Create a `.env` file in the root directory of your project with the following content:

```env
GEMINI_API_KEY=<your-gemini-api-key>  # Get from https://ai.google.dev/aistudio
DATABASE_URL=postgresql+asyncpg://myuser:mypassword@localhost:5432/pdf_chat_db
PYTHONPATH=.
```

## Common Problems and Solutions

### Problem 1: Is using the Gemini 1.5 Flash that has 1 Million context size enough, or is Retrieval-Augmented Generation (RAG) a better approach?

**Solution**:  
RAG is generally a better approach for handling large datasets and specific information retrieval tasks, as it can dynamically fetch and utilize relevant information, reducing the burden on the model's context size.

### Problem 2: Having 1 Million context size is great, but output tokens are limited to 8196. How would you handle queries that have more than 8196 tokens?

**Solution**:
- **Chunking**: Split the input into smaller chunks that fit within the token limit and process each chunk separately.

### Problem 3: Writing unit tests is great for ensuring the app works just fine, but how would you evaluate the performance of the Large Language Model?

**Solution**:
- **Benchmarking**: Use standard benchmarks like GLUE, SQuAD, etc.
- **Human Evaluation**: Conduct human evaluations to assess the quality of the model's outputs.
- **AI Evaluating AI**: Train another model on human evaluations to predict the quality of the generated text. This can provide an automated way to evaluate the model's performance.







