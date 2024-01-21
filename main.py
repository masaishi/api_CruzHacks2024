import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import openai
from typing import List, Dict, Any, Tuple

openai.api_key = os.environ.get('OPENAI_API_KEY')

app = FastAPI()
origins = [
	"http://localhost",
	"http://localhost:3000",
	"https://cruzhacks2024.netlify.app",
	"https://web-cruz-hacks2024.vercel.app",
	"https://web-cruz-hacks2024.vercel.app/"
]
app.add_middleware(
	CORSMiddleware,
	allow_origins=origins,
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


# Create an SQLAlchemy engine
engine = create_engine('sqlite:///./data/hot_data.db')

# Create a Session local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

categories = ["all", "neutral", "positive", "negative"]

@app.get("/chatgpt")
def chatgpt(
	input: str,
	prompt: str = "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."
) -> Dict[str, Any]:
	"""
	Get chatgpt response.

	Args:
	prompt (str): Prompt to get response for.

	Returns:
	Dict[str, Any]: Dictionary containing chatgpt response.
	"""
	completion = openai.ChatCompletion.create(
		model="gpt-3.5-turbo",
		messages=[
			{"role": "system", "content": prompt},
			{"role": "user", "content": input},
		]
	)
	return completion.choices[0]


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

@app.get("/examples/{word}")
def examples(
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
			response = {'examples': []}
			example_sentences = fetch_example_sentences(session, word, limit)
			comment_ids = [fetch_comment_from_sentence(session, sentence["id"]) for sentence in example_sentences]
			for comment_id in comment_ids:
				sentence_ids = fetch_sentences_from_comment(session, comment_id)
				comment = []
				for sentence_id in sentence_ids:
					comment.append(fetch_sentence_data(session, sentence_id))
				response['examples'].append(comment)
			return response
		except Exception as e:
			# Log the exception or handle it as needed
			print(f"An error occurred: {e}")
			raise HTTPException(status_code=500, detail="Internal server error")


def create_word_query(freq_column: str, limit: int) -> str:
	"""Create SQL query to fetch words and their frequencies."""
	return f"""
	SELECT *
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
			outputs = [format_word_data(word) for word in words]
		except Exception as e:
			# Log the exception or handle it as needed
			print(f"An error occurred: {e}")
	return outputs

def fetch_sentence_data(session, sentence_id: int) -> Dict[str, Any]:
	"""Fetch sentence data for a given sentence."""
	query = text(f"""
	SELECT *
	FROM sentences
	WHERE id = '{sentence_id}'
	""")
	try:
		sentence = session.execute(query).fetchone()
		return format_sentence_data(sentence)
	except Exception as e:
		# Log the exception or handle it as needed
		print(f"Error fetching sentence: {e}")
		return {}

def fetch_comment_from_sentence(session, sentence_id: int) -> Dict[str, Any]:
	"""Fetch comment data for a given sentence."""
	query = text(f"""
	SELECT comment_id
	FROM comment_sentences
	WHERE sentence_id = '{sentence_id}'
	""")
	try:
		comment = session.execute(query).fetchone()
		return comment[0]
	except Exception as e:
		# Log the exception or handle it as needed
		print(f"Error fetching comment: {e}")
		return {}

def fetch_sentences_from_comment(session, comment_id: int) -> List[Dict[str, Any]]:
	"""Fetch sentences for a given comment."""
	query = text(f"""
	SELECT sentence_id
	FROM comment_sentences
	WHERE comment_id = '{comment_id}'
	""")
	try:
		sentences = session.execute(query).fetchall()
		return [sentence[0] for sentence in sentences]
	except Exception as e:
		# Log the exception or handle it as needed
		print(f"Error fetching sentences: {e}")
		return []

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


def format_comment_data(comment: Tuple) -> Dict[str, Any]:
	"""Format comment data into a dictionary."""
	return {
		"id": comment[0],
		"post_id": comment[1],
		"created": comment[2],
		"text": comment[3],
		"label": comment[4]
	}

def format_sentence_data(sentence: Tuple) -> Dict[str, Any]:
	"""Format sentence data into a dictionary."""
	return {
		"id": sentence[0],
		"emotion_label": sentence[1],
		"emotion_score": sentence[2],
		"text": sentence[3],
		"label": sentence[4]
	}

def format_word_data(word: Tuple) -> Dict[str, Any]:
	"""Format word data into a dictionary."""
	return {
		"id": word[0],
		"word": word[1],
		"all_freq": word[2],
		"neutral_freq": word[3],
		"positive_freq": word[4],
		"negative_freq": word[5],
		"all_tfidf": word[6],
		"neutral_tfidf": word[7],
		"positive_tfidf": word[8],
		"negative_tfidf": word[9],
		"neutral_num": word[10],
		"positive_num": word[11],
		"negative_num": word[12],
	}

