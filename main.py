import os
import asyncio
from dotenv import load_dotenv
from toolhouse import Toolhouse
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize clients
th = Toolhouse(api_key=os.environ.get('TOOLHOUSE_API_KEY'))
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))
MODEL = "llama3-groq-70b-8192-tool-use-preview"

class NightmareDebug:
    def __init__(self, toolhouse_instance, groq_client):
        self.th = toolhouse_instance
        self.client = groq_client
        self.messages = []

    async def analyze_bug(self, code_snippet):
        print("\n🔍 Analyzing code for bugs...")

        print(th.get_tools())
        print('----------')
        
        # Prepare the analysis message
        self.messages = [{
            "role": "user",
            "content": f"""
            1. Analyze this code for bugs:
            {code_snippet}
            
            2. Generate a horror-themed monster description based on the bugs found.
            For example:
            - Memory leaks become hungry zombies
            - Infinite loops become serpents eating their own tails
            - Null pointers become ghost-like apparitions
            
            3. Use image_generation_flux to create the monster visualization.
            """
        }]

        try:
            # Get available tools
            tools = self.th.get_tools()

            # Create completion with tools
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=self.messages,
                tools=tools
            )

            # Run the tools
            tool_run = self.th.run_tools(response)
            self.messages.extend(tool_run)

            print("\n🎨 Generated Analysis:")
            print("=" * 50)
            print(response.choices[0].message.content)
            print("=" * 50)

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return None
        
class CodeWatcher(FileSystemEventHandler):
    def __init__(self):
        self.bug_monster = BugMonster()
        self.last_modified = 0
        self.debounce_time = 2.0  # Wait 2 seconds after last change
        self.timer = None
        
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            # Cancel previous timer
            if self.timer:
                self.timer.cancel()
            
            # Start new timer
            self.timer = threading.Timer(
                self.debounce_time, 
                self.analyze_file, 
                args=[event.src_path]
            )
            self.timer.start()
    
    def analyze_file(self, filepath):
        try:
            with open(filepath, 'r') as file:
                code = file.read()
                
            # Only analyze if code can be parsed (is complete)
            try:
                ast.parse(code)
                if code != self.bug_monster.last_analyzed:
                    self.bug_monster.last_analyzed = code
                    print("\n🔍 Analyzing completed code...")
                    bugs = self.bug_monster.analyze_code(code)
                    
                    if bugs:
                        print(f"🐛 Found bugs: {', '.join(bugs)}")
                        self.bug_monster.generate_monster(bugs)
            except SyntaxError:
                print("Code incomplete, waiting for more...")
                
        except Exception as e:
            print(f"Error processing file: {e}")

async def main():
    # Test cases
    test_cases = {
        "memory_leak": """
            def leaky_function():
                data = []
                while True:
                    data.append("memory leak")
        """,
        
        "infinite_loop": """
            def endless_loop():
                x = 0
                while x < 10:
                    print(x)
                    # Forgot to increment x
        """
    }

    # Create debug instance
    debug = NightmareDebug(th, client)

    # Test each bug type
    for bug_type, code in test_cases.items():
        print(f"\n🔮 Testing {bug_type.upper()} bug:")
        print("-" * 50)
        print("Code to analyze:")
        print(code)
        
        result = await debug.analyze_bug(code)
        
        if result:
            print("\n✅ Analysis complete!")
        else:
            print("\n❌ Analysis failed!")

# Run the async main function
if __name__ == "__main__":
    print("🚀 Starting Nightmare Debug...")
    asyncio.run(main())