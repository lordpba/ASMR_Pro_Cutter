import os
import tempfile
import numpy as np
import librosa
from moviepy.editor import VideoFileClip, concatenate_videoclips
from moviepy.audio.fx.all import audio_normalize
from scipy.signal import find_peaks

# --- DIRECTOR PARAMETERS (Tweak these to change the "feel") ---
INPUT_FOLDER = "video_input"  # Folder containing source videos to process
OUTPUT_SUFFIX = "_shorts"     # Suffix for output folders

# Parameters modifiable from GUI or script
TARGET_DURATION = 58.0  # Target duration for final short
PRE_ROLL = 1.2    # Seconds to show BEFORE the click
POST_ROLL = 1.3   # Seconds to show AFTER the click
FINAL_CLIP_EXTRA = 2.0  # Extra seconds for last clip (closing shot)
MERGE_CLIPS = False # If True, merge all clips into one video. If False, save separate clips.
AUDIO_NORMALIZE = False # If True, normalize audio for each clip
# Total clip duration = 2.5s. With 58s target, we'll have ~23 clips.

MIN_FREQ = 1800   # Hz. Filter out low frequencies. We only want the "snap".
HOP_LENGTH = 512  # Constant hop for syncing time/frames in features

# Encoding parameters
ENCODING_PRESET = "nvidia"  # Options: "nvidia", "intel", "amd"
VIDEO_CODEC = "h264_nvenc"
ENCODING_QUALITY = "18"  # CQ value for constant quality
AUDIO_BITRATE = "320k"
THREADS = 4
ENCODING_SPEED = "slow"  # Preset speed: slow, medium, fast

# GPU Presets
GPU_PRESETS = {
    "nvidia": {
        "codec": "h264_nvenc",
        "quality_param": "-cq",
        "quality_value": "18",
        "preset": "slow",
        "extra_params": ["-profile:v", "high", "-rc:v", "vbr", "-gpu", "0"]
    },
    "intel": {
        "codec": "h264_qsv",
        "quality_param": "-global_quality",
        "quality_value": "18",
        "preset": "slow",
        "extra_params": ["-profile:v", "high"]
    },
    "amd": {
        "codec": "h264_amf",
        "quality_param": "-qp_i",
        "quality_value": "18",
        "preset": "quality",
        "extra_params": ["-profile:v", "high", "-quality", "quality"]
    }
}

def calculate_crispness_index(y, sr, hop_length: int = HOP_LENGTH):
    """
    Calculate the 'Crispness' index.
    In a clean video, this distinguishes a sharp cut from background noise.
    """
    # 1. Spectral Centroid (Brightness)
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]
    centroid_norm = librosa.util.normalize(spectral_centroid)
    
    # 2. Onset Strength (Suddenness)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    onset_norm = librosa.util.normalize(onset_env)
    
    # 3. Zero Crossing Rate (Typical of sharp metallic/plastic sounds)
    zcr = librosa.feature.zero_crossing_rate(y, hop_length=hop_length)[0]
    zcr_norm = librosa.util.normalize(zcr)

    # SCORING FORMULA
    # Give high weight to Onset (impact) and Centroid (quality)
    combined_score = (onset_norm * 0.5) + (centroid_norm * 0.3) + (zcr_norm * 0.2)
    
    # Square it to clearly separate top sounds from average ones
    return combined_score ** 2

def generate_asmr_short(video_path, output_folder):
    print(f"\n{'='*60}")
    print(f"--- AUTO DIRECTOR START: {os.path.basename(video_path)} ---")
    print(f"{'='*60}")
    
    # 1. Audio Analysis
    print("Extracting audio from video...")
    clip = VideoFileClip(video_path)
    # Extract audio robustly via temporary WAV (compatible with all codecs)
    sr = 44100
    fd, tmp_wav = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    try:
        clip.audio.write_audiofile(
            tmp_wav,
            fps=sr,
            nbytes=2,
            codec="pcm_s16le",
            ffmpeg_params=["-ac", "1"],
            logger=None,
        )
        y, sr = librosa.load(tmp_wav, sr=None, mono=True)
    finally:
        try:
            os.remove(tmp_wav)
        except OSError:
            pass
    
    print("Calculating crispness index...")
    quality_scores = calculate_crispness_index(y, sr, hop_length=HOP_LENGTH)
    
    # 2. Find peaks (Events)
    # Minimum distance in FRAMES: prevents duplicates too close together
    frames_per_sec = sr / HOP_LENGTH
    min_dist_frames = int((PRE_ROLL + POST_ROLL) * frames_per_sec)
    
    peaks, properties = find_peaks(
        quality_scores, 
        height=np.mean(quality_scores) * 1.2, # Adaptive threshold
        distance=min_dist_frames
    )
    
    peak_times = librosa.frames_to_time(peaks, sr=sr, hop_length=HOP_LENGTH)
    peak_scores = properties['peak_heights']
    
    print(f"Found {len(peak_times)} potential ASMR triggers.")

    # 3. Strategic Selection (Ranking)
    clip_duration = PRE_ROLL + POST_ROLL
    max_clips = int(TARGET_DURATION / clip_duration)
    
    # Create pairs (time, score)
    candidates = list(zip(peak_times, peak_scores))
    
    # Sort by SCORE (the best sounds overall)
    candidates.sort(key=lambda x: x[1], reverse=True)
    
    # Take the best to fill the time
    best_moments = candidates[:max_clips]
    
    # Re-sort by TIME (chronological order)
    best_moments.sort(key=lambda x: x[0])
    
    final_timestamps = [x[0] for x in best_moments]

    # 4. Save Clips
    if MERGE_CLIPS:
        print(f"Preparing {len(final_timestamps)} clips for merging...")
    else:
        print(f"Saving {len(final_timestamps)} separate clips to '{output_folder}/'...")
    
    # Create folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    clips_to_merge = []
    
    for idx, t_event in enumerate(final_timestamps, start=1):
        # Check if this is the last clip
        is_last_clip = (idx == len(final_timestamps))
        
        # Asymmetric cutting logic (Pre-Roll vs Post-Roll)
        t_start = max(0, t_event - PRE_ROLL)
        
        # Last clip gets extra time for closing shot
        if is_last_clip:
            t_end = min(clip.duration, t_event + POST_ROLL + FINAL_CLIP_EXTRA)
        else:
            t_end = min(clip.duration, t_event + POST_ROLL)
        
        # Cut - preserve original dimensions
        sub = clip.subclip(t_start, t_end)
        
        # Micro-fade audio (essential to avoid 'pop')
        sub = sub.audio_fadein(0.05).audio_fadeout(0.05)
        
        # Normalize audio if requested
        if AUDIO_NORMALIZE:
            sub = sub.fx(audio_normalize)
        
        if MERGE_CLIPS:
            clips_to_merge.append(sub)
        else:
            # Save with timestamp in name for guaranteed sorting
            time_marker = f"{int(t_event):04d}s"
            output_filename = os.path.join(output_folder, f"clip_{idx:03d}_at_{time_marker}.mp4")
            
            # Get encoding preset
            preset = GPU_PRESETS.get(ENCODING_PRESET, GPU_PRESETS["nvidia"])
            
            # Build ffmpeg parameters
            ffmpeg_params = [
                "-pix_fmt", "yuv420p",
                preset["quality_param"], preset["quality_value"],
                "-b:a", AUDIO_BITRATE,
            ] + preset["extra_params"]
            
            try:
                sub.write_videofile(
                    output_filename,
                    codec=preset["codec"],
                    audio_codec="aac",
                    fps=clip.fps,  # Keep original FPS
                    preset=preset["preset"],
                    bitrate=None,  # Disable fixed bitrate for quality-based encoding
                    threads=THREADS,
                    logger=None,
                    ffmpeg_params=ffmpeg_params
                )
                print(f"  ✓ Clip {idx}/{len(final_timestamps)}: {output_filename}")
            except Exception as e:
                print(f"  ✗ Error on clip {idx}: {e}")

    if MERGE_CLIPS and clips_to_merge:
        print(f"Merging {len(clips_to_merge)} clips into one video...")
        try:
            final_clip = concatenate_videoclips(clips_to_merge)
            
            output_filename = os.path.join(output_folder, "final_short.mp4")
            
            # Get encoding preset
            preset = GPU_PRESETS.get(ENCODING_PRESET, GPU_PRESETS["nvidia"])
            
            # Build ffmpeg parameters
            ffmpeg_params = [
                "-pix_fmt", "yuv420p",
                preset["quality_param"], preset["quality_value"],
                "-b:a", AUDIO_BITRATE,
            ] + preset["extra_params"]
            
            final_clip.write_videofile(
                output_filename,
                codec=preset["codec"],
                audio_codec="aac",
                fps=clip.fps,
                preset=preset["preset"],
                bitrate=None,
                threads=THREADS,
                logger=None,
                ffmpeg_params=ffmpeg_params
            )
            print(f"  ✓ Saved merged video: {output_filename}")
        except Exception as e:
            print(f"  ✗ Error saving merged video: {e}")

    print(f"\n✅ Completed '{os.path.basename(video_path)}'!")
    
    clip.close()


def process_single_video(video_path, output_folder=None):
    """Process a single video.
    
    Args:
        video_path: Path to video file
        output_folder: Output folder (optional). If None, uses same folder as video.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video not found: {video_path}")
    
    # If output not specified, create folder in same directory as video
    if output_folder is None:
        video_dir = os.path.dirname(os.path.abspath(video_path))
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        output_folder = os.path.join(video_dir, f"{video_name}{OUTPUT_SUFFIX}")
    
    generate_asmr_short(video_path, output_folder)
    return output_folder


def process_all_videos():
    """Process all videos in INPUT_FOLDER"""
    
    # Create input folder if it doesn't exist
    if not os.path.exists(INPUT_FOLDER):
        os.makedirs(INPUT_FOLDER)
        print(f"Created folder '{INPUT_FOLDER}/'")
        print(f"Place videos to process in this folder and rerun the program.")
        return
    
    # Find all videos (mp4, mov, avi, mkv)
    video_extensions = ('.mp4', '.MP4', '.mov', '.MOV', '.avi', '.AVI', '.mkv', '.MKV')
    video_files = [f for f in os.listdir(INPUT_FOLDER) 
                   if f.endswith(video_extensions)]
    
    if not video_files:
        print(f"No videos found in '{INPUT_FOLDER}/'")
        print(f"Supported formats: {', '.join(video_extensions)}")
        return
    
    print(f"Found {len(video_files)} videos to process:")
    for vf in video_files:
        print(f"  - {vf}")
    print()
    
    # Process each video
    for video_file in video_files:
        video_path = os.path.join(INPUT_FOLDER, video_file)
        
        try:
            process_single_video(video_path)
        except Exception as e:
            print(f"\n❌ ERROR processing '{video_file}':")
            print(f"   {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*60}")
    print("🎬 PROCESSING COMPLETE!")
    print(f"{'='*60}")


if __name__ == "__main__":
    process_all_videos()