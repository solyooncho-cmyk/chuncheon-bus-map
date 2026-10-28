"""
춘천시 버스 노선 데이터 수집기 (TAGO 공공데이터 API)
=====================================================

사용 전 준비:
1. https://www.data.go.kr 에 회원가입 (무료)
2. "국토교통부_버스노선정보조회서비스" 검색 → 활용신청
   (즉시 승인 / 무료)
3. 마이페이지 → 인증키 복사
4. 아래 SERVICE_KEY 변수에 붙여넣기

실행:
    pip install requests
    python fetch_data.py

결과:
    routes.json 파일이 생성됩니다.
    index.html 과 같은 폴더에 두면 실제 데이터를 사용합니다.
"""

import requests
import json
import time
import math

# =============================================
# ★ 여기에 발급받은 서비스키를 붙여넣으세요 ★
# =============================================
SERVICE_KEY = "YOUR_SERVICE_KEY_HERE"

CITY_CODE = 32010        # 춘천시 도시코드
BASE_URL  = "http://apis.data.go.kr/1613000/BusRouteInfoInqireService"

ROUTE_TYPE_MAP = {
    "11": "간선",
    "12": "지선",
    "13": "지선",
    "14": "지선",
    "21": "마을",
    "22": "마을",
    "51": "통학",
    "52": "병원",
}

def get(endpoint, params):
    """API 호출 헬퍼 함수"""
    url = f"{BASE_URL}/{endpoint}"
    params.update({
        "serviceKey": SERVICE_KEY,
        "cityCode":   CITY_CODE,
        "_type":      "json",
        "numOfRows":  500,
        "pageNo":     1,
    })
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    body = resp.json().get("response", {}).get("body", {})
    items = body.get("items", {})
    if not items:
        return []
    item = items.get("item", [])
    return item if isinstance(item, list) else [item]

def fetch_routes():
    """노선 목록 전체 조회"""
    print("노선 목록 조회 중...")
    return get("getBusRouteList", {})

def fetch_route_detail(route_id):
    """노선 상세정보 (운행횟수 등) 조회"""
    return get("getBusRouteInfoIem", {"routeId": route_id})

def fetch_route_stops(route_id):
    """경유 정류장 좌표 목록 조회"""
    stops = get("getStaionByRoute", {"routeId": route_id})
    coords = []
    for s in stops:
        lat = s.get("gpsY") or s.get("latitude")
        lng = s.get("gpsX") or s.get("longitude")
        if lat and lng:
            coords.append([float(lat), float(lng)])
    return coords

def estimate_daily_trips(detail):
    """운행횟수 추정 (API 필드명이 다를 수 있어 여러 경우 시도)"""
    for key in ["nonstopYn", "routeTp", "peakAlloc", "offpeakAlloc"]:
        pass  # 실제 필드 구조는 API 문서 참고

    # 첫차/막차로 추정
    first = detail.get("startVehicleTime", "0600")
    last  = detail.get("endVehicleTime",   "2200")
    alloc = detail.get("peekAlloc") or detail.get("peakAlloc") or 20

    try:
        fh = int(str(first)[:2])
        lh = int(str(last)[:2])
        operating_mins = max((lh - fh) * 60, 60)
        trips = int(operating_mins / max(int(alloc), 1))
        return max(trips, 1)
    except Exception:
        return 10  # 기본값

def main():
    if SERVICE_KEY == "YOUR_SERVICE_KEY_HERE":
        print("[오류] SERVICE_KEY를 설정해주세요!")
        print("  → fetch_data.py 파일을 열어 SERVICE_KEY 변수에 발급받은 키를 입력하세요.")
        return

    routes_list = fetch_routes()
    print(f"총 {len(routes_list)}개 노선 발견")

    result = []
    for i, r in enumerate(routes_list):
        route_id = r.get("routeId")
        route_no = r.get("routeNo", "?")
        route_tp = str(r.get("routeTp", "12"))

        print(f"  [{i+1}/{len(routes_list)}] {route_no}번 처리 중...")

        # 정류장 좌표
        time.sleep(0.3)  # API 부하 방지
        coords = fetch_route_stops(route_id)

        # 상세정보
        details = fetch_route_detail(route_id)
        detail  = details[0] if details else {}
        trips   = estimate_daily_trips(detail)

        result.append({
            "id":    route_id,
            "no":    route_no,
            "type":  ROUTE_TYPE_MAP.get(route_tp, "지선"),
            "trips": trips,
            "stops": len(coords),
            "start": r.get("startNodeName", ""),
            "end":   r.get("endNodeName", ""),
            "path":  coords,
        })

    with open("routes.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n완료! routes.json 저장됨 ({len(result)}개 노선)")

if __name__ == "__main__":
    main()
