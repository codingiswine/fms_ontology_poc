from rdflib import Graph, Namespace
from pathlib import Path
import os

# 그래프 생성 및 RDF 불러오기
BASE_DIR = Path(__file__).resolve().parent
RDF_PATH = Path(os.getenv("FMS_SPARQL_RDF", BASE_DIR / "1122.rdf"))
g = Graph()
g.parse(str(RDF_PATH), format=RDF_PATH.suffix.replace(".", ""))

# 네임스페이스 정의 (앞에서 설정한 fms:)
fms = Namespace("http://linkfms.kr/ontology/fms#")

# SPARQL 질의문
query = """
SELECT ?worker ?content WHERE {
  ?work a fms:Work ;
        fms:hasDate fms:Date_2025_06_16 ;
        fms:hasWorker ?worker ;
        fms:hasWorkContent ?content .
}
"""

# 질의 실행
results = g.query(query, initNs={"fms": fms})

# 결과 출력
for row in results:
    print("작업자:", row.worker.split("#")[-1], "| 업무내용:", row.content)
