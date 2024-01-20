from fastapi import FastAPI, HTTPException,  Query
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pandas as pd
from typing import List, Dict, Any

app = FastAPI()

hot_df = pd.read_csv("./data/hot_results_20240113231450.csv")

def get_word_frequencies(text_data):
    # Initialize the CountVectorizer
    vectorizer = CountVectorizer(stop_words='english')

    word_count = vectorizer.fit_transform(text_data)

    sum_words = word_count.sum(axis=0)
    word_freq = [(word, int(sum_words[0, idx])) for word, idx in vectorizer.vocabulary_.items()]
    word_freq = sorted(word_freq, key=lambda x: x[1], reverse=True)

    word_freq = [{"word": word, "count": count} for word, count in word_freq]

    return word_freq

labels = ['neutral', 'surprise', 'sadness', 'joy', 'fear', 'disgust', 'anger']
label_word_freq = {}
for label in labels:
    filtered_data = hot_df[hot_df['label'] == label]['text']
    word_freq = get_word_frequencies(filtered_data)
    label_word_freq[label] = word_freq

filtered_data = hot_df['text']
word_freq = get_word_frequencies(filtered_data)
label_word_freq['all'] = word_freq


@app.get("/word-frequency")
def word_frequency(
    limit: int = 50,
    examples_num: int = 5,
    label: str = Query("all", enum=labels + ["all"], description="Label to filter by"),
) -> List[Dict[str, Any]]:
    if label not in label_word_freq:
        return {"error": "Label not found"}

    words = label_word_freq[label][:limit]

    if examples_num > 0:
        for word_info in words:
            example_texts = hot_df[hot_df["text"].str.contains(word_info["word"], na=False)]["text"].tolist()[:examples_num]
            word_info["examples"] = example_texts if example_texts else ["No examples found"]

    return words