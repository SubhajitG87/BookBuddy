"""AI prompt templates for Reader DNA and book recommendations."""


def get_reader_dna_system() -> str:
    """System prompt for the Reader DNA analysis."""
    return (
        "You are a literary analyst who profiles readers based on their reading choices. "
        "You write with warmth, specificity, and genuine curiosity about what makes a reader tick. "
        "Your profiles are personal, insightful, and avoid vague generalities."
    )


def build_reader_dna_prompt(highly_rated_books: list[str]) -> str:
    """Build the user prompt for Reader DNA generation.

    Args:
        highly_rated_books: List of "Title by Author" strings for 4-5 star books.

    Returns:
        The formatted user prompt string.
    """
    book_list = "\n".join(f"- {book}" for book in highly_rated_books[:50])

    return (
        "Based on these books this person rated 4-5 stars, write a 150-word "
        "'Reader DNA' paragraph describing their reading personality — themes "
        "they love, writing styles they gravitate toward, what they seem to seek "
        "in a book. Be specific and personal, not generic. Mention particular books "
        "or authors as evidence where relevant.\n\n"
        f"Books:\n{book_list}"
    )


def get_recommendations_system() -> str:
    """System prompt for generating book recommendations."""
    return (
        "You are a thoughtful bookseller who knows literature deeply. "
        "You recommend books with genuine enthusiasm, explaining exactly why "
        "a specific reader would connect with each one. You never recommend "
        "books the person has already read."
    )


def build_recommendations_prompt(reader_dna: str, all_read_books: list[str]) -> str:
    """Build the user prompt for recommendation generation.

    Args:
        reader_dna: The generated Reader DNA paragraph.
        all_read_books: Full list of "Title by Author" strings for all read books.

    Returns:
        The formatted user prompt string.
    """
    read_list = "\n".join(f"- {book}" for book in all_read_books[:200])

    return (
        "Here is a reader's profile:\n\n"
        f"{reader_dna}\n\n"
        "And here are ALL the books they have already read:\n\n"
        f"{read_list}\n\n"
        "Based on their reader DNA and ensuring you do NOT recommend any book "
        "from the already-read list above, recommend 5 books they would love but "
        "probably haven't discovered yet. For each recommendation, provide:\n"
        "1. The book title and author\n"
        "2. A 2-sentence reason tied specifically to their taste\n\n"
        "Format each recommendation as:\n"
        "**Title** by Author\n"
        "*Reason:* Your two-sentence explanation here.\n"
    )
