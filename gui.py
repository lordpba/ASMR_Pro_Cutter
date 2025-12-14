import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import sys
import json
import webbrowser
from pathlib import Path

# Import main logic
import main

SETTINGS_FILE = "settings.json"

class TextRedirector:
    def __init__(self, text_widget, root):
        self.text_widget = text_widget
        self.root = root

    def write(self, string):
        self.root.after(0, lambda: self._insert(string))

    def _insert(self, string):
        try:
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, string)
            self.text_widget.see(tk.END)
            self.text_widget.config(state=tk.DISABLED)
        except:
            pass

    def flush(self):
        pass

class ASMRCutterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ASMR Pro Cutter")
        self.root.geometry("850x1000")
        self.root.resizable(True, True)
        
        # Variables
        self.input_video = tk.StringVar(value="")
        self.output_folder = tk.StringVar(value="")
        self.target_duration = tk.DoubleVar(value=main.TARGET_DURATION)
        self.pre_roll = tk.DoubleVar(value=main.PRE_ROLL)
        self.post_roll = tk.DoubleVar(value=main.POST_ROLL)
        self.final_clip_extra = tk.DoubleVar(value=main.FINAL_CLIP_EXTRA)
        self.min_freq = tk.IntVar(value=main.MIN_FREQ)
        self.hop_length = tk.IntVar(value=main.HOP_LENGTH)
        self.encoding_preset = tk.StringVar(value=main.ENCODING_PRESET)
        self.encoding_quality = tk.StringVar(value=main.ENCODING_QUALITY)
        self.audio_bitrate = tk.StringVar(value=main.AUDIO_BITRATE)
        self.threads = tk.IntVar(value=main.THREADS)
        self.merge_clips = tk.BooleanVar(value=main.MERGE_CLIPS)
        self.audio_normalize = tk.BooleanVar(value=main.AUDIO_NORMALIZE)
        self.processing = False
        
        # Load saved settings if exist
        self.load_settings()
        
        self.create_menu()
        self.setup_ui()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save Settings", command=self.save_settings)
        file_menu.add_command(label="Load Settings", command=self.load_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Guide / Instructions", command=self.show_guide)
        help_menu.add_command(label="Support & Request Feature", command=self.show_support)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)

    def show_support(self):
        msg = "If you want to request a new feature or need support, please consider buying me a coffee!\n\n" \
              "Write your request in the donation comment.\n" \
              "My commitment to adding features is fueled by coffee! ☕\n\n" \
              "Click OK to open the donation page."
        if messagebox.askokcancel("Support & Request Feature", msg, icon='info'):
            self.open_coffee()

    def show_guide(self):
        guide_text = """
ASMR Pro Cutter - Quick Guide

1. Select Source Video:
   Choose your long ASMR video file (MP4, MOV, etc.).

2. Output Folder (Optional):
   If left empty, a new folder will be created automatically in the same location as the video.

3. Clip Parameters:
   - Total target duration: The desired length of the final short (e.g., 58s).
   - Pre-roll: Seconds to include BEFORE the detected sound (click/snap).
   - Post-roll: Seconds to include AFTER the detected sound.
   - Final clip extra: Extra time added to the very last clip for a smooth ending.

4. Advanced Parameters:
   - Min frequency: Filter out low rumbles. Higher values focus on sharp clicks.
   - Hop length: Precision of audio analysis.

5. Encoding Settings:
   - GPU Preset: Choose your GPU brand (NVIDIA, Intel, AMD) for hardware acceleration.
   - Quality (CQ): Lower is better quality (0-51). 18 is near lossless.
   - Audio bitrate: 320k is recommended for ASMR.

6. Start Processing:
   Click the green button and wait. The log will show progress.
        """
        messagebox.showinfo("Guide / Instructions", guide_text)

    def show_about(self):
        about_text = """
ASMR Pro Cutter v1.0
Created by lordpba

An automated tool to extract crisp ASMR triggers from long videos and compile them into YouTube Shorts.

Features:
- Smart audio analysis to find clicks/snaps
- GPU accelerated encoding (NVIDIA/Intel/AMD)
- High quality audio preservation
- Batch processing ready
        """
        messagebox.showinfo("About", about_text)
    
    def save_settings(self):
        """Save current settings to JSON file"""
        settings = {
            "target_duration": self.target_duration.get(),
            "pre_roll": self.pre_roll.get(),
            "post_roll": self.post_roll.get(),
            "final_clip_extra": self.final_clip_extra.get(),
            "min_freq": self.min_freq.get(),
            "hop_length": self.hop_length.get(),
            "encoding_preset": self.encoding_preset.get(),
            "encoding_quality": self.encoding_quality.get(),
            "audio_bitrate": self.audio_bitrate.get(),
            "threads": self.threads.get(),
            "merge_clips": self.merge_clips.get(),
            "audio_normalize": self.audio_normalize.get()
        }
        try:
            with open(SETTINGS_FILE, 'w') as f:
                json.dump(settings, f, indent=2)
            self.log("✅ Settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully!")
        except Exception as e:
            self.log(f"❌ Error saving settings: {e}")
            messagebox.showerror("Error", f"Could not save settings: {e}")
    
    def load_settings(self):
        """Load settings from JSON file"""
        if not os.path.exists(SETTINGS_FILE):
            return
        
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
            
            self.target_duration.set(settings.get("target_duration", main.TARGET_DURATION))
            self.pre_roll.set(settings.get("pre_roll", main.PRE_ROLL))
            self.post_roll.set(settings.get("post_roll", main.POST_ROLL))
            self.final_clip_extra.set(settings.get("final_clip_extra", main.FINAL_CLIP_EXTRA))
            self.min_freq.set(settings.get("min_freq", main.MIN_FREQ))
            self.hop_length.set(settings.get("hop_length", main.HOP_LENGTH))
            self.encoding_preset.set(settings.get("encoding_preset", main.ENCODING_PRESET))
            self.encoding_quality.set(settings.get("encoding_quality", main.ENCODING_QUALITY))
            self.audio_bitrate.set(settings.get("audio_bitrate", main.AUDIO_BITRATE))
            self.threads.set(settings.get("threads", main.THREADS))
            self.merge_clips.set(settings.get("merge_clips", main.MERGE_CLIPS))
            self.audio_normalize.set(settings.get("audio_normalize", main.AUDIO_NORMALIZE))
        except Exception as e:
            print(f"Error loading settings: {e}")
        
    def setup_ui(self):
        # Header
        header_frame = tk.Frame(self.root, bg="#2b2b2b", height=80)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title = tk.Label(
            header_frame, 
            text="🎬 ASMR Pro Cutter",
            font=("Segoe UI", 20, "bold"),
            bg="#2b2b2b",
            fg="white"
        )
        title.pack(pady=20)
        
        # Main content
        main_frame = tk.Frame(self.root, padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 1. Video Input
        video_frame = tk.LabelFrame(main_frame, text="📹 Source Video", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        video_frame.pack(fill=tk.X, pady=(0, 10))
        
        video_input_frame = tk.Frame(video_frame)
        video_input_frame.pack(fill=tk.X)
        
        tk.Entry(
            video_input_frame, 
            textvariable=self.input_video, 
            font=("Segoe UI", 9),
            state="readonly"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            video_input_frame,
            text="Select Video",
            command=self.browse_video,
            font=("Segoe UI", 9),
            bg="#0078d4",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT)
        
        # 2. Output Folder (optional)
        output_frame = tk.LabelFrame(main_frame, text="📁 Output Folder (optional - leave empty for auto)", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        output_frame.pack(fill=tk.X, pady=(0, 10))
        
        output_input_frame = tk.Frame(output_frame)
        output_input_frame.pack(fill=tk.X)
        
        tk.Entry(
            output_input_frame, 
            textvariable=self.output_folder, 
            font=("Segoe UI", 9),
            state="readonly"
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        tk.Button(
            output_input_frame,
            text="Browse",
            command=self.browse_output,
            font=("Segoe UI", 9),
            bg="#5c5c5c",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=15,
            pady=5
        ).pack(side=tk.RIGHT, padx=(0, 5))
        
        tk.Button(
            output_input_frame,
            text="Reset",
            command=lambda: self.output_folder.set(""),
            font=("Segoe UI", 9),
            bg="#8c8c8c",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack(side=tk.RIGHT)
        
        # Merge clips option
        tk.Checkbutton(
            output_frame,
            text="Merge all clips into a single video file",
            variable=self.merge_clips,
            font=("Segoe UI", 9),
            onvalue=True,
            offvalue=False
        ).pack(anchor=tk.W, pady=(5, 0))
        
        # 3. Parameters
        params_frame = tk.LabelFrame(main_frame, text="⚙️ Clip Parameters", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        params_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Grid for parameters
        params_grid = tk.Frame(params_frame)
        params_grid.pack(fill=tk.X)
        
        # Target Duration
        tk.Label(params_grid, text="Total target duration (s):", font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, pady=5)
        tk.Spinbox(
            params_grid, 
            from_=10, 
            to=120, 
            textvariable=self.target_duration,
            font=("Segoe UI", 9),
            width=10
        ).grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # Pre-roll
        tk.Label(params_grid, text="Pre-roll (s):", font=("Segoe UI", 9)).grid(row=1, column=0, sticky=tk.W, pady=5)
        tk.Spinbox(
            params_grid, 
            from_=0.1, 
            to=5.0, 
            increment=0.1,
            textvariable=self.pre_roll,
            font=("Segoe UI", 9),
            width=10,
            format="%.1f"
        ).grid(row=1, column=1, sticky=tk.W, padx=10)
        
        # Post-roll
        tk.Label(params_grid, text="Post-roll (s):", font=("Segoe UI", 9)).grid(row=2, column=0, sticky=tk.W, pady=5)
        tk.Spinbox(
            params_grid, 
            from_=0.1, 
            to=5.0, 
            increment=0.1,
            textvariable=self.post_roll,
            font=("Segoe UI", 9),
            width=10,
            format="%.1f"
        ).grid(row=2, column=1, sticky=tk.W, padx=10)
        
        # Final clip extra
        tk.Label(params_grid, text="Final clip extra (s):", font=("Segoe UI", 9)).grid(row=3, column=0, sticky=tk.W, pady=5)
        tk.Spinbox(
            params_grid, 
            from_=0.0, 
            to=10.0, 
            increment=0.5,
            textvariable=self.final_clip_extra,
            font=("Segoe UI", 9),
            width=10,
            format="%.1f"
        ).grid(row=3, column=1, sticky=tk.W, padx=10)
        
        # Advanced parameters (collapsible)
        advanced_frame = tk.LabelFrame(main_frame, text="🔧 Advanced Parameters", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        advanced_frame.pack(fill=tk.X, pady=(0, 10))
        
        advanced_grid = tk.Frame(advanced_frame)
        advanced_grid.pack(fill=tk.X)
        
        # Min frequency
        tk.Label(advanced_grid, text="Min frequency (Hz):", font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, pady=5)
        tk.Spinbox(
            advanced_grid, 
            from_=500, 
            to=5000, 
            increment=100,
            textvariable=self.min_freq,
            font=("Segoe UI", 9),
            width=10
        ).grid(row=0, column=1, sticky=tk.W, padx=10)
        tk.Label(advanced_grid, text="(Filter low frequencies - higher = crisper)", font=("Segoe UI", 8, "italic"), fg="#666").grid(row=0, column=2, sticky=tk.W, padx=10)
        
        # Hop length
        tk.Label(advanced_grid, text="Hop length:", font=("Segoe UI", 9)).grid(row=1, column=0, sticky=tk.W, pady=5)
        tk.Spinbox(
            advanced_grid, 
            from_=128, 
            to=2048, 
            increment=128,
            textvariable=self.hop_length,
            font=("Segoe UI", 9),
            width=10
        ).grid(row=1, column=1, sticky=tk.W, padx=10)
        tk.Label(advanced_grid, text="(Audio analysis precision - lower = more precise)", font=("Segoe UI", 8, "italic"), fg="#666").grid(row=1, column=2, sticky=tk.W, padx=10)
        
        # Audio Normalize
        tk.Label(advanced_grid, text="Audio Normalize:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky=tk.W, pady=5)
        tk.Checkbutton(
            advanced_grid,
            text="Normalize audio levels (max volume)",
            variable=self.audio_normalize,
            font=("Segoe UI", 9),
            onvalue=True,
            offvalue=False
        ).grid(row=2, column=1, columnspan=2, sticky=tk.W, padx=5)
        
        # Encoding settings
        encoding_frame = tk.LabelFrame(main_frame, text="🎞️ Encoding Settings", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        encoding_frame.pack(fill=tk.X, pady=(0, 10))
        
        encoding_grid = tk.Frame(encoding_frame)
        encoding_grid.pack(fill=tk.X)
        
        # GPU Preset
        tk.Label(encoding_grid, text="GPU Preset:", font=("Segoe UI", 9)).grid(row=0, column=0, sticky=tk.W, pady=5)
        preset_combo = ttk.Combobox(
            encoding_grid,
            textvariable=self.encoding_preset,
            values=["nvidia", "intel", "amd"],
            state="readonly",
            font=("Segoe UI", 9),
            width=12
        )
        preset_combo.grid(row=0, column=1, sticky=tk.W, padx=10)
        
        # Codec info label
        self.codec_info = tk.Label(encoding_grid, text="Codec: h264_nvenc", font=("Segoe UI", 8, "italic"), fg="#0078d4")
        self.codec_info.grid(row=0, column=2, sticky=tk.W, padx=10)
        
        # Update codec info when preset changes
        def update_codec_info(*args):
            preset = self.encoding_preset.get()
            codec = main.GPU_PRESETS.get(preset, main.GPU_PRESETS["nvidia"])["codec"]
            self.codec_info.config(text=f"Codec: {codec}")
        
        self.encoding_preset.trace_add("write", update_codec_info)
        
        # Quality
        tk.Label(encoding_grid, text="Quality (CQ):", font=("Segoe UI", 9)).grid(row=1, column=0, sticky=tk.W, pady=5)
        tk.Spinbox(
            encoding_grid,
            from_=0,
            to=51,
            textvariable=self.encoding_quality,
            font=("Segoe UI", 9),
            width=12
        ).grid(row=1, column=1, sticky=tk.W, padx=10)
        tk.Label(encoding_grid, text="(0=lossless, 18=near lossless, 23=high, 28=medium)", font=("Segoe UI", 8, "italic"), fg="#666").grid(row=1, column=2, sticky=tk.W, padx=10)
        
        # Audio bitrate
        tk.Label(encoding_grid, text="Audio bitrate:", font=("Segoe UI", 9)).grid(row=2, column=0, sticky=tk.W, pady=5)
        audio_combo = ttk.Combobox(
            encoding_grid,
            textvariable=self.audio_bitrate,
            values=["128k", "192k", "256k", "320k"],
            state="readonly",
            font=("Segoe UI", 9),
            width=12
        )
        audio_combo.grid(row=2, column=1, sticky=tk.W, padx=10)
        tk.Label(encoding_grid, text="(320k = maximum quality for ASMR)", font=("Segoe UI", 8, "italic"), fg="#666").grid(row=2, column=2, sticky=tk.W, padx=10)
        
        # Threads
        tk.Label(encoding_grid, text="Threads:", font=("Segoe UI", 9)).grid(row=3, column=0, sticky=tk.W, pady=5)
        tk.Spinbox(
            encoding_grid,
            from_=1,
            to=16,
            textvariable=self.threads,
            font=("Segoe UI", 9),
            width=12
        ).grid(row=3, column=1, sticky=tk.W, padx=10)
        tk.Label(encoding_grid, text="(Number of CPU threads for encoding)", font=("Segoe UI", 8, "italic"), fg="#666").grid(row=3, column=2, sticky=tk.W, padx=10)
        
        # Clip info duration
        self.clip_info = tk.Label(
            params_grid, 
            text=f"→ Single clip duration: {self.pre_roll.get() + self.post_roll.get():.1f}s",
            font=("Segoe UI", 9, "italic"),
            fg="#0078d4"
        )
        self.clip_info.grid(row=1, column=2, rowspan=2, sticky=tk.W, padx=20)
        
        # Update info when values change
        self.pre_roll.trace_add("write", self.update_clip_info)
        self.post_roll.trace_add("write", self.update_clip_info)
        
        # 4. Start Button
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.process_btn = tk.Button(
            button_frame,
            text="▶️  START PROCESSING",
            command=self.start_processing,
            font=("Segoe UI", 12, "bold"),
            bg="#107c10",
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=20,
            pady=12
        )
        self.process_btn.pack(fill=tk.X)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # 5. Log Output
        log_frame = tk.LabelFrame(main_frame, text="📋 Log", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=("Consolas", 10),
            bg="#1e1e1e",
            fg="#d4d4d4",
            insertbackground="white",
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("✅ Ready. Select a video and press START PROCESSING.")
        self.log("💡 If you don't select an output folder, it will be created automatically in the same folder as the video.")
        
    def update_clip_info(self, *args):
        try:
            duration = self.pre_roll.get() + self.post_roll.get()
            self.clip_info.config(text=f"→ Single clip duration: {duration:.1f}s")
        except:
            pass
    
    def browse_video(self):
        video = filedialog.askopenfilename(
            title="Select video to process",
            filetypes=[
                ("Video files", "*.mp4 *.mov *.avi *.mkv *.MP4 *.MOV *.AVI *.MKV"),
                ("All files", "*.*")
            ]
        )
        if video:
            self.input_video.set(video)
            self.log(f"📹 Video selected: {os.path.basename(video)}")
    
    def browse_output(self):
        folder = filedialog.askdirectory(
            title="Select output folder"
        )
        if folder:
            self.output_folder.set(folder)
            self.log(f"📁 Output set to: {folder}")
    
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def start_processing(self):
        if self.processing:
            messagebox.showwarning("In Progress", "Processing already in progress!")
            return
        
        if not self.input_video.get():
            messagebox.showerror("Error", "Select a video!")
            return
        
        if not os.path.exists(self.input_video.get()):
            messagebox.showerror("Error", "Video file does not exist!")
            return
        
        # Update parameters in main module
        main.TARGET_DURATION = self.target_duration.get()
        main.PRE_ROLL = self.pre_roll.get()
        main.POST_ROLL = self.post_roll.get()
        main.FINAL_CLIP_EXTRA = self.final_clip_extra.get()
        main.MIN_FREQ = self.min_freq.get()
        main.HOP_LENGTH = self.hop_length.get()
        main.ENCODING_PRESET = self.encoding_preset.get()
        main.ENCODING_QUALITY = self.encoding_quality.get()
        main.AUDIO_BITRATE = self.audio_bitrate.get()
        main.THREADS = self.threads.get()
        main.MERGE_CLIPS = self.merge_clips.get()
        main.AUDIO_NORMALIZE = self.audio_normalize.get()
        
        # Start in separate thread
        self.processing = True
        self.process_btn.config(state=tk.DISABLED, text="⏳ Processing in progress...", bg="#666666")
        self.progress.start(10)
        self.log("\n" + "="*60)
        self.log("🚀 STARTING PROCESSING...")
        self.log("="*60)
        
        thread = threading.Thread(target=self.run_processing, daemon=True)
        thread.start()
    
    def run_processing(self):
        try:
            # Redirect stdout to capture prints in real-time
            from contextlib import redirect_stdout, redirect_stderr
            
            output_folder = self.output_folder.get() if self.output_folder.get() else None
            
            # Create redirector
            redirector = TextRedirector(self.log_text, self.root)
            
            # Redirect both stdout and stderr to the log window
            with redirect_stdout(redirector), redirect_stderr(redirector):
                result_folder = main.process_single_video(self.input_video.get(), output_folder)
            
            self.root.after(0, lambda: self.log(f"\n✅ Clips saved to: {result_folder}"))
            self.root.after(0, lambda: messagebox.showinfo("Completed", f"Processing completed!\n\nClips saved to:\n{result_folder}"))
            
        except Exception as e:
            error_msg = f"❌ ERROR: {str(e)}"
            self.root.after(0, lambda: self.log(error_msg))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            import traceback
            self.root.after(0, lambda: self.log(traceback.format_exc()))
        
        finally:
            self.root.after(0, self.processing_complete)
    
    def processing_complete(self):
        self.processing = False
        self.process_btn.config(state=tk.NORMAL, text="▶️  START PROCESSING", bg="#107c10")
        self.progress.stop()

    def open_coffee(self):
        webbrowser.open("https://buymeacoffee.com/mariopbay")


def main_gui():
    root = tk.Tk()
    app = ASMRCutterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main_gui()
