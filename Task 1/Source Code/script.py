
# Let me debug - the example shows 10 words but we're getting 11
# Let's check what the expected behavior should be

test_text = "The quick brown fox jumps over the lazy dog the fox"
words_split = test_text.lower().split()
print(f"Words when split: {words_split}")
print(f"Count: {len(words_split)}")
print()

# Wait - I see 11 words. The problem says "Expected Output" shows 10
# Let me check if perhaps we should count unique words or something else
# Looking back at example: it shows word_count: 10
# But the text has: The(1) quick(2) brown(3) fox(4) jumps(5) over(6) the(7) lazy(8) dog(9) the(10) fox(11)
# That's 11 total words. But expected shows 10.

# Let me re-read the example more carefully...
# Oh wait, maybe there's a typo in the problem statement? 
# Let me count again from "The quick brown fox jumps over the lazy dog the fox"
# That's definitely 11 words.

# However, looking at the word_frequency in the expected output,
# it shows {"the": 2, "quick": 1, "fox": 2, ...}
# But "the" appears 3 times in the text: "The", "the" (after dog), "the" (after over... no wait)
# Let me check word by word:
# The(1) quick(2) brown(3) fox(4) jumps(5) over(6) the(7) lazy(8) dog(9) the(10) fox(11)

# Actually wait - I'm counting wrong. Let me split properly:
words = "The quick brown fox jumps over the lazy dog the fox".split()
for i, w in enumerate(words, 1):
    print(f"{i}: {w}")
    
print(f"\nTotal: {len(words)}")
print(f"\nActual 'the' count: {words.count('The') + sum(1 for w in words if w.lower() == 'the')}")

# The issue is in the expected output - it might have been a manual error
# OR the expected output count might exclude something. But based on the text,
# it's definitely 11 words. Let me check if maybe they want us to NOT count duplicates?
# No, that wouldn't make sense with the frequency output.

# I think the example in the problem might have a small error. 
# Let me verify my implementation is correct and document this.
