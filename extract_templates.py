import urllib.request
import json
import os

links = [
    "https://alienart.io/projects/6af26821fb1a2e56fcbc5666",
    "https://alienart.io/projects/6aed009d29543f79d69a2e4f",
    "https://alienart.io/projects/6aecf8c029543f79d695391b",
    "https://alienart.io/projects/6ae71dd115f2e50af26aee9b",
    "https://alienart.io/projects/6aeb0ec0584440b52eacc1ba",
    "https://alienart.io/projects/6ae40ac39fb324834076a1c0",
    "https://alienart.io/projects/6ad9c0211107b1191fd52a47",
    "https://alienart.io/projects/6acf358d2a7baf2aee0e40b1",
    "https://alienart.io/projects/6abe2013c9e292c751eff877",
    "https://alienart.io/projects/6ac59c129e3a114181ed7075"
]

results = []
for link in links:
    pid = link.split("/")[-1]
    url = f"https://alienart.io/api/projects/{pid}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req) as res:
            d = json.loads(res.read().decode("utf-8"))
            proj = d.get("project", {})
            title = proj.get("title", "Untitled")
            layers = proj.get("layers", [])
            comp_layer = None
            bg_layer = None
            for l in layers:
                if l.get("type") in ["advancedComparison", "comparison"]:
                    comp_layer = l
                elif l.get("type") == "image" and l.get("title") == "Background":
                    bg_layer = l
            
            elements_info = []
            if comp_layer:
                vals = comp_layer.get("values", {})
                for el in comp_layer.get("elements", []):
                    el_type = el.get("type")
                    el_title = el.get("title")
                    top = el.get("top")
                    h = el.get("height")
                    v = el.get("values", {})
                    elements_info.append({
                        "title": el_title,
                        "type": el_type,
                        "top": top,
                        "height": h,
                        "color": v.get("color"),
                        "gradient": v.get("gradient"),
                        "font": v.get("fontFamily"),
                        "fontSize": v.get("fontSize"),
                        "values": v
                    })
            results.append({
                "id": pid,
                "title": title,
                "bg_color": bg_layer.get("values", {}).get("color") if bg_layer else None,
                "itemWidth": comp_layer.get("values", {}).get("itemWidth") if comp_layer else None,
                "elements": elements_info
            })
    except Exception as e:
        results.append({"id": pid, "error": str(e)})

os.makedirs("config", exist_ok=True)
with open("config/alienart_extracted_projects.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"Total projects extracted: {len(results)}")
for r in results:
    print(f"\n==========================================")
    print(f"ID: {r.get('id')} | Title: {r.get('title')}")
    print(f"Item Width: {r.get('itemWidth')} | BG: {r.get('bg_color')}")
    for el in r.get('elements', []):
        grad_txt = "HAS_GRADIENT" if el.get('gradient') else "no_grad"
        print(f"  [{el.get('type'):<6}] top={str(el.get('top')):<4} h={str(el.get('height')):<4} font={str(el.get('font')):<12} {el.get('title')} ({grad_txt})")
