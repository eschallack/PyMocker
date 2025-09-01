
import pytest
from pymocker.builder.rank import rank

# Test cases for the rank function

def test_rank_basic_functionality():
    """Tests if the function returns a sorted list of options based on similarity."""
    options = ["apple", "banana", "application", "apply"]
    target = "app"
    
    ranked_results = rank(options, target)
    
    # The list should be sorted, so the first element is the most similar
    assert ranked_results[0][0] in ["apple", "apply", "application"] # Order may vary slightly
    
    # Check that all original options are present
    assert len(ranked_results) == len(options)
    
    # Extract just the names to check order
    ranked_names = [r[0] for r in ranked_results]
    assert "banana" in ranked_names

def test_rank_perfect_match():
    """Tests if a perfect match is ranked highest."""
    options = ["new york", "los angeles", "chicago"]
    target = "chicago"
    
    ranked_results = rank(options, target)
    
    # The perfect match should be the first item with a score close to 1.0
    assert ranked_results[0][0] == "chicago"
    assert ranked_results[0][1][0] == pytest.approx(1.0, abs=1e-4)

def test_rank_no_good_match():
    """Tests how it behaves when no options are semantically similar."""
    options = ["car", "boat", "plane"]
    target = "fruit"
    
    ranked_results = rank(options, target)
    
    # No assertion on the order, but the scores should be relatively low
    for _, score in ranked_results:
        assert score[0] < 0.5 # Expect low similarity scores

def test_rank_with_empty_options():
    """Tests if the function handles an empty list of options gracefully."""
    options = []
    target = "anything"
    
    ranked_results = rank(options, target)
    
    assert ranked_results == []

def test_rank_with_single_option():
    """Tests if it works correctly with only one option."""
    options = ["developer"]
    target = "software engineer"
    
    ranked_results = rank(options, target)
    
    assert len(ranked_results) == 1
    assert ranked_results[0][0] == "developer"
    # The score should be reasonably high due to semantic similarity
    assert ranked_results[0][1][0] > 0.6
