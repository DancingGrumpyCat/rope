from enum import Enum
from typing import Callable, Self, Sequence


class Justification(Enum):
    START = "START"
    CENTERED = "CENTERED"
    END = "END"


class BorderType(dict):
    NO_BORDER = "NO_BORDER"

    def __init__(
        self, top, right, bottom, left, topleft, topright, bottomleft, bottomright
    ) -> None:
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left
        self.topleft = topleft
        self.topright = topright
        self.bottomleft = bottomleft
        self.bottomright = bottomright

    @staticmethod
    def make_border(string: str, spacer: str = " ") -> Self:
        return BorderType(
            f"{spacer}{string}",
            f"{string}",
            f"{spacer}{string}",
            f"{string}",
            f"{string}",
            f"{string}",
            f"{string}",
            f"{string}",
        )


NO_BORDER = BorderType(
    top=" ",
    right=" ",
    bottom=" ",
    left=" ",
    topleft=" ",
    topright=" ",
    bottomleft=" ",
    bottomright=" ",
)

ASCII = BorderType(
    top="-",
    right="|",
    bottom="_",
    left="|",
    topleft="/",
    topright="\\",
    bottomleft="\\",
    bottomright="/",
)

SINGLE = BorderType(
    top="─",
    right="│",
    bottom="─",
    left="│",
    topleft="┌",
    topright="┐",
    bottomleft="└",
    bottomright="┘",
)

DOUBLE = BorderType(
    top="═",
    right="║",
    bottom="═",
    left="║",
    topleft="╔",
    topright="╗",
    bottomleft="╚",
    bottomright="╝",
)


HEAVY = BorderType(
    top="━",
    right="┃",
    bottom="━",
    left="┃",
    topleft="┏",
    topright="┓",
    bottomleft="┗",
    bottomright="┛",
)


class AreaText:
    def __init__(
        self,
        text: str | None = None,
        /,
        *,
        sequence: Sequence | None = None,
        columns: int = 10,
        border: BorderType = SINGLE,
        indent=0,
        padding: int | None = None,
        padding_inline: int | None = None,
        padding_block: int | None = None,
        padding_top: int = 0,
        padding_left: int = 0,
        padding_bottom: int = 0,
        padding_right: int = 0,
        min_height: int = 0,
    ):
        if sequence is not None:
            self.raw_text = "".join(sequence)
            self.lines = sequence
            self.border = border
            self.padded = self
            return

        self.raw_text = text
        self.columns = columns
        self.border = border
        self.indent = indent
        if padding is not None:
            padding_top = padding_left = padding_bottom = padding_right = padding
        if padding_block is not None:
            padding_top = padding_bottom = padding_block
        if padding_inline is not None:
            padding_left = padding_right = padding_inline

        lines = []

        splitwords = list(text.split(" "))
        if self.indent > 0:
            splitwords.insert(0, " " * indent)

        splitwords = list(reversed(splitwords))
        current_line = 0
        current_length = 0
        lines.append("")

        while splitwords:
            word = splitwords.pop()
            if current_length + len(word) > self.columns and len(word) <= self.columns:
                current_length = 0
                lines.append("" if self.indent >= 0 else " " * -self.indent)
                current_line += 1

            joiner = " " if lines[current_line] else ""
            if "\n" in word:
                string = word.split("\n")
                lines[current_line] += joiner
                for substring in string:
                    try:
                        lines[current_line] += substring
                    except IndexError:
                        lines.append("")
                        lines[current_line] += substring
                    current_line += 1
            elif word != "":
                lines[current_line] = joiner.join([lines[current_line], word])
            current_length += len(word)

        self.lines = lines

        self.padded = self.pad(
            padding_top=padding_top,
            padding_left=padding_left,
            padding_bottom=padding_bottom,
            padding_right=padding_right,
            min_height=min_height,
        )

    def __str__(self):
        b = self.border

        def cutoff_repeat(string, width) -> str:
            return string * (width // len(string)) + string[: width % len(string)]

        width = self.padded.width

        first, last = (
            b.topleft + cutoff_repeat(b.top, width) + b.topright + "\n",
            "\n" + b.bottomleft + cutoff_repeat(b.bottom, width) + b.bottomright,
        )
        newline_sep = f"{b.left}\n{b.right}"
        return (
            first
            + f"{b.left}{f'{newline_sep}'.join(self.padded.lines)}{b.right}"
            + last
        )

    @property
    def width(self) -> int:
        return max(len(line) for line in self.lines)

    @property
    def height(self) -> int:
        return len(self.lines)

    @property
    def dimensions(self) -> tuple[int, int]:
        return (self.width, self.height)

    def pad(
        self,
        padding_top: int = 0,
        padding_left: int = 0,
        padding_bottom: int = 0,
        padding_right: int = 0,
        min_height: int = 0,
    ):
        if min_height > self.height:
            padding_bottom += min_height - self.height

        if padding_top:
            self.lines = [""] * padding_top + self.lines
        if padding_bottom:
            self.lines = self.lines + [""] * padding_bottom
        if padding_left:
            self.lines = [(" " * padding_left) + line for line in self.lines]
        if padding_right:
            self.lines = [line + (" " * padding_right) for line in self.lines]

        return self.align(Justification.START)

    @staticmethod
    def align_line(line, length, alignment: Justification):
        alignments: dict[Justification, Callable[[str, int, str], str]] = {
            Justification.START: str.ljust,
            Justification.END: str.rjust,
            Justification.CENTERED: str.center,
        }

        if (method := alignments.get(alignment)) is None:
            raise ValueError
        return method(line, length)

    def align(self, inline_alignment: Justification):
        out = [
            AreaText.align_line(line, length=self.width, alignment=inline_alignment)
            for line in self.lines
        ]
        return AreaText(sequence=out, border=self.border)


#############################################
#                  EXAMPLE                  #
#############################################

text = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, \
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. \
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris \
    nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in \
    reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla \
    pariatur. Excepteur sint occaecat cupidatat non proident, sunt in \
    culpa qui officia deserunt mollit anim id est laborum."""

s = AreaText(text, columns=40, padding_inline=1, border=SINGLE)
print(s.align(Justification.CENTERED).pad(3, 6, 3, 6))
