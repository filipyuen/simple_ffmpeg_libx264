import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
import subprocess
from threading import Thread

class VideoEncoderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FFmpeg x264 Video Encoder")
        self.input_files = []
        self.output_folder = ""

        # Input Files Selection
        self.label_files = tk.Label(root, text="Input Files: None selected", anchor="w")
        self.label_files.pack(fill="x", padx=10, pady=5)
        self.btn_select_files = tk.Button(root, text="1) Select Files: 0", command=self.select_files)
        self.btn_select_files.pack(fill="x", padx=10, pady=5)

        # Output Folder Selection
        self.label_output = tk.Label(root, text="Output Folder: None selected", anchor="w")
        self.label_output.pack(fill="x", padx=10, pady=5)
        self.btn_select_output = tk.Button(root, text="2) Select Output Folder", command=self.select_output_folder)
        self.btn_select_output.pack(fill="x", padx=10, pady=5)

        # Configuration Frame for Left-Aligned Options
        self.config_frame = tk.Frame(root)
        self.config_frame.pack(fill="x", padx=10, pady=5)

        # Resolution Configuration with Checkbox
        self.resolution_enabled = tk.BooleanVar(value=True)
        self.check_resolution = tk.Checkbutton(self.config_frame, text="", variable=self.resolution_enabled)
        self.check_resolution.grid(row=0, column=0, sticky="w", pady=2)
        self.label_resolution = tk.Label(self.config_frame, text="Resolution (e.g., 1280x720):", width=25, anchor="w")
        self.label_resolution.grid(row=0, column=1, sticky="w", pady=2)
        self.resolution_entry = tk.Entry(self.config_frame)
        self.resolution_entry.insert(0, "1280x720")
        self.resolution_entry.grid(row=0, column=2, sticky="w")

        # Scaler Selection
        self.label_scaler = tk.Label(self.config_frame, text="Scaler:", width=25, anchor="w")
        self.label_scaler.grid(row=1, column=1, sticky="w", pady=2)
        self.scaler_var = tk.StringVar(value="lanczos")
        scaler_options = ["lanczos", "bicubic", "bilinear", "fast_bilinear", "spline"]
        self.scaler_menu = ttk.Combobox(self.config_frame, textvariable=self.scaler_var, values=scaler_options, state="readonly", width=17)
        self.scaler_menu.grid(row=1, column=2, sticky="w")

        # x264 Configuration
        self.label_crf = tk.Label(self.config_frame, text="CRF (0-51):", width=25, anchor="w")
        self.label_crf.grid(row=2, column=1, sticky="w", pady=2)
        self.crf_entry = tk.Entry(self.config_frame)
        self.crf_entry.insert(0, "24")
        self.crf_entry.grid(row=2, column=2, sticky="w")

        self.label_me = tk.Label(self.config_frame, text="Motion Estimation (me):", width=25, anchor="w")
        self.label_me.grid(row=3, column=1, sticky="w", pady=2)
        self.me_var = tk.StringVar(value="umh")
        me_options = ["dia", "hex", "umh", "esa", "tesa"]
        self.me_menu = ttk.Combobox(self.config_frame, textvariable=self.me_var, values=me_options, state="readonly", width=17)
        self.me_menu.grid(row=3, column=2, sticky="w")

        self.label_ref = tk.Label(self.config_frame, text="Reference Frames (1-16):", width=25, anchor="w")
        self.label_ref.grid(row=4, column=1, sticky="w", pady=2)
        self.ref_entry = tk.Entry(self.config_frame)
        self.ref_entry.insert(0, "5")
        self.ref_entry.grid(row=4, column=2, sticky="w")

        self.label_subme = tk.Label(self.config_frame, text="Subpixel ME (0-11):", width=25, anchor="w")
        self.label_subme.grid(row=5, column=1, sticky="w", pady=2)
        self.subme_entry = tk.Entry(self.config_frame)
        self.subme_entry.insert(0, "10")
        self.subme_entry.grid(row=5, column=2, sticky="w")

        self.label_me_range = tk.Label(self.config_frame, text="ME Range (4-64):", width=25, anchor="w")
        self.label_me_range.grid(row=6, column=1, sticky="w", pady=2)
        self.me_range_entry = tk.Entry(self.config_frame)
        self.me_range_entry.insert(0, "32")
        self.me_range_entry.grid(row=6, column=2, sticky="w")

        self.label_b_adapt = tk.Label(self.config_frame, text="B-Frame Adapt (0-2):", width=25, anchor="w")
        self.label_b_adapt.grid(row=7, column=1, sticky="w", pady=2)
        self.b_adapt_entry = tk.Entry(self.config_frame)
        self.b_adapt_entry.insert(0, "2")
        self.b_adapt_entry.grid(row=7, column=2, sticky="w")

        self.label_rc_lookahead = tk.Label(self.config_frame, text="RC Lookahead (0-250):", width=25, anchor="w")
        self.label_rc_lookahead.grid(row=8, column=1, sticky="w", pady=2)
        self.rc_lookahead_entry = tk.Entry(self.config_frame)
        self.rc_lookahead_entry.insert(0, "50")
        self.rc_lookahead_entry.grid(row=8, column=2, sticky="w")

        # Audio Configuration with Checkbox
        self.audio_enabled = tk.BooleanVar(value=True)
        self.check_audio = tk.Checkbutton(self.config_frame, text="", variable=self.audio_enabled)
        self.check_audio.grid(row=9, column=0, sticky="w", pady=2)
        self.label_audio = tk.Label(self.config_frame, text="AAC Bitrate (kbps):", width=25, anchor="w")
        self.label_audio.grid(row=9, column=1, sticky="w", pady=2)
        self.audio_bitrate_entry = tk.Entry(self.config_frame)
        self.audio_bitrate_entry.insert(0, "128")
        self.audio_bitrate_entry.grid(row=9, column=2, sticky="w")

        # CLI Output Window
        self.cli_label = tk.Label(root, text="FFmpeg Output:", anchor="w")
        self.cli_label.pack(fill="x", padx=10, pady=5)
        self.cli_output = tk.Text(root, height=10, width=50, state="disabled")
        self.cli_output.pack(fill="both", padx=10, pady=5, expand=True)
        self.scrollbar = tk.Scrollbar(root, orient="vertical", command=self.cli_output.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.cli_output.config(yscrollcommand=self.scrollbar.set)

        # Run Button
        self.btn_run = tk.Button(root, text="3) Run Encoding", command=self.start_encoding)
        self.btn_run.pack(fill="x", padx=10, pady=10)

    def select_files(self):
        files = filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4 *.mkv *.avi *.mov")])
        self.input_files = files
        self.label_files.config(text=f"Input Files: {len(files)} file(s) selected")
        self.btn_select_files.config(text=f"1) Select Files: {len(files)}")

    def select_output_folder(self):
        folder = filedialog.askdirectory()
        self.output_folder = folder
        self.label_output.config(text=f"Output Folder: {folder if folder else 'None selected'}")

    def append_to_cli(self, text):
        self.cli_output.config(state="normal")
        self.cli_output.insert(tk.END, text + "\n")
        self.cli_output.see(tk.END)
        self.cli_output.config(state="disabled")
        self.root.update()

    def show_temp_message(self, title, message, timeout=2000):
        """Show a messagebox that auto-closes after timeout (ms)."""
        popup = tk.Toplevel()
        popup.title(title)
        tk.Label(popup, text=message, padx=20, pady=20).pack()
        popup.transient(self.root)
        popup.geometry(f"300x100+{self.root.winfo_x()+100}+{self.root.winfo_y()+100}")
        popup.after(timeout, popup.destroy)

    def run_encoding(self):
        if not self.input_files:
            messagebox.showerror("Error", "Please select at least one input file.")
            return
        if not self.output_folder:
            messagebox.showerror("Error", "Please select an output folder.")
            return

        resolution = self.resolution_entry.get().strip()
        scaler = self.scaler_var.get()
        crf = self.crf_entry.get().strip()
        me = self.me_var.get()
        ref = self.ref_entry.get().strip()
        subme = self.subme_entry.get().strip()
        me_range = self.me_range_entry.get().strip()
        b_adapt = self.b_adapt_entry.get().strip()
        rc_lookahead = self.rc_lookahead_entry.get().strip()
        audio_bitrate = self.audio_bitrate_entry.get().strip()

        # Validate inputs
        try:
            if self.resolution_enabled.get() and (not resolution or not all(x.isdigit() for x in resolution.split("x"))):
                raise ValueError("Invalid resolution format (use WIDTHxHEIGHT, e.g., 1280x720)")
            if not (0 <= int(crf) <= 51):
                raise ValueError("CRF must be between 0 and 51")
            if not (1 <= int(ref) <= 16):
                raise ValueError("Reference Frames must be between 1 and 16")
            if not (0 <= int(subme) <= 11):
                raise ValueError("Subpixel ME must be between 0 and 11")
            if not (4 <= int(me_range) <= 64):
                raise ValueError("ME Range must be between 4 and 64")
            if not (0 <= int(b_adapt) <= 2):
                raise ValueError("B-Frame Adapt must be between 0 and 2")
            if not (0 <= int(rc_lookahead) <= 250):
                raise ValueError("RC Lookahead must be between 0 and 250")
            if self.audio_enabled.get() and not (1 <= int(audio_bitrate) <= 1000):
                raise ValueError("AAC Bitrate must be between 1 and 1000 kbps")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
            return

        # Construct x264 parameters
        x264_params = f"me={me}:ref={ref}:subme={subme}:me_range={me_range}:b_adapt={b_adapt}:rc_lookahead={rc_lookahead}"

        # Process each file
        for input_file in self.input_files:
            filename = os.path.basename(input_file)
            output_file = os.path.join(self.output_folder, filename)
            cmd = ["ffmpeg", "-i", input_file]
            
            # Add video filter only if resolution is enabled
            if self.resolution_enabled.get():
                cmd.extend(["-vf", f"scale={resolution}:flags={scaler}"])
                
            cmd.extend([
                "-c:v", "libx264", "-crf", crf,
                "-x264-params", x264_params
            ])
            
            # Add audio options only if audio is enabled
            if self.audio_enabled.get():
                cmd.extend(["-c:a", "aac", "-b:a", f"{audio_bitrate}k"])
            else:
                cmd.append("-an")
                
            cmd.extend(["-y", output_file])
            
            self.append_to_cli(f"Running: {' '.join(cmd)}")
            try:
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, universal_newlines=True)
                for line in process.stdout:
                    self.append_to_cli(line.strip())
                process.wait()
                if process.returncode == 0:
                    self.append_to_cli(f"Success: Encoded {filename}")
                    self.show_temp_message("Success", f"Encoded: {filename}", timeout=2000)
                else:
                    self.append_to_cli(f"Error: Failed to encode {filename}")
                    messagebox.showerror("Error", f"Failed to encode {filename}")
            except subprocess.CalledProcessError as e:
                self.append_to_cli(f"Error: {e.stderr}")
                messagebox.showerror("Error", f"Failed to encode {filename}: {e.stderr}")

    def start_encoding(self):
        # Run encoding in a separate thread to keep UI responsive
        Thread(target=self.run_encoding, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoEncoderApp(root)
    root.geometry("500x700")
    root.mainloop()