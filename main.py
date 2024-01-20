from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any

app = FastAPI()

# Create an SQLAlchemy engine
engine = create_engine('sqlite:///./data/hot_data.db')

# Create a Session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

categories = ["all", "neutral", "positive", "negative"]

@app.get("/word_freq")
def word_freq(
    limit: int = 50,
    examples_num: int = 5,
    label: str = Query("all", enum=categories, description="Label to filter by"),
) -> List[Dict[str, Any]]:
    freq_column = f"{label}_freq"

    # SQL query to retrieve words and their frequencies
    query = text(f"""
    SELECT `index`, `{freq_column}`
    FROM words
    WHERE `{freq_column}` IS NOT NULL
    ORDER BY `{freq_column}` DESC
    LIMIT {limit}
    """)

    # Execute the query using a session
    with SessionLocal() as session:
        results = session.execute(query).fetchall()

    # Prepare the output
    output = []
    for i, (word, freq) in enumerate(results):
        output.append({"word": word, "frequency": freq})
        # Limit the number of examples
        if i >= examples_num - 1:
            break

    return output
