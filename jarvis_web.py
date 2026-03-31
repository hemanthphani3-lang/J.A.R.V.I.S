import requests
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_url(self, url):
        """Quickly scrape a URL using BeautifulSoup."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # Extract text and clean it up
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                return text[:2000] # Limit output
            return None
        except Exception as e:
            print(f"[Scraper Error] {e}")
            return None

    def extract_headlines(self, url):
        """Extract main headlines from a news site."""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                headlines = []
                # Common headline tags
                for tag in ['h1', 'h2', 'h3']:
                    for element in soup.find_all(tag):
                        text = element.get_text().strip()
                        if len(text) > 20: # Filter out short junk
                            headlines.append(text)
                return headlines[:10]
            return []
        except Exception as e:
            print(f"[Headline Error] {e}")
            return []

class WebAutomator:
    def __init__(self, headless=True):
        self.options = Options()
        if headless:
            self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--window-size=1920,1080")
        self.driver = None

    def start_driver(self):
        if not self.driver:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)

    def stop_driver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def search_and_extract(self, query):
        """Automate a search and extract main content from the first result."""
        try:
            self.start_driver()
            search_url = f"https://www.google.com/search?q={query}"
            self.driver.get(search_url)
            time.sleep(2) # Wait for results
            
            # Find the first result link
            results = self.driver.find_elements("css selector", "h3")
            if results:
                results[0].click()
                time.sleep(3) # Wait for page load
                content = self.driver.page_source
                soup = BeautifulSoup(content, 'html.parser')
                for script in soup(["script", "style"]):
                    script.decompose()
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                return text[:1500]
            return "No search results found."
        except Exception as e:
            return f"Automation Error: {str(e)}"
        finally:
            self.stop_driver()

class WebArchitect:
    def __init__(self):
        self.project_base = "web_projects"
        if not os.path.exists(self.project_base):
            os.makedirs(self.project_base)

    def create_project(self, project_id, html_content, css_content="", js_content=""):
        """Save a new web project to the disk."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        project_dir = os.path.join(self.project_base, f"{project_id}_{timestamp}")
        os.makedirs(project_dir, exist_ok=True)
        
        # Save HTML
        html_path = os.path.join(project_dir, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Save CSS (if provided)
        if css_content:
            css_path = os.path.join(project_dir, "style.css")
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(css_content)
            # Ensure HTML links to CSS
            if "style.css" not in html_content:
                html_content = html_content.replace("</head>", '<link rel="stylesheet" href="style.css"></head>')
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)

        # Save JS (if provided)
        if js_content:
            js_path = os.path.join(project_dir, "script.js")
            with open(js_path, "w", encoding="utf-8") as f:
                f.write(js_content)
            # Ensure HTML links to JS
            if "script.js" not in html_content:
                html_content = html_content.replace("</body>", '<script src="script.js"></script></body>')
                with open(html_path, "w", encoding="utf-8") as f:
                    f.write(html_content)
        
        return html_path

    def preview_project(self, html_path):
        """Open the generated project in the browser using Selenium."""
        import os
        abs_path = os.path.abspath(html_path)
        url = f"file:///{abs_path}"
        
        # Use visible browser for "WOW" factor as per plan
        automator = WebAutomator(headless=False) 
        try:
            automator.start_driver()
            automator.driver.get(url)
            # Keep browser open for a while so user can see it
            time.sleep(10)
            return f"Project live Preview: {url}"
        except Exception as e:
            return f"Preview Error: {str(e)}"
        finally:
            # We don't necessarily want to close it immediately if the user wants to admire it
            # but for automation safety we'll stop it here. The user can open manually too.
            automator.stop_driver()

class WebHost:
    def __init__(self):
        self.processes = {}

    def start_hosting(self, project_path, port=8000):
        """Host a project folder on localhost:port using a background process."""
        import subprocess
        import sys
        import socket
        
        # Ensure port is available
        def is_port_in_use(p):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', p)) == 0

        actual_port = port
        while is_port_in_use(actual_port):
            actual_port += 1
            if actual_port > port + 10: break # Limit search
            
        try:
            # Run python -m http.server as a subprocess
            cmd = [sys.executable, "-m", "http.server", str(actual_port)]
            proc = subprocess.Popen(cmd, cwd=project_path, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.processes[actual_port] = proc
            url = f"http://localhost:{actual_port}"
            return url
        except Exception as e:
            return f"Hosting Error: {str(e)}"

    def stop_hosting(self, port=8000):
        """Terminate the hosting process on a specific port."""
        if port in self.processes:
            self.processes[port].terminate()
            del self.processes[port]
            return f"Hosting on port {port} stopped."
        return "No active hosting found on that port."

# Unified Intelligence function
def web_intelligence_logic(query):
    scraper = WebScraper()
    # Check if query looks like a URL
    if query.startswith("http"):
        return scraper.scrape_url(query)
    
    # Otherwise, it's a search-like request
    automator = WebAutomator(headless=True)
    return automator.search_and_extract(query)
