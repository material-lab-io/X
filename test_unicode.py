#!/usr/bin/env python3
import json

# Read the file
with open('generated_threads_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Get a tweet with Unicode
tweet = data[0]['generatedTweets'][1]
print("Original tweet:")
print(repr(tweet))
print("\nDecoded tweet:")
print(tweet)

# Test decoding
print("\nTesting decode methods:")
# Method 1: Direct print (should work if terminal supports UTF-8)
print("Method 1 - Direct:", tweet)

# Method 2: Encode then decode
try:
    decoded = tweet.encode('utf-8').decode('unicode-escape')
    print("Method 2 - unicode-escape:", decoded)
except Exception as e:
    print(f"Method 2 failed: {e}")

# Method 3: Using json.loads on the escaped string
try:
    # Wrap in quotes to make it valid JSON string
    decoded = json.loads(f'"{tweet}"')
    print("Method 3 - json.loads:", decoded)
except Exception as e:
    print(f"Method 3 failed: {e}")