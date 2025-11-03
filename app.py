import http.server
import socketserver
import urllib.parse
import wikipedia
import requests
import json
from datetime import datetime

# Konfigurasi Wikipedia
wikipedia.set_lang("id")

class WikipediaHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        keyword = query_params.get('keyword', ['Python Programming'])[0]
        html_content = self.generate_html(keyword)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def get_long_article(self, keyword):
        """Ambil artikel yang lebih panjang dan detail"""
        try:
            # Method 1: Ambil summary dengan lebih banyak sentences
            summary = wikipedia.summary(keyword, sentences=30)  # 30 kalimat!
            return summary
            
        except:
            try:
                # Method 2: Ambil konten lengkap page
                page = wikipedia.page(keyword)
                full_content = page.content
                
                # Potong menjadi bagian yang lebih readable
                paragraphs = full_content.split('\n\n')
                meaningful_content = []
                char_count = 0
                
                for para in paragraphs:
                    if len(para) > 50:  # Hanya paragraph yang meaningful
                        meaningful_content.append(para)
                        char_count += len(para)
                        if char_count > 4000:  # Batasi total karakter
                            break
                
                return '\n\n'.join(meaningful_content)
                
            except:
                return f"Tidak dapat mengambil konten panjang untuk '{keyword}'"
    
    def get_wikipedia_images(self, keyword, limit=6):
        """Ambil gambar dari Wikipedia untuk sidebar"""
        images = []
        try:
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&generator=search&gsrsearch={keyword}&gsrnamespace=6&gsrlimit={limit}&prop=imageinfo&iiprop=url&iiurlwidth=200&format=json&origin=*"
            
            response = requests.get(search_url)
            data = response.json()
            
            if 'query' in data:
                for page_id, page_data in data['query']['pages'].items():
                    if 'imageinfo' in page_data:
                        image_info = page_data['imageinfo'][0]
                        images.append({
                            'title': page_data['title'].replace('File:', ''),
                            'url': image_info['thumburl'],
                            'description': f"Gambar {keyword} dari Wikipedia"
                        })
        except:
            # Fallback ke mock images
            images = self.generate_mock_images(keyword, limit)
        
        return images
    
    def generate_mock_images(self, keyword, count):
        """Generate mock images untuk demo"""
        images = []
        for i in range(count):
            images.append({
                'title': f"{keyword} image {i+1}",
                'url': f"https://picsum.photos/300/200?random={i}",
                'description': f"Gambar {keyword} dari koleksi Wikipedia"
            })
        return images
    
    def generate_html(self, keyword):
        try:
            page = wikipedia.page(keyword)
            
            # AMBIL ARTIKEL PANJANG - 30 kalimat!
            summary = wikipedia.summary(keyword, sentences=30)
            
            # Ambil gambar terkait
            related_images = self.get_wikipedia_images(keyword, 4)
            
            # Ambil artikel terkait
            related_articles = []
            try:
                search_results = wikipedia.search(keyword, results=10)
                for title in search_results:
                    try:
                        if title.lower() != keyword.lower() and len(related_articles) < 6:
                            related_summary = wikipedia.summary(title, sentences=2)
                            related_articles.append({
                                'title': title,
                                'summary': related_summary
                            })
                    except:
                        continue
            except:
                related_articles = []
            
        except wikipedia.exceptions.DisambiguationError as e:
            try:
                page = wikipedia.page(e.options[0])
                summary = wikipedia.summary(e.options[0], sentences=25)
                related_images = self.get_wikipedia_images(e.options[0], 4)
                related_articles = []
            except:
                summary = f"Terjadi kesalahan saat mengambil artikel untuk '{keyword}'. Silakan coba kata kunci lain."
                related_images = []
                related_articles = []
        except wikipedia.exceptions.PageError:
            summary = f"Tidak ditemukan artikel untuk '{keyword}'. Silakan coba kata kunci lain."
            related_images = []
            related_articles = []
        except Exception as e:
            summary = f"Terjadi kesalahan: {str(e)}"
            related_images = []
            related_articles = []

        # Format artikel dengan HTML yang lebih baik
        safe_summary = summary.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        safe_summary = safe_summary.replace('\n', '</p><p style=\"margin-bottom: 1.5rem;\">')
        safe_keyword = keyword.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

        # Hitung statistik
        word_count = len(summary.split())
        sentence_count = summary.count('.')
        read_time = max(1, word_count // 200)

        # Build HTML dengan desain modern
        html = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>WikiExplorer 2025 - {safe_keyword}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* COPY ALL CSS FROM THE BEAUTIFUL INDEX.HTML WE CREATED EARLIER */
        :root {{
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --secondary: #10b981;
            --accent: #f59e0b;
            --danger: #ef4444;
            --dark: #1f2937;
            --light: #f8fafc;
            --gray: #6b7280;
            --card-bg: #ffffff;
            --shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            --gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
            background: var(--light);
            color: var(--dark);
            line-height: 1.7;
        }}

        .container {{
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 2rem;
        }}

        .main-content {{
            background: var(--card-bg);
            border-radius: 1.5rem;
            padding: 2rem;
            box-shadow: var(--shadow);
        }}

        .article-header {{
            margin-bottom: 2rem;
        }}

        .article-title {{
            font-size: 2.5rem;
            font-weight: 800;
            color: var(--primary);
            margin-bottom: 1rem;
            line-height: 1.2;
        }}

        .article-stats {{
            display: flex;
            gap: 2rem;
            color: var(--gray);
            font-size: 0.9rem;
            margin-bottom: 1.5rem;
        }}

        .article-content {{
            font-size: 1.1rem;
            line-height: 1.8;
        }}

        .article-content p {{
            margin-bottom: 1.5rem;
            text-align: justify;
        }}

        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 2rem;
        }}

        .card {{
            background: var(--card-bg);
            border-radius: 1rem;
            padding: 1.5rem;
            box-shadow: var(--shadow);
        }}

        .card-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .image-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }}

        .image-card {{
            border-radius: 0.5rem;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}

        .image-card img {{
            width: 100%;
            height: 120px;
            object-fit: cover;
        }}

        .related-list {{
            list-style: none;
        }}

        .related-list li {{
            padding: 1rem;
            border-bottom: 1px solid rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .related-list li:hover {{
            background: var(--light);
            color: var(--primary);
        }}

        .search-container {{
            background: var(--gradient);
            padding: 2rem;
            border-radius: 1rem;
            margin-bottom: 2rem;
        }}

        .search-form {{
            display: flex;
            gap: 1rem;
        }}

        .search-input {{
            flex: 1;
            padding: 1rem;
            border: none;
            border-radius: 0.5rem;
            font-size: 1rem;
        }}

        .search-btn {{
            background: var(--accent);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-weight: 600;
        }}

        @media (max-width: 768px) {{
            .container {{
                grid-template-columns: 1fr;
                padding: 1rem;
            }}
            
            .article-title {{
                font-size: 2rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="search-container">
        <form method="GET" class="search-form">
            <input type="text" name="keyword" class="search-input" 
                   placeholder="Cari artikel Wikipedia..." value="{safe_keyword}">
            <button type="submit" class="search-btn">
                <i class="fas fa-search"></i> Cari
            </button>
        </form>
    </div>

    <div class="container">
        <main class="main-content">
            <div class="article-header">
                <h1 class="article-title">📚 {safe_keyword}</h1>
                <div class="article-stats">
                    <span><i class="fas fa-file-alt"></i> {sentence_count} kalimat</span>
                    <span><i class="fas fa-words"></i> {word_count} kata</span>
                    <span><i class="fas fa-clock"></i> {read_time} menit baca</span>
                </div>
            </div>

            <div class="article-content">
                <p>{safe_summary}</p>
            </div>
        </main>

        <aside class="sidebar">
            <!-- Related Images -->
            <div class="card">
                <h3 class="card-title"><i class="fas fa-images"></i> Gambar Terkait</h3>
                <div class="image-grid">
                    {"".join([f'''
                    <div class="image-card">
                        <img src="{img['url']}" alt="{img['title']}">
                    </div>
                    ''' for img in related_images])}
                </div>
            </div>

            <!-- Related Articles -->
            <div class="card">
                <h3 class="card-title"><i class="fas fa-link"></i> Artikel Terkait</h3>
                <ul class="related-list">
                    {"".join([f'''
                    <li onclick="window.location='?keyword={urllib.parse.quote(article['title'])}'">
                        <strong>{article['title']}</strong><br>
                        <small style="color: var(--gray);">{article['summary'][:80]}...</small>
                    </li>
                    ''' for article in related_articles])}
                </ul>
            </div>

            <!-- Quick Actions -->
            <div class="card">
                <h3 class="card-title"><i class="fas fa-bolt"></i> Akses Cepat</h3>
                <div style="display: grid; gap: 0.5rem;">
                    <button onclick="window.location='?keyword=Indonesia'" style="background: var(--primary); color: white; border: none; padding: 0.75rem; border-radius: 0.5rem; cursor: pointer;">
                        🇮🇩 Indonesia
                    </button>
                    <button onclick="window.location='?keyword=Teknologi'" style="background: var(--secondary); color: white; border: none; padding: 0.75rem; border-radius: 0.5rem; cursor: pointer;">
                        💻 Teknologi
                    </button>
                    <button onclick="window.location='?keyword=Sejarah'" style="background: var(--accent); color: white; border: none; padding: 0.75rem; border-radius: 0.5rem; cursor: pointer;">
                        📜 Sejarah
                    </button>
                </div>
            </div>
        </aside>
    </div>

    <script>
        // Tambah interactivity
        document.addEventListener('DOMContentLoaded', function() {{
            // Smooth scroll untuk related articles
            document.querySelectorAll('.related-list li').forEach(item => {{
                item.style.cursor = 'pointer';
            }});
        }});
    </script>
</body>
</html>"""
        
        return html

if __name__ == "__main__":
    PORT = 8000
    with socketserver.TCPServer(("", PORT), WikipediaHandler) as httpd:
        print(f"🚀 Server Python berjalan di http://localhost:{PORT}")
        print("📍 Contoh: http://localhost:8000/?keyword=Indonesia")
        print("📍 Contoh: http://localhost:8000/?keyword=Sejarah%20Indonesia")
        print("⏹️  Tekan Ctrl+C untuk menghentikan server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server dihentikan")
