def copy_block(label: str, text: str, key: str, height: int = 180):
    safe_text = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = f"""
    <div style="
        border:1px solid #2b2b2b;
        border-radius:12px;
        padding:12px;
        background:#0b0b0b;
        color:#ffffff;
        margin-bottom:14px;
    ">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
        <div style="font-weight:700;font-size:14px;color:#ffffff;">{label}</div>
        <button
          id="btn-{key}"
          style="
            padding:7px 12px;
            border-radius:10px;
            border:1px solid #3a3a3a;
            background:#151515;
            color:#ffffff;
            cursor:pointer;
            font-size:13px;
          "
          onclick="navigator.clipboard.writeText(document.getElementById('ta-{key}').value)
            .then(() => {{
              const b = document.getElementById('btn-{key}');
              const old = b.innerText;
              b.innerText = 'Copiado ✓';
              setTimeout(() => b.innerText = old, 1200);
            }});"
        >Copiar</button>
      </div>

      <textarea
        id="ta-{key}"
        readonly
        style="
          width:100%;
          height:{height}px;
          resize:vertical;
          border-radius:10px;
          border:1px solid #2b2b2b;
          padding:12px;
          font-size:13px;
          line-height:1.4;
          background:#000000;
          color:#ffffff;
          outline:none;
        "
      >{safe_text}</textarea>
    </div>
    """
    components.html(html, height=height + 90)
