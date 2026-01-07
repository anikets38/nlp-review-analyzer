# NLP Review Analysis Web Application

A beautiful, responsive web application for analyzing product reviews using Natural Language Processing.

## Features

- 📊 **Interactive Dashboard** - Visual overview of review statistics and sentiment
- 💬 **Review Browser** - Browse all customer reviews with ratings
- ❤️ **Sentiment Analysis** - Deep dive into positive/negative sentiment patterns
- 💡 **Insights & Q&A** - Actionable insights and auto-generated Q&A
- 📱 **Fully Responsive** - Works perfectly on desktop, tablet, and mobile
- 🎨 **Modern UI** - Beautiful glassmorphism design with smooth animations

## Installation

1. Navigate to the webapp directory:
```bash
cd webapp
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
webapp/
├── app.py                 # Flask application backend
├── requirements.txt       # Python dependencies
├── templates/            # HTML templates
│   ├── base.html        # Base template with navigation
│   ├── index.html       # Home page with dashboard
│   ├── reviews.html     # Reviews listing page
│   ├── sentiment.html   # Sentiment analysis page
│   └── insights.html    # Insights and Q&A page
└── static/              # Static assets (CSS, JS)
```

## Technologies Used

- **Backend**: Flask (Python)
- **Frontend**: HTML5, TailwindCSS
- **Charts**: Chart.js
- **Icons**: Font Awesome
- **Data Processing**: Pandas, NumPy

## Features Overview

### Dashboard (Home Page)
- Total reviews count
- Average rating
- Sentiment distribution (positive/negative/neutral %)
- Interactive charts (pie, bar, horizontal bar)
- Top keywords visualization
- Quick navigation cards

### Reviews Page
- All customer reviews with full text
- Star ratings display
- Review author and date
- Interactive hover effects
- Helpful/Share buttons

### Sentiment Analysis Page
- Sentiment distribution overview
- Interactive pie and bar charts
- Top positive reviews showcase
- Negative reviews for improvement areas
- Color-coded sentiment indicators

### Insights Page
- Auto-generated Q&A based on analysis
- Review summary clusters
- Key strengths and weaknesses
- Actionable recommendations
- Analysis summary

## API Endpoints

- `/` - Home dashboard
- `/reviews` - Reviews listing
- `/sentiment` - Sentiment analysis
- `/insights` - Insights and Q&A
- `/api/sentiment_data` - JSON: Sentiment distribution data
- `/api/rating_distribution` - JSON: Rating distribution data
- `/api/top_words` - JSON: Top keywords frequency

## Customization

### Changing Colors
Edit the gradient colors in `templates/base.html`:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Modifying Charts
Chart configurations can be found in the JavaScript sections of each template file.

## Notes

- The application reads data from CSV files in the parent directory
- Make sure all required CSV files are present before running
- The app runs on port 5000 by default (can be changed in app.py)

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## License

This project is part of an NLP Mini Project for educational purposes.
