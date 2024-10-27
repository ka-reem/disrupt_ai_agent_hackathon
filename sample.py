import os
import time
import ast
import webview
import requests
import threading
from dotenv import load_dotenv
from toolhouse import Toolhouse
from groq import Groq
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

# Initialize clients
th = Toolhouse(api_key=os.environ.get('TOOLHOUSE_API_KEY'))
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
MODEL = "llama3-groq-70b-8192-tool-use-preview"

# Global window reference
window = None

class BugMonster:
    def __init__(self):
        self.last_analyzed = ""
        self.bug_types = {
        'infinite_loop': "A digital snake trapped in an endless cycle, its body made of repeating code fragments. Each loop of its body shows the same variables stuck in time. Glowing error messages spiral around it. Horror style.",
        'memory_leak': "A monstrous data structure that won't die, overflowing with unused variables. Memory addresses leak from its form like toxic waste. RAM meters show critical levels. Dark digital horror.",
        'null_pointer': "A corrupted object monster reaching for data that doesn't exist. Its body glitches between solid and void, with NULL errors floating through its transparent form. Digital horror.",
        'index_error': "A beast made of broken array brackets, desperately reaching beyond its bounds. Its limbs glitch out at invalid indices [i+1]. Shows array bounds and error messages. Horror style.",
        'syntax_error': "A creature formed from mangled code brackets and missing semicolons. Its body breaks apart at syntax errors, revealing corrupt code within. Error messages pulse through its form."
    }

    def extract_image_url(self, result):
        """Extract image URL from markdown format ![](url)"""
        try:
            start = result.find('(') + 1
            end = result.find(')')
            if start > 0 and end > 0:
                return result[start:end]
        except:
            return None
        return None

    def get_monster_html(self, image_url, bug_type):
        """Generate HTML for the monster window"""
        return f"""
        <html>
        <head>
            <style>
                body {{
                    margin: 0;
                    padding: 20px;
                    background: #1a1a1a;
                    color: #ff4444;
                    font-family: 'Courier New', monospace;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100vh;
                    overflow: hidden;
                }}
                .container {{
                    text-align: center;
                    max-width: 800px;
                }}
                .title {{
                    font-size: 24px;
                    margin-bottom: 20px;
                    text-transform: uppercase;
                    letter-spacing: 2px;
                    text-shadow: 0 0 10px #ff0000;
                }}
                .monster-image {{
                    max-width: 90%;
                    max-height: 70vh;
                    border: 3px solid #ff4444;
                    box-shadow: 0 0 20px #ff0000;
                    margin: 20px 0;
                }}
                .bug-info {{
                    font-size: 16px;
                    margin-top: 20px;
                    padding: 15px;
                    background: rgba(255, 0, 0, 0.1);
                    border-radius: 5px;
                }}
                @keyframes glitch {{
                    0% {{ transform: translate(0) }}
                    20% {{ transform: translate(-2px, 2px) }}
                    40% {{ transform: translate(-2px, -2px) }}
                    60% {{ transform: translate(2px, 2px) }}
                    80% {{ transform: translate(2px, -2px) }}
                    100% {{ transform: translate(0) }}
                }}
                .glitch {{
                    animation: glitch 0.3s ease infinite;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="title glitch">🐛 Bug Monster Detected! 🐛</div>
                <img src="{image_url}" class="monster-image" alt="Bug Monster">
                <div class="bug-info">
                    Type: {bug_type.upper()}<br>
                    Status: Active<br>
                    Threat Level: HIGH
                </div>
            </div>
        </body>
        </html>
        """

    def analyze_code(self, code):
        try:
            tree = ast.parse(code)
            bugs = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.While):
                    has_increment = False
                    for child in ast.walk(node):
                        if isinstance(child, (ast.AugAssign, ast.Assign)):
                            has_increment = True
                            break
                    if not has_increment:
                        bugs.append('infinite_loop')
                
                if isinstance(node, ast.While) or isinstance(node, ast.For):
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call) and 'append' in ast.unparse(child):
                            bugs.append('memory_leak')
                            break
            
            return bugs
        except SyntaxError:
            return ['syntax_error']
        except Exception as e:
            print(f"Analysis error: {e}")
            return []

    def generate_monster(self, bug_types):
        if not bug_types:
            return None
        
        bug_type = bug_types[0]
        prompt = self.bug_types.get(bug_type, "A generic code bug monster")
        
        messages = [{
            "role": "user",
            "content": f"""Please use image_generation_flux to generate a monster for this bug:
            Tool: image_generation_flux
            Parameters:
            - prompt: {prompt}
            - height: 1024
            - width: 1024
            - steps: 50"""
        }]

        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=th.get_tools()
            )
            
            result = th.run_tools(response)
            image_url = self.extract_image_url(str(result))
            
            if image_url:
                # Update the window HTML on the main thread
                html_content = self.get_monster_html(image_url, bug_type)
                webview.windows[0].load_html(html_content)
            
            return result
        except Exception as e:
            print(f"Generation error: {e}")
            return None

class CodeWatcher(FileSystemEventHandler):
    def __init__(self):
        self.bug_monster = BugMonster()
        self.last_modified = 0
        
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            current_time = time.time()
            if current_time - self.last_modified < 1:
                return
            self.last_modified = current_time
            
            try:
                with open(event.src_path, 'r') as file:
                    code = file.read()
                    
                if code != self.bug_monster.last_analyzed:
                    self.bug_monster.last_analyzed = code
                    print("\n🔍 Analyzing code for bugs...")
                    bugs = self.bug_monster.analyze_code(code)
                    
                    if bugs:
                        print(f"🐛 Found potential bugs: {', '.join(bugs)}")
                        print("🎨 Generating bug monster...")
                        self.bug_monster.generate_monster(bugs)
                    else:
                        print("✅ No bugs detected!")
                        
            except Exception as e:
                print(f"Error processing file: {e}")

def start_file_monitor():
    event_handler = CodeWatcher()
    observer = Observer()
    observer.schedule(event_handler, ".", recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    print("🚀 Starting Nightmare Debug Live Monitor...")
    
    # Create initial window
    html = """
    <html>
    <body style="background: #1a1a1a; color: #ff4444; font-family: monospace; text-align: center; padding: 20px;">
        <h2>🔮 Nightmare Debug is watching your code...</h2>
        <p>Save any .py file to generate bug monsters!</p>
    </body>
    </html>
    """
    window = webview.create_window('Nightmare Debug', html=html, width=600, height=800)
    
    # Start file monitoring in a separate thread
    monitor_thread = threading.Thread(target=start_file_monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Start webview in main thread
    webview.start(debug=True)

if __name__ == "__main__":
    main()