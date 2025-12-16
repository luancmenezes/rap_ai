import json
import os

def generate_html(data, output_path="data/outputs/batalha.html"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>Rima Poética</title>
        <style>
            body {{
                font-family: Arial;
                margin: 40px;
            }}
            .punchline {{
                margin-bottom: 20px;
                padding: 10px;
                border-left: 4px solid #555;
                background: #f4f4f4;
            }}
        </style>
    </head>
    <body>
        <h1>Punchlines</h1>
    """

    for p in data["punchlines"]:
        html += f"""
        <div class="punchline">
            <h3>{p['texto']}</h3>
            <p><b>Impacto:</b> {p['score']}/10</p>
            <p>{p['analise']}</p>
        </div>
        """

    html += f"""
        <h2>Poema Final</h2>
        <pre>{data["poema"]}</pre>

    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf8") as f:
        f.write(html)

    return output_path
