# AI-powered Query Answering with Google Generative AI and DuckDuckGo Search

This project implements an AI-powered query answering system using **Google Generative AI (Gemini model)**. It integrates search results from **DuckDuckGo** and processes URLs to extract **video thumbnails** and metadata.

---

## Features
- **Search DuckDuckGo** for query results.
- Extract video information (e.g., YouTube and Vimeo thumbnails).
- Retrieve **Open Graph (OG) images** from non-video URLs.
- Uses **Google Generative AI (Gemini)** for generating answers based on search results.
- **Concurrent processing** for fast search result handling.

---

## Prerequisites

1. **Python** installed on your machine.
2. Create a **Google Generative AI API key**:
   - Visit [Google Cloud](https://cloud.google.com) and get an API key for Gemini models.

3. Install the required Python packages:
   ```bash
   pip install google-generativeai python-dotenv duckduckgo-search beautifulsoup4 requests
