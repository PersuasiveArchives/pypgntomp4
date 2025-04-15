import chess.pgn
import chess.svg
import cairosvg
from moviepy.editor import ImageSequenceClip, concatenate_videoclips
import tkinter as tk
from tkinter import filedialog
import tempfile
import os
import random
import string

def choose_pgn_file():
    root = tk.Tk()
    root.withdraw()  
    file_path = filedialog.askopenfilename(
        title="Select PGN File",
        filetypes=[("PGN Files", "*.pgn"), ("All Files", "*.*")]
    )
    return file_path

def generate_random_filename(length=10):
    """Generate a random string of letters and numbers."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length)) + ".mp4"

def process_game(game, tempdir, fps=1):
    """Process a single game and return a video clip"""
    board = game.board()
    images = []
    move_number = 0

    for move in game.mainline_moves():
        board.push(move)
        move_number += 1

        
        svg_data = chess.svg.board(board, size=500)
        svg_path = os.path.join(tempdir, f"frame_{move_number:03d}.svg")
        png_path = os.path.join(tempdir, f"frame_{move_number:03d}.png")

        
        with open(svg_path, 'w') as f:
            f.write(svg_data)
        cairosvg.svg2png(url=svg_path, write_to=png_path)

        images.append(png_path)

    
    clip = ImageSequenceClip(images, fps=fps)

    
    clip = clip.subclip(0, clip.duration - 3)  
    last_frame = ImageSequenceClip([images[-1]], fps=fps)
    last_frame = last_frame.set_duration(3)  

    final_clip = concatenate_videoclips([clip, last_frame])  

    return final_clip

def pgn_to_video(pgn_file_path, output_filename=None, fps=1, combine_games=True):
    with open(pgn_file_path, 'r', encoding='utf-8') as file:
        game = chess.pgn.read_game(file)
        games = []

        while game:
            games.append(game)
            game = chess.pgn.read_game(file)

    with tempfile.TemporaryDirectory() as tempdir:
        clips = []

        for game in games:
            clip = process_game(game, tempdir, fps)
            clips.append(clip)

        if combine_games:
            
            final_clip = concatenate_videoclips(clips)
        else:
            
            final_clip = clips[0]

        
        if not output_filename:
            output_filename = generate_random_filename()

        
        final_clip.write_videofile(output_filename, codec='libx264', audio=False)

if __name__ == "__main__":
    pgn_file = choose_pgn_file()
    if pgn_file:
        print(f"Processing PGN file: {pgn_file}")
        output_name = os.path.splitext(os.path.basename(pgn_file))[0] + "_" + generate_random_filename()
        pgn_to_video(pgn_file, output_filename=output_name, fps=1, combine_games=True)  # Set combine_games=False for separate videos
        print(f"Video saved as: {output_name}")
    else:
        print("No PGN file selected.")
