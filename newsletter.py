from datetime import datetime
from dateutil import tz
import requests, pandas as pd, yaml, os, io, csv
from jinja2 import Template

CONFIG_PATH = "config.yaml"
EDITO_PATH = "data/edito.md"
TEMPLATE_PATH = "templates/newsletter.html.j2"

# --- URLs officielles ---
DG_API = "https://www.data.gouv.fr/api/1/datasets/"
CRE_DATASET_METROPOLE = "arretes-tarifaires-photovoltaiques-en-metropole"
CRE_DATASET_ZNI = "arretes-tarifaires-photovoltaiques-en-zones-non-interconnectees-zni"

def paris_now_iso():
    tz_paris = tz.gettz("Europe/Paris")
    return datetime.now(tz_paris).strftime("%Y-%m-%d %H:%M")

def latest_resource_url(slug, prefer=("csv","xlsx","json")):
    ds = requests.get(f"{DG_API}{slug}/", timeout=30).json()
    resources = ds.get("resources", [])
    for fmt in prefer:
        cand = [r for r in resources if r.get("format","").lower()==fmt]
        if cand:
            best = sorted(cand, key=lambda r: r.get("last_modified") or r.get("created_at") or "", reverse=True)[0]
            rid = best["id"]
            return f"https://www.data.gouv.fr/api/1/datasets/r/{rid}", ds
    return (resources[0]["url"] if resources else None), ds

def read_cre_table(slug):
    url, ds = latest_resource_url(slug)
    if not url: 
        return None, ds
    r = requests.get(url, timeout=60, allow_redirects=True)
    ct = (r.headers.get("Content-Type") or "").lower()
    if "csv" in ct or url.endswith(".csv"):
        # détection séparateur
        try:
            dialect = csv.Sniffer().sniff(r.text.splitlines()[0])
            df = pd.read_csv(io.StringIO(r.text), dialect=dialect)
        except Exception:
            df = pd.read_csv(io.StringIO(r.text), sep=";")
    elif "json" in ct or url.endswith(".json"):
        df = pd.read_json(io.StringIO(r.text))
    else:
        df = None
    return df, ds

def pick_tarif_surplus_cents(df: pd.DataFrame):
    if df is None or df.empty:
        return None
    # heuristique: cherche une colonne mentionnant "surplus" et numérique
    candidates = [c for c in df.columns if "surplus" in c.lower()]
    for c in candidates:
        s = pd.to_numeric(df[c], errors="coerce").dropna()
        if not s.empty and s.iloc[0] > 0:
            return f"{round(float(s.iloc[0]), 2)} c€/kWh"
    return None

def md_to_html(md_text: str) -> str:
    # mini markdown -> html (bold/italic/links) pour éviter une dépendance
    import re
    html = md_text
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    html = re.sub(r"\[(.+?)\]\((https?://[^\s)]+)\)", r"<a href='\2' target='_blank'>\1</a>", html)
    html = html.replace("\n", "<br/>")
    return html

def main():
    # 1) config & template
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        tpl = Template(f.read())

    # 2) contenu manuel (edito)
    edito_md = ""
    if os.path.exists(EDITO_PATH):
        with open(EDITO_PATH, "r", encoding="utf-8") as f:
            edito_md = f.read().strip()
    edito_html = md_to_html(edito_md) if edito_md else "<em>(Pas d’édito ce mois)</em>"

    # 3) données CRE
    df_metro, ds_metro = read_cre_table(CRE_DATASET_METROPOLE)
    df_zni, ds_zni = read_cre_table(CRE_DATASET_ZNI)
    cre_last_metro = (ds_metro or {}).get("last_modified")
    cre_last_zni = (ds_zni or {}).get("last_modified")
    chiffre_mois = pick_tarif_surplus_cents(df_metro) or "À confirmer (lecture CRE)"

    html = tpl.render(
        site_title = cfg.get("site_title", "Newsletter Echome Energies — Photovoltaïque"),
        brand_color = cfg.get("brand_color", "#37C3AF"),
        text_color = cfg.get("text_color", "#1C1C1C"),
        blocks = cfg.get("blocks", []),
        links = cfg.get("links", {}),
        now_paris = paris_now_iso(),
        edito_html = edito_html,
        cre_last_metro = cre_last_metro,
        cre_last_zni = cre_last_zni,
        chiffre_mois = chiffre_mois
    )
    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Newsletter générée: docs/index.html")

if __name__ == "__main__":
    main()
