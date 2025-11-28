import string
from collections import Counter


def analyze_text(text):
    """
    Analyzes text and returns comprehensive statistics.
    
    The function handles punctuation removal, case normalization, and provides
    robust error handling for edge cases.
    
    Args:
        text (str): The input text to analyze. Must be a non-empty string.
            
    Raises:
        TypeError: If input is not a string type
        ValueError: If input is empty or contains no valid words after cleaning
    """
    
    # Input Validation
    
    # Check if input is a string
    if not isinstance(text, str):
        raise TypeError(f"Input must be a string, got {type(text).__name__} instead")
    
    # Check if input is empty or only whitespace
    if not text.strip():
        raise ValueError("Input string cannot be empty or contain only whitespace")
    
    
    # Text Normalization
    
    # Convert to lowercase for case-insensitive analysis
    # This ensures "The", "THE", and "the" are counted as the same word
    text_lower = text.lower()
    
    
    # Remove Puncuations
    
    # Remove punctuation efficiently using translation table
    # str.maketrans creates a mapping from punctuation characters to None
    # This approach is more efficient than regex or list comprehensions
    # because it processes the entire string in a single pass
    translator = str.maketrans('', '', string.punctuation)
    text_cleaned = text_lower.translate(translator)
    
    
    # Tokanization
    
    # Split text into individual words
    # The list comprehension filters out empty strings that result from
    # punctuation removal (e.g., "word,word" becomes ["word", "", "word"])
    words = [word for word in text_cleaned.split() if word]
    
    
    # Validation - after the cleaning
    
    # Verify we have at least one valid word after cleaning
    if not words:
        raise ValueError("No valid words found after removing punctuation")
    
    
    # Calculate word count
    
    # Simply the length of our words list
    word_count = len(words)
    
    
    # Average Word length calculation
    
    # Calculate total characters across all words
    total_length = sum(len(word) for word in words)
    
    # Divide by word count and round to 2 decimal places
    # This follows standard mathematical rounding rules
    average_word_length = round(total_length / word_count, 2)
    
    
    # Identify the longest word
    
    # Find the maximum word length
    max_length = max(len(word) for word in words)
    
    # Create list of all words matching maximum length
    # Using set() to remove duplicates (if "hello" appears twice and is longest)
    # Then convert back to list and sort alphabetically for consistent output
    longest_words = sorted(list(set(
        [word for word in words if len(word) == max_length]
    )))
    
    
    # Word frequency calculation
    
    # Use Counter from collections module for efficient frequency counting
    # Counter is optimized for exactly this task and provides O(n) performance
    word_frequency = dict(Counter(words))
    
    # Sort the frequency dictionary for better readability
    # Primary sort: by frequency in descending order (most common first)
    # Secondary sort: alphabetically for consistent ordering within same frequency
    # The lambda function returns a tuple: (-frequency, word)
    # Negative frequency ensures descending order
    word_frequency = dict(sorted(
        word_frequency.items(),
        key=lambda x: (-x[1], x[0])
    ))
    
    
    # Result 
    
    return {
        "word_count": word_count,
        "average_word_length": average_word_length,
        "longest_words": longest_words,
        "word_frequency": word_frequency
    }


# Example usage

if __name__ == "__main__":
    
    # Example 1: Basic usage
    print("Example 1: Basic Usage")
    print("-" * 50)
    text1 = "The quick brown fox jumps over the lazy dog the fox"
    result1 = analyze_text(text1)
    print(f"Input: {text1}")
    print(f"Word count: {result1['word_count']}")
    print(f"Average word length: {result1['average_word_length']}")
    print(f"Longest words: {result1['longest_words']}")
    print(f"Word frequency: {result1['word_frequency']}")
    print()
    
    # Example 2: Text with punctuation
    print("Example 2: Punctuation Handling")
    print("-" * 50)
    text2 = "Hello, world! Hello? How are you... fine, fine."
    result2 = analyze_text(text2)
    print(f"Input: {text2}")
    print(f"Word count: {result2['word_count']}")
    print(f"Most frequent word: {list(result2['word_frequency'].keys())[0]}")
    print()
    
    # Example 3: Error handling - empty input
    print("Example 3: Error Handling - Empty Input")
    print("-" * 50)
    try:
        analyze_text("   ")
    except ValueError as e:
        print(f"Caught error: {e}")
    print()
    
    # Example 4: Error handling - wrong type
    print("Example 4: Error Handling - Wrong Type")
    print("-" * 50)
    try:
        analyze_text(12345)
    except TypeError as e:
        print(f"Caught error: {e}")
    print()
    
    # Example 5: Only punctuation
    print("Example 5: Error Handling - Only Punctuation")
    print("-" * 50)
    try:
        analyze_text("!@#$%^&*()")
    except ValueError as e:
        print(f"Caught error: {e}")
