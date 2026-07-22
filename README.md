# Advanced Ontology – 시설물 업무일지 구조화 PoC

<p align="center">
  <img src="docs/images/ontology_based_chatbot.png" alt="LINK FMS Main" width="100%">
</p>

<p align="center">
  <img src="docs/images/graph_search1.png" alt="LINK FMS Main" width="100%">
</p>

<p align="center">
  <img src="docs/images/graph_search2.png" alt="LINK FMS Main" width="100%">
</p>


<br>

대기업 시설물 관리팀의 수기 업무일지를 **Ontology 기반 지식 그래프**로 변환하고, GPT + SPARQL 조합으로 질의응답을 수행하는 PoC 프로젝트입니다. 자유서술형 텍스트를 자동으로 추출·정제해 작업/설비/조치 관계를 명시적으로 표현하고, RDF 그래프를 통해 탐색할 수 있도록 설계했습니다.



## 🧾 프로젝트 개요

- **데이터**: 2024년 이전 업무일지(엑셀/CSV)에 기록된 자유서술형 텍스트
- **목표**:
  1. 장소/업무/조치 등의 핵심 속성을 자동 추출
  2. Ontology(OWL/RDF)로 구조화해 관계를 명시
  3. GPT가 SPARQL 질의를 생성하고 RDF 그래프를 조회하는 RAG 파이프라인 구현
  4. 그래프 시각화로 업무 관계를 탐색할 수 있는 PoC 제공

---

## 🛠 기술 스택

- **Python**: 데이터 전처리, RDF 생성, SPARQL 실행
- **GPT API**: 자연어 질의 → SPARQL 변환
- **rdflib**: RDF/TTL 파일 생성 및 질의
- **Protégé**: Ontology 설계 및 관리
- **pyvis**: RDF 그래프 시각화
- **Regex/Pandas**: 자유서술형 텍스트에서 속성 추출

---

## 📁 주요 파일

| 파일 | 설명 |
| --- | --- |
| `automatic_classification.py` | CSV 업무일지를 읽어 장소/업무/조치/자재 등을 추출하고 FMS Ontology 개체로 RDF 트리플 생성 |
| `2sparql_gpt.py` | 사용자 질문을 GPT-4o로 SPARQL 쿼리로 변환 후 RDF 그래프를 조회하는 CLI |
| `1sparql.py` | 직접 SPARQL을 작성해 RDF 그래프를 조회하는 예제 |
| `3pyvis.py`, `4pyvis_search.py` | RDF 그래프를 pyvis로 시각화 (검색/하이라이트 기능 포함) |
| `*.rdf`, `*.ttl` | Protégé에서 관리하는 Ontology 및 최신 병합 데이터 (`11final_merge.ttl` 등) |

---

## 🚀 실행 방법

1. **가상환경 구성 및 패키지 설치**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt  # rdflib, openai, pyvis 등
   ```

2. **업무일지 → RDF 변환**
   ```bash
   python automatic_classification.py
   ```
   - `latest_electricity_data.csv` 경로를 수정하여 사용
   - 결과 RDF가 `/mnt/data/protege_ready_electricity_data.rdf` 등으로 저장됨

3. **GPT 기반 SPARQL 질의**
   ```bash
   python 2sparql_gpt.py
   ```
   - `.env` 파일에 `OPENAI_API_KEY` 필요
   - 자연어 질문 입력 → GPT가 SPARQL 생성 → RDF 그래프 질의 결과 출력

4. **그래프 시각화**
   ```bash
   python 3pyvis.py          # 기본 시각화
   python 4pyvis_search.py   # 검색/하이라이트 기능 포함
   ```
   - 결과 HTML(`rdf_graph_grouped.html` 등)을 브라우저에서 열어 관계 탐색

---

## 📊 Ontology 구조

- 네임스페이스: `http://linkfms.kr/ontology/fms#`
- 주요 개체
  - `Work`: 개별 작업 (일자/시간/작업자/내용 연결)
  - `Worker`: 작업자 및 이름
  - `Location`, `Plan`, `Material`, `Date`, `Time` 등
- Ontology는 Protégé에서 관리하며 `11final_merge.ttl`, `owl_vol1_clean.rdf` 등으로 버전 관리됩니다.

---

## 🔮 향후 개선 아이디어

- 자동 추출 정확도 향상을 위한 NER/ML 모델 도입
- SPARQL 결과를 자연어로 후처리하는 Answer Agent화
- 관계 시각화 대시보드 웹앱 전환

---

## 📩 문의

- maintainer: danielshin (Internship 프로젝트)
- 용도: PoC / 연구 목적

언제든지 issue나 PR로 개선점을 제안해 주세요! 😊
