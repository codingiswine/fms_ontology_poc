from rdflib import Graph
from pyvis.network import Network
from rdflib.namespace import RDF
from pathlib import Path
import os

# RDF 파일 불러오기
BASE_DIR = Path(__file__).resolve().parent
RDF_PATH = Path(os.getenv("FMS_VIS_RDF", BASE_DIR / "11final_merge.ttl"))
OUTPUT_HTML = Path(os.getenv("FMS_VIS_OUTPUT", BASE_DIR / "rdf_graph_grouped.html"))
g = Graph()
g.parse(str(RDF_PATH), format="turtle")

# pyvis 초기화
net = Network(height="800px", width="100%", notebook=False, directed=True)
net.force_atlas_2based()

# 클래스별 색상 지정
class_colors = {
    "Work": "#FFADAD",
    "Worker": "#FFD6A5",
    "Date": "#FDFFB6",
    "Material": "#CAFFBF",
    "Location": "#9BF6FF",
    "Plan": "#A0C4FF",
    "Time": "#BDB2FF",
    "Quantity": "#FFC6FF",
    "Specification": "#FFFFFC"
}

added_nodes = set()
node_classes = {}

# 클래스 정보를 먼저 수집
for s, p, o in g.triples((None, RDF.type, None)):
    node_classes[str(s)] = o.split("#")[-1] if "#" in o else o

# triple 순회하면서 노드와 엣지 추가
for s, p, o in g:
    s, p, o = str(s), str(p), str(o)

    for node in [s, o]:
        if node not in added_nodes:
            node_class = node_classes.get(node, "")
            label = node.split("#")[-1]
            color = class_colors.get(node_class, "#D3D3D3")  # 기본 회색
            net.add_node(node, label=label, color=color, title=node_class)
            added_nodes.add(node)

    net.add_edge(s, o, label=p.split("#")[-1])

# pyvis 인터랙션 옵션 추가 (검색창 등)
net.toggle_physics(True)
net.show_buttons(filter_=['interaction'])

# 저장
net.save_graph(str(OUTPUT_HTML))
print(f"✅ Graph saved to {OUTPUT_HTML}")
