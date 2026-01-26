def generate_latex_report(df):
    # Start LaTeX Document
    latex_doc = r"""
    \documentclass{article}
    \usepackage{graphicx}
    \begin{document}
    \title{Project Summary Report}
    \author{Generated Report}
    \date{\today}
    \maketitle
    \section*{Summary}
    """

    # Generate section per date
    for date in df['date']:
        latex_doc += f"\n\\section*{{\\textbf{{Date: {date}}}}}\n"
        filtered = df[df['date'] == date]
        for _, row in filtered.iterrows():
            if row['People'] != "":
                 latex_doc += f"\\textbf{{People:}} {row['People']}\\\n\n"
            if row['rating'] != "":
                 latex_doc += f"\\textbf{{rating:}} {row['rating']}\\\n\n"
            if row['Activities'] != "":
                 latex_doc += f"\\textbf{{Activities:}} {row['Activities']}\\\n\n"
            latex_doc += f"\\textbf{{Content:}}\n{row['content']}\\\\\n\n"
    latex_doc += f"\n\\section*{{\\textbf{{TODOS:}}}}\n"
    for date in df['date'].unique():
        filtered = df[df['date'] == date]
        for _, row in filtered.iterrows():
            if row['TODOS'] != "false":
                 if row['TODOS'] != "":
                     latex_doc += f"\\textbf{{TODOS:}} {row['TODOS']}\\\n\n"

    # End LaTeX Document
    latex_doc += "\n\\end{document}"

    # Save LaTeX file
    with open("../outputs/summary_report.tex", "w") as file:
        file.write(latex_doc)

    print("LaTeX report generated as 'summary_report.tex'")

