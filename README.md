# 춘천시 버스 노선 빈도 지도

춘천시 시내버스 노선별 하루 운행횟수를 **선 굵기**로 표현한 인터랙티브 지도 웹앱입니다.

## 바로 사용하기 (데모 데이터)

`index.html` 파일을 브라우저로 열면 됩니다. 인터넷 연결만 있으면 서버 없이 바로 실행됩니다.

## 실제 데이터로 전환하기

### 1단계: API 서비스키 발급 (무료, 즉시 승인)

> **서비스키(API Key)란?**  
> 공공데이터를 사용할 때 "나는 이 사람이에요"라고 인증하는 비밀번호 같은 문자열입니다.  
> 공공데이터 포털에서 무료로 즉시 발급됩니다.

1. [data.go.kr](https://www.data.go.kr) 접속 → 회원가입 (무료)
2. 검색창에 **"국토교통부_버스노선정보조회서비스"** 검색
3. [활용신청] 버튼 클릭 → 개발 목적 간단히 입력 → 즉시 승인
4. 마이페이지 → **인증키** 탭 → Decoding 키 복사

### 2단계: 데이터 수집

```bash
pip install requests
```

`fetch_data.py` 파일을 열어 `SERVICE_KEY` 변수에 복사한 키를 붙여넣은 후:

```bash
python fetch_data.py
```

같은 폴더에 `routes.json` 파일이 생성됩니다.

### 3단계: 웹앱에 실데이터 연결

`index.html`의 `ROUTES` 변수 부분을 아래 코드로 교체:

```javascript
// 기존 ROUTES = [...] 대신
let ROUTES = [];
fetch('routes.json')
  .then(r => r.json())
  .then(data => {
    ROUTES = data;
    buildFilters();
    buildLegend();
    buildStats();
    renderRoutes();
  });
```

> **주의**: `routes.json`을 로드하려면 로컬 웹서버가 필요합니다.  
> `python -m http.server 8080` 실행 후 `http://localhost:8080` 접속

## 파일 구조

```
chuncheon-bus-map/
├── index.html       ← 메인 웹앱 (여기만 열면 됨)
├── fetch_data.py    ← 실데이터 수집 스크립트
├── routes.json      ← (선택) 실데이터 수집 후 생성됨
└── README.md        ← 이 파일
```

## 기능

- 노선 유형별 색상 구분 (간선/지선/마을/통학/병원)
- 선 굵기 = 하루 운행횟수 (로그 스케일, 최소 3.5px 보장)
- 유형별 필터 ON/OFF
- 노선 클릭 시 상세정보 팝업 (운행횟수, 배차간격, 정류장 수)
- 글로우 효과로 노선 시각적 강조
