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
	examples_limit: int = 5,
	label: str = Query("all", enum=categories, description="Label to filter by"),
) -> List[Dict[str, Any]]:
	freq_column = f"{label}_freq"

	# SQL query to retrieve words and their frequencies
	word_query = text(f"""
	SELECT `index`, `{freq_column}`
	FROM words
	WHERE `{freq_column}` IS NOT NULL
	ORDER BY `{freq_column}` DESC
	LIMIT {limit}
	""")

	# Prepare the output
	outputs = []

	with SessionLocal() as session:
		words = session.execute(word_query).fetchall()

		for i, (word, freq) in enumerate(words):
			# SQL query to retrieve example sentences for the word
			sentence_query = text(f"""
			SELECT *
			FROM sentences
			WHERE text LIKE '%{word}%'
			LIMIT {examples_limit}
			""")

			example_sentences = session.execute(sentence_query).fetchall()
			example_sentences = [sentence for sentence in example_sentences]
			examples = []
			for sentence in example_sentences:
				comment_sentence_query = text(f"""
				SELECT *
				FROM comment_sentences
				WHERE sentence_id = '{sentence.id}'
				""")
				comment_sentence = session.execute(comment_sentence_query).fetchone()
				
				sentences_query = text(f"""
				SELECT *
				FROM comment_sentences
				WHERE comment_id = '{comment_sentence.comment_id}'
				""")
				sentences = session.execute(sentences_query).fetchall()

				sentence_ids_str = ','.join(f"'{s[1]}'" for s in sentences)
				print(sentence_ids_str)
				sentences_query = text(f"""
				SELECT *
				FROM sentences
				WHERE id IN ({sentence_ids_str})
				ORDER BY 'order'
				""")
				sentences = session.execute(sentences_query).fetchall()
				
				#id	emotion_label	emotion_score	text label
				examples.append({
					"id": sentence[0],
					"emotion_label": sentence[1],
					"emotion_score": sentence[2],
					"text": sentence[3],
					"label": sentence[4],
				})
	
			outputs.append({
				"word": word,
				"frequency": freq,
				"examples": examples,
			})

			# Limit the number of words returned
			if i >= examples_limit - 1:
				break

	return outputs
