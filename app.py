import re
import streamlit as st
import streamlit.components.v1 as components

BRANDS = [
    "YAMAHA", "HONDA", "KAWASAKI", "SUZUKI", "BMW", "DUCATI", "KTM",
    "TRIUMPH", "HARLEY", "BAJAJ", "DAFRA", "KASINSKI", "HAOJUE",
    "SHINERAY", "ROYAL ENFIELD", "PIAGGIO", "APRILIA", "AGUSTA", "MV"
]

YEAR_RE = re.compile(r"\b(19\d{2}|20\d{2})\b")

def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def find_brand_index(tokens):
    up_tokens = [t.upper() for t in tokens]
    brands_sorted = sorted(BRANDS, key=lambda b: len(b.split()), reverse=True)
    for brand in brands_sorted:
        parts = brand.split()
        for i in range(len(up_tokens) - len(parts) + 1):
            if up_tokens[i:i+len(parts)] == parts:
                return i, brand
    return None, None

def parse_years(text: str):
    years = [int(y) for y in YEAR_RE.findall(text)]
    years = sorted(set(years))
    if not years:
        return None, None, []
    if len(years) == 1:
        y0 = years[0]
        return y0, y0, [y0]
    y0, y1 = min(years), max(years)
    return y0, y1, list(range(y0, y1 + 1))

def parse_title(title: str):
    raw = normalize_spaces(title)
    y0, y1, years_list = parse_years(raw)

    wo_years = YEAR_RE.sub("", raw)
    wo_years = wo_years.replace("(", " ").replace(")", " ")
    wo_years = normalize_spaces(wo_years)

    tokens = wo_years.split(" ")
    brand_idx, brand_upper = find_brand_index(tokens)

    product = ""
    brand = ""
    model = ""

    if brand_idx is not None:
        product = " ".join(tokens[:brand_idx]).strip()
        brand = brand_upper.title()
        brand_len = len(brand_upper.split())
        model = " ".join(tokens[brand_idx + brand_len:]).strip()
    else:
        product = wo_years

    return {
        "product": normalize_spaces(product),
        "brand": normalize_spaces(brand),
        "model": normalize_spaces(model),
        "year_start": y0,
        "year_end": y1,
        "years_list": years_list
    }

def format_years_display(y0, y1):
    if not y0:
        return ""
    if y0 == y1:
        return f"{y0}"
    return f"{y0} a {y1}"

def format_years_list(years_list):
    return ", ".join(str(y) for y in years_list)

def build_description(product, brand, model, y0, y1, years_list, condition_text):
    years_display = format_years_display(y0, y1)

    item_line = f"01 {product.upper()} - {brand.upper()} - {model.upper()}"
    if years_display:
        item_line += f" ( {years_display} )"

    if years_list:
        aplicaveis_block = (
            "Aplicável para os seguintes veículos:\n"
            f"Marca: {brand.upper()}\n"
            f"Modelo: {model.upper()}\n"
            f"Compatibilidade: {format_years_list(years_list)}\n"
        )
        compat_line = f"{brand.upper()} - {model.upper()} ({format_years_list(years_list)})"
    else:
        aplicaveis_block = (
            "Aplicável para os seguintes veículos:\n"
            f"Marca: {brand.upper()}\n"
            f"Modelo: {model.upper()}\n"
        )
        compat_line = f"{brand.upper()} - {model.upper()}"

    desc = f"""Esse anúncio contém:

{item_line}

{condition_text}

Favor verificar todas as fotos antes de efetuar a compra.

Veículo sucata adquirido em leilão.

{aplicaveis_block}
Procedência:
Adquirimos nossas peças diretamente de leilões de seguradora, veículos com baixa no DETRAN ou sucata legalizada, sempre com nota fiscal e conforme a lei

Sobre a Wise Moto Parts:
Nos desafiamos a ser referência em reuso selo verde, padronização e fornecimento de peças originais e confiáveis, com produtos genuínos de qualidade e prontos para uso, tornando-nos referência em reciclagem e reutilização no ramo de moto peças.

Compatível com os seguintes veículos:

{compat_line}
"""
    return desc.strip()

def build_meta_description(product, brand, model, y0, y1):
    years_display = format_years_display(y0, y1)
    if years_display:
        base = f"{product} original usada para {brand} {model} ({years_display}). Envio rápido. Veja fotos e garanta na Wise Moto Parts."
    else:
        base = f"{product} original usada para {brand} {model}. Envio rápido. Veja fotos e garanta na Wise Moto Parts."
    return normalize_spaces(base)

def build_keywords(product, brand, model, y0, y1, years_list):
    variants = [
        f"{product} {brand} {model}",
        f"{product} {model}",
        f"{product} original",
        f"{product} usado",
        f"peças {brand} {model}",
    ]
    if y0 and y1:
        variants.append(f"{product} {model} {y0} a {y1}")
        for y in years_list:
            variants.append(f"{product} {model} {y}")

    out = []
    seen = set()
    for v in variants:
        v2 = normalize_spaces(v)
        if v2.lower() not in seen:
            seen.add(v2.lower())
            out.append(v2)
    return ", ".join(out)

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


# ---------------- Interface ----------------
st.set_page_config(page_title="Wise Moto Parts - Gerador", layout="centered")

left, right = st.columns([3, 1])
with left:
    st.title("Wise Moto Parts — Gerador automático")
with right:
  st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], .stApp {
  background: #0f0f0f !important;
  color: #ffffff !important;
}
[data-testid="stHeader"] { background: #0f0f0f !important; }
</style>
""", unsafe_allow_html=True)

default_title = "Acabamento Interno Direito Yamaha Ténéré 250 2011 a 2014"
title = st.text_input("Cole o título do anúncio", value=default_title)

parsed = parse_title(title)

col1, col2 = st.columns(2)
with col1:
    product = st.text_input("Nome do produto", value=parsed["product"])
    brand = st.text_input("Marca", value=parsed["brand"])
with col2:
    model = st.text_input("Modelo", value=parsed["model"])
    year_start = st.number_input("Ano inicial", value=parsed["year_start"] or 0, min_value=0, max_value=2100)
    year_end = st.number_input("Ano final", value=parsed["year_end"] or 0, min_value=0, max_value=2100)

condition = st.selectbox("Condição", [
    "Produto bom: Produto usado em condições de uso.",
    "Produto com detalhe: Produto usado com pequenas avarias.",
    "Produto novo: Produto novo/sem uso."
])

years_list = []
y0 = year_start if year_start != 0 else None
y1 = year_end if year_end != 0 else None
if y0 and y1:
    if y1 < y0:
        y0, y1 = y1, y0
    years_list = list(range(int(y0), int(y1) + 1))
elif y0 and not y1:
    years_list = [int(y0)]
    y1 = y0

if st.button("Gerar conteúdo"):
    if not product or not brand or not model:
        st.error("Preencha Nome, Marca e Modelo.")
    else:
        description = build_description(product, brand, model, y0, y1, years_list, condition)
        meta = build_meta_description(product, brand, model, y0, y1)
        keywords = build_keywords(product, brand, model, y0, y1, years_list)

        copy_block("Descrição", description, "desc", 360)
        copy_block("Meta-description", meta, "meta", 120)
        copy_block("Palavras-chave", keywords, "kw", 160)
