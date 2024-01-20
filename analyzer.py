import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

class TextAnalyzer:
	def __init__(self, data_file):
		self.data = pd.read_csv(data_file)
		self.labels = ['neutral', 'surprise', 'sadness', 'joy', 'fear', 'disgust', 'anger']
		self.categories = {
			'all': self.labels,
			'neutral': ['neutral'],
			'negative': ['sadness', 'fear', 'disgust', 'anger'],
			'positive': ['joy', 'surprise']
		}
		self.label_word_freq = {}
		self.label_word_tfidf = {}

	def get_word_frequencies(self, text_data):
		vectorizer = CountVectorizer(stop_words='english')
		word_count = vectorizer.fit_transform(text_data)
		sum_words = word_count.sum(axis=0)
		word_freq = [(word, int(sum_words[0, idx])) for word, idx in vectorizer.vocabulary_.items()]
		return sorted(word_freq, key=lambda x: x[1], reverse=True)

	def get_tfidf_word_frequencies(self, text_data):
		vectorizer = TfidfVectorizer(stop_words='english')
		tfidf_matrix = vectorizer.fit_transform(text_data)
		feature_names = vectorizer.get_feature_names_out()
		dense = tfidf_matrix.todense()
		denselist = dense.tolist()
		df = pd.DataFrame(denselist, columns=feature_names)
		return df.mean(axis=0).sort_values(ascending=False).reset_index().rename(columns={0: 'score'})

	def analyze(self):
		for key in self.categories.keys():
			filtered_data = self.data[self.data['label'].isin(self.categories[key])]['text']
			self.label_word_freq[key] = self.get_word_frequencies(filtered_data)
			self.label_word_tfidf[key] = self.get_tfidf_word_frequencies(filtered_data)

		print("Done loading data")

if __name__ == "__main__":
	text_analyzer = TextAnalyzer("data/hot_results.csv")
	text_analyzer.analyze()

	print("Word frequencies:")
	print(text_analyzer.label_word_freq)
	
