
from pylsp.workspace import Document


def lint_example(document: Document):
    diagnostics = []
    diagnostics.append(
        {
            "source": "Open Pectus",
            "range": {
                "start": {"line": 0, "character": 0},
                # Client is supposed to clip end column to line length.
                "end": {"line": 0, "character": 1000},
            },
            "code": "Foo bar",
            "message": "my error",
            "severity": 1,  # Error: 1, Warning: 2, Information: 3, Hint: 4
        }
    )    
    pos = find_first_word_position(document, "secret")
    if pos is not None:
        diagnostics.append(
            {
                "source": "Open Pectus",
                "range": {
                    "start": pos,
                    # Client is supposed to clip end column to line length.
                    "end": {"line": pos["line"], \
                            "character": int(pos["character"]) + len("secret")},
                },
                "code": "Secret error",
                "message": "Do not type the secret word",
                "severity": 2,  # Error: 1, Warning: 2, Information: 3, Hint: 4
            }
        )
    return diagnostics


def find_first_word_position(document: Document, word: str):

    for i, line in enumerate(document.lines):
        if word in line:
            character = line.index(word)
            return {"line": i, "character": character}
    return None
