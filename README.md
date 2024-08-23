# pdf-chat-api

The PDF Chat API is a sophisticated backend application built using FastAPI that enables users to interact with PDF documents via a chat interface. This project leverages natural language processing (NLP) and advanced text extraction techniques to allow users to ask questions and receive answers based on the content of uploaded PDFs.

Problem 1: Is using the Gemini 1.5 Flash that has 1 Million context size enough or Retrieval-Augmented Generation (RAG) is a better approach?

RAG is generally a better approach for handling large datasets and specific information retrieval tasks, as it can dynamically fetch and utilize relevant information, reducing the burden on the model's context size.

Problem 2: Having 1 Million context size is great but output tokens are limited to 8196, how would you handle queries that have more than 8196 tokens?

Solution:

Chunking: Split the input into smaller chunks that fit within the token limit and process each chunk separately.

Problem 3: Writing unit tests are great for ensuring the app works just fine, but how would you evaluate the performance of the Large Language Model?

Benchmarking: (e.g., GLUE, SQuAD, etc.)..
Human Evaluation: Conduct human evaluations to assess the quality of the model's outputs.
AI evaluating AI: Train another model on human evaluations to predict the quality of the generated text. This can provide an automated way to evaluate the model's performance.
