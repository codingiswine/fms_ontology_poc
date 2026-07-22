from rdflib import Graph, Namespace
from openai import OpenAI
import os
from dotenv import load_dotenv
import re
from pathlib import Path

# 🔐 OpenAI API 키 로딩
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 📂 RDF 그래프 불러오기
BASE_DIR = Path(__file__).resolve().parent
RDF_PATH = Path(os.getenv("FMS_RDF_PATH", BASE_DIR / "11final_merge.ttl"))
g = Graph()
g.parse(str(RDF_PATH), format="turtle")


# 📦 네임스페이스 설정
fms = Namespace("http://linkfms.kr/ontology/fms#")
rdf = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")


##### 테스트 코드 시작
# ✅ 📌 여기에 디버깅 코드 추가
#print("[location 값에 '옥상' 들어간 것 출력]")
#for s, p, o in g:
#    if "옥상" in str(o):
#        print(s, p, o)
#
#for s, p, o in g.triples((None, fms.hasLocation, None)):
#    print("📍hasLocation triple →", s, p, o, "TYPE:", type(o))



####### 테스트 코드 끝


# 💬 사용자 질문 루프
while True:
    user_question = input("\n사용자 질문 (종료하려면 '종료' 입력): ").strip()
    if user_question.lower() in ["종료", "exit", "quit"]:
        print("✅ 종료합니다.")
        break

    # 🤖 GPT 프롬프트 구성
    sparql_prompt = f"""
    너는 RDF 온톨로지 기반 전기 작업 데이터를 검색하는 전문가야.
    내가 묻는 질문을 메인 키워드로 잡고 그것에 관련된 내용을 보여주고 관련된 게 많다면 관련도가 높은 순서대로 3개씩 보여줘
    네임스페이스는 fms: 이고 주요 속성은 다음과 같아:

    - fms:Work (rdf:type)
    - fms:hasDate (날짜, 예: "2025_06_17")
    - fms:hasWorker (작업자, 연결된 개체)
    - fms:hasName (작업자 이름 속성, 예: "박기준")
    - fms:hasLocation (장소, 예: "1층 로비")
    - fms:hasTime (시간, 예: "14:00~15:00")
    - fms:hasPlan (업무계획, 예: "옥상 점검")
    - fms:hasWorkContent (업무내용, 예: "센서 교체")

    사용자 질문에 따라 정확한 SPARQL SELECT 쿼리만 작성해줘.
    설명 없이 SELECT ~ WHERE {{ ... }} 형식만 반환하고,
    반드시 점(.)으로 triple을 나눠 써줘.
    PREFIX는 생략하고 fms: 접두어만 써.
    
    ❗️필수 규칙:
    - 작업자 이름 검색 시: ?work → hasWorker → ?worker → hasName → ?name → FILTER(CONTAINS(?name, "박기준"))
    - 날짜는 MONTH 같은 함수 쓰지 말고 CONTAINS(STR(?date), "2025_06") 처럼 처리해
    - 장소/업무내용 검색 시에는 CONTAINS + LCASE 조합을 써도 좋아

    예시 질문:
    "박기준 업무내역 알려줘"
    → SELECT ?content WHERE {{
        ?work rdf:type fms:Work .
        ?work fms:hasWorker ?worker .
        ?worker fms:hasName ?name .
        ?work fms:hasWorkContent ?content .
        FILTER(CONTAINS(?name, "박기준"))
    }}

    질문: {user_question}
    """

    # 🧠 GPT에게 쿼리 생성 요청
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "너는 RDF 온톨로지 데이터에서 SPARQL 쿼리를 생성하는 전문가야."},
            {"role": "user", "content": sparql_prompt}
        ]
    )

    # 🎯 SPARQL 쿼리 추출
    gpt_text = response.choices[0].message.content.strip()
    sparql_match = re.search(r"SELECT\s+.*?WHERE\s*\{.*?\}", gpt_text, re.DOTALL | re.IGNORECASE)

    if not sparql_match:
        print("❌ GPT 응답에서 유효한 SPARQL 쿼리를 찾을 수 없습니다.")
        print("GPT 응답 전체:\n", gpt_text)
        continue

    sparql_query = sparql_match.group(0)
    print("\n✅ 최종 SPARQL 실행 쿼리:")
    print(sparql_query)

    # 🧾 SPARQL 쿼리 실행
    try:
        results = g.query(sparql_query, initNs={"fms": fms, "rdf": rdf})
        print("\n📌 질의 결과:")
        found = False
        for row in results:
            found = True
            for var, val in row.asdict().items():
                print(f"{var}: {val}")
            print("-----")
        if not found:
            print("⚠️ 결과 없음.")
    except Exception as e:
        print("\n❌ SPARQL 실행 오류:", e)
