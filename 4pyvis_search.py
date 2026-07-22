from rdflib import Graph
from pyvis.network import Network
from rdflib.namespace import RDF
from pathlib import Path
import os

# ✅ RDF 파일 로딩
BASE_DIR = Path(__file__).resolve().parent
RDF_PATH = Path(os.getenv("FMS_VIS_RDF", BASE_DIR / "11final_merge.ttl"))
OUTPUT_HTML = Path(os.getenv("FMS_VIS_SEARCH_OUTPUT", BASE_DIR / "rdf_graph_search_with_esc.html"))
g = Graph()
g.parse(str(RDF_PATH), format="turtle")

# ✅ pyvis 네트워크 초기화
net = Network(height="800px", width="100%", notebook=False, directed=True)
net.force_atlas_2based()

# ✅ 클래스별 색상 정의
class_colors = {
    "Work": "#FFADAD", "Worker": "#FFD6A5", "Date": "#FDFFB6",
    "Material": "#CAFFBF", "Location": "#9BF6FF", "Plan": "#A0C4FF",
    "Time": "#BDB2FF", "Quantity": "#FFC6FF", "Specification": "#FFFFFC"
}

added_nodes = set()
node_classes = {}

# ✅ 클래스 정보 수집
for s, p, o in g.triples((None, RDF.type, None)):
    node_classes[str(s)] = o.split("#")[-1] if "#" in o else o

# ✅ triple에서 노드 및 엣지 추가
for s, p, o in g:
    s, p, o = str(s), str(p), str(o)
    for node in [s, o]:
        if node not in added_nodes:
            label = node.split("#")[-1]
            node_class = node_classes.get(node, "")
            color = class_colors.get(node_class, "#D3D3D3")
            net.add_node(node, label=label, color=color, title=node_class)
            added_nodes.add(node)
    net.add_edge(s, o, label=p.split("#")[-1])

# ✅ 저장 경로 설정
net.save_graph(str(OUTPUT_HTML))

# ✅ 검색 기능 + Enter 순환 + ESC 해제 기능 JS 삽입
with open(OUTPUT_HTML, "r", encoding="utf-8") as f:
    html = f.read()

search_box = """
<input type="text" id="searchInput" placeholder="노드 검색 (예: 5층)" style="position:fixed; top:10px; right:20px; z-index:999; padding:5px; font-size:16px;">
<div id="resultList" style="position:fixed; top:50px; right:20px; z-index:999; background:#fff; max-height:300px; overflow:auto; font-size:14px; border:1px solid #ccc; padding:5px;"></div>

<script>
let searchResults = [];
let searchIndex = 0;

document.getElementById('searchInput').addEventListener('input', function() {
  let query = this.value.toLowerCase();
  let htmlList = '';
  searchResults = [];

  if (query.length === 0) {
    document.getElementById('resultList').innerHTML = '';
    return;
  }

  nodes.forEach(function(node) {
    if (node.label.toLowerCase().includes(query)) {
      let degree = network.getConnectedEdges(node.id).length;
      searchResults.push({node, degree});
    }
  });

  if (searchResults.length > 0) {
    searchResults.sort((a, b) => b.degree - a.degree);
    searchIndex = 0;
    focusAndHighlight(searchResults[searchIndex].node.id);

    searchResults.forEach(c => {
      htmlList += '<div>' + c.node.label + '</div>';
    });
    document.getElementById('resultList').innerHTML = htmlList;
  } else {
    document.getElementById('resultList').innerHTML = "<i>검색 결과 없음</i>";
  }
});

document.getElementById('searchInput').addEventListener('keydown', function(e) {
  if (e.key === "Enter" && searchResults.length > 0) {
    searchIndex = (searchIndex + 1) % searchResults.length;
    focusAndHighlight(searchResults[searchIndex].node.id);
  }
});

document.addEventListener('keydown', function(e) {
  if (e.key === "Escape") {
    network.unselectAll();
  }
});

function focusAndHighlight(nodeId) {
  network.selectNodes([nodeId]);
  network.focus(nodeId, {
    scale: 2,
    animation: { duration: 1000, easingFunction: 'easeInOutQuad' }
  });
  setTimeout(() => {
    network.unselectAll();
  }, 1200);
}
</script>
"""

# ✅ HTML 수정 반영
html = html.replace("</body>", search_box + "\n</body>")
with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Graph with search saved to {OUTPUT_HTML}")
