# test_bugs.py

def infinite_loop_bug():
    print("Testing infinite loop...")
    x = 0
    while x < 10:
        print(f"Stuck at x = {x}")
        # Bug: Forgot to increment x
        # This will loop forever at x = 0

def memory_leak_bug():
    print("Testing memory leak...")
    memory_list = []
    while True:
        # Bug: Continuously appending without cleanup
        memory_list.append("leaking memory")
        if len(memory_list) > 1000:  # Safety break
            break

def null_pointer_bug():
    print("Testing null pointer...")
    data = None
    # Bug: Trying to access attribute of None
    return data.something()

def index_error_bug():
    print("Testing index error...")
    array = [1, 2, 3]
    # Bug: Trying to access index beyond array bounds
    for i in range(len(array)):
        print(array[i + 1])  # Will fail at last iteration

def syntax_error_bug():
    print("Testing syntax error...")
    # Bug: Missing closing parenthesis
    x = 5
    if x > 3:
        print("Missing colon here")
    
# Test individual bugs by uncommenting them

if __name__ == "__main__":
    try:
        # Uncomment one at a time to test different bugs
        # infinite_loop_bug()
        # memory_leak_bug()
        # null_pointer_bug()
        # index_error_bug()
        # syntax_error_bug()
    except Exception as e:
        print(f"Bug caught: {e}")
