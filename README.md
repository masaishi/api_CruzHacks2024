# Sitegeist API

[parent(Sitegeist)](https://github.com/masaishi/Sitegeist)

## Project Overview

This FastAPI project is designed to analyze and interact with textual data, focusing on Natural Language Processing (NLP) and sentiment analysis. It utilizes OpenAI's GPT-3.5 to generate conversational responses and conducts various analyses on word frequencies and example sentences from a dataset.

## Documentation

**Explore the full API documentation here: [API Documentation](https://api-cruzhacks2024.onrender.com/docs)**

This comprehensive guide provides detailed information on all API endpoints, their usage, and examples.

## Features

- **ChatGPT Integration**: Utilizes OpenAI's GPT-3.5 model to generate conversational responses based on user input.
- **Word Frequency Analysis**: Retrieves word frequencies, filtered by sentiment categories like neutral, positive, and negative.
- **Example Sentences**: Provides example sentences for a given word, helping in understanding the context of its usage.
- **Comments and Sentences Data Retrieval**: Fetches data for specific comments or sentences based on their IDs.
- **Word Data Analysis**: Offers detailed analysis of words including frequency and TF-IDF values across different sentiment categories.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- FastAPI
- Uvicorn (for running the server)
- SQLAlchemy
- OpenAI API key

### Installation

1. Clone the repository to your local machine.
2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set your OpenAI API key as an environment variable:

   ```bash
   export OPENAI_API_KEY='your_api_key_here'
   ```

### Running the Server

Run the server using Uvicorn:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`.

## Deployment

This project is configured for automatic deployment. Whenever you commit to the `main` branch, the application will automatically deploy, ensuring that the latest version is always live.

## Database Configuration

The project uses an SQLite database to store and retrieve word, sentence, and comment data. SQLAlchemy is used for database interactions.

## CORS Configuration

Cross-Origin Resource Sharing (CORS) is configured to allow requests from specific origins including local development environments and deployed frontend applications.
