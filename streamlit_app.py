import streamlit as st
import chess
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(page_title="3D Chess Arena", page_icon="♟️", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 1rem 0;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .move-button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        border-radius: 5px;
        font-weight: bold;
        cursor: pointer;
    }
    .status-alert {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-weight: bold;
    }
    .check-alert { background-color: #fff3cd; color: #856404; }
    .checkmate-alert { background-color: #f8d7da; color: #721c24; }
    .stalemate-alert { background-color: #d1ecf1; color: #0c5460; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'board' not in st.session_state:
    st.session_state.board = chess.Board()
if 'move_history' not in st.session_state:
    st.session_state.move_history = []
if 'white_time' not in st.session_state:
    st.session_state.white_time = 600  # 10 minutes
if 'black_time' not in st.session_state:
    st.session_state.black_time = 600
if 'game_mode' not in st.session_state:
    st.session_state.game_mode = 'Standard'
if 'captured_pieces' not in st.session_state:
    st.session_state.captured_pieces = {'white': [], 'black': []}
if 'move_times' not in st.session_state:
    st.session_state.move_times = []

# Piece symbols
piece_symbols = {
    'P': '♙', 'N': '♘', 'B': '♗', 'R': '♖', 'Q': '♕', 'K': '♔',
    'p': '♟', 'n': '♞', 'b': '♝', 'r': '♜', 'q': '♛', 'k': '♚'
}

piece_values = {
    chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
    chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
}

def create_3d_chess_board():
    board = st.session_state.board
    fig = go.Figure()
    
    # Create board base
    board_x = []
    board_y = []
    board_z = []
    board_i = []
    board_j = []
    board_k = []
    board_colors = []
    
    vertex_count = 0
    
    for rank in range(8):
        for file in range(8):
            # Square color
            is_light = (rank + file) % 2 == 0
            color = 'rgb(240, 217, 181)' if is_light else 'rgb(181, 136, 99)'
            
            # Create a 3D square (thin box)
            vertices_x = [file, file+1, file+1, file, file, file+1, file+1, file]
            vertices_y = [rank, rank, rank+1, rank+1, rank, rank, rank+1, rank+1]
            vertices_z = [0, 0, 0, 0, 0.05, 0.05, 0.05, 0.05]
            
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
        lighting=dict(ambient=0.7, diffuse=0.8, specular=0.2),
        lightposition=dict(x=4, y=4, z=10)
    ))
    
    # Add coordinate labels
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for i, file_label in enumerate(files):
        fig.add_trace(go.Scatter3d(
            x=[i + 0.5], y=[-0.3], z=[0],
            mode='text',
            text=file_label,
            textfont=dict(size=14, color='black'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    for i in range(8):
        fig.add_trace(go.Scatter3d(
            x=[-0.3], y=[i + 0.5], z=[0],
            mode='text',
            text=str(i + 1),
            textfont=dict(size=14, color='black'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Add pieces
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            if piece:
                piece_char = piece.symbol()
                piece_color = '#FFFFFF' if piece.color else '#2C2C2C'
                piece_size = 40 if piece.piece_type == chess.KING else 35
                
                # Create 3D piece with shadow
                fig.add_trace(go.Scatter3d(
                    x=[file + 0.5],
                    y=[rank + 0.5],
                    z=[0.05],
                    mode='text',
                    text=piece_symbols.get(piece_char, piece_char),
                    textfont=dict(
                        size=piece_size, 
                        color=piece_color,
                        family='Arial Black'
                    ),
                    showlegend=False,
                    hovertemplate=f'<b>{chess.square_name(square)}</b><br>' +
                                  f'Piece: {chess.piece_name(piece.piece_type).title()}<br>' +
                                  f'Color: {"White" if piece.color else "Black"}<extra></extra>'
                ))
    
    # Configure layout
    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-0.5, 8.5], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[-0.5, 8.5], showgrid=False, zeroline=False, showticklabels=False),
            zaxis=dict(range=[-0.2, 2], showgrid=False, zeroline=False, showticklabels=False),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=0.25),
            camera=dict(
                eye=dict(x=1.3, y=1.3, z=1.0),
                center=dict(x=0, y=0, z=-0.1)
            ),
            bgcolor='rgb(250, 250, 250)'
        ),
        height=700,
        margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def calculate_material_advantage():
    board = st.session_state.board
    white_material = 0
    black_material = 0
    
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_values.get(piece.piece_type, 0)
            if piece.color:
                white_material += value
            else:
                black_material += value
    
    return white_material - black_material

def get_legal_moves_for_square(square_name):
    try:
        square = chess.parse_square(square_name)
        board = st.session_state.board
        legal_moves = [move for move in board.legal_moves if move.from_square == square]
        return [chess.square_name(move.to_square) for move in legal_moves]
    except:
        return []

# Header
st.markdown('<div class="main-header">♟️ 3D Chess Arena ♔</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/ChessSet.jpg/300px-ChessSet.jpg", 
             use_container_width=True)
    
    st.markdown("### ⚙️ Game Settings")
    
    game_mode = st.selectbox(
        "Game Mode",
        ["Standard", "Blitz (5min)", "Rapid (10min)", "Classical (30min)"],
        index=["Standard", "Blitz (5min)", "Rapid (10min)", "Classical (30min)"].index(st.session_state.game_mode)
    )
    st.session_state.game_mode = game_mode
    
    st.markdown("---")
    st.markdown("### 📊 Game Statistics")
    
    total_moves = len(st.session_state.move_history)
    st.metric("Total Moves", total_moves)
    
    material_adv = calculate_material_advantage()
    if material_adv > 0:
        st.metric("Material Advantage", f"White +{material_adv}")
    elif material_adv < 0:
        st.metric("Material Advantage", f"Black +{abs(material_adv)}")
    else:
        st.metric("Material Advantage", "Equal")
    
    st.markdown("---")
    st.markdown("### 🎯 Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Game", use_container_width=True):
            st.session_state.board = chess.Board()
            st.session_state.move_history = []
            st.session_state.captured_pieces = {'white': [], 'black': []}
            st.session_state.move_times = []
            st.rerun()
    
    with col2:
        if st.button("↶ Undo Move", use_container_width=True):
            if len(st.session_state.board.move_stack) > 0:
                st.session_state.board.pop()
                if st.session_state.move_history:
                    st.session_state.move_history.pop()
                st.rerun()
    
    if st.button("🔀 Flip Board", use_container_width=True):
        st.info("Rotate the 3D board with your mouse!")
    
    st.markdown("---")
    st.markdown("### 📜 Export Options")
    
    if st.session_state.move_history:
        pgn_moves = " ".join([f"{i//2 + 1}." if i % 2 == 0 else "" + move 
                              for i, move in enumerate(st.session_state.move_history)])
        st.download_button(
            "💾 Download PGN",
            data=f"[Event \"3D Chess Game\"]\n[Date \"{datetime.now().strftime('%Y.%m.%d')}\"]\n\n{pgn_moves}",
            file_name=f"chess_game_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pgn",
            mime="text/plain",
            use_container_width=True
        )

# Main content
col_left, col_center, col_right = st.columns([1, 3, 1])

with col_left:
    st.markdown("### ⚪ White Pieces")
    
    # Captured white pieces
    if st.session_state.captured_pieces['white']:
        captured_white = " ".join([piece_symbols.get(p, p) for p in st.session_state.captured_pieces['white']])
        st.markdown(f"**Captured:** {captured_white}")
    else:
        st.markdown("*No captures yet*")
    
    st.markdown("---")
    
    # Move suggestion
    st.markdown("### 💡 Legal Moves")
    square_check = st.text_input("Check square (e.g., e2):", key="square_check")
    if square_check:
        legal_moves = get_legal_moves_for_square(square_check)
        if legal_moves:
            st.success(f"**Legal moves:** {', '.join(legal_moves)}")
        else:
            st.warning("No legal moves or invalid square")

with col_center:
    # Game status
    turn = "⚪ White" if st.session_state.board.turn else "⚫ Black"
    
    status_col1, status_col2, status_col3 = st.columns(3)
    with status_col1:
        st.markdown(f"<div class='stats-card'><h3>{turn}</h3><p>Current Turn</p></div>", unsafe_allow_html=True)
    with status_col2:
        move_count = len(st.session_state.move_history)
        st.markdown(f"<div class='stats-card'><h3>{move_count}</h3><p>Moves Played</p></div>", unsafe_allow_html=True)
    with status_col3:
        if st.session_state.board.is_check():
            status_text = "CHECK!"
        elif st.session_state.board.is_checkmate():
            status_text = "CHECKMATE!"
        elif st.session_state.board.is_stalemate():
            status_text = "STALEMATE"
        else:
            status_text = "In Progress"
        st.markdown(f"<div class='stats-card'><h3>{status_text}</h3><p>Game Status</p></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 3D Chess Board
    fig = create_3d_chess_board()
    st.plotly_chart(fig, use_container_width=True)
    
    # Move input
    st.markdown("### 🎮 Make Your Move")
    move_col1, move_col2, move_col3 = st.columns([3, 1, 1])
    
    with move_col1:
        move_input = st.text_input(
            "Enter move (UCI format: e2e4, e7e8q for promotion):",
            key="move_input",
            placeholder="e.g., e2e4, g1f3, e1g1"
        )
    
    with move_col2:
        make_move = st.button("▶️ Move", use_container_width=True)
    
    with move_col3:
        random_move = st.button("🎲 Random", use_container_width=True)
    
    if make_move and move_input:
        try:
            move = chess.Move.from_uci(move_input)
            if move in st.session_state.board.legal_moves:
                # Track captured pieces
                captured = st.session_state.board.piece_at(move.to_square)
                if captured:
                    color = 'white' if captured.color else 'black'
                    st.session_state.captured_pieces[color].append(captured.symbol())
                
                st.session_state.board.push(move)
                st.session_state.move_history.append(move_input)
                st.session_state.move_times.append(datetime.now())
                st.success(f"✅ Move {move_input} executed!")
                st.rerun()
            else:
                st.error("❌ Illegal move! Please try again.")
        except Exception as e:
            st.error(f"❌ Invalid move format! Use UCI notation (e.g., e2e4)")
    
    if random_move:
        legal_moves = list(st.session_state.board.legal_moves)
        if legal_moves:
            import random
            move = random.choice(legal_moves)
            st.session_state.board.push(move)
            st.session_state.move_history.append(move.uci())
            st.session_state.move_times.append(datetime.now())
            st.success(f"🎲 Random move: {move.uci()}")
            st.rerun()

with col_right:
    st.markdown("### ⚫ Black Pieces")
    
    # Captured black pieces
    if st.session_state.captured_pieces['black']:
        captured_black = " ".join([piece_symbols.get(p, p) for p in st.session_state.captured_pieces['black']])
        st.markdown(f"**Captured:** {captured_black}")
    else:
        st.markdown("*No captures yet*")
    
    st.markdown("---")
    
    # Move history
    st.markdown("### 📋 Move History")
    if st.session_state.move_history:
        history_text = ""
        for i in range(0, len(st.session_state.move_history), 2):
            move_num = i // 2 + 1
            white_move = st.session_state.move_history[i]
            black_move = st.session_state.move_history[i + 1] if i + 1 < len(st.session_state.move_history) else "..."
            history_text += f"{move_num}. {white_move} {black_move}\n"
        
        st.text_area("Moves:", value=history_text, height=300, disabled=True)
    else:
        st.info("No moves yet. Start playing!")

# Instructions expander
with st.expander("📖 How to Play"):
    st.markdown("""
    ### Game Controls
    - **UCI Notation**: Enter moves like `e2e4` (from e2 to e4)
    - **Castling**: `e1g1` (kingside), `e1c1` (queenside)
    - **Promotion**: `e7e8q` (promote to queen), `e7e8n` (knight), etc.
    - **Check Square**: Enter a square to see all legal moves from that position
    
    ### Features
    - 🎨 **3D Visualization**: Rotate and zoom the board with your mouse
    - 🎲 **Random Move**: Let the computer make a random legal move
    - ↶ **Undo**: Take back your last move
    - 💾 **Export**: Download your game in PGN format
    - 📊 **Statistics**: Track material advantage and move count
    
    ### Tips
    - Click and drag on the 3D board to rotate
    - Scroll to zoom in/out
    - Watch for check, checkmate, and stalemate notifications
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Built with ❤️ using Streamlit & Plotly | "
    "Powered by python-chess</div>",
    unsafe_allow_html=True
)
