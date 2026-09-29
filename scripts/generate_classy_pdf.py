"""
SkillSprint AI — Classy PDF & HTML Master Documentation Generator
Engineered by Team NASR (Zero External Dependencies)
Converts MASTER_SYSTEM_DOCUMENTATION.md into an executive, highly polished HTML & PDF report.
"""

import os
import re
import subprocess

def parse_markdown_to_html(md_text):
    lines = md_text.splitlines()
    html_lines = []
    in_code_block = False
    code_block_lines = []
    code_lang = ""
    in_table = False
    table_rows = []

    def flush_table():
        nonlocal in_table, table_rows
        if not in_table or not table_rows:
            return ""
        tbl_html = ["<table>"]
        for idx, row in enumerate(table_rows):
            cells = [c.strip() for c in row.strip("|").split("|")]
            if idx == 0:
                tbl_html.append("  <thead><tr>" + "".join(f"<th>{c}</th>" for c in cells) + "</tr></thead>")
                tbl_html.append("  <tbody>")
            elif idx == 1 and all(set(c.replace(":", "").replace("-", "").strip()) == set() for c in cells):
                continue
            else:
                tbl_html.append("    <tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
        tbl_html.append("  </tbody></table>")
        in_table = False
        table_rows = []
        return "\n".join(tbl_html)

    for line in lines:
        # Code Blocks
        if line.startswith("```"):
            if in_code_block:
                code_content = "\n".join(code_block_lines)
                html_lines.append(f'<pre><code class="{code_lang}">{code_content}</code></pre>')
                in_code_block = False
                code_block_lines = []
                code_lang = ""
            else:
                if in_table:
                    html_lines.append(flush_table())
                in_code_block = True
                code_lang = line.strip("`").strip()
            continue

        if in_code_block:
            code_block_lines.append(line.replace("<", "&lt;").replace(">", "&gt;"))
            continue

        # Tables
        if "|" in line and (line.strip().startswith("|") or line.strip().endswith("|")):
            in_table = True
            table_rows.append(line)
            continue
        elif in_table:
            html_lines.append(flush_table())

        # Headings
        if line.startswith("# "):
            html_lines.append(f"<h1>{line[2:].strip()}</h1>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:].strip()}</h2>")
        elif line.startswith("### "):
            html_lines.append(f"<h3>{line[4:].strip()}</h3>")
        elif line.startswith("#### "):
            html_lines.append(f"<h4>{line[5:].strip()}</h4>")
        elif line.startswith("> [!IMPORTANT]"):
            html_lines.append('<div class="callout callout-important">')
        elif line.startswith("> ") and '<div class="callout' in (html_lines[-1] if html_lines else ""):
            html_lines.append(f"<p>{line[2:].strip()}</p>")
        elif line.startswith("> "):
            html_lines.append(f"<blockquote>{line[2:].strip()}</blockquote>")
        elif line.startswith("---"):
            html_lines.append("<hr/>")
        elif line.startswith("- ") or line.startswith("* "):
            html_lines.append(f"<li>{line[2:].strip()}</li>")
        elif re.match(r"^\d+\.\s+", line):
            content = re.sub(r"^\d+\.\s+", "", line)
            html_lines.append(f"<li>{content.strip()}</li>")
        elif line.strip():
            html_lines.append(f"<p>{line.strip()}</p>")

    if in_table:
        html_lines.append(flush_table())

    res_html = "\n".join(html_lines)

    # Images
    def repl_img(match):
        alt = match.group(1)
        src = match.group(2)
        return f'<div class="img-container"><img src="{src}" alt="{alt}"/></div>'

    res_html = re.sub(r"!\[(.*?)\]\((.*?)\)", repl_img, res_html)

    # Bold and inline code
    res_html = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", res_html)
    res_html = re.sub(r"\*(.*?)\*", r"<em>\1</em>", res_html)
    res_html = re.sub(r"`(.*?)`", r"<code>\1</code>", res_html)

    return res_html


def generate_doc():
    doc_path = os.path.join("docs", "submission", "MASTER_SYSTEM_DOCUMENTATION.md")
    html_out_path = os.path.join("docs", "submission", "SkillSprint_AI_Master_Documentation_Team_NASR.html")
    pdf_out_path = os.path.join("docs", "submission", "SkillSprint_AI_Master_Documentation_Team_NASR.pdf")

    if not os.path.exists(doc_path):
        print(f"Error: {doc_path} not found.")
        return

    with open(doc_path, "r", encoding="utf-8") as f:
        md_content = f.read()

    body_html = parse_markdown_to_html(md_content)

    brain_dir = os.path.abspath(os.path.join(os.path.expanduser("~"), ".gemini", "antigravity", "brain", "f6c3e8e7-dd1a-40b8-8402-59dead6c2e30"))
    
    def fix_img_src(match):
        img_path = match.group(1)
        filename = os.path.basename(img_path)
        local_img = os.path.join(brain_dir, filename)
        if os.path.exists(local_img):
            uri = "file:///" + local_img.replace("\\", "/")
            return f'src="{uri}"'
        return match.group(0)

    body_html = re.sub(r'src="([^"]+)"', fix_img_src, body_html)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SkillSprint AI — Master System Documentation | Team NASR</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

    @page {{
        size: A4 portrait;
        margin: 18mm 14mm 18mm 14mm;
        @bottom-right {{
            content: "Page " counter(page);
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 8pt;
            color: #64748b;
        }}
        @bottom-left {{
            content: "SkillSprint AI — Designed & Developed by Team NASR";
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 8pt;
            font-weight: 700;
            color: #2563eb;
        }}
    }}

    body {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1e293b;
        background-color: #ffffff;
        line-height: 1.65;
        font-size: 10pt;
        margin: 0;
        padding: 24px;
    }}

    /* Cover Card Header */
    .cover-card {{
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #ffffff;
        border-radius: 16px;
        padding: 45px 35px;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.25);
        border: 2px solid #334155;
    }}

    .team-badge {{
        display: inline-block;
        background: linear-gradient(90deg, #d97706 0%, #f59e0b 100%);
        color: #ffffff;
        font-weight: 800;
        font-size: 14pt;
        padding: 10px 28px;
        border-radius: 9999px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        box-shadow: 0 4px 14px rgba(245, 158, 11, 0.45);
        margin-bottom: 20px;
    }}

    .cover-title {{
        font-size: 24pt;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0 0 12px 0;
        color: #ffffff;
    }}

    .cover-subtitle {{
        font-size: 12.5pt;
        color: #cbd5e1;
        font-weight: 500;
        margin-bottom: 25px;
    }}

    .meta-bar {{
        display: flex;
        justify-content: center;
        gap: 12px;
        font-size: 8.5pt;
        color: #94a3b8;
        font-family: 'JetBrains Mono', monospace;
    }}

    .meta-item {{
        background: rgba(255, 255, 255, 0.12);
        padding: 6px 14px;
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }}

    /* Typography & Section Titles */
    h1 {{
        font-size: 17pt;
        border-bottom: 3px solid #2563eb;
        padding-bottom: 8px;
        margin-top: 35px;
        color: #1e3a8a;
        font-weight: 800;
    }}

    h2 {{
        font-size: 13.5pt;
        color: #0f172a;
        margin-top: 25px;
        border-left: 5px solid #2563eb;
        padding-left: 12px;
        font-weight: 700;
    }}

    h3 {{
        font-size: 11.5pt;
        color: #334155;
        margin-top: 20px;
        font-weight: 700;
    }}

    p, li {{
        font-size: 9.8pt;
        color: #334155;
    }}

    /* Tables */
    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 8.8pt;
        page-break-inside: avoid;
    }}

    th {{
        background-color: #0f172a;
        color: #ffffff;
        font-weight: 700;
        text-align: left;
        padding: 10px 12px;
        border: 1px solid #1e293b;
    }}

    td {{
        padding: 8px 12px;
        border: 1px solid #e2e8f0;
        color: #334155;
    }}

    tr:nth-child(even) {{
        background-color: #f8fafc;
    }}

    /* Code Blocks */
    code {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 8.5pt;
        background: #f1f5f9;
        color: #0f172a;
        padding: 2px 6px;
        border-radius: 4px;
    }}

    pre {{
        background: #0f172a;
        color: #f8fafc;
        padding: 16px;
        border-radius: 10px;
        overflow-x: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 8.5pt;
        line-height: 1.5;
        page-break-inside: avoid;
        border: 1px solid #334155;
    }}

    pre code {{
        background: transparent;
        color: inherit;
        padding: 0;
    }}

    /* Callouts & Blockquotes */
    blockquote {{
        background: #f0f9ff;
        border-left: 5px solid #0284c7;
        margin: 20px 0;
        padding: 14px 18px;
        border-radius: 0 10px 10px 0;
        font-size: 9.5pt;
        color: #0369a1;
    }}

    /* Images */
    .img-container {{
        text-align: center;
        margin: 20px 0;
        page-break-inside: avoid;
    }}

    img {{
        max-width: 100%;
        height: auto;
        border-radius: 12px;
        box-shadow: 0 12px 20px -5px rgba(0, 0, 0, 0.15);
        border: 1.5px solid #cbd5e1;
    }}

    em {{
        display: block;
        font-size: 8.5pt;
        color: #64748b;
        font-style: italic;
        text-align: center;
        margin-top: 6px;
    }}
</style>
</head>
<body>

<div class="cover-card">
    <div class="team-badge">🏆 DESIGNED & DEVELOPED BY TEAM NASR 🏆</div>
    <div class="cover-title">SkillSprint AI — Master System & Operational Documentation</div>
    <div class="cover-subtitle">Generative AI PowerPlay Corporate Training & Onboarding Intelligence Platform</div>
    <div class="meta-bar">
        <span class="meta-item">Specification: SkillSprint AI SRS v1.0</span>
        <span class="meta-item">Version: 1.0.0</span>
        <span class="meta-item">Status: 100% Production Verified</span>
    </div>
</div>

{body_html}

</body>
</html>
"""

    with open(html_out_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Classy HTML report generated at: {html_out_path}")

    # Convert to PDF via Microsoft Edge Headless
    edge_cmd = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    if not os.path.exists(edge_cmd):
        edge_cmd = "msedge"

    print("Compiling Executive PDF using Microsoft Edge Headless engine...")
    try:
        abs_html = os.path.abspath(html_out_path)
        abs_pdf = os.path.abspath(pdf_out_path)
        cmd = [
            edge_cmd,
            "--headless",
            "--disable-gpu",
            "--print-to-pdf-no-header",
            f"--print-to-pdf={abs_pdf}",
            abs_html
        ]
        subprocess.run(cmd, capture_output=True, text=True)
        if os.path.exists(abs_pdf):
            print(f"Successfully created Classy Master PDF Report at: {pdf_out_path}")
        else:
            print(f"PDF creation failed.")
    except Exception as e:
        print(f"Error running PDF compilation: {e}")

if __name__ == "__main__":
    generate_doc()
