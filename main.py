from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import List, Dict, Any, Tuple

app = FastAPI()

# Create an SQLAlchemy engine
engine = create_engine('sqlite:///./data/hot_data.db')

# Create a Session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

categories = ["all", "neutral", "positive", "negative"]
from typing import List, Dict, Optional

@app.get("/word_freq")
def word_freq(
	limit: int = 50,
	label: str = Query("all", enum=categories, description="Label to filter by")
) -> List[Dict[str, Any]]:
	"""
	Get word frequencies.

	Args:
	limit (int): Number of words to return.
	label (str): Label to filter the words by.

	Returns:
	List[Dict[str, Any]]: List of words with frequencies.
	"""
	freq_column = f"{label}_freq"
	word_query = create_word_query(freq_column, limit)
	return fetch_word_data(word_query)

@app.get("/detailed/{word}")
def detailed_word_data(
	word: str,
	limit: int = 10,
) -> Dict[str, Any]:
	"""
	Get example sentences for a given word.

	Args:
	word (str): Word to get data for.
	limit (int): Number of example sentences to return.

	Returns:
	Dict[str, Any]: Dictionary containing word data and example sentences.
	"""
	with SessionLocal() as session:
		try:
			word_data = {}
			word_data["examples"] = fetch_example_sentences(session, word, limit)
			print("word_data", word_data)
			return word_data
		except Exception as e:
			# Log the exception or handle it as needed
			print(f"An error occurred: {e}")
			raise HTTPException(status_code=500, detail="Internal server error")


def create_word_query(freq_column: str, limit: int) -> str:
	"""Create SQL query to fetch words and their frequencies."""
	return f"""
	SELECT `index`, `{freq_column}`
	FROM words
	WHERE `{freq_column}` IS NOT NULL
	ORDER BY `{freq_column}` DESC
	LIMIT {limit}
	"""

def fetch_word_data(query: str) -> List[Dict[str, Any]]:
	"""Fetch words from the database."""
	outputs = []
	with SessionLocal() as session:
		try:
			words = session.execute(text(query)).fetchall()
			for word, freq in words:
				outputs.append({"word": word, "frequency": freq})
		except Exception as e:
			# Log the exception or handle it as needed
			print(f"An error occurred: {e}")
	return outputs

def fetch_example_sentences(session, word: str, limit: int) -> List[Dict[str, Any]]:
	"""Fetch example sentences for a given word."""
	query = text(f"""
	SELECT *
	FROM sentences
	WHERE text LIKE '%{word}%'
	LIMIT {limit}
	""")
	try:
		sentences = session.execute(query).fetchall()
		return [format_sentence_data(sentence) for sentence in sentences]
	except Exception as e:
		# Log the exception or handle it as needed
		print(f"Error fetching sentences: {e}")
		return []

def format_sentence_data(sentence: Tuple) -> Dict[str, Any]:
	"""Format sentence data into a dictionary."""
	# Assuming the sentence tuple contains id, text, and other fields as needed
	#id	emotion_label	emotion_score	text label
	return {
		"id": sentence[0],
		"emotion_label": sentence[1],
		"emotion_score": sentence[2],
		"text": sentence[3],
		"label": sentence[4]
	}
