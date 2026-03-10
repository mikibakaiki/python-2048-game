from __future__ import annotations

import random
from copy import deepcopy

import streamlit as st

BOARD_SIZE = 4
WIN_TILE = 2048
NEW_TILE_OPTIONS = (2, 2, 2, 2, 2, 2, 2, 2, 2, 4)

TILE_COLORS = {
    0: ("", "#cdc1b4", "#cdc1b4"),
    2: ("#776e65", "#eee4da", "#eee4da"),
    4: ("#776e65", "#ede0c8", "#ede0c8"),
    8: ("#f9f6f2", "#f2b179", "#f2b179"),
    16: ("#f9f6f2", "#f59563", "#f59563"),
    32: ("#f9f6f2", "#f67c5f", "#f67c5f"),
    64: ("#f9f6f2", "#f65e3b", "#f65e3b"),
    128: ("#f9f6f2", "#edcf72", "#edcf72"),
    256: ("#f9f6f2", "#edcc61", "#edcc61"),
    512: ("#f9f6f2", "#edc850", "#edc850"),
    1024: ("#f9f6f2", "#edc53f", "#edc53f"),
    2048: ("#f9f6f2", "#edc22e", "#edc22e"),
}

st.set_page_config(page_title="2048", page_icon="🎮", layout="centered")


def empty_board() -> list[list[int]]:
    return [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def board_copy(board: list[list[int]]) -> list[list[int]]:
    return deepcopy(board)


def open_positions(board: list[list[int]]) -> list[tuple[int, int]]:
    return [
        (row_index, col_index)
        for row_index, row in enumerate(board)
        for col_index, value in enumerate(row)
        if value == 0
    ]


def spawn_tile(board: list[list[int]]) -> bool:
    candidates = open_positions(board)
    if not candidates:
        return False

    row_index, col_index = random.choice(candidates)
    board[row_index][col_index] = random.choice(NEW_TILE_OPTIONS)
    return True


def fresh_board() -> list[list[int]]:
    board = empty_board()
    spawn_tile(board)
    spawn_tile(board)
    return board


def merge_line_left(line: list[int]) -> tuple[list[int], int]:
    values = [value for value in line if value != 0]
    merged: list[int] = []
    gained_score = 0
    index = 0

    while index < len(values):
        current = values[index]
        if index + 1 < len(values) and values[index + 1] == current:
            current *= 2
            gained_score += current
            index += 2
        else:
            index += 1
        merged.append(current)

    merged.extend([0] * (BOARD_SIZE - len(merged)))
    return merged, gained_score


def move_left(board: list[list[int]]) -> tuple[list[list[int]], int, bool]:
    next_board: list[list[int]] = []
    total_score = 0
    changed = False

    for row in board:
        merged_row, gained_score = merge_line_left(row)
        next_board.append(merged_row)
        total_score += gained_score
        changed = changed or merged_row != row

    return next_board, total_score, changed


def reverse_rows(board: list[list[int]]) -> list[list[int]]:
    return [list(reversed(row)) for row in board]


def transpose(board: list[list[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*board)]


def move_right(board: list[list[int]]) -> tuple[list[list[int]], int, bool]:
    reversed_board = reverse_rows(board)
    moved_board, score_gain, changed = move_left(reversed_board)
    return reverse_rows(moved_board), score_gain, changed


def move_up(board: list[list[int]]) -> tuple[list[list[int]], int, bool]:
    transposed_board = transpose(board)
    moved_board, score_gain, changed = move_left(transposed_board)
    return transpose(moved_board), score_gain, changed


def move_down(board: list[list[int]]) -> tuple[list[list[int]], int, bool]:
    transposed_board = transpose(board)
    moved_board, score_gain, changed = move_right(transposed_board)
    return transpose(moved_board), score_gain, changed


def can_move(board: list[list[int]]) -> bool:
    if open_positions(board):
        return True

    for row_index in range(BOARD_SIZE):
        for col_index in range(BOARD_SIZE):
            current = board[row_index][col_index]
            if row_index + 1 < BOARD_SIZE and board[row_index + 1][col_index] == current:
                return True
            if col_index + 1 < BOARD_SIZE and board[row_index][col_index + 1] == current:
                return True

    return False


def init_state() -> None:
    if "board" not in st.session_state:
        st.session_state.board = fresh_board()
        st.session_state.score = 0
        st.session_state.best_score = 0
        st.session_state.move_count = 0
        st.session_state.game_over = False
        st.session_state.won = False
        st.session_state.last_action = "Game started"


def reset_game() -> None:
    st.session_state.board = fresh_board()
    st.session_state.score = 0
    st.session_state.move_count = 0
    st.session_state.game_over = False
    st.session_state.won = False
    st.session_state.last_action = "Started a new game"


def perform_move(direction: str) -> None:
    if st.session_state.game_over:
        st.session_state.last_action = "Game over — press N to start again"
        return

    moves = {
        "left": move_left,
        "right": move_right,
        "up": move_up,
        "down": move_down,
    }
    move_fn = moves[direction]

    next_board, score_gain, changed = move_fn(board_copy(st.session_state.board))
    if not changed:
        st.session_state.last_action = f"{direction.title()} had no effect"
        return

    spawn_tile(next_board)
    st.session_state.board = next_board
    st.session_state.score += score_gain
    st.session_state.best_score = max(st.session_state.best_score, st.session_state.score)
    st.session_state.move_count += 1
    st.session_state.last_action = f"Moved {direction}"

    if any(value >= WIN_TILE for row in next_board for value in row):
        st.session_state.won = True

    if not can_move(next_board):
        st.session_state.game_over = True
        st.session_state.last_action = "No moves left — press N for a new game"


def tile_style(value: int) -> tuple[str, str, str]:
    if value in TILE_COLORS:
        return TILE_COLORS[value]
    return "#f9f6f2", "#3c3a32", "#3c3a32"


def render_board(board: list[list[int]]) -> str:
    tile_markup: list[str] = []
    for row in board:
        for value in row:
            text_color, background, border = tile_style(value)
            label = "" if value == 0 else str(value)
            font_size = "2rem" if value < 1024 else "1.6rem"
            tile_markup.append(
                (
                    f'<div class="tile" style="color:{text_color};'
                    f'background:{background};border-color:{border};font-size:{font_size};">'
                    f"{label}</div>"
                )
            )

    return f'<div class="board">{"".join(tile_markup)}</div>'


def register_keyboard_shortcuts() -> None:
    with st.container():
        st.button("Move left", key="move_left_arrow", shortcut="Left", on_click=perform_move, args=("left",))
        st.button("Move right", key="move_right_arrow", shortcut="Right", on_click=perform_move, args=("right",))
        st.button("Move up", key="move_up_arrow", shortcut="Up", on_click=perform_move, args=("up",))
        st.button("Move down", key="move_down_arrow", shortcut="Down", on_click=perform_move, args=("down",))
        st.button("Move left (A)", key="move_left_a", shortcut="A", on_click=perform_move, args=("left",))
        st.button("Move right (D)", key="move_right_d", shortcut="D", on_click=perform_move, args=("right",))
        st.button("Move up (W)", key="move_up_w", shortcut="W", on_click=perform_move, args=("up",))
        st.button("Move down (S)", key="move_down_s", shortcut="S", on_click=perform_move, args=("down",))
        st.button("New game", key="new_game_n", shortcut="N", on_click=reset_game)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .st-key-move_left_arrow,
            .st-key-move_right_arrow,
            .st-key-move_up_arrow,
            .st-key-move_down_arrow,
            .st-key-move_left_a,
            .st-key-move_right_d,
            .st-key-move_up_w,
            .st-key-move_down_s,
            .st-key-new_game_n {
                position: absolute !important;
                width: 1px !important;
                height: 1px !important;
                margin: 0 !important;
                padding: 0 !important;
                overflow: hidden !important;
                clip: rect(0, 0, 0, 0) !important;
                white-space: nowrap !important;
                border: 0 !important;
            }

            .block-container {
                max-width: 780px;
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            .hud {
                background: linear-gradient(135deg, #faf8ef 0%, #f3efe6 100%);
                border: 1px solid #e4dccf;
                border-radius: 20px;
                padding: 1.25rem;
                margin-bottom: 1rem;
            }

            .hud h1 {
                color: #776e65;
                font-size: 3rem;
                margin: 0 0 0.5rem 0;
            }

            .hud p {
                color: #776e65;
                font-size: 1rem;
                margin: 0.25rem 0;
            }

            .board {
                display: grid;
                grid-template-columns: repeat(4, minmax(0, 1fr));
                gap: 0.85rem;
                padding: 0.85rem;
                background: #bbada0;
                border-radius: 24px;
                box-shadow: 0 14px 36px rgba(119, 110, 101, 0.18);
            }

            .tile {
                aspect-ratio: 1 / 1;
                border-radius: 18px;
                border: 1px solid transparent;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 800;
                font-family: "Arial", sans-serif;
                line-height: 1;
            }

            .status-card {
                background: #ffffff;
                border: 1px solid #ede7dc;
                border-radius: 18px;
                padding: 1rem 1.25rem;
                margin-top: 1rem;
            }

            .status-card strong {
                color: #776e65;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    init_state()
    inject_styles()
    register_keyboard_shortcuts()

    st.markdown(
        """
        <div class="hud">
            <h1>2048 Vibecoding</h1>
            <p>Keyboard-only controls. Use the arrow keys or <strong>W A S D</strong> to move.</p>
            <p>Press <strong>N</strong> to start a new game. Keep the browser tab focused while playing.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    score_col, best_col, moves_col = st.columns(3)
    score_col.metric("Score", st.session_state.score)
    best_col.metric("Best", st.session_state.best_score)
    moves_col.metric("Moves", st.session_state.move_count)

    if st.session_state.won:
        st.success("You reached 2048! Keep going for a bigger tile.")

    if st.session_state.game_over:
        st.error("Game over. Press N to start a fresh board.")

    st.markdown(render_board(st.session_state.board), unsafe_allow_html=True)

    st.markdown(
        (
            '<div class="status-card">'
            f'<strong>Last action:</strong> {st.session_state.last_action}'
            "</div>"
        ),
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
