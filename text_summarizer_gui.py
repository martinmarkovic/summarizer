"""
Text Summarizer GUI (View)
Handles all user interface components and interactions.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from typing import Callable, Optional
import os

class SummarizerGUI:
    """Main GUI class for the Text Summarizer application."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Advanced Text & SRT Summarizer")
        self.root.geometry("1200x800")
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
        main_frame.rowconfigure(5, weight=1)

        # Title with styling
        title_label = ttk.Label(main_frame, text="🔍 Advanced Text & SRT Summarizer", 
                               font=('Arial', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 25))

        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="📁 File Selection", padding="15")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Selected File:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)

        self.file_entry = ttk.Entry(file_frame, textvariable=self.file_path, 
                                   font=('Arial', 10), width=60, state="readonly")
        self.file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(15, 15))

        self.browse_btn = ttk.Button(file_frame, text="Browse Files...", 
                                    command=self._handle_browse, width=15)
        self.browse_btn.grid(row=0, column=2)

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Summarization Options", padding="15")
        options_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        options_frame.columnconfigure(1, weight=1)

        # Method selection
        ttk.Label(options_frame, text="Algorithm:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))

        self.method_combo = ttk.Combobox(options_frame, textvariable=self.summary_method, 
                                        values=["weighted", "tfidf", "keywords", "basic"], 
                                        state="readonly", width=15)
        self.method_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 30))

        # Number of sentences
        ttk.Label(options_frame, text="Summary Sentences:", font=('Arial', 10, 'bold')).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))

        self.sentences_spin = ttk.Spinbox(options_frame, from_=1, to=10, width=8, 
                                         textvariable=self.summary_sentences, 
                                         font=('Arial', 10))
        self.sentences_spin.grid(row=0, column=3, padx=(0, 20))

        # Algorithm info
        self.info_label = ttk.Label(options_frame, text="Multi-factor algorithm (position + frequency + length)", 
                                   font=('Arial', 9), foreground='#666666')
        self.info_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(10, 0))

        # Control buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, columnspan=3, pady=(0, 15))

        self.summarize_btn = ttk.Button(buttons_frame, text="🚀 Generate Summary", 
                                       command=self._handle_summarize, width=20)
        self.summarize_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.clear_btn = ttk.Button(buttons_frame, text="🗑️ Clear All", 
                                   command=self._handle_clear, width=15)
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 15))

        # Progress bar (initially hidden)
        self.progress = ttk.Progressbar(buttons_frame, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, padx=(15, 0))

        # Statistics frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        self.stats_label = ttk.Label(stats_frame, text="Ready to process text files", 
                                    font=('Arial', 9), foreground='#0066cc')
        self.stats_label.pack(side=tk.LEFT)

        # Text areas frame
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.columnconfigure(1, weight=1)
        text_frame.rowconfigure(0, weight=1)

        # Original text area
        original_frame = ttk.LabelFrame(text_frame, text="📄 Original Text", padding="8")
        original_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 8))
        original_frame.columnconfigure(0, weight=1)
        original_frame.rowconfigure(0, weight=1)

        self.original_text = scrolledtext.ScrolledText(original_frame, wrap=tk.WORD, 
                                                      height=25, width=45, 
                                                      font=('Consolas', 10))
        self.original_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Summary text area
        summary_frame = ttk.LabelFrame(text_frame, text="✨ Generated Summary", padding="8")
        summary_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(8, 0))
        summary_frame.columnconfigure(0, weight=1)
        summary_frame.rowconfigure(0, weight=1)

        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD, 
                                                     height=25, width=45,
                                                     font=('Consolas', 10),
                                                     foreground='#2d5a2d')
        self.summary_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W, font=('Arial', 9))
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(15, 0))

    def _setup_bindings(self):
        """Setup event bindings."""
        # Method change binding
        self.method_combo.bind('<<ComboboxSelected>>', self._on_method_changed)

        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self._handle_browse())
        self.root.bind('<Control-s>', lambda e: self._handle_summarize())
        self.root.bind('<Control-l>', lambda e: self._handle_clear())

        # Text change tracking for statistics
        self.original_text.bind('<KeyRelease>', self._update_text_stats)

    def _handle_browse(self):
        """Handle file browse button click."""
        file_path = filedialog.askopenfilename(
            title="Select Text or SRT File",
            filetypes=[
                ("Text files", "*.txt"),
                ("SRT files", "*.srt"),
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
            messagebox.showwarning("Warning", "No text to summarize. Please load a file or enter text manually.")
            return

        if self.on_summarize:
            # Show progress
            self.progress.start()
            self.summarize_btn.configure(state='disabled')
            self.status_var.set("Generating summary...")

            # Use after() to allow UI to update
            self.root.after(100, lambda: self._perform_summarization(content, method, n_sentences))

    def _perform_summarization(self, content: str, method: str, n_sentences: int):
        """Perform the actual summarization."""
        try:
            if self.on_summarize:
                summary = self.on_summarize(content, method, n_sentences)
                self.display_summary(summary)
        except Exception as e:
            messagebox.showerror("Error", f"Summarization failed: {str(e)}")
        finally:
            # Hide progress
            self.progress.stop()
            self.summarize_btn.configure(state='normal')

    def _handle_clear(self):
        """Handle clear button click."""
        if self.on_clear:
            self.on_clear()

    def _on_method_changed(self, event=None):
        """Handle method selection change."""
        method = self.summary_method.get()

        # Update info label
        method_info = {
            "weighted": "Multi-factor algorithm (position + frequency + length)",
            "tfidf": "TF-IDF based sentence ranking with length filtering", 
            "keywords": "Keyword density based sentence selection",
            "basic": "Improved frequency-based algorithm with filtering"
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
            self.stats_label.config(text=f"📊 {words:,} words, {chars:,} characters")
        else:
            self.stats_label.config(text="Ready to process text files")

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
            compression_ratio = len(summary) / len(original_content) * 100
            self.status_var.set(f"Summary generated • Compression: {compression_ratio:.1f}%")
        else:
            self.status_var.set("Summary generated")

    def clear_all_text(self):
        """Clear both text areas."""
        self.original_text.delete(1.0, tk.END)
        self.summary_text.delete(1.0, tk.END)
        self.file_path.set("")
        self.status_var.set("Text cleared")
        self.stats_label.config(text="Ready to process text files")

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
        """Get current summary method and sentence count."""
        return self.summary_method.get(), self.summary_sentences.get()


# Style configuration for better appearance
def configure_styles():
    """Configure ttk styles for better appearance."""
    style = ttk.Style()

    # Use a modern theme if available
    try:
        style.theme_use('clam')
    except:
        pass

    # Configure button styles
    style.configure('Accent.TButton', font=('Arial', 10, 'bold'))


if __name__ == "__main__":
    # Test the GUI
    root = tk.Tk()
    configure_styles()
    gui = SummarizerGUI(root)

    # Test callbacks
    gui.on_file_browse = lambda path: print(f"File selected: {path}")
    gui.on_summarize = lambda text, method, n: f"Test summary of {len(text)} chars using {method}"
    gui.on_clear = lambda: print("Clear requested")

    root.mainloop()
