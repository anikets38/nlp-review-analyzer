from flask import Flask, render_template, jsonify
import pandas as pd
import os
from collections import Counter
import json
from functools import lru_cache

app = Flask(__name__)

# Get the current directory path (where CSV files are located)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cache for data loading - prevents reloading CSV files on every request
_data_cache = {}
_cache_initialized = False

@lru_cache(maxsize=1)
def load_data():
    """Load all CSV data files with caching"""
    global _data_cache, _cache_initialized
    
    if _cache_initialized:
        return _data_cache
    
    data = {}
    
    # Load main reviews
    reviews_file = os.path.join(BASE_DIR, "salicylic_lha_cleanser_reviews.csv")
    if os.path.exists(reviews_file):
        data['reviews'] = pd.read_csv(reviews_file, encoding='utf-8')
    
    # Load cleaned reviews
    cleaned_file = os.path.join(BASE_DIR, "salicylic_lha_cleanser_reviews_cleaned.csv")
    if os.path.exists(cleaned_file):
        data['cleaned'] = pd.read_csv(cleaned_file, encoding='utf-8')
    
    # Load sentiment analysis
    sentiment_file = os.path.join(BASE_DIR, "salicylic_lha_cleanser_spacy_sentiment.csv")
    if os.path.exists(sentiment_file):
        data['sentiment'] = pd.read_csv(sentiment_file, encoding='utf-8')
    else:
        # Fallback: use cleaned data and create basic sentiment if needed
        print(f"⚠️ Sentiment file not found at: {sentiment_file}")
        print("Using cleaned data as fallback...")
        if 'cleaned' in data:
            # Create placeholder sentiment data from cleaned reviews
            sentiment_df = data['cleaned'][['S.No', 'Name', 'cleaned_review', 'Rating']].copy()
            # Handle NaN values in cleaned_review
            sentiment_df['cleaned_review'] = sentiment_df['cleaned_review'].fillna('No review text available')
            # Simple sentiment based on rating
            sentiment_df['sentiment_score'] = (sentiment_df['Rating'].astype(float) - 3) / 2
            sentiment_df['sentiment_label'] = sentiment_df['Rating'].astype(float).apply(
                lambda x: 'positive' if x >= 4 else ('negative' if x <= 2 else 'neutral')
            )
            data['sentiment'] = sentiment_df
            print("✅ Created fallback sentiment data from ratings")
    
    # Load Q&A summary
    qa_file = os.path.join(BASE_DIR, "salicylic_cleanser_QA_summary.csv")
    if os.path.exists(qa_file):
        data['qa'] = pd.read_csv(qa_file, encoding='utf-8')
    
    # Load review summary
    summary_file = os.path.join(BASE_DIR, "review_summary_similarity_index.csv")
    if os.path.exists(summary_file):
        data['summary'] = pd.read_csv(summary_file, encoding='utf-8')
    
    _data_cache = data
    _cache_initialized = True
    
    return data

@lru_cache(maxsize=1)
def get_statistics(data_key='stats'):
    """Calculate key statistics with caching"""
    data = load_data()
    stats = {}
    
    if 'reviews' in data:
        stats['total_reviews'] = len(data['reviews'])
        stats['avg_rating'] = round(data['reviews']['Rating'].astype(float).mean(), 2)
    
    if 'sentiment' in data:
        sentiment_counts = data['sentiment']['sentiment_label'].value_counts()
        total = len(data['sentiment'])
        stats['positive_percent'] = round((sentiment_counts.get('positive', 0) / total) * 100, 1)
        stats['negative_percent'] = round((sentiment_counts.get('negative', 0) / total) * 100, 1)
        stats['neutral_percent'] = round((sentiment_counts.get('neutral', 0) / total) * 100, 1)
        stats['sentiment_distribution'] = sentiment_counts.to_dict()
    
    return stats

@app.route('/')
def index():
    """Home page with overview"""
    stats = get_statistics()
    return render_template('index.html', stats=stats)

@app.route('/reviews')
def reviews():
    """Reviews page showing all reviews"""
    data = load_data()
    reviews_data = data.get('reviews', pd.DataFrame()).to_dict('records')
    return render_template('reviews.html', reviews=reviews_data)

@app.route('/sentiment')
def sentiment():
    """Sentiment analysis page"""
    data = load_data()
    stats = get_statistics()
    
    # Get all reviews by sentiment
    if 'sentiment' in data and len(data['sentiment']) > 0:
        positive_reviews = data['sentiment'][data['sentiment']['sentiment_label'] == 'positive']
        negative_reviews = data['sentiment'][data['sentiment']['sentiment_label'] == 'negative']
        neutral_reviews = data['sentiment'][data['sentiment']['sentiment_label'] == 'neutral']
        
        return render_template('sentiment.html', 
                             stats=stats,
                             positive_reviews=positive_reviews.to_dict('records'),
                             negative_reviews=negative_reviews.to_dict('records'),
                             neutral_reviews=neutral_reviews.to_dict('records'))
    
    return render_template('sentiment.html', 
                         stats=stats,
                         positive_reviews=[],
                         negative_reviews=[],
                         neutral_reviews=[])

@app.route('/insights')
def insights():
    """Insights and Q&A page"""
    data = load_data()
    stats = get_statistics()
    
    qa_data = []
    if 'qa' in data:
        qa_data = data['qa'].to_dict('records')
    
    summary_data = []
    if 'summary' in data:
        summary_data = data['summary'].head(15).to_dict('records')
    
    return render_template('insights.html', qa=qa_data, summary=summary_data, stats=stats)

@app.route('/api/sentiment_data')
def sentiment_data():
    """API endpoint for sentiment chart data"""
    stats = get_statistics()
    
    return jsonify({
        'labels': ['Positive', 'Negative', 'Neutral'],
        'data': [
            stats.get('positive_percent', 0),
            stats.get('negative_percent', 0),
            stats.get('neutral_percent', 0)
        ],
        'colors': ['#10b981', '#ef4444', '#6b7280']
    })

@app.route('/api/rating_distribution')
def rating_distribution():
    """API endpoint for rating distribution"""
    data = load_data()
    
    if 'reviews' in data:
        ratings = data['reviews']['Rating'].astype(float)
        rating_counts = ratings.value_counts().sort_index()
        
        return jsonify({
            'labels': [str(int(r)) for r in rating_counts.index],
            'data': rating_counts.values.tolist()
        })
    
    return jsonify({'labels': [], 'data': []})

# Cache for top words computation
_top_words_cache = None

@app.route('/api/top_words')
def top_words():
    """API endpoint for top words/keywords"""
    global _top_words_cache
    
    if _top_words_cache is not None:
        return jsonify(_top_words_cache)
    
    data = load_data()
    
    if 'cleaned' in data and 'lemmatized_tokens' in data['cleaned'].columns:
        all_words = []
        for tokens in data['cleaned']['lemmatized_tokens'].dropna():
            if isinstance(tokens, str):
                # Parse the string representation of list
                words = tokens.strip("[]").replace("'", "").split(", ")
                all_words.extend([w.strip() for w in words if w.strip() and len(w.strip()) > 3])
        
        word_freq = Counter(all_words).most_common(20)
        
        result = {
            'labels': [w[0] for w in word_freq],
            'data': [w[1] for w in word_freq]
        }
        _top_words_cache = result
        return jsonify(result)
    
    return jsonify({'labels': [], 'data': []})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
