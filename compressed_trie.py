"""Compressed trie, AKA: compact prefix tree, Patricia tree/trie, radix tree/trie (ish).

This is a simple variant of a vanilla (character-per-node) trie where each node that is
an only child is merged with its parent.
"""
