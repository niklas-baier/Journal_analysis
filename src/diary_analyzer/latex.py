import re
import pandas as pd

def generate_latex_report(df):
    # Create a copy and handle NaN values to prevent errors
    df_clean = df.copy().fillna("")
    
    # Include 'date' in text columns to ensure it gets sanitized as well
    text_cols = ['date', 'People', 'rating', 'Activities', 'content', 'TODOS']
    
    for col in text_cols:
        if col in df_clean.columns:
            # 1. Convert to string and strip outer whitespace
            s = df_clean[col].astype(str).str.strip()
            
            # 2. Strip out all \cite{...}, \include{...}, and \input{...} instances
            s = s.apply(lambda x: re.sub(r'\\cite\{.*?\}', '', x))
            s = s.apply(lambda x: re.sub(r'\\include\{.*?\}', '', x))
            s = s.apply(lambda x: re.sub(r'\\input\{.*?\}', '', x))
            
            # Convert custom corporate "kit-" colors to standard LaTeX safe colors
            s = s.apply(lambda x: re.sub(r'kit-green\d*', 'green', x))
            s = s.apply(lambda x: re.sub(r'kit-blue\d*', 'blue', x))
            s = s.apply(lambda x: re.sub(r'kit-[a-zA-Z0-9]+', 'gray', x)) 
            
            # 3. Escape raw LaTeX special characters FIRST
            # Uses negative lookbehinds (?<!\\) to avoid double-escaping 
            # characters that are already safely escaped (like \& or \_) in pasted tables/equations.
            s = s.apply(lambda x: re.sub(r'(?<!\\)\$', r'\$', x))
            s = s.apply(lambda x: re.sub(r'(?<!\\)#', r'\#', x))
            s = s.apply(lambda x: re.sub(r'(?<!\\)_', r'\_', x))
            s = s.apply(lambda x: re.sub(r'(?<!\\)&', r'\&', x))
            s = s.apply(lambda x: re.sub(r'(?<!\\)%', r'\%', x))
            
            # 4. Strip out hidden/problematic Unicode characters
            s = s.str.replace('\u200b', '', regex=False) 
            
            # 5. Replace problematic Unicode characters with safe LaTeX equivalents
            s = s.str.replace('✅', '[DONE]', regex=False)
            s = s.str.replace('█', r'\rule{0.6em}{1.2ex}', regex=False)
            s = s.str.replace('✓', r'\checkmark', regex=False)
            
            # Using \ensuretext/\ensuremath allows these to work in BOTH plain text and equation blocks safely
            s = s.str.replace('θ', r'\ensuremath{\theta}', regex=False) 
            s = s.str.replace('⋅', r'\ensuremath{\cdot}', regex=False)   
            s = s.str.replace('−', r'\ensuremath{-}', regex=False)   
            s = s.str.replace('′', "'", regex=False)                 
            
            # Fix for OT1 Encoding error (converts chevrons to text-safe alternatives)
            s = s.str.replace('»', '>>', regex=False)
            s = s.str.replace('«', '<<', regex=False)
            
            df_clean[col] = s

    # Helper function to append elements safely without triggering "There's no line here to end"
    def safe_append(label, value):
        val = value.strip()
        if not val:
            return ""
        
        # FIX: Added \end{columns} to the line-break exclusion list to prevent vertical mode crashes
        if (val.endswith(r"\end{table}") or 
            val.endswith(r"\end{equation}") or 
            val.endswith(r"\end{columns}") or
            val.endswith(r"\\") or 
            val.endswith("}")):
            return f"\\textbf{{{label}:}} {val}\n\n"
        
        return f"\\textbf{{{label}:}} {val}\\\\\n\n"

    # Start LaTeX Document
    latex_doc = r"""
    \documentclass{article}
    \usepackage[T1]{fontenc} 
    \usepackage[utf8]{inputenc}
    \usepackage{beamerarticle} % FIX: Allows an article class to understand Beamer environments like columns
    \usepackage{amsmath}   % Required to fix "Environment bmatrix undefined"
    \usepackage{amssymb}   % Required to render the \checkmark symbol natively
    \usepackage{graphicx}
    \usepackage{booktabs}  % Required to support \toprule, \midrule, and \bottomrule tables
    \usepackage{xcolor}    % Required to provide the \colorbox engine support
    
    % Safe macro fallback configuration for non-standard text notes
    \providecommand{\note}[1]{\textbf{Note:} #1}
    
    \begin{document}
    \title{Project Summary Report}
    \author{Generated Report}
    \date{\today}
    \maketitle
    \section*{Summary}
    """

    # Generate section per unique date
    for date in df_clean['date'].unique():
        latex_doc += f"\n\\section*{{\\textbf{{Date: {date}}}}}\n"
        filtered = df_clean[df_clean['date'] == date]
        for _, row in filtered.iterrows():
            latex_doc += safe_append('People', row['People'])
            latex_doc += safe_append('rating', row['rating'])
            latex_doc += safe_append('Activities', row['Activities'])
            latex_doc += safe_append('Content', row['content'])
            
    latex_doc += f"\n\\section*{{\\textbf{{TODOS:}}}}\n"
    for date in df_clean['date'].unique():
        filtered = df_clean[df_clean['date'] == date]
        for _, row in filtered.iterrows():
            if row['TODOS'] != "false":
                latex_doc += safe_append('TODOS', row['TODOS'])

    # End LaTeX Document
    latex_doc += "\n\\end{document}"

    # Save LaTeX file
    with open("../outputs/summary_report.tex", "w") as file:
        file.write(latex_doc)

    print("LaTeX report generated as 'summary_report.tex'")

