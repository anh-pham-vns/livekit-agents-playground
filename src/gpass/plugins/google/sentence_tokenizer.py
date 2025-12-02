import regex
from livekit import blingfire
from livekit.agents.tokenize import BufferedSentenceStream, SentenceStream
from livekit.agents.tokenize.blingfire import SentenceTokenizer


class SegmentedTokenizer(SentenceTokenizer):
    """Sentence tokenizer that enforces a UTF-8 byte limit per chunk.
    Sentences are first detected with BlingFire. Any sentence whose UTF-8 size
    exceeds `bytes_limit` is split on Unicode grapheme cluster boundaries,
    ensuring no code points are cut in the middle.
    """

    def __init__(self, bytes_limit: int):
        self.bytes_limit = bytes_limit
        super().__init__(retain_format=True)

    def tokenize(self, text: str, *, language: str | None = None) -> list[str]:
        """Tokenize text into sentences, then byte-limit them if needed.

        Blank lines are ignored. Long sentences are split at grapheme boundaries
        so each chunk fits within `bytes_limit`.
        """
        lines = (line for line in text.splitlines() if line)
        return [
            chunk
            for line in lines
            for sentence in super().tokenize(line)
            for chunk in (
                [sentence]
                if _utf8_len(sentence) <= self.bytes_limit
                else [
                    chunk
                    for chunk, _, _ in _iter_grapheme_chunks(sentence, self.bytes_limit)
                ]
            )
        ]

    def stream(self, *, language: str | None = None) -> SentenceStream:
        return BufferedSentenceStream(
            tokenizer=self._tokenize_with_offsets,
            min_token_len=self._config.min_sentence_len,
            min_ctx_len=self._config.stream_context_len,
        )

    def _tokenize_with_offsets(self, text: str) -> list[tuple[str, int, int]]:
        tokens: list[tuple[str, int, int]] = []
        abs_idx = 0  # Absolute index into the original `text`

        for raw_line in text.splitlines(
            keepends=True,  # Keeps newline chars so abs_idx can track exact positions
        ):
            # Remove trailing newlines before tokenizing, but still count them in abs_idx
            line = raw_line.rstrip("\r\n")

            if not line:
                abs_idx += len(raw_line)
                continue

            _, offsets = blingfire.text_to_sentences_with_offsets(line)

            for s_rel, e_rel in offsets:
                if s_rel >= e_rel:
                    continue

                sentence = line[s_rel:e_rel]

                if _utf8_len(sentence) <= self.bytes_limit:
                    tokens.append((sentence, abs_idx + s_rel, abs_idx + e_rel))
                else:
                    for chunk, rel_start, rel_end in _iter_grapheme_chunks(
                        sentence, self.bytes_limit
                    ):
                        # Convert to absolute offsets by adding `abs_idx`
                        tokens.append(
                            (
                                chunk,
                                abs_idx + s_rel + rel_start,
                                abs_idx + s_rel + rel_end,
                            )
                        )

            # Always advance by the full raw line length (including newline chars)
            abs_idx += len(raw_line)

        return tokens


_GRAPHEME_RE = regex.compile(r"\X")


def _iter_grapheme_chunks(text: str, bytes_limit: int):
    """Yield grapheme-aligned chunks that fit within a UTF-8 byte limit"""
    if not text:
        return

    if _utf8_len(text) <= bytes_limit:
        yield text, 0, len(text)
        return

    start = 0
    current_bytes = 0

    # Iterate over grapheme matches to know exact boundary indices
    for grapheme_match in _GRAPHEME_RE.finditer(text):
        grapheme = grapheme_match.group(0)
        grapheme_bytes = _utf8_len(grapheme)

        # If adding this grapheme would exceed the limit and we already have content,
        # emit the chunk up to the start of this grapheme
        if current_bytes and current_bytes + grapheme_bytes > bytes_limit:
            end = grapheme_match.start()
            yield text[start:end], start, end
            start = end
            current_bytes = 0  # Reset for the new chunk

        current_bytes += grapheme_bytes

    # Emit the trailing chunk
    if start < len(text):
        yield text[start:], start, len(text)


def _utf8_len(text: str) -> int:
    return len(text.encode("utf-8"))
