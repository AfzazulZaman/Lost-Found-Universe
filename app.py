from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import json

# Initialize Flask application
app = Flask(__name__)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'lost_and_found_universe.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# Define Entry model
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    feeling = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Entry {self.id}: {self.feeling}>'


# Create the database tables
with app.app_context():
    db.create_all()

# List of predefined feelings for the dropdown
FEELINGS = [
    "bittersweet", "regret", "epic", "melancholy", "nostalgic",
    "hopeful", "curious", "wistful", "ethereal", "haunting"
]

# HTML template for the main page
BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lost & Found Universe</title>
    <style>
        /* CSS styling for the entire application */
        :root {
            --primary-color: #f8f0ff;
            --accent-color: #c4a9ff;
            --text-color: #414156;
            --shadow-color: rgba(156, 136, 255, 0.3);
            --highlight-color: #9c88ff;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e8eaec 100%);
            color: var(--text-color);
            line-height: 1.6;
            padding: 0;
            margin: 0;
            min-height: 100vh;
        }

        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 0;
        }

        header {
            text-align: center;
            margin-bottom: 3rem;
        }

        h1 {
            font-size: 3rem;
            font-weight: 300;
            color: var(--text-color);
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px var(--shadow-color);
        }

        .tagline {
            font-size: 1.2rem;
            color: #6c6c84;
            font-style: italic;
            margin-bottom: 2rem;
        }

        .submission-form {
            background: rgba(255, 255, 255, 0.9);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 8px 32px var(--shadow-color);
            backdrop-filter: blur(8px);
            margin-bottom: 3rem;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: var(--text-color);
        }

        textarea {
            width: 100%;
            padding: 1rem;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.8);
            font-family: inherit;
            font-size: 1rem;
            resize: vertical;
            min-height: 120px;
            transition: border-color 0.3s, box-shadow 0.3s;
        }

        textarea:focus {
            outline: none;
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px var(--shadow-color);
        }

        select {
            width: 100%;
            padding: 0.75rem;
            border: 1px solid #ddd;
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.8);
            font-family: inherit;
            font-size: 1rem;
            color: var(--text-color);
        }

        button {
            background: var(--highlight-color);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            transition: background 0.3s, transform 0.2s;
            box-shadow: 0 4px 12px var(--shadow-color);
        }

        button:hover {
            background: #8a71eb;
            transform: translateY(-2px);
        }

        button:active {
            transform: translateY(0);
        }

        .filter-container {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 2rem;
            justify-content: center;
        }

        .filter-btn {
            background: transparent;
            border: 1px solid var(--accent-color);
            color: var(--text-color);
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .filter-btn:hover, .filter-btn.active {
            background: var(--accent-color);
            color: white;
            box-shadow: 0 2px 8px var(--shadow-color);
        }

        .entries-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 2rem;
        }

        .entry-card {
            background: rgba(255, 255, 255, 0.85);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 6px 24px var(--shadow-color);
            backdrop-filter: blur(5px);
            transition: transform 0.3s, box-shadow 0.3s;
            position: relative;
            overflow: hidden;
        }

        .entry-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 32px var(--shadow-color);
        }

        .entry-content {
            margin-bottom: 1rem;
            font-size: 1.1rem;
            line-height: 1.7;
            white-space: pre-wrap;
        }

        .entry-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
            color: #888;
        }

        .feeling-badge {
            background: var(--accent-color);
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            letter-spacing: 0.5px;
            text-transform: lowercase;
        }

        .timestamp {
            font-style: italic;
            opacity: 0.8;
        }

        @media (max-width: 768px) {
            .entries-grid {
                grid-template-columns: 1fr;
            }

            .submission-form {
                padding: 1.5rem;
            }

            h1 {
                font-size: 2.5rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Lost & Found Universe</h1>
            <p class="tagline">A digital diary for your lost dreams, thoughts, and moments</p>
        </header>

        <div class="submission-form">
            <form id="entryForm" method="post" action="/">
                <div class="form-group">
                    <label for="content">Share what's been lost...</label>
                    <textarea id="content" name="content" placeholder="Type your lost thought, dream, or moment here..."></textarea>
                </div>
                <div class="form-group">
                    <label for="feeling">How does it feel?</label>
                    <select id="feeling" name="feeling">
                        {% for feeling in feelings %}
                            <option value="{{ feeling }}">{{ feeling }}</option>
                        {% endfor %}
                    </select>
                </div>
                <button type="submit">Release to the Universe</button>
            </form>
        </div>

        <div class="filter-container">
            <a href="{{ url_for('index') }}" class="filter-btn {% if not current_feeling %}active{% endif %}">all</a>
            {% for feeling in distinct_feelings %}
                <a href="{{ url_for('filter_entries', feeling=feeling) }}" 
                   class="filter-btn {% if feeling == current_feeling %}active{% endif %}">
                   {{ feeling }}
                </a>
            {% endfor %}
        </div>

        <div class="entries-grid">
            {% for entry in entries %}
                <div class="entry-card" data-feeling="{{ entry.feeling }}">
                    <div class="entry-content">{{ entry.content }}</div>
                    <div class="entry-meta">
                        <span class="feeling-badge">{{ entry.feeling }}</span>
                        <span class="timestamp">{{ entry.timestamp.strftime('%b %d, %Y • %H:%M') }}</span>
                    </div>
                </div>
            {% endfor %}
        </div>
    </div>

    <script>
        // Client-side form validation
        document.getElementById('entryForm').addEventListener('submit', function(e) {
            const content = document.getElementById('content').value.trim();
            if (!content) {
                e.preventDefault();
                alert('Please share something before releasing it to the universe.');
                return false;
            }
            return true;
        });

        // Optional feature: Client-side filtering without reload
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function(e) {
                // We only handle clicks on buttons that aren't links to server routes
                if (this.getAttribute('href') && this.getAttribute('href').includes('filter')) {
                    return; // Let the link handle it
                }

                e.preventDefault();
                const feeling = this.textContent.trim();

                // Update active button state
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                // Filter the cards
                const cards = document.querySelectorAll('.entry-card');
                cards.forEach(card => {
                    if (feeling === 'all' || card.dataset.feeling === feeling) {
                        card.style.display = 'block';
                    } else {
                        card.style.display = 'none';
                    }
                });
            });
        });
    </script>
</body>
</html>
'''


# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        content = request.form.get('content')
        feeling = request.form.get('feeling')

        # Validate and create new entry
        if content and feeling:
            new_entry = Entry(content=content, feeling=feeling)
            db.session.add(new_entry)
            db.session.commit()

        # Redirect to homepage after processing
        return redirect(url_for('index'))

    # For GET requests, fetch and display entries
    entries = Entry.query.order_by(Entry.timestamp.desc()).all()
    distinct_feelings = db.session.query(Entry.feeling).distinct().order_by(Entry.feeling).all()
    distinct_feelings = [feeling[0] for feeling in distinct_feelings]  # Extract string values

    # Render the template with data
    return render_template_string(
        BASE_TEMPLATE,
        entries=entries,
        feelings=FEELINGS,
        distinct_feelings=distinct_feelings,
        current_feeling=None
    )


@app.route('/filter/<feeling>', methods=['GET'])
def filter_entries(feeling):
    # Filter entries by feeling
    entries = Entry.query.filter_by(feeling=feeling).order_by(Entry.timestamp.desc()).all()

    # Get list of distinct feelings for the filter menu
    distinct_feelings = db.session.query(Entry.feeling).distinct().order_by(Entry.feeling).all()
    distinct_feelings = [f[0] for f in distinct_feelings]

    # Render the template with filtered data
    return render_template_string(
        BASE_TEMPLATE,
        entries=entries,
        feelings=FEELINGS,
        distinct_feelings=distinct_feelings,
        current_feeling=feeling
    )


# Run the application
if __name__ == '__main__':
    app.run(debug=True, port=5000)