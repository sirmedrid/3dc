import streamlit as st
import chess
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(page_title="Chess", page_icon="♟", layout="wide")

# Custom CSS - Black and White minimal design
st.markdown("""
<style>
    .main {
        background-color: #000000;
        color: #ffffff;
    }
    .stApp {
        background-color: #000000;
    }
    h1, h2, h3, h4, h5, h6, p, div, span {
        color: #ffffff !important;
    }
    .mode-btn {
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #ffffff;
        padding: 10px 20px;
        cursor: pointer;
        font-weight: bold;
        transition: all 0.3s;
    }
    .mode-btn:hover {
        background-color: #000000;
        color: #ffffff;
    }
    .mode-btn.active {
        background-color: #666666;
        color: #ffffff;
    }
    .control-btn {
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #ffffff;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        font-size: 24px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s;
    }
    .control-btn:hover {
        background-color: #cccccc;
    }
    .joystick-container {
        position: relative;
        width: 150px;
        height: 150px;
        background-color: #1a1a1a;
        border: 3px solid #ffffff;
        border-radius: 50%;
    }
    .joystick-center {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 50px;
        height: 50px;
        background-color: #ffffff;
        border-radius: 50%;
    }
    .highlight-square {
        opacity: 0.6;
        fill: #00ff00;
    }
    .selected-square {
        stroke: #ffff00;
        stroke-width: 3px;
    }
    .stButton button {
        background-color: #ffffff;
        color: #000000;
        border: 2px solid #ffffff;
    }
    .stButton button:hover {
        background-color: #cccccc;
        color: #000000;
    }
    .stTextInput input {
        background-color: #1a1a1a;
        color: #ffffff;
        border: 2px solid #ffffff;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'move_history' not in st.session_state:
    st.session_state.move_history = []
if 'mode' not in st.session_state:
    st.session_state.mode = '3D'
if 'selected_square' not in st.session_state:
    st.session_state.selected_square = None
if 'camera_theta' not in st.session_state:
    st.session_state.camera_theta = 45
if 'camera_phi' not in st.session_state:
    st.session_state.camera_phi = 45
if 'camera_distance' not in st.session_state:
    st.session_state.camera_distance = 1.5

# Piece symbols
piece_symbols = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

def get_legal_moves_for_square(square):
    """Get all legal moves from a given square"""
    board = st.session_state.board
    legal_moves = []
    for move in board.legal_moves:
        if move.from_square == square:
            legal_moves.append(move.to_square)
    return legal_moves

def create_2d_board():
    """Create 2D chess board"""
    board = st.session_state.board
    fig = go.Figure()
    
    # Draw board squares
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            is_light = (rank + file) % 2 == 0
            color = '#ffffff' if is_light else '#000000'
            
            # Check if this square should be highlighted
            is_selected = st.session_state.selected_square == square
            legal_moves = []
            if st.session_state.selected_square is not None:
                legal_moves = get_legal_moves_for_square(st.session_state.selected_square)
            
            # Highlight color
            if square in legal_moves:
                color = '#666666'
            
            # Draw square
            fig.add_shape(
                type="rect",
                x0=file, y0=rank, x1=file+1, y1=rank+1,
                fillcolor=color,
                line=dict(color='#ffffff' if is_selected else color, width=3 if is_selected else 1)
            )
            
            # Add piece if present
            piece = board.piece_at(square)
            if piece:
                piece_char = piece.symbol()
                piece_color = '#ffffff' if piece.color else '#cccccc'
                if not piece.color:  # Black pieces
                    piece_color = '#333333'
                
                fig.add_trace(go.Scatter(
                    x=[file + 0.5],
                    y=[rank + 0.5],
                    mode='text',
                    text=piece_symbols.get(piece_char, piece_char),
                    textfont=dict(size=40, color=piece_color),
                    showlegend=False,
                    hoverinfo='skip'
                ))
    
    # Add file labels (a-h)
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for i, file_label in enumerate(files):
        fig.add_annotation(
            x=i+0.5, y=-0.3,
            text=file_label,
            showarrow=False,
            font=dict(size=16, color='#ffffff')
        )
    
    # Add rank labels (1-8)
    for i in range(8):
        fig.add_annotation(
            x=-0.3, y=i+0.5,
            text=str(i+1),
            showarrow=False,
            font=dict(size=16, color='#ffffff')
        )
    
    fig.update_xaxes(range=[-0.5, 8.5], showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(range=[-0.5, 8.5], showgrid=False, zeroline=False, showticklabels=False)
    fig.update_layout(
        height=700,
        width=700,
        plot_bgcolor='#000000',
        paper_bgcolor='#000000',
        margin=dict(l=50, r=50, t=50, b=50),
        xaxis=dict(scaleanchor="y", scaleratio=1)
    )
    
    return fig

def create_3d_board():
    """Create 3D chess board"""
    board = st.session_state.board
    fig = go.Figure()
    
    # Create board using Mesh3d
    board_x, board_y, board_z = [], [], []
    board_i, board_j, board_k = [], [], []
    board_colors = []
    
    vertex_count = 0
    
    # Get legal moves for highlighting
    legal_moves = []
    if st.session_state.selected_square is not None:
        legal_moves = get_legal_moves_for_square(st.session_state.selected_square)
    
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            is_light = (rank + file) % 2 == 0
            
            # Determine color
            if square in legal_moves:
                color = 'rgb(100, 100, 100)'
            elif st.session_state.selected_square == square:
                color = 'rgb(150, 150, 150)'
            else:
                color = 'rgb(255, 255, 255)' if is_light else 'rgb(50, 50, 50)'
            
            # Create 3D square
            vertices_x = [file, file+1, file+1, file, file, file+1, file+1, file]
            vertices_y = [rank, rank, rank+1, rank+1, rank, rank, rank+1, rank+1]
            vertices_z = [0, 0, 0, 0, 0.1, 0.1, 0.1, 0.1]
            
            board_x.extend(vertices_x)
            board_y.extend(vertices_y)
            board_z.extend(vertices_z)
            
            # Define faces
            faces = [
                [0, 1, 2], [0, 2, 3],  # Bottom
                [4, 5, 6], [4, 6, 7],  # Top
                [0, 1, 5], [0, 5, 4],  # Front
                [2, 3, 7], [2, 7, 6],  # Back
                [0, 3, 7], [0, 7, 4],  # Left
                [1, 2, 6], [1, 6, 5],  # Right
            ]
            
            for face in faces:
                board_i.append(vertex_count + face[0])
                board_j.append(vertex_count + face[1])
                board_k.append(vertex_count + face[2])
                board_colors.append(color)
            
            vertex_count += 8
    
    # Add board mesh
    fig.add_trace(go.Mesh3d(
        x=board_x, y=board_y, z=board_z,
        i=board_i, j=board_j, k=board_k,
        facecolor=board_colors,
        showlegend=False,
        hoverinfo='skip',
        lighting=dict(ambient=0.5, diffuse=0.8, specular=0.3),
        lightposition=dict(x=4, y=4, z=10)
    ))
    
    # Add pieces
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            if piece:
                piece_char = piece.symbol()
                piece_color = '#ffffff' if piece.color else '#333333'
                
                fig.add_trace(go.Scatter3d(
                    x=[file + 0.5],
                    y=[rank + 0.5],
                    z=[0.8],
                    mode='text',
                    text=piece_symbols.get(piece_char, piece_char),
                    textfont=dict(size=35, color=piece_color),
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=f'{chess.square_name(square)}'
                ))
    
    # Calculate camera position from theta and phi
    theta_rad = np.radians(st.session_state.camera_theta)
    phi_rad = np.radians(st.session_state.camera_phi)
    distance = st.session_state.camera_distance
    
    camera_x = distance * np.sin(phi_rad) * np.cos(theta_rad)
    camera_y = distance * np.sin(phi_rad) * np.sin(theta_rad)
    camera_z = distance * np.cos(phi_rad)
    
    # Configure layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[0, 8], showgrid=False, zeroline=False, showticklabels=False, showbackground=False),
            yaxis=dict(range=[0, 8], showgrid=False, zeroline=False, showticklabels=False, showbackground=False),
            zaxis=dict(range=[0, 2], showgrid=False, zeroline=False, showticklabels=False, showbackground=False),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.3),
            camera=dict(
                eye=dict(x=camera_x, y=camera_y, z=camera_z),
                center=dict(x=0, y=0, z=0)
            ),
            bgcolor='#000000'
        ),
        height=700,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='#000000',
        plot_bgcolor='#000000'
    )
    
    return fig

def handle_square_click(square_name):
    """Handle clicking on a square"""
    try:
        square = chess.parse_square(square_name)
        board = st.session_state.board
        
        # If a square is already selected
        if st.session_state.selected_square is not None:
            # Check if clicked square is a legal move destination
            legal_moves = get_legal_moves_for_square(st.session_state.selected_square)
            
            if square in legal_moves:
                # Make the move
                move = chess.Move(st.session_state.selected_square, square)
                
                # Check for pawn promotion
                piece = board.piece_at(st.session_state.selected_square)
                if piece and piece.piece_type == chess.PAWN:
                    if (piece.color and chess.square_rank(square) == 7) or \
                       (not piece.color and chess.square_rank(square) == 0):
                        move = chess.Move(st.session_state.selected_square, square, promotion=chess.QUEEN)
                
                if move in board.legal_moves:
                    board.push(move)
                    st.session_state.move_history.append(move.uci())
                    st.session_state.selected_square = None
                    st.rerun()
            else:
                # Select new square if it has a piece
                piece = board.piece_at(square)
                if piece and piece.color == board.turn:
                    st.session_state.selected_square = square
                else:
                    st.session_state.selected_square = None
                st.rerun()
        else:
            # Select square if it has a piece of current player
            piece = board.piece_at(square)
            if piece and piece.color == board.turn:
                st.session_state.selected_square = square
                st.rerun()
    except:
        pass

# Main UI
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.markdown("### MODE")
    
    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        if st.button("2D", key="2d_btn", use_container_width=True):
            st.session_state.mode = '2D'
            st.rerun()
    with mode_col2:
        if st.button("3D", key="3d_btn", use_container_width=True):
            st.session_state.mode = '3D'
            st.rerun()
    
    st.markdown(f"**Current: {st.session_state.mode}**")
    
    st.markdown("---")
    st.markdown("### CONTROLS")
    
    if st.button("NEW", use_container_width=True):
        st.session_state.board = chess.Board()
        st.session_state.move_history = []
        st.session_state.selected_square = None
        st.rerun()
    
    if st.button("UNDO", use_container_width=True):
        if len(st.session_state.board.move_stack) > 0:
            st.session_state.board.pop()
            if st.session_state.move_history:
                st.session_state.move_history.pop()
            st.session_state.selected_square = None
            st.rerun()
    
    st.markdown("---")
    st.markdown("### MOVE")
    
    move_input = st.text_input("UCI:", placeholder="e2e4")
    if st.button("GO", use_container_width=True) and move_input:
        try:
            move = chess.Move.from_uci(move_input)
            if move in st.session_state.board.legal_moves:
                st.session_state.board.push(move)
                st.session_state.move_history.append(move_input)
                st.session_state.selected_square = None
                st.rerun()
        except:
            pass

with col2:
    # Display board
    if st.session_state.mode == '2D':
        fig = create_2d_board()
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = create_3d_board()
        st.plotly_chart(fig, use_container_width=True)
    
    # Square selection input
    st.markdown("### SELECT SQUARE")
    square_col1, square_col2 = st.columns([3, 1])
    with square_col1:
        square_input = st.text_input("Square:", placeholder="e2", label_visibility="collapsed")
    with square_col2:
        if st.button("SELECT", use_container_width=True):
            handle_square_click(square_input)
    
    # 3D Camera controls
    if st.session_state.mode == '3D':
        st.markdown("### CAMERA")
        
        ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4, ctrl_col5, ctrl_col6 = st.columns(6)
        
        with ctrl_col1:
            if st.button("↑", key="cam_up", use_container_width=True):
                st.session_state.camera_phi = max(5, st.session_state.camera_phi - 10)
                st.rerun()
        
        with ctrl_col2:
            if st.button("↓", key="cam_down", use_container_width=True):
                st.session_state.camera_phi = min(85, st.session_state.camera_phi + 10)
                st.rerun()
        
        with ctrl_col3:
            if st.button("←", key="cam_left", use_container_width=True):
                st.session_state.camera_theta = (st.session_state.camera_theta - 15) % 360
                st.rerun()
        
        with ctrl_col4:
            if st.button("→", key="cam_right", use_container_width=True):
                st.session_state.camera_theta = (st.session_state.camera_theta + 15) % 360
                st.rerun()
        
        with ctrl_col5:
            if st.button("+", key="zoom_in", use_container_width=True):
                st.session_state.camera_distance = max(1.0, st.session_state.camera_distance - 0.2)
                st.rerun()
        
        with ctrl_col6:
            if st.button("-", key="zoom_out", use_container_width=True):
                st.session_state.camera_distance = min(3.0, st.session_state.camera_distance + 0.2)
                st.rerun()

with col3:
    st.markdown("### STATUS")
    
    turn = "WHITE" if st.session_state.board.turn else "BLACK"
    st.markdown(f"**Turn:** {turn}")
    
    if st.session_state.board.is_checkmate():
        winner = "BLACK" if st.session_state.board.turn else "WHITE"
        st.markdown(f"**CHECKMATE - {winner} WINS**")
    elif st.session_state.board.is_stalemate():
        st.markdown("**STALEMATE**")
    elif st.session_state.board.is_check():
        st.markdown("**CHECK**")
    
    st.markdown("---")
    st.markdown("### HISTORY")
    
    if st.session_state.move_history:
        history_text = ""
        for i in range(0, len(st.session_state.move_history), 2):
            move_num = i // 2 + 1
            white_move = st.session_state.move_history[i]
            black_move = st.session_state.move_history[i + 1] if i + 1 < len(st.session_state.move_history) else ""
            history_text += f"{move_num}. {white_move} {black_move}\n"
        
        st.text_area("", value=history_text, height=400, disabled=True, label_visibility="collapsed")
