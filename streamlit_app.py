import streamlit as st
import chess
import plotly.graph_objects as go
import numpy as np

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'selected_square' not in st.session_state:
    st.session_state.selected_square = None
if 'move_history' not in st.session_state:
    st.session_state.move_history = []

# Piece shapes and colors
piece_symbols = {
    'P': '♙', 'N': '♞', 'B': '♗', 'R': '♜', 'Q': '♛', 'K': '♚',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

def create_3d_chess_board():
    board = st.session_state.board
    fig = go.Figure()
    
    # Create chess board squares
    for rank in range(8):
        for file in range(8):
            # Alternate colors for chess board
            color = 'lightgray' if (rank + file) % 2 == 0 else 'saddlebrown'
            
            # Create square
            x = [file, file+1, file+1, file, file]
            y = [rank, rank, rank+1, rank+1, rank]
            z = [0, 0, 0, 0, 0]
            
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode='lines',
                line=dict(color=color, width=8),
                fill='toself',
                fillcolor=color,
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Add piece if present
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            if piece:
                piece_char = piece.symbol()
                piece_color = 'white' if piece.color else 'black'
                
                # Create 3D piece representation (cylinder for simplicity)
                height = 0.8 if piece.piece_type == chess.KING else 0.6
                
                fig.add_trace(go.Scatter3d(
                    x=[file + 0.5],
                    y=[rank + 0.5],
                    z=[height],
                    mode='text',
                    text=piece_symbols.get(piece_char, piece_char),
                    textfont=dict(size=30, color=piece_color),
                    showlegend=False,
                    hovertemplate=f'{chess.square_name(square)}: {piece_char}<extra></extra>'
                ))
    
    # Configure layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-0.5, 8.5], showticklabels=True, 
                      ticktext=['a','b','c','d','e','f','g','h'],
                      tickvals=list(range(8))),
            yaxis=dict(range=[-0.5, 8.5], showticklabels=True,
                      ticktext=['1','2','3','4','5','6','7','8'],
                      tickvals=list(range(8))),
            zaxis=dict(range=[0, 2], showticklabels=False),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.3),
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=1.2)
            )
        ),
        height=700,
        margin=dict(l=0, r=0, t=30, b=0),
        title="3D Chess Board"
    )
    
    return fig

# Streamlit UI
st.title("♟️ 3D Chess Game")

col1, col2 = st.columns([3, 1])

with col1:
    # Display 3D chess board
    fig = create_3d_chess_board()
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Game Controls")
    
    # Turn indicator
    turn = "White" if st.session_state.board.turn else "Black"
    st.write(f"**Turn:** {turn}")
    
    # Move input
    st.write("**Make a Move**")
    st.write("Enter move in UCI format (e.g., e2e4)")
    move_input = st.text_input("Move:", key="move_input")
    
    if st.button("Make Move"):
        try:
            move = chess.Move.from_uci(move_input)
            if move in st.session_state.board.legal_moves:
                st.session_state.board.push(move)
                st.session_state.move_history.append(move_input)
                st.success(f"Move {move_input} made!")
                st.rerun()
            else:
                st.error("Illegal move!")
        except:
            st.error("Invalid move format!")
    
    # Reset button
    if st.button("Reset Game"):
        st.session_state.board = chess.Board()
        st.session_state.move_history = []
        st.rerun()
    
    # Game status
    st.write("---")
    if st.session_state.board.is_checkmate():
        winner = "Black" if st.session_state.board.turn else "White"
        st.error(f"Checkmate! {winner} wins!")
    elif st.session_state.board.is_stalemate():
        st.warning("Stalemate!")
    elif st.session_state.board.is_check():
        st.warning("Check!")
    
    # Move history
    if st.session_state.move_history:
        st.write("**Move History:**")
        for i, move in enumerate(st.session_state.move_history, 1):
            st.text(f"{i}. {move}")

# Instructions
with st.expander("How to Play"):
    st.write("""
    **Move Format:** Use UCI notation (e.g., e2e4, g1f3)
    - First two characters: starting square
    - Last two characters: destination square
    - For promotion, add piece letter (e.g., e7e8q for queen promotion)
    
    **Examples:**
    - e2e4 (pawn to e4)
    - g1f3 (knight to f3)
    - e1g1 (kingside castle)
    - e7e8q (pawn promotion to queen)
    """)
