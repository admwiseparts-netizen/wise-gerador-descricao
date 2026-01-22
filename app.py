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

def build_meta_description(product, brand, model, y0, y1, years_list):
    """
    Meta description curta (SEO). Ideal ~ 140-160 caracteres, mas não precisa travar.
    """
    years_display = format_years_display(y0, y1)
    if years_display:
        base = f"{product} original usada para {brand} {model} ({years_display}). Peça revisada, envio rápido. Veja fotos e garanta na Wise Moto Parts."
    else:
        base = f"{product} original usada para {brand} {model}. Peça revisada, envio rápido. Veja fotos e garanta na Wise Moto Parts."
    return normalize_spaces(base)

def build_keywords(product, brand, model, y0, y1, years_list):
    """
    Gera palavras-chave/termos de busca (SEO).
    Retorna uma lista em uma linha separada por vírgula.
    """
    product_clean = normalize_spaces(product)
    brand_clean = normalize_spaces(brand)
    model_clean = normalize_spaces(model)

    variants = []

    # Principais combinações
    variants.append(f"{product_clean} {brand_clean} {model_clean}")
    variants.append(f"{product_clean} {model_clean}")
    variants.append(f"{product_clean} {brand_clean}")
    variants.append(f"peça original {brand_clean} {model_clean}")
    variants.append(f"{product_clean} original")
    variants.append(f"{product_clean} usado")
    variants.append(f"{product_clean} original usado")
    variants.append(f"moto {brand_clean} {model_clean} peças")
    variants.append(f"peças {brand_clean} {model_clean}")

    # Anos (range e anos separados)
    if y0 and y1:
        variants.append(f"{product_clean} {brand_clean} {model_clean} {y0} {y1}")
        variants.append(f"{product_clean} {model_clean} {y0} a {y1}")
        if years_list:
            # adiciona alguns anos individuais (todos pode ficar muito longo; mas dá pra deixar todos)
            for y in years_list:
                variants.append(f"{product_clean} {model_clean} {y}")

    # Limpeza / dedupe mantendo ordem
    seen = set()
    out = []
    for v in variants:
        v2 = normalize_spaces(v)
        key = v2.lower()
        if v2 and key not in seen:
            seen.add(key)
            out.append(v2)

    return ", ".join(out)
  def copy_block(label: str, text: str, key: str, height: int = 180):
    """
    Renderiza um bloco com textarea (somente leitura) + botão Copiar.
    """
    safe_text = (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = f"""
    <div style="border:1px solid #e6e6e6;border-radius:10px;padding:12px;background:#fafafa;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;">
        <div style="font-weight:600;font-size:14px;">{label}</div>
        <button
          id="btn-{key}"
          style="
            padding:6px 10px;
            border-radius:8px;
            border:1px solid #d0d0d0;
            background:white;
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
          border-radius:8px;
          border:1px solid #e6e6e6;
          padding:10px;
          font-size:13px;
          line-height:1.35;
          background:white;
        "
      >{safe_text}</textarea>
    </div>
    """
    components.html(html, height=height + 70)



# -------------------------
# Interface
# -------------------------
st.set_page_config(page_title="Wise Moto Parts - Gerador de Descrição", layout="centered")
# Topo com informações fixas (canto superior direito)
left, right = st.columns([3, 1])

with left:
    st.title("Wise Moto Parts — Gerador automático de descrição")

with right:
    st.markdown(
        """
        <div style="
            text-align:right;
            border:1px solid #e6e6e6;
            padding:10px 12px;
            border-radius:10px;
            background:#000000;
            font-size:14px;
            ">
            <b>NCM:</b> 87141000<br>
            <b>CEST:</b> 0107600
        </div>
        """,
        unsafe_allow_html=True
    )


default_title = "Acabamento Interno Direito Yamaha Ténéré 250 2011 a 2014"
title = st.text_input("Cole o título do anúncio", value=default_title)

parsed = parse_title(title)

col1, col2 = st.columns(2)
with col1:
    product = st.text_input("Nome do produto", value=parsed["product"])
    brand = st.text_input("Marca", value=parsed["brand"])
with col2:
    model = st.text_input("Modelo", value=parsed["model"])
    year_start = st.number_input("Ano inicial (opcional)", value=parsed["year_start"] or 0, min_value=0, max_value=2100)
    year_end = st.number_input("Ano final (opcional)", value=parsed["year_end"] or 0, min_value=0, max_value=2100)

condition = st.selectbox(
    "Condição",
    [
        "Produto bom: Produto usado em condições de uso.",
        "Produto com detalhe: Produto usado com pequenas avarias.",
        "Produto novo: Produto novo/sem uso."
    ]
)

# Reconstrói anos se editado manualmente
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
        st.error("Preencha pelo menos: Nome do produto, Marca e Modelo.")
    else:
        description = build_description(product, brand, model, y0, y1, years_list, condition)
        meta = build_meta_description(product, brand, model, y0, y1, years_list)
        keywords = build_keywords(product, brand, model, y0, y1, years_list)

               st.subheader("Descrição")
        copy_block("Descrição (Magazord)", description, key="desc", height=360)

        st.subheader("Meta-description")
        copy_block("Meta-description (SEO)", meta, key="meta", height=120)

        st.subheader("Palavras-chave (SEO)")
        copy_block("Palavras-chave (SEO / Busca interna)", keywords, key="kw", height=160)
