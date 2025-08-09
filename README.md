# Advanced Text & SRT Summarizer

A sophisticated text summarization application with multiple algorithms and SRT subtitle support.

## Features

- **Multiple Algorithms**: 4 different summarization methods
  - **Weighted**: Multi-factor algorithm (position + frequency + length) - *Recommended*
  - **TF-IDF**: Term Frequency-Inverse Document Frequency with filtering
  - **Keywords**: Keyword density-based sentence ranking  
  - **Basic**: Improved frequency-based with short sentence filtering

- **File Support**: 
  - Plain text files (.txt)
  - SRT subtitle files (.srt) with automatic parsing

- **Smart Processing**:
  - Filters out very short sentences (< 6 words)
  - Position weighting (beginning/end sentences prioritized)
  - Length normalization to avoid bias
  - Real-time text statistics

## Installation & Setup

1. **Install Python 3.7+**

2. **Install required packages**:
   ```bash
   pip install nltk tkinter
   ```

3. **Download NLTK data** (first run only):
   ```python
   import nltk
   nltk.download('punkt_tab')
   nltk.download('stopwords')
   ```

## Usage

### Quick Start
```bash
python text_summarizer_app.py
```

### File Structure (MVC Architecture)
```
project/
├── text_summarizer_app.py      # Main application (Controller)
├── text_summarizer_core.py     # Summarization logic (Model)  
├── text_summarizer_gui.py      # User interface (View)
└── README.md                   # This file
```

### Using the Application

1. **Load a file**: Click "Browse Files..." and select a .txt or .srt file
2. **Choose algorithm**: Select from dropdown (weighted recommended)
3. **Set sentence count**: Choose 1-10 sentences for summary
4. **Generate summary**: Click "Generate Summary" button
5. **View results**: Compare original and summary side-by-side

### Keyboard Shortcuts
- `Ctrl+O`: Browse for file
- `Ctrl+S`: Generate summary
- `Ctrl+L`: Clear all text

## Algorithm Comparison

| Algorithm | Best For | Pros | Cons |
|-----------|----------|------|------|
| **Weighted** | General use | Balanced, considers multiple factors | More complex |
| **TF-IDF** | Academic texts | Good for formal documents | May miss context |
| **Keywords** | Keyword-heavy content | Fast, simple | May miss nuanced content |
| **Basic** | Simple documents | Very fast | Limited sophistication |

## Troubleshooting

### Common Issues

1. **"Resource not found" NLTK error**:
   ```python
   import nltk
   nltk.download('punkt_tab')
   nltk.download('stopwords')
   ```

2. **File encoding errors**:
   - App tries UTF-8 first, then Latin-1
   - For other encodings, convert file to UTF-8 first

3. **Poor summary quality**:
   - Try different algorithms
   - Increase sentence count
   - Ensure text is substantial (>100 words)

4. **SRT parsing issues**:
   - Ensure proper SRT format with time codes
   - Remove any non-standard formatting

## Technical Details

### Architecture
- **MVC Pattern**: Clean separation of concerns
- **Modular Design**: Easy to extend with new algorithms
- **Error Handling**: Comprehensive error catching and user feedback

### Core Algorithms

1. **Weighted Algorithm** (Recommended):
   ```
   Score = (FrequencyScore × 0.5) + (PositionScore × 0.3) + (LengthScore × 0.2)
   ```

2. **TF-IDF Algorithm**:
   ```
   TF = TermCount / TotalTermsInSentence  
   IDF = log(TotalSentences / SentencesContainingTerm)
   Score = TF × IDF
   ```

### Performance
- Handles documents up to 100,000+ words
- Sub-second processing for most texts
- Memory efficient with streaming processing

## Extending the Application

### Adding New Algorithms

1. Add method to `TextSummarizer` class in `text_summarizer_core.py`:
   ```python
   def _summarize_new_method(self, text: str, n_sent: int = 3) -> str:
       # Your algorithm here
       pass
   ```

2. Register in `__init__`:
   ```python
   self.algorithms['new_method'] = self._summarize_new_method
   ```

3. Update GUI combobox values in `text_summarizer_gui.py`

### Adding File Format Support

1. Create parser class in `text_summarizer_core.py`
2. Add file type detection in `SummarizerController.handle_file_selection()`
3. Update GUI file dialog filters

## License

This project is provided as-is for educational and personal use.

## Version History

- **v2.0.0**: Complete rewrite with MVC architecture, multiple algorithms
- **v1.0.0**: Basic GUI with single algorithm

---

For issues or suggestions, please refer to the source code comments or create an issue.
