from rdflib import Graph, Literal, Namespace, RDF, URIRef
import pandas as pd
import re
from pathlib import Path
import os

# ✅ CSV 불러오기 (이미 업로드된 파일 사용)
BASE_DIR = Path(__file__).resolve().parent
default_csv = BASE_DIR / "최종업무일지데이터.csv"
csv_path = Path(os.getenv("FMS_SOURCE_CSV", default_csv))
df = pd.read_csv(csv_path)

# ✅ 네임스페이스 정의
FMS = Namespace("http://linkfms.kr/ontology/fms#")
g = Graph()
g.bind("fms", FMS)

# ✅ 장소 + 내용 분리 함수
def split_location_content(text):
    if pd.isna(text):
        return "", ""
    match = re.match(r'^(.*?(?:층|계단|로비|실|공조실|EPS|정산소|분수대|복도|외곽|강당|청사측|매장창고|사무실|관제실|CCTV|PI|대강당))[, ]?(.*)$', text)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    else:
        return "", text.strip()

# ✅ RDF 트리플 생성
for idx, row in df.iterrows():
    work_id = f"Work_{idx+1:04d}"
    work_uri = FMS[work_id]
    g.add((work_uri, RDF.type, FMS.Work))

    # 날짜
    if pd.notna(row["일자"]):
        date_uri = FMS[f"Date_{row['일자']}"]
        g.add((date_uri, RDF.type, FMS.Date))
        g.add((work_uri, FMS.hasDate, date_uri))

    # 작업자
    if isinstance(row["작업자"], str):
        for name in re.split(r"[,\s]", row["작업자"]):
            name = name.strip()
            if name:
                worker_uri = FMS[f"Worker_{name}"]
                g.add((worker_uri, RDF.type, FMS.Worker))
                g.add((worker_uri, FMS.hasName, Literal(name)))
                g.add((work_uri, FMS.hasWorker, worker_uri))

    # 작업시간
    if isinstance(row["작업시간"], str):
        g.add((work_uri, FMS.hasTime, Literal(row["작업시간"])))

    # 장소와 업무내용 분리
    location, content = split_location_content(row["업무내용"])
    if location:
        g.add((work_uri, FMS.hasLocation, Literal(location)))
    if content:
        g.add((work_uri, FMS.hasWorkContent, Literal(content)))

    # 업무계획
    if isinstance(row["업무계획"], str) and row["업무계획"].strip():
        g.add((work_uri, FMS.hasPlan, Literal(row["업무계획"])))

    # 자재 정보
    if isinstance(row["품명"], str):
        mat_uri = FMS[f"Material_{idx+1:04d}"]
        g.add((mat_uri, RDF.type, FMS.Material))
        g.add((mat_uri, FMS.hasName, Literal(row["품명"])))
        g.add((work_uri, FMS.hasMaterial, mat_uri))
        if isinstance(row["규격"], str):
            g.add((mat_uri, FMS.hasSpecification, Literal(row["규격"])))
        if pd.notna(row["수량"]):
            g.add((mat_uri, FMS.hasQuantity, Literal(row["수량"])))

# ✅ RDF 저장
output_path = Path(os.getenv("FMS_RDF_OUTPUT", BASE_DIR / "protege_ready_electricity_data.rdf"))
g.serialize(destination=str(output_path), format="xml")

print(f"✅ RDF saved to {output_path}")
