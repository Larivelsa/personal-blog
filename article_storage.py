import json
import os
from datetime import datetime
import uuid

ARTICLES_DIR = 'articles'

def ensure_articles_dir():
    """Create articles directory if it doesn't exist"""
    if not os.path.exists(ARTICLES_DIR):
        os.makedirs(ARTICLES_DIR)

def generate_article_id(title):
    """Generate a unique ID for the article based on title and timestamp"""
    # Create a URL-friendly slug from title
    slug = title.lower().replace(' ', '-')
    slug = ''.join(c for c in slug if c.isalnum() or c == '-')
    # Add timestamp to ensure uniqueness
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    return f"{slug}-{timestamp}"

def save_article(title, content, publication_date):
    """Save an article as a JSON file. Returns the article ID."""
    ensure_articles_dir()
    
    article_id = generate_article_id(title)
    
    article_data = {
        'id': article_id,
        'title': title,
        'content': content,
        'publication_date': publication_date.isoformat() if hasattr(publication_date, 'isoformat') else str(publication_date),
        'created_at': datetime.now().isoformat()
    }
    
    filename = os.path.join(ARTICLES_DIR, f"{article_id}.json")
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(article_data, f, indent=2, ensure_ascii=False)
    
    return article_id

def get_article(article_id):
    """Retrieve a single article by ID. Returns None if not found."""
    filename = os.path.join(ARTICLES_DIR, f"{article_id}.json")
    
    if not os.path.exists(filename):
        return None
    
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_all_articles():
    """Retrieve all articles. Returns a list of articles sorted by publication date (newest first)."""
    ensure_articles_dir()
    
    articles = []
    
    for filename in os.listdir(ARTICLES_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(ARTICLES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                    articles.append(article)
            except (json.JSONDecodeError, IOError):
                # Skip corrupted files
                continue
    
    # Sort by publication date (newest first)
    articles.sort(key=lambda x: x.get('publication_date', ''), reverse=True)
    
    return articles

def update_article(article_id, title, content, publication_date):
    """Update an existing article. Preserves the article ID and created_at timestamp.
    Returns True if successful, False if article doesn't exist."""
    filename = os.path.join(ARTICLES_DIR, f"{article_id}.json")
    
    if not os.path.exists(filename):
        return False
    
    # Load existing article to preserve created_at
    with open(filename, 'r', encoding='utf-8') as f:
        existing_article = json.load(f)
    
    # Update article data
    article_data = {
        'id': article_id,  # Preserve original ID
        'title': title,
        'content': content,
        'publication_date': publication_date.isoformat() if hasattr(publication_date, 'isoformat') else str(publication_date),
        'created_at': existing_article.get('created_at', datetime.now().isoformat()),  # Preserve original creation date
        'updated_at': datetime.now().isoformat()  # Add update timestamp
    }
    
    # Save updated article
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(article_data, f, indent=2, ensure_ascii=False)
    
    return True

def delete_article(article_id):
    """Delete an article by ID. Returns True if successful, False otherwise."""
    filename = os.path.join(ARTICLES_DIR, f"{article_id}.json")
    
    if os.path.exists(filename):
        os.remove(filename)
        return True
    return False

