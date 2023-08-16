from typing import Callable, Literal


class Rope(str):
    def surround(self, left: str, right: str):
        return self.join(f"{left}{right}")


def align(
    strings: list[str],
    side: Literal["left", "right", "center"] | None = None,
    /,
    *,
    character: str | None = None,
    fill_char: str = " ",
) -> list[str]:
    if side is None and character is None:
        side = "left"

    # align to character
    if side is None:
        strings = [(str(s)).split(character, 1) for s in strings]
        length_1: int = max(len(s) for s, _ in strings)
        length_2: int = max(len(s) for _, s in strings)
        return [
            s1.rjust(length_1, fill_char) + character + s2.ljust(length_2, fill_char)
            for s1, s2 in strings
        ]

    # align to side
    length = max(map(len, strings))

    alignment_sides: dict[str, Callable[[str, int, str], str]] = {
        "left": str.ljust,
        "right": str.rjust,
        "center": str.center,
    }

    if (method := alignment_sides.get(side)) is None:
        raise ValueError("side must be one of 'left', 'right', or 'center'")
    return [method(s, length, fill_char) for s in strings]


def align2d(
    strings: list[list[str]],
    side: Literal["left", "right", "center"] | None = None,
    /,
    *,
    character: str | None = None,
    fill_char: str = " ",
):
    return list(
        zip(
            *(
                align(s, side, character=character, fill_char=fill_char)
                for s in list(zip(*strings))
            )
        )
    )
