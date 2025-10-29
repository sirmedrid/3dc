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
    st.session_state.camera_distance = 2.0
if 'click_data' not in st.session_state:
    st.session_state.click_data = None

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

def create_3d_piece_mesh(piece_type, color, x, y):
    """Create 3D mesh for chess pieces"""
    meshes = []
    
    # Base cylinder for all pieces
    theta = np.linspace(0, 2*np.pi, 20)
    base_radius = 0.3
    base_height = 0.15
    
    # Create base cylinder
    x_base = []
    y_base = []
    z_base = []
    i_base = []
    j_base = []
    k_base = []
    
    # Bottom circle
    for i in range(len(theta)):
        x_base.append(x + 0.5 + base_radius * np.cos(theta[i]))
        y_base.append(y + 0.5 + base_radius * np.sin(theta[i]))
        z_base.append(0.1)
    
    # Top circle
    for i in range(len(theta)):
        x_base.append(x + 0.5 + base_radius * np.cos(theta[i]))
        y_base.append(y + 0.5 + base_radius * np.sin(theta[i]))
        z_base.append(0.1 + base_height)
    
    # Center points
    x_base.append(x + 0.5)
    y_base.append(y + 0.5)
    z_base.append(0.1)
    
    x_base.append(x + 0.5)
    y_base.append(y + 0.5)
    z_base.append(0.1 + base_height)
    
    n = len(theta)
    center_bottom = 2 * n
    center_top = 2 * n + 1
    
    # Create faces
    for i in range(n):
        next_i = (i + 1) % n
        # Side faces
        i_base.extend([i, next_i, n + next_i])
        j_base.extend([next_i, n + next_i, i])
        k_base.extend([n + next_i, i, n + i])
        
        # Bottom face
        i_base.append(center_bottom)
        j_base.append(i)
        k_base.append(next_i)
        
        # Top face
        i_base.append(center_top)
        j_base.append(n + i)
        k_base.append(n + next_i)
    
    piece_color = '#ffffff' if color else '#333333'
    
    meshes.append(go.Mesh3d(
        x=x_base, y=y_base, z=z_base,
        i=i_base, j=j_base, k=k_base,
        color=piece_color,
        opacity=1.0,
        flatshading=True,
        lighting=dict(ambient=0.5, diffuse=0.7, specular=0.5, roughness=0.5),
        lightposition=dict(x=100, y=100, z=100)
    ))
    
    # Add piece-specific top parts
    top_height = 0.4
    top_z_start = 0.1 + base_height
    
    if piece_type == chess.PAWN:
        # Small sphere on top
        u = np.linspace(0, 2 * np.pi, 15)
        v = np.linspace(0, np.pi, 15)
        sphere_radius = 0.15
        x_sphere = x + 0.5 + sphere_radius * np.outer(np.cos(u), np.sin(v))
        y_sphere = y + 0.5 + sphere_radius * np.outer(np.sin(u), np.sin(v))
        z_sphere = top_z_start + 0.2 + sphere_radius * np.outer(np.ones(np.size(u)), np.cos(v))
        
        meshes.append(go.Surface(
            x=x_sphere, y=y_sphere, z=z_sphere,
            colorscale=[[0, piece_color], [1, piece_color]],
            showscale=False,
            lighting=dict(ambient=0.5, diffuse=0.7, specular=0.5)
        ))
    
    elif piece_type == chess.KING:
        # Tall cylinder with cross on top
        x_king = []
        y_king = []
        z_king = []
        i_king = []
        j_king = []
        k_king = []
        
        king_radius = 0.2
        king_height = 0.5
        
        for i in range(len(theta)):
            x_king.append(x + 0.5 + king_radius * np.cos(theta[i]))
            y_king.append(y + 0.5 + king_radius * np.sin(theta[i]))
            z_king.append(top_z_start)
        
        for i in range(len(theta)):
            x_king.append(x + 0.5 + king_radius * np.cos(theta[i]))
            y_king.append(y + 0.5 + king_radius * np.sin(theta[i]))
            z_king.append(top_z_start + king_height)
        
        for i in range(n):
            next_i = (i + 1) % n
            i_king.extend([i, next_i, n + next_i])
            j_king.extend([next_i, n + next_i, i])
            k_king.extend([n + next_i, i, n + i])
        
        meshes.append(go.Mesh3d(
            x=x_king, y=y_king, z=z_king,
            i=i_king, j=j_king, k=k_king,
            color=piece_color,
            opacity=1.0,
            flatshading=True,
            lighting=dict(ambient=0.5, diffuse=0.7, specular=0.5)
        ))
    
    elif piece_type == chess.QUEEN:
        # Cone shape
        x_queen = []
        y_queen = []
        z_queen = []
        i_queen = []
        j_queen = []
        k_queen = []
        
        queen_height = 0.6
        
        for i in range(len(theta)):
            x_queen.append(x + 0.5 + 0.25 * np.cos(theta[i]))
            y_queen.append(y + 0.5 + 0.25 * np.sin(theta[i]))
            z_queen.append(top_z_start)
        
        x_queen.append(x + 0.5)
        y_queen.append(y + 0.5)
        z_queen.append(top_z_start + queen_height)
        
        apex = len(theta)
        
        for i in range(n):
            next_i = (i + 1) % n
            i_queen.append(i)
            j_queen.append(next_i)
            k_queen.append(apex)
        
        meshes.append(go.Mesh3d(
            x=x_queen, y=y_queen, z=z_queen,
            i=i_queen, j=j_queen, k=k_queen,
            color=piece_color,
            opacity=1.0,
            flatshading=True,
            lighting=dict(ambient=0.5, diffuse=0.7, specular=0.5)
        ))
    
    elif piece_type in [chess.ROOK, chess.BISHOP, chess.KNIGHT]:
        # Medium cylinder
        x_piece = []
        y_piece = []
        z_piece = []
        i_piece = []
        j_piece = []
        k_piece = []
        
        piece_radius = 0.22
        piece_height = 0.45
        
        for i in range(len(theta)):
            x_piece.append(x + 0.5 + piece_radius * np.cos(theta[i]))
            y_piece.append(y + 0.5 + piece_radius * np.sin(theta[i]))
            z_piece.append(top_z_start)
        
        for i in range(len(theta)):
            x_piece.append(x + 0.5 + piece_radius * np.cos(theta[i]))
            y_piece.append(y + 0.5 + piece_radius * np.sin(theta[i]))
            z_piece.append(top_z_start + piece_height)
        
        for i in range(n):
            next_i = (i + 1) % n
            i_piece.extend([i, next_i, n + next_i])
            j_piece.extend([next_i, n + next_i, i])
            k_piece.extend([n + next_i, i, n + i])
        
        meshes.append(go.Mesh3d(
            x=x_piece, y=y_piece, z=z_piece,
            i=i_piece, j=j_piece, k=k_piece,
            color=piece_color,
            opacity=1.0,
            flatshading=True,
            lighting=dict(ambient=0.5, diffuse=0.7, specular=0.5)
        ))
    
    return meshes

def create_2d_board():
    """Create 2D chess board"""
    board = st.session_state.board
    fig = go.Figure()
    
    # Get legal moves for highlighting
    legal_moves = []
    if st.session_state.selected_square is not None:
        legal_moves = get_legal_moves_for_square(st.session_state.selected_square)
    
    # Draw board squares
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            is_light = (rank + file) % 2 == 0
            color = '#ffffff' if is_light else '#000000'
            
            # Check if this square should be highlighted
            is_selected = st.session_state.selected_square == square
            
            # Highlight color
            if square in legal_moves:
                color = '#00ff00'
            
            # Draw square
            fig.add_shape(
                type="rect",
                x0=file, y0=rank, x1=file+1, y1=rank+1,
                fillcolor=color,
                line=dict(color='#ffff00' if is_selected else color, width=3 if is_selected else 1)
            )
            
            # Add piece if present
            piece = board.piece_at(square)
            if piece:
                piece_char = piece.symbol()
                piece_color = '#ffffff' if piece.color else '#333333'
                
                fig.add_trace(go.Scatter(
                    x=[file + 0.5],
                    y=[rank + 0.5],
                    mode='text',
                    text=piece_symbols.get(piece_char, piece_char),
                    textfont=dict(size=40, color=piece_color),
                    showlegend=False,
                    hoverinfo='text',
                    hovertext=chess.square_name(square),
                    customdata=[square]
                ))
    
    # Add file labels
    files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    for i, file_label in enumerate(files):
        fig.add_annotation(
            x=i+0.5, y=-0.3,
            text=file_label,
            showarrow=False,
            font=dict(size=16, color='#ffffff')
        )
    
    # Add rank labels
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
        xaxis=dict(scaleanchor="y", scaleratio=1),
        clickmode='event+select'
    )
    
    return fig

def create_3d_board():
    """Create 3D chess board"""
    board = st.session_state.board
    fig = go.Figure()
    
    # Get legal moves for highlighting
    legal_moves = []
    if st.session_state.selected_square is not None:
        legal_moves = get_legal_moves_for_square(st.session_state.selected_square)
    
    # Create board using Mesh3d
    board_x, board_y, board_z = [], [], []
    board_i, board_j, board_k = [], [], []
    board_colors = []
    
    vertex_count = 0
    
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            is_light = (rank + file) % 2 == 0
            
            # Determine color
            if square in legal_moves:
                color = 'rgb(0, 255, 0)'
            elif st.session_state.selected_square == square:
                color = 'rgb(255, 255, 0)'
            else:
                color = 'rgb(255, 255, 255)' if is_light else 'rgb(50, 50, 50)'
            
            # Create 3D square (on the ground)
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
        lightposition=dict(x=100, y=100, z=100)
    ))
    
    # Add 3D pieces
    for rank in range(8):
        for file in range(8):
            square = chess.square(file, rank)
            piece = board.piece_at(square)
            
            if piece:
                meshes = create_3d_piece_mesh(piece.piece_type, piece.color, file, rank)
                for mesh in meshes:
                    # Add custom data for click detection
                    if hasattr(mesh, 'customdata'):
                        mesh.customdata = [[square]]
                    mesh.hoverinfo = 'text'
                    mesh.hovertext = chess.square_name(square)
                    mesh.showlegend = False
                    fig.add_trace(mesh)
    
    # Calculate camera position
    theta_rad = np.radians(st.session_state.camera_theta)
    phi_rad = np.radians(st.session_state.camera_phi)
    distance = st.session_state.camera_distance
    
    camera_x = distance * np.sin(phi_rad) * np.cos(theta_rad)
    camera_y = distance * np.sin(phi_rad) * np.sin(theta_rad)
    camera_z = distance * np.cos(phi_rad)
    
    # Configure layout - DISABLE INTERACTION
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
            bgcolor='#000000',
            dragmode=False  # Disable dragging
        ),
        height=700,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='#000000',
        plot_bgcolor='#000000',
        clickmode='event+select',
        dragmode=False,  # Disable drag to rotate
        hovermode='closest'
    )
    
    # Add config to disable all interactions except click
    config = {
        'staticPlot': False,
        'scrollZoom': False,
        'doubleClick': False,
        'showTips': False,
        'displayModeBar': False,
        'displaylogo': False
    }
    
    return fig, config

def handle_click(click_data):
    """Handle clicking on board"""
    if click_data is None:
        return
    
    try:
        # Try to get clicked square from hover data
        points = click_data.get('points', [])
        if not points:
            return
        
        point = points[0]
        
        # For 2D mode
        if st.session_state.mode == '2D':
            x = point.get('x')
            y = point.get('y')
            if x is not None and y is not None:
                file = int(x)
                rank = int(y)
                if 0 <= file < 8 and 0 <= rank < 8:
                    square = chess.square(file, rank)
                    process_square_click(square)
        
        # For 3D mode - extract from hover text
        elif st.session_state.mode == '3D':
            hover_text = point.get('hovertext', '')
            if hover_text and len(hover_text) == 2:
                try:
                    square = chess.parse_square(hover_text)
                    process_square_click(square)
                except:
                    pass
    except Exception as e:
        pass

def process_square_click(square):
    """Process a square click"""
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
                st.rerun()
            else:
                st.session_state.selected_square = None
                st.rerun()
    else:
        # Select square if it has a piece of current player
        piece = board.piece_at(square)
        if piece and piece.color == board.turn:
            st.session_state.selected_square = square
            st.rerun()

# Main UI
col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.markdown("### MODE")
    
    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        if st.button("2D", key="2d_btn", use_container_width=True):
            st.session_state.mode = '2D'
            st.session_state.selected_square = None
            st.rerun()
    with mode_col2:
        if st.button("3D", key="3d_btn", use_container_width=True):
            st.session_state.mode = '3D'
            st.session_state.selected_square = None
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

with col2:
    # Display board
    if st.session_state.mode == '2D':
        fig = create_2d_board()
        click_data = st.plotly_chart(fig, use_container_width=True, on_select="rerun", key="2d_board")
        if click_data and click_data.selection and click_data.selection.points:
            handle_click(click_data.selection)
    else:
        fig, config = create_3d_board()
        click_data = st.plotly_chart(fig, use_container_width=True, config=config, on_select="rerun", key="3d_board")
        if click_data and click_data.selection and click_data.selection.points:
            handle_click(click_data.selection)
    
    # 3D Camera controls
    if st.session_state.mode == '3D':
        st.markdown("### CAMERA")
        
        ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4, ctrl_col5, ctrl_col6 = st.columns(6)
        
        with ctrl_col1:
            if st.button("↑", key="cam_up", use_container_width=True):
                st.session_state.camera_phi = max(10, st.session_state.camera_phi - 10)
                st.rerun()
        
        with ctrl_col2:
            if st.button("↓", key="cam_down", use_container_width=True):
                st.session_state.camera_phi = min(80, st.session_state.camera_phi + 10)
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
                st.session_state.camera_distance = max(1.2, st.session_state.camera_distance - 0.2)
                st.rerun()
        
        with ctrl_col6:
            if st.button("-", key="zoom_out", use_container_width=True):
                st.session_state.camera_distance = min(3.5, st.session_state.camera_distance + 0.2)
                st.rerun()

with col3:
    st.markdown("### STATUS")
    
    turn = "WHITE" if st.session_state.board.turn else "BLACK"
    st.markdown(f"**{turn}**")
    
    if st.session_state.board.is_checkmate():
        winner = "BLACK" if st.session_state.board.turn else "WHITE"
        st.markdown(f"**{winner} WINS**")
    elif st.session_state.board.is_stalemate():
        st.markdown("**DRAW**")
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
    else:
        st.markdown("*No moves yet*")
