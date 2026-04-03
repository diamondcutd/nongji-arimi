# 농지알리미

카카오톡 채널 기반 농지 알림 서비스

## 프로젝트 구조

```
nongji-alert/
├── frontend/           ← 랜딩페이지
│   └── index.html
├── database/           ← PostgreSQL 스키마
│   ├── schema/         ← 테이블 정의 (00~09)
│   ├── seeds/          ← 시도 17개 시드
│   └── migrate.sh      ← 마이그레이션 스크립트
└── backend/            ← 크롤러
    ├── crawler/        ← 농지은행 크롤러
    └── requirements.txt
```

## 시작하기

### 1. DB 마이그레이션

```bash
chmod +x database/migrate.sh
./database/migrate.sh
```

### 2. 크롤러 실행

```bash
cd backend
pip install -r requirements.txt
playwright install chromium
python -m crawler.main
```

## 로드맵

1. 랜딩페이지 + DB 구축 (현재)
2. 크롤러 개발
3. 카카오 채널 + 챗봇 webhook
4. 매칭 엔진 + 알림 발송
5. 카카오 로그인 연동
6. 일지 모듈
