# add.py
def add(a, b):
    """Add two numbers"""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        raise TypeError(
            "The inputs to the `add` function must be numbers (int or float)!"
        )

    return a + b
