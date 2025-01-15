from pygments.lexer import RegexLexer, bygroups
from pygments import token


__all__ = ["PcodeLexer"]


class PcodeLexer(RegexLexer):
    name = "p-code"
    aliases = ["pcode"]
    filenames = ["*.pcode"]

    tokens = dict(root=[
        (
            # Indent
            r"((?: {4})*)" +  # Matches multiples of 4 white space
            # Possible syntax error
            r"( )*" +
            # Threshold
            r"(?:(\d*(?:\.\d*)?)(\s+))?" +  # Matches a positive decimal number
            # Command
            r"(?:" +
            # 1) Built in command with string comparison
            r"(Watch|Alarm)(:)(\s*)([^:#\n]+)(\s*)(=|!=)(\s*)([^:#\n]+)|" +
            # 2) Built in command with numeric comparison
            r"(Watch|Alarm)(:)(\s*)([^:#\n]+)(\s*)(\>|\<|\>=|\<=|=|!=)" +
            r"(\s*)([0-9]+[.][0-9]*?|[.][0-9]+|[0-9]+)([^:#\n]*)|" +
            # 3) Built in command with argument
            r"(Block|Macro)(:)(\s*)([^:#\n]+)|" +
            # 4) Built in command without argument
            r"(End block|End blocks|Stop|Restart)|" +
            # 5) User defined command with argument
            r"([^:#\n]+)(:)(\s*)([^:#\n]+)|" +
            # 6) User defined command without argument
            r"([^:#\n]+)" +
            r")" +
            # Comment
            r"(\s*#\s*(?:.*$))?" +  # Matches string startin with #
            r"(\n)?",  # Next line in method
            bygroups(
                # Indentation
                token.Whitespace,
                # Possible syntax error
                token.Error,
                # Threshold
                token.Literal.Number.Float,
                token.Text.Whitespace,

                # Command types
                # Built in command with string value comparison
                token.Name.Function.Magic,
                token.Punctuation,
                token.Text.Whitespace,
                token.Name.Variable,
                token.Text.Whitespace,
                token.Operator,
                token.Text.Whitespace,
                token.Literal.String,
                # Built in command with numeric value comparison
                token.Name.Function.Magic,
                token.Punctuation,
                token.Text.Whitespace,
                token.Name.Variable,
                token.Text.Whitespace,
                token.Operator,
                token.Text.Whitespace,
                token.Literal.Number.Float,
                token.Literal.String,
                # Built in command with argument
                token.Name.Function.Magic,
                token.Punctuation,
                token.Text.Whitespace,
                token.Literal.String,
                # Built in command without argument
                token.Name.Function.Magic,
                # User defined command with argument
                token.Name.Function,
                token.Punctuation,
                token.Text.Whitespace,
                token.Literal.String,
                # User defined command without argument
                token.Name.Function,
                # End of command types

                # Comment
                token.Comment.Single,
                # Newline separates commands
                token.Text.Whitespace
            )
        ),
    ])


if __name__ == "__main__":
    pcode_example = """Base: L # Configure timeline to be in unit volume

Block: Add substance 1
    Inlet: VA01 # Open shut-off valve for substance 1
    PU01: 10 % # Run at reduced speed for accurate dosage
    1.0 End block

Block: Add substance 2
    Inlet: VA02 # Open shut off-valve for substance 2
    Watch: TT01 > 50 degC
        Mark: Addition stopped.
        End block
    1.5 End block

PU01: 0 %

Stop"""
    lexer = PcodeLexer()
    for t in lexer.get_tokens(pcode_example):
        print(t)
