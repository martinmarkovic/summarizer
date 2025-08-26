"""
Enhanced Text Summarizer GUI (View) - FIXED VERSION
Updated GUI with support for advanced algorithms and timestamp display.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from typing import Callable, Optional
import os

class SummarizerGUI:
    """Enhanced GUI class for the Text Summarizer application."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🤖 Advanced AI Text & SRT Summarizer")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')

        # Callback functions (to be set by controller)
        self.on_file_browse: Optional[Callable[[str], None]] = None
        self.on_summarize: Optional[Callable[[str, str, int], str]] = None
        self.on_clear: Optional[Callable[[], None]] = None
        self.on_method_change: Optional[Callable[[str], None]] = None

        # Variables
        self.file_path = tk.StringVar()
        self.summary_method = tk.StringVar(value="weighted")
        self.summary_sentences = tk.IntVar(value=3)
        self.show_timestamps = tk.BooleanVar(value=True)

        self._create_widgets()
        self._setup_bindings()

    def _create_widgets(self):
        """Create all GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)

        # Enhanced title - FIXED: Using tk.Label instead of ttk.Label for font compatibility
        title_label = tk.Label(main_frame, text="🤖 Advanced AI Text & SRT Summarizer v2.0",
                              font=('Arial', 20, 'bold'), bg='#f0f0f0')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 25))

        subtitle_label = tk.Label(main_frame, text="8 Advanced Algorithms • SRT Timestamps • Multi-Factor Analysis",
                                 font=('Arial', 11), foreground='#666666', bg='#f0f0f0')
        subtitle_label.grid(row=1, column=0, columnspan=3, pady=(0, 20))

        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="📁 File Selection", padding="15")
        file_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)

        # FIXED: Removed font= from ttk.Label
        ttk.Label(file_frame, text="Selected File:").grid(row=0, column=0, sticky=tk.W)

        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path, width=70, state="readonly")
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(15, 15))

        self.browse_btn = ttk.Button(file_frame, text="📂 Browse Files...",
                                    command=self._handle_browse, width=18)
        self.browse_btn.grid(row=0, column=2)

        # Advanced options frame
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Advanced Summarization Options", padding="15")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        options_frame.columnconfigure(1, weight=1)

        # First row - Algorithm and sentences - FIXED: Removed font= from ttk widgets
        ttk.Label(options_frame, text="AI Algorithm:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        algorithm_values = [
            "weighted", "textrank", "semantic", "tfidf",
            "lexrank", "centroid", "keywords", "basic"
        ]

        self.method_combo = ttk.Combobox(options_frame, textvariable=self.summary_method,
                                        values=algorithm_values,
                                        state="readonly", width=12)
        self.method_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 30))

        ttk.Label(options_frame, text="Summary Length:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))

        self.sentences_spin = ttk.Spinbox(options_frame, from_=1, to=15, width=8,
                                         textvariable=self.summary_sentences)
        self.sentences_spin.grid(row=0, column=3, padx=(0, 20))

        ttk.Label(options_frame, text="sentences").grid(row=0, column=4, sticky=tk.W)

        # Second row - Additional options
        self.timestamp_check = ttk.Checkbutton(options_frame, text="📅 Include SRT Timestamps",
                                              variable=self.show_timestamps)
        self.timestamp_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))

        # Algorithm description - FIXED: Using tk.Label for text wrapping
        self.info_label = tk.Label(options_frame, 
                                  text="Multi-factor algorithm (position + frequency + length) - Best for general use",
                                  font=('Arial', 9), foreground='#0066cc', 
                                  wraplength=600, bg='#f0f0f0', justify='left')
        self.info_label.grid(row=2, column=0, columnspan=5, sticky=tk.W, pady=(10, 0))

        # Control buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=(0, 15))

        self.summarize_btn = ttk.Button(buttons_frame, text="🚀 Generate AI Summary",
                                       command=self._handle_summarize, width=25)
        self.summarize_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.clear_btn = ttk.Button(buttons_frame, text="🗑️ Clear All",
                                   command=self._handle_clear, width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.export_btn = ttk.Button(buttons_frame, text="💾 Export Summary",
                                    command=self._handle_export, width=18)
        self.export_btn.pack(side=tk.LEFT, padx=(0, 15))

        # Progress bar
        self.progress = ttk.Progressbar(buttons_frame, mode='indeterminate', length=150)
        self.progress.pack(side=tk.LEFT, padx=(15, 0))

        # Enhanced statistics frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        # FIXED: Using tk.Label for better font control
        self.stats_label = tk.Label(stats_frame, 
                                   text="📊 Ready to process text files • Select algorithm and load content",
                                   font=('Arial', 9), foreground='#0066cc', bg='#f0f0f0')
        self.stats_label.pack(side=tk.LEFT)

        self.algorithm_stats = tk.Label(stats_frame, text="",
                                       font=('Arial', 9), foreground='#666666', bg='#f0f0f0')
        self.algorithm_stats.pack(side=tk.RIGHT)

        # Text areas frame with enhanced layout
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(1, weight=1)
        text_frame.rowconfigure(0, weight=1)

        # Original text area
        original_frame = ttk.LabelFrame(text_frame, text="📄 Original Text Content", padding="8")
        original_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 8))
        original_frame.columnconfigure(0, weight=1)
        original_frame.rowconfigure(0, weight=1)

        # FIXED: Proper font configuration for ScrolledText
        self.original_text = scrolledtext.ScrolledText(original_frame, wrap=tk.WORD,
                                                      height=28, width=50,
                                                      font=('Consolas', 10),
                                                      bg='#ffffff', fg='#333333')
        self.original_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Summary text area with enhanced styling
        summary_frame = ttk.LabelFrame(text_frame, text="✨ AI-Generated Summary", padding="8")
        summary_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(8, 0))
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.rowconfigure(0, weight=1)

        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD,
                                                     height=28, width=50,
                                                     font=('Consolas', 10),
                                                     bg='#f8fff8', fg='#2d5a2d',
                                                     selectbackground='#e8f5e8')
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Enhanced status bar - FIXED: Using tk.Label
        self.status_var = tk.StringVar(value="🤖 AI Summarizer Ready • Load a file to begin intelligent analysis")
        status_bar = tk.Label(main_frame, textvariable=self.status_var,
                             relief=tk.SUNKEN, anchor=tk.W, font=('Arial', 9),
                             foreground='#0066cc', bg='#f0f0f0')
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))

    def _setup_bindings(self):
        """Setup event bindings."""
        self.method_combo.bind('<<ComboboxSelected>>', self._on_method_changed)

        # Enhanced keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self._handle_browse())
        self.root.bind('<Control-s>', lambda e: self._handle_summarize())
        self.root.bind('<Control-l>', lambda e: self._handle_clear())
        self.root.bind('<Control-e>', lambda e: self._handle_export())
        self.root.bind('<F1>', lambda e: self._show_help())

        self.original_text.bind('<KeyRelease>', self._update_text_stats)
        self.original_text.bind('<Button-1>', self._update_text_stats)

    def _handle_browse(self):
        """Handle file browse button click."""
        file_path = filedialog.askopenfilename(
            title="Select Text or SRT File for AI Analysis",
            filetypes=[
                ("Text files", "*.txt"),
                ("SRT Subtitle files", "*.srt"),
                ("All text files", "*.txt *.srt"),
                ("All files", "*.*")
            ]
        )

        if file_path and self.on_file_browse:
            self.on_file_browse(file_path)

    def _handle_summarize(self):
        """Handle summarize button click."""
        content = self.original_text.get(1.0, tk.END).strip()
        method = self.summary_method.get()
        n_sentences = self.summary_sentences.get()

        if not content:
            messagebox.showwarning("⚠️ No Content",
                                 "No text to summarize. Please load a file or enter text manually.\n\n" +
                                 "Supported formats: .txt, .srt")
            return

        if self.on_summarize:
            self.progress.start()
            self.summarize_btn.configure(state='disabled')
            self.status_var.set(f"🤖 AI processing with {method.upper()} algorithm...")

            self.root.after(100, lambda: self._perform_summarization(content, method, n_sentences))

    def _perform_summarization(self, content: str, method: str, n_sentences: int):
        """Perform the actual summarization."""
        try:
            if self.on_summarize:
                summary = self.on_summarize(content, method, n_sentences)
                self.display_summary(summary)

                # Update algorithm stats
                self.algorithm_stats.config(text=f"Algorithm: {method.upper()}")

        except Exception as e:
            messagebox.showerror("❌ Processing Error", f"AI summarization failed:\n\n{str(e)}")
            self.status_var.set("❌ Summarization failed")
        finally:
            self.progress.stop()
            self.summarize_btn.configure(state='normal')

    def _handle_clear(self):
        """Handle clear button click."""
        if self.on_clear:
            self.on_clear()

    def _handle_export(self):
        """Handle export summary button click."""
        summary_content = self.summary_text.get(1.0, tk.END).strip()

        if not summary_content:
            messagebox.showwarning("⚠️ No Summary", "No summary to export. Generate a summary first.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Export Summary",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("Markdown files", "*.md"),
                ("All files", "*.*")
            ]
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"AI-Generated Summary\n")
                    f.write(f"Algorithm: {self.summary_method.get().upper()}\n")
                    f.write(f"Length: {self.summary_sentences.get()} sentences\n")
                    f.write(f"Generated: {self._get_current_timestamp()}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(summary_content)

                messagebox.showinfo("✅ Export Successful", f"Summary exported to:\n{file_path}")
                self.status_var.set(f"📁 Summary exported to {os.path.basename(file_path)}")

            except Exception as e:
                messagebox.showerror("❌ Export Failed", f"Could not export summary:\n{str(e)}")

    def _show_help(self):
        """Show help dialog."""
        help_text = """🤖 AI Text Summarizer Help

ALGORITHMS:
• Weighted: Multi-factor analysis (recommended)
• TextRank: Graph-based PageRank algorithm  
• Semantic: Clustering with diversity maximization
• TF-IDF: Term frequency analysis
• LexRank: Centrality-based ranking
• Centroid: Vector space similarity
• Keywords: Enhanced keyword density
• Basic: Simple frequency-based

FEATURES:
• SRT timestamp preservation
• Multi-format support (.txt, .srt)
• Export functionality
• Real-time statistics

SHORTCUTS:
• Ctrl+O: Browse files
• Ctrl+S: Summarize
• Ctrl+L: Clear all
• Ctrl+E: Export
• F1: Help"""

        messagebox.showinfo("📖 Help", help_text)

    def _on_method_changed(self, event=None):
        """Handle method selection change."""
        method = self.summary_method.get()

        # Enhanced method descriptions
        method_info = {
            "weighted": "Multi-factor algorithm (position + frequency + length) - Best for general use",
            "textrank": "Graph-based PageRank algorithm for sentence ranking - Excellent for structured content", 
            "semantic": "Semantic clustering with diversity maximization - Great for varied topics",
            "tfidf": "Term Frequency-Inverse Document Frequency with sklearn - Good for academic texts",
            "lexrank": "Centrality-based graph algorithm with similarity thresholding - Balanced approach",
            "centroid": "Vector space model using document centroid similarity - Fast and effective",
            "keywords": "Enhanced keyword density with rarity bonuses - Perfect for keyword-heavy content",
            "basic": "Improved frequency-based algorithm with filtering - Simple and reliable"
        }

        self.info_label.config(text=method_info.get(method, "Unknown algorithm"))

        if self.on_method_change:
            self.on_method_change(method)

    def _update_text_stats(self, event=None):
        """Update text statistics."""
        content = self.original_text.get(1.0, tk.END).strip()
        if content:
            words = len(content.split())
            chars = len(content)
            sentences = len([s for s in content.split('.') if s.strip()])

            self.stats_label.config(text=f"📊 Content: {words:,} words • {chars:,} characters • ~{sentences} sentences")
        else:
            self.stats_label.config(text="📊 Ready to process text files • Select algorithm and load content")

    def _get_current_timestamp(self):
        """Get current timestamp for export."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Public interface methods for controller

    def set_file_path(self, path: str):
        """Set the displayed file path."""
        self.file_path.set(path)

    def display_original_text(self, text: str):
        """Display text in the original text area."""
        self.original_text.delete(1.0, tk.END)
        self.original_text.insert(tk.END, text)
        self._update_text_stats()

    def display_summary(self, summary: str):
        """Display text in the summary area."""
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary)

        # Update statistics
        original_content = self.original_text.get(1.0, tk.END).strip()
        if original_content and summary:
            original_words = len(original_content.split())
            summary_words = len(summary.split())
            compression_ratio = (summary_words / original_words) * 100 if original_words > 0 else 0

            self.status_var.set(f"✅ AI Summary Complete • Compression: {original_words:,} → {summary_words:,} words ({compression_ratio:.1f}%)")
        else:
            self.status_var.set("✅ AI summary generated successfully")

    def clear_all_text(self):
        """Clear both text areas."""
        self.original_text.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)
        self.file_path.set("")
        self.status_var.set("🗑️ Content cleared • Ready for new analysis")
        self.algorithm_stats.config(text="")
        self.stats_label.config(text="📊 Ready to process text files • Select algorithm and load content")

    def set_status(self, status: str):
        """Set status bar text."""
        self.status_var.set(status)

    def show_error(self, title: str, message: str):
        """Show error dialog."""
        messagebox.showerror(title, message)

    def show_info(self, title: str, message: str):
        """Show info dialog."""
        messagebox.showinfo(title, message)

    def get_summary_settings(self) -> tuple:
        """Get current summary settings."""
        return (self.summary_method.get(), 
                self.summary_sentences.get(), 
                self.show_timestamps.get())


# FIXED: Simplified style configuration
def configure_styles():
    """Configure basic ttk styles without conflicting font settings."""
    style = ttk.Style()

    try:
        style.theme_use('clam')
    except:
        pass

    # Removed conflicting font configurations


if __name__ == "__main__":
    # Test the fixed GUI
    root = tk.Tk()
    configure_styles()
    gui = SummarizerGUI(root)

    # Test callbacks
    gui.on_file_browse = lambda path: print(f"File selected: {path}")
    gui.on_summarize = lambda text, method, n: f"Test AI summary of {len(text)} chars using {method}"
    gui.on_clear = lambda: print("Clear requested")

    root.mainloop()
