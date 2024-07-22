import streamlit as st
import numpy as np
import random
import heapq

class Minesweeper:
    def __init__(self, rows=6, cols=6, mines=6):
        self.rows = rows
        self.cols = cols
        self.mines = mines
        self.board = np.zeros((rows, cols), dtype=int)
        self.revealed = np.zeros((rows, cols), dtype=bool)
        self.flagged = np.zeros((rows, cols), dtype=bool)
        self.game_over = False
        self.create_board()

    def create_board(self):
        mine_positions = set()
        while len(mine_positions) < self.mines:
            pos = (random.randint(0, self.rows - 1), random.randint(0, self.cols - 1))
            mine_positions.add(pos)
        for (r, c) in mine_positions:
            self.board[r, c] = -1

        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r, c] == -1:
                    continue
                self.board[r, c] = self.count_adjacent_mines(r, c)

    def count_adjacent_mines(self, row, col):
        count = 0
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = row + dr, col + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols and self.board[nr, nc] == -1:
                    count += 1
        return count

    def reveal_cell(self, row, col):
        if self.game_over or self.revealed[row, col] or self.flagged[row, col]:
            return
        self.revealed[row, col] = True
        if self.board[row, col] == -1:
            self.game_over = True
            return
        if self.board[row, col] == 0:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        self.reveal_cell(nr, nc)

    def toggle_flag(self, row, col):
        if self.game_over or self.revealed[row, col]:
            return
        self.flagged[row, col] = not self.flagged[row, col]

    def check_win(self):
        return np.sum(self.revealed) + self.mines == self.rows * self.cols

    def solve(self):
        return gbfs_algorithm(self)

def gbfs_algorithm(game):
    def heuristic(r, c):
        if game.board[r, c] == -1:
            return 0
        return float('inf') 

    pq = []
    for r in range(game.rows):
        for c in range(game.cols):
            if not game.revealed[r, c]:
                heapq.heappush(pq, (heuristic(r, c), (r, c)))

    visited = np.zeros_like(game.board, dtype=bool)
    mines_found = []

    while pq:
        _, (r, c) = heapq.heappop(pq)
        if game.board[r, c] == -1:
            mines_found.append((r, c))
            game.reveal_cell(r, c)
        visited[r, c] = True

    return mines_found

def main():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: black;
            color: white;
        }
        .stButton button {
            color: black;
            background-color: white;
            width: 80px;
            height: 40px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            border: 2px solid #ccc;
            cursor: pointer;
        }
        .stButton button:hover {
            background-color: #f0f0f0;
            border-color: #bbb;
        }
        .stButton button:disabled {
            color: white;
            background-color: #555;
            border-color: #444;
            cursor: not-allowed;
        }
        .square-button {
            display: inline-block;
            margin: 1px;
        }
        .game-message {
            text-align: center;
            margin-bottom: 20px;
            font-size: 24px;
            font-weight: bold;
            color: red;
        }
        </style>
        """, unsafe_allow_html=True
    )

    st.title("Minesweeper")

    if 'game' not in st.session_state:
        st.session_state.game = Minesweeper()

    game = st.session_state.game

    sidebar = st.sidebar
    sidebar.header("Mines Found")

    if game.game_over:
        st.markdown('<div class="game-message">Game Over!</div>', unsafe_allow_html=True)
    elif game.check_win():
        st.markdown('<div class="game-message">You Win!</div>', unsafe_allow_html=True)

    for r in range(game.rows):
        cols = st.columns(game.cols)
        for c in range(game.cols):
            key = f"{r}-{c}"
            if game.revealed[r, c] or game.game_over:
                if game.board[r, c] == -1:
                    cols[c].button("💣", key=key, disabled=True)
                else:
                    cols[c].button(f"{game.board[r, c]}", key=key, disabled=True)
            else:
                if game.flagged[r, c]:
                    if cols[c].button("🚩", key=key):
                        game.toggle_flag(r, c)
                        st.experimental_rerun()
                else:
                    if cols[c].button(" ", key=key):
                        game.reveal_cell(r, c)
                        st.experimental_rerun()

    if sidebar.button("Solve"):
        mines = game.solve()
        if mines:
            sidebar.write("Mines found at:")
            for (r, c) in mines:
                sidebar.write(f"Mine at ({r}, {c})")
        else:
            sidebar.write("No mines found or game over.")

if __name__ == "__main__":
    main()
