"""Interactive terminal UI for imquest."""

from __future__ import annotations

import curses
from dataclasses import asdict
from pathlib import Path

from imquest.client import ImQuestClient
from imquest.models import GeneratedImage, PhotoResult
from imquest.utils.download import download_photo, save_generated_image


class ImQuestTUI:
    def __init__(self, client: ImQuestClient | None = None) -> None:
        self.client = client or ImQuestClient()
        self.query = ""
        self.results: list[PhotoResult] = []
        self.generated_image: GeneratedImage | None = None
        self.selected_idx = 0
        self.message = "Type / to search, g to generate fallback, d to download, q to quit."

    def run(self) -> None:
        curses.wrapper(self._main)

    def _main(self, stdscr) -> None:
        curses.curs_set(0)
        stdscr.nodelay(False)
        stdscr.keypad(True)

        while True:
            self._draw(stdscr)
            ch = stdscr.getch()

            if ch in {ord("q"), 27}:  # q or ESC
                return
            if ch in {curses.KEY_DOWN, ord("j")}:
                if self.selected_idx < max(0, len(self.results) - 1):
                    self.selected_idx += 1
            elif ch in {curses.KEY_UP, ord("k")}:
                self.selected_idx = max(0, self.selected_idx - 1)
            elif ch == ord("/"):
                self._interactive_search(stdscr)
            elif ch == ord("g"):
                self._interactive_generate(stdscr)
            elif ch == ord("d"):
                self._interactive_download(stdscr)
            elif ch == ord("r"):
                self._show_selected_json(stdscr)

    def _draw(self, stdscr) -> None:
        stdscr.erase()
        h, w = stdscr.getmaxyx()

        title = "imquest TUI  |  / search  g generate  d download  r details  q quit"
        stdscr.addstr(0, 0, title[: w - 1], curses.A_BOLD)
        stdscr.addstr(1, 0, f"Query: {self.query}"[: w - 1])
        stdscr.addstr(2, 0, f"Results: {len(self.results)}"[: w - 1])
        if self.generated_image:
            stdscr.addstr(3, 0, f"Generated fallback available from {self.generated_image.provider}"[: w - 1])

        start = 5
        visible_rows = max(1, h - start - 2)
        offset = 0
        if self.selected_idx >= visible_rows:
            offset = self.selected_idx - visible_rows + 1

        for i, item in enumerate(self.results[offset : offset + visible_rows]):
            absolute_idx = i + offset
            marker = ">" if absolute_idx == self.selected_idx else " "
            line = f"{marker} [{item.provider}] {item.id} :: {item.url}"
            attr = curses.A_REVERSE if absolute_idx == self.selected_idx else curses.A_NORMAL
            stdscr.addstr(start + i, 0, line[: w - 1], attr)

        stdscr.addstr(h - 1, 0, self.message[: w - 1], curses.A_DIM)
        stdscr.refresh()

    def _interactive_search(self, stdscr) -> None:
        query = self._prompt(stdscr, "Search query")
        if not query:
            self.message = "Search cancelled."
            return

        self.query = query
        self.message = "Searching..."
        response, generated = self.client.search_or_generate(query)
        self.results = response.results
        self.generated_image = generated
        self.selected_idx = 0

        if self.results:
            self.message = f"Found {len(self.results)} results."
        elif generated:
            self.message = "No search results. AI generated fallback image available."
        else:
            self.message = "No results and no AI generation configured."

    def _interactive_generate(self, stdscr) -> None:
        prompt = self._prompt(stdscr, "Generation prompt")
        if not prompt:
            self.message = "Generate cancelled."
            return

        image = self.client.generate_image(prompt)
        if image:
            self.generated_image = image
            self.message = f"Generated image from {image.provider}. Press d to save."
        else:
            self.message = "No generators configured or generation failed."

    def _interactive_download(self, stdscr) -> None:
        dest = self._prompt(stdscr, "Destination directory", default="downloads")
        if not dest:
            self.message = "Download cancelled."
            return

        dest_path = Path(dest)
        saved: list[Path] = []

        if self.results:
            idx = min(self.selected_idx, len(self.results) - 1)
            selected = self.results[idx]
            saved.append(download_photo(selected, dest_path))
        elif self.generated_image:
            saved.append(save_generated_image(self.generated_image, dest_path))

        if saved:
            self.message = f"Saved: {saved[0]}"
        else:
            self.message = "Nothing to download yet. Search or generate first."

    def _show_selected_json(self, stdscr) -> None:
        if not self.results:
            self.message = "No selected result available."
            return

        idx = min(self.selected_idx, len(self.results) - 1)
        payload = asdict(self.results[idx])
        self.message = str(payload)

    def _prompt(self, stdscr, label: str, default: str = "") -> str:
        curses.echo()
        h, w = stdscr.getmaxyx()
        stdscr.move(h - 1, 0)
        stdscr.clrtoeol()
        prompt_text = f"{label}: "
        stdscr.addstr(h - 1, 0, prompt_text)
        stdscr.refresh()
        value = stdscr.getstr(h - 1, len(prompt_text), max(1, w - len(prompt_text) - 1)).decode("utf-8").strip()
        curses.noecho()
        return value or default


def run_tui() -> None:
    ImQuestTUI().run()
