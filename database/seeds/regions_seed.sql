-- =============================================
-- 농지알리미 regions 시드 데이터
-- 시도 17개 + 시군구 228개 = 총 245건
-- pgAdmin에서 실행 (트랜잭션으로 묶음)
-- =============================================

BEGIN;

-- ── 1단계: 시도 17개 ──────────────────────────

INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  (NULL, '11', '서울특별시',       1, '서울특별시'),
  (NULL, '26', '부산광역시',       1, '부산광역시'),
  (NULL, '27', '대구광역시',       1, '대구광역시'),
  (NULL, '28', '인천광역시',       1, '인천광역시'),
  (NULL, '29', '광주광역시',       1, '광주광역시'),
  (NULL, '30', '대전광역시',       1, '대전광역시'),
  (NULL, '31', '울산광역시',       1, '울산광역시'),
  (NULL, '36', '세종특별자치시',   1, '세종특별자치시'),
  (NULL, '41', '경기도',           1, '경기도'),
  (NULL, '42', '강원특별자치도',   1, '강원특별자치도'),
  (NULL, '43', '충청북도',         1, '충청북도'),
  (NULL, '44', '충청남도',         1, '충청남도'),
  (NULL, '45', '전북특별자치도',   1, '전북특별자치도'),
  (NULL, '46', '전라남도',         1, '전라남도'),
  (NULL, '47', '경상북도',         1, '경상북도'),
  (NULL, '48', '경상남도',         1, '경상남도'),
  (NULL, '50', '제주특별자치도',   1, '제주특별자치도');

-- ── 2단계: 시군구 228개 ───────────────────────
-- parent_id는 시도 code로 조회

-- ■ 서울특별시 (25구)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='11'), '11010', '종로구',     2, '서울특별시 > 종로구'),
  ((SELECT id FROM regions WHERE code='11'), '11020', '중구',       2, '서울특별시 > 중구'),
  ((SELECT id FROM regions WHERE code='11'), '11030', '용산구',     2, '서울특별시 > 용산구'),
  ((SELECT id FROM regions WHERE code='11'), '11040', '성동구',     2, '서울특별시 > 성동구'),
  ((SELECT id FROM regions WHERE code='11'), '11050', '광진구',     2, '서울특별시 > 광진구'),
  ((SELECT id FROM regions WHERE code='11'), '11060', '동대문구',   2, '서울특별시 > 동대문구'),
  ((SELECT id FROM regions WHERE code='11'), '11070', '중랑구',     2, '서울특별시 > 중랑구'),
  ((SELECT id FROM regions WHERE code='11'), '11080', '성북구',     2, '서울특별시 > 성북구'),
  ((SELECT id FROM regions WHERE code='11'), '11090', '강북구',     2, '서울특별시 > 강북구'),
  ((SELECT id FROM regions WHERE code='11'), '11100', '도봉구',     2, '서울특별시 > 도봉구'),
  ((SELECT id FROM regions WHERE code='11'), '11110', '노원구',     2, '서울특별시 > 노원구'),
  ((SELECT id FROM regions WHERE code='11'), '11120', '은평구',     2, '서울특별시 > 은평구'),
  ((SELECT id FROM regions WHERE code='11'), '11130', '서대문구',   2, '서울특별시 > 서대문구'),
  ((SELECT id FROM regions WHERE code='11'), '11140', '마포구',     2, '서울특별시 > 마포구'),
  ((SELECT id FROM regions WHERE code='11'), '11150', '양천구',     2, '서울특별시 > 양천구'),
  ((SELECT id FROM regions WHERE code='11'), '11160', '강서구',     2, '서울특별시 > 강서구'),
  ((SELECT id FROM regions WHERE code='11'), '11170', '구로구',     2, '서울특별시 > 구로구'),
  ((SELECT id FROM regions WHERE code='11'), '11180', '금천구',     2, '서울특별시 > 금천구'),
  ((SELECT id FROM regions WHERE code='11'), '11190', '영등포구',   2, '서울특별시 > 영등포구'),
  ((SELECT id FROM regions WHERE code='11'), '11200', '동작구',     2, '서울특별시 > 동작구'),
  ((SELECT id FROM regions WHERE code='11'), '11210', '관악구',     2, '서울특별시 > 관악구'),
  ((SELECT id FROM regions WHERE code='11'), '11220', '서초구',     2, '서울특별시 > 서초구'),
  ((SELECT id FROM regions WHERE code='11'), '11230', '강남구',     2, '서울특별시 > 강남구'),
  ((SELECT id FROM regions WHERE code='11'), '11240', '송파구',     2, '서울특별시 > 송파구'),
  ((SELECT id FROM regions WHERE code='11'), '11250', '강동구',     2, '서울특별시 > 강동구');

-- ■ 부산광역시 (15구 1군 = 16)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='26'), '26010', '중구',       2, '부산광역시 > 중구'),
  ((SELECT id FROM regions WHERE code='26'), '26020', '서구',       2, '부산광역시 > 서구'),
  ((SELECT id FROM regions WHERE code='26'), '26030', '동구',       2, '부산광역시 > 동구'),
  ((SELECT id FROM regions WHERE code='26'), '26040', '영도구',     2, '부산광역시 > 영도구'),
  ((SELECT id FROM regions WHERE code='26'), '26050', '부산진구',   2, '부산광역시 > 부산진구'),
  ((SELECT id FROM regions WHERE code='26'), '26060', '동래구',     2, '부산광역시 > 동래구'),
  ((SELECT id FROM regions WHERE code='26'), '26070', '남구',       2, '부산광역시 > 남구'),
  ((SELECT id FROM regions WHERE code='26'), '26080', '북구',       2, '부산광역시 > 북구'),
  ((SELECT id FROM regions WHERE code='26'), '26090', '해운대구',   2, '부산광역시 > 해운대구'),
  ((SELECT id FROM regions WHERE code='26'), '26100', '사하구',     2, '부산광역시 > 사하구'),
  ((SELECT id FROM regions WHERE code='26'), '26110', '금정구',     2, '부산광역시 > 금정구'),
  ((SELECT id FROM regions WHERE code='26'), '26120', '강서구',     2, '부산광역시 > 강서구'),
  ((SELECT id FROM regions WHERE code='26'), '26130', '연제구',     2, '부산광역시 > 연제구'),
  ((SELECT id FROM regions WHERE code='26'), '26140', '수영구',     2, '부산광역시 > 수영구'),
  ((SELECT id FROM regions WHERE code='26'), '26150', '사상구',     2, '부산광역시 > 사상구'),
  ((SELECT id FROM regions WHERE code='26'), '26310', '기장군',     2, '부산광역시 > 기장군');

-- ■ 대구광역시 (7구 2군 = 9) — 군위군 2023년 편입
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='27'), '27010', '중구',       2, '대구광역시 > 중구'),
  ((SELECT id FROM regions WHERE code='27'), '27020', '동구',       2, '대구광역시 > 동구'),
  ((SELECT id FROM regions WHERE code='27'), '27030', '서구',       2, '대구광역시 > 서구'),
  ((SELECT id FROM regions WHERE code='27'), '27040', '남구',       2, '대구광역시 > 남구'),
  ((SELECT id FROM regions WHERE code='27'), '27050', '북구',       2, '대구광역시 > 북구'),
  ((SELECT id FROM regions WHERE code='27'), '27060', '수성구',     2, '대구광역시 > 수성구'),
  ((SELECT id FROM regions WHERE code='27'), '27070', '달서구',     2, '대구광역시 > 달서구'),
  ((SELECT id FROM regions WHERE code='27'), '27310', '달성군',     2, '대구광역시 > 달성군'),
  ((SELECT id FROM regions WHERE code='27'), '27320', '군위군',     2, '대구광역시 > 군위군');

-- ■ 인천광역시 (8구 2군 = 10)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='28'), '28010', '중구',       2, '인천광역시 > 중구'),
  ((SELECT id FROM regions WHERE code='28'), '28020', '동구',       2, '인천광역시 > 동구'),
  ((SELECT id FROM regions WHERE code='28'), '28030', '미추홀구',   2, '인천광역시 > 미추홀구'),
  ((SELECT id FROM regions WHERE code='28'), '28040', '연수구',     2, '인천광역시 > 연수구'),
  ((SELECT id FROM regions WHERE code='28'), '28050', '남동구',     2, '인천광역시 > 남동구'),
  ((SELECT id FROM regions WHERE code='28'), '28060', '부평구',     2, '인천광역시 > 부평구'),
  ((SELECT id FROM regions WHERE code='28'), '28070', '계양구',     2, '인천광역시 > 계양구'),
  ((SELECT id FROM regions WHERE code='28'), '28080', '서구',       2, '인천광역시 > 서구'),
  ((SELECT id FROM regions WHERE code='28'), '28310', '강화군',     2, '인천광역시 > 강화군'),
  ((SELECT id FROM regions WHERE code='28'), '28320', '옹진군',     2, '인천광역시 > 옹진군');

-- ■ 광주광역시 (5구)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='29'), '29010', '동구',       2, '광주광역시 > 동구'),
  ((SELECT id FROM regions WHERE code='29'), '29020', '서구',       2, '광주광역시 > 서구'),
  ((SELECT id FROM regions WHERE code='29'), '29030', '남구',       2, '광주광역시 > 남구'),
  ((SELECT id FROM regions WHERE code='29'), '29040', '북구',       2, '광주광역시 > 북구'),
  ((SELECT id FROM regions WHERE code='29'), '29050', '광산구',     2, '광주광역시 > 광산구');

-- ■ 대전광역시 (5구)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='30'), '30010', '동구',       2, '대전광역시 > 동구'),
  ((SELECT id FROM regions WHERE code='30'), '30020', '중구',       2, '대전광역시 > 중구'),
  ((SELECT id FROM regions WHERE code='30'), '30030', '서구',       2, '대전광역시 > 서구'),
  ((SELECT id FROM regions WHERE code='30'), '30040', '유성구',     2, '대전광역시 > 유성구'),
  ((SELECT id FROM regions WHERE code='30'), '30050', '대덕구',     2, '대전광역시 > 대덕구');

-- ■ 울산광역시 (4구 1군 = 5)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='31'), '31010', '중구',       2, '울산광역시 > 중구'),
  ((SELECT id FROM regions WHERE code='31'), '31020', '남구',       2, '울산광역시 > 남구'),
  ((SELECT id FROM regions WHERE code='31'), '31030', '동구',       2, '울산광역시 > 동구'),
  ((SELECT id FROM regions WHERE code='31'), '31040', '북구',       2, '울산광역시 > 북구'),
  ((SELECT id FROM regions WHERE code='31'), '31310', '울주군',     2, '울산광역시 > 울주군');

-- ■ 세종특별자치시 — 시군구 없음 (단일 행정구역, 바로 읍면동)

-- ■ 경기도 (28시 3군 = 31)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='41'), '41010', '수원시',     2, '경기도 > 수원시'),
  ((SELECT id FROM regions WHERE code='41'), '41020', '성남시',     2, '경기도 > 성남시'),
  ((SELECT id FROM regions WHERE code='41'), '41030', '의정부시',   2, '경기도 > 의정부시'),
  ((SELECT id FROM regions WHERE code='41'), '41040', '안양시',     2, '경기도 > 안양시'),
  ((SELECT id FROM regions WHERE code='41'), '41050', '부천시',     2, '경기도 > 부천시'),
  ((SELECT id FROM regions WHERE code='41'), '41060', '광명시',     2, '경기도 > 광명시'),
  ((SELECT id FROM regions WHERE code='41'), '41070', '평택시',     2, '경기도 > 평택시'),
  ((SELECT id FROM regions WHERE code='41'), '41080', '동두천시',   2, '경기도 > 동두천시'),
  ((SELECT id FROM regions WHERE code='41'), '41090', '안산시',     2, '경기도 > 안산시'),
  ((SELECT id FROM regions WHERE code='41'), '41100', '고양시',     2, '경기도 > 고양시'),
  ((SELECT id FROM regions WHERE code='41'), '41110', '과천시',     2, '경기도 > 과천시'),
  ((SELECT id FROM regions WHERE code='41'), '41120', '구리시',     2, '경기도 > 구리시'),
  ((SELECT id FROM regions WHERE code='41'), '41130', '남양주시',   2, '경기도 > 남양주시'),
  ((SELECT id FROM regions WHERE code='41'), '41140', '오산시',     2, '경기도 > 오산시'),
  ((SELECT id FROM regions WHERE code='41'), '41150', '시흥시',     2, '경기도 > 시흥시'),
  ((SELECT id FROM regions WHERE code='41'), '41160', '군포시',     2, '경기도 > 군포시'),
  ((SELECT id FROM regions WHERE code='41'), '41170', '의왕시',     2, '경기도 > 의왕시'),
  ((SELECT id FROM regions WHERE code='41'), '41180', '하남시',     2, '경기도 > 하남시'),
  ((SELECT id FROM regions WHERE code='41'), '41190', '용인시',     2, '경기도 > 용인시'),
  ((SELECT id FROM regions WHERE code='41'), '41200', '파주시',     2, '경기도 > 파주시'),
  ((SELECT id FROM regions WHERE code='41'), '41210', '이천시',     2, '경기도 > 이천시'),
  ((SELECT id FROM regions WHERE code='41'), '41220', '안성시',     2, '경기도 > 안성시'),
  ((SELECT id FROM regions WHERE code='41'), '41230', '김포시',     2, '경기도 > 김포시'),
  ((SELECT id FROM regions WHERE code='41'), '41240', '화성시',     2, '경기도 > 화성시'),
  ((SELECT id FROM regions WHERE code='41'), '41250', '광주시',     2, '경기도 > 광주시'),
  ((SELECT id FROM regions WHERE code='41'), '41260', '양주시',     2, '경기도 > 양주시'),
  ((SELECT id FROM regions WHERE code='41'), '41270', '포천시',     2, '경기도 > 포천시'),
  ((SELECT id FROM regions WHERE code='41'), '41280', '여주시',     2, '경기도 > 여주시'),
  ((SELECT id FROM regions WHERE code='41'), '41310', '연천군',     2, '경기도 > 연천군'),
  ((SELECT id FROM regions WHERE code='41'), '41320', '가평군',     2, '경기도 > 가평군'),
  ((SELECT id FROM regions WHERE code='41'), '41330', '양평군',     2, '경기도 > 양평군');

-- ■ 강원특별자치도 (7시 11군 = 18)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='42'), '42010', '춘천시',     2, '강원특별자치도 > 춘천시'),
  ((SELECT id FROM regions WHERE code='42'), '42020', '원주시',     2, '강원특별자치도 > 원주시'),
  ((SELECT id FROM regions WHERE code='42'), '42030', '강릉시',     2, '강원특별자치도 > 강릉시'),
  ((SELECT id FROM regions WHERE code='42'), '42040', '동해시',     2, '강원특별자치도 > 동해시'),
  ((SELECT id FROM regions WHERE code='42'), '42050', '태백시',     2, '강원특별자치도 > 태백시'),
  ((SELECT id FROM regions WHERE code='42'), '42060', '속초시',     2, '강원특별자치도 > 속초시'),
  ((SELECT id FROM regions WHERE code='42'), '42070', '삼척시',     2, '강원특별자치도 > 삼척시'),
  ((SELECT id FROM regions WHERE code='42'), '42310', '홍천군',     2, '강원특별자치도 > 홍천군'),
  ((SELECT id FROM regions WHERE code='42'), '42320', '횡성군',     2, '강원특별자치도 > 횡성군'),
  ((SELECT id FROM regions WHERE code='42'), '42330', '영월군',     2, '강원특별자치도 > 영월군'),
  ((SELECT id FROM regions WHERE code='42'), '42340', '평창군',     2, '강원특별자치도 > 평창군'),
  ((SELECT id FROM regions WHERE code='42'), '42350', '정선군',     2, '강원특별자치도 > 정선군'),
  ((SELECT id FROM regions WHERE code='42'), '42360', '철원군',     2, '강원특별자치도 > 철원군'),
  ((SELECT id FROM regions WHERE code='42'), '42370', '화천군',     2, '강원특별자치도 > 화천군'),
  ((SELECT id FROM regions WHERE code='42'), '42380', '양구군',     2, '강원특별자치도 > 양구군'),
  ((SELECT id FROM regions WHERE code='42'), '42390', '인제군',     2, '강원특별자치도 > 인제군'),
  ((SELECT id FROM regions WHERE code='42'), '42400', '고성군',     2, '강원특별자치도 > 고성군'),
  ((SELECT id FROM regions WHERE code='42'), '42410', '양양군',     2, '강원특별자치도 > 양양군');

-- ■ 충청북도 (3시 8군 = 11)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='43'), '43010', '청주시',     2, '충청북도 > 청주시'),
  ((SELECT id FROM regions WHERE code='43'), '43020', '충주시',     2, '충청북도 > 충주시'),
  ((SELECT id FROM regions WHERE code='43'), '43030', '제천시',     2, '충청북도 > 제천시'),
  ((SELECT id FROM regions WHERE code='43'), '43310', '보은군',     2, '충청북도 > 보은군'),
  ((SELECT id FROM regions WHERE code='43'), '43320', '옥천군',     2, '충청북도 > 옥천군'),
  ((SELECT id FROM regions WHERE code='43'), '43330', '영동군',     2, '충청북도 > 영동군'),
  ((SELECT id FROM regions WHERE code='43'), '43340', '증평군',     2, '충청북도 > 증평군'),
  ((SELECT id FROM regions WHERE code='43'), '43350', '진천군',     2, '충청북도 > 진천군'),
  ((SELECT id FROM regions WHERE code='43'), '43360', '괴산군',     2, '충청북도 > 괴산군'),
  ((SELECT id FROM regions WHERE code='43'), '43370', '음성군',     2, '충청북도 > 음성군'),
  ((SELECT id FROM regions WHERE code='43'), '43380', '단양군',     2, '충청북도 > 단양군');

-- ■ 충청남도 (8시 7군 = 15)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='44'), '44010', '천안시',     2, '충청남도 > 천안시'),
  ((SELECT id FROM regions WHERE code='44'), '44020', '공주시',     2, '충청남도 > 공주시'),
  ((SELECT id FROM regions WHERE code='44'), '44030', '보령시',     2, '충청남도 > 보령시'),
  ((SELECT id FROM regions WHERE code='44'), '44040', '아산시',     2, '충청남도 > 아산시'),
  ((SELECT id FROM regions WHERE code='44'), '44050', '서산시',     2, '충청남도 > 서산시'),
  ((SELECT id FROM regions WHERE code='44'), '44060', '논산시',     2, '충청남도 > 논산시'),
  ((SELECT id FROM regions WHERE code='44'), '44070', '계룡시',     2, '충청남도 > 계룡시'),
  ((SELECT id FROM regions WHERE code='44'), '44080', '당진시',     2, '충청남도 > 당진시'),
  ((SELECT id FROM regions WHERE code='44'), '44310', '금산군',     2, '충청남도 > 금산군'),
  ((SELECT id FROM regions WHERE code='44'), '44320', '부여군',     2, '충청남도 > 부여군'),
  ((SELECT id FROM regions WHERE code='44'), '44330', '서천군',     2, '충청남도 > 서천군'),
  ((SELECT id FROM regions WHERE code='44'), '44340', '청양군',     2, '충청남도 > 청양군'),
  ((SELECT id FROM regions WHERE code='44'), '44350', '홍성군',     2, '충청남도 > 홍성군'),
  ((SELECT id FROM regions WHERE code='44'), '44360', '예산군',     2, '충청남도 > 예산군'),
  ((SELECT id FROM regions WHERE code='44'), '44370', '태안군',     2, '충청남도 > 태안군');

-- ■ 전북특별자치도 (6시 8군 = 14)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='45'), '45010', '전주시',     2, '전북특별자치도 > 전주시'),
  ((SELECT id FROM regions WHERE code='45'), '45020', '군산시',     2, '전북특별자치도 > 군산시'),
  ((SELECT id FROM regions WHERE code='45'), '45030', '익산시',     2, '전북특별자치도 > 익산시'),
  ((SELECT id FROM regions WHERE code='45'), '45040', '정읍시',     2, '전북특별자치도 > 정읍시'),
  ((SELECT id FROM regions WHERE code='45'), '45050', '남원시',     2, '전북특별자치도 > 남원시'),
  ((SELECT id FROM regions WHERE code='45'), '45060', '김제시',     2, '전북특별자치도 > 김제시'),
  ((SELECT id FROM regions WHERE code='45'), '45310', '완주군',     2, '전북특별자치도 > 완주군'),
  ((SELECT id FROM regions WHERE code='45'), '45320', '진안군',     2, '전북특별자치도 > 진안군'),
  ((SELECT id FROM regions WHERE code='45'), '45330', '무주군',     2, '전북특별자치도 > 무주군'),
  ((SELECT id FROM regions WHERE code='45'), '45340', '장수군',     2, '전북특별자치도 > 장수군'),
  ((SELECT id FROM regions WHERE code='45'), '45350', '임실군',     2, '전북특별자치도 > 임실군'),
  ((SELECT id FROM regions WHERE code='45'), '45360', '순창군',     2, '전북특별자치도 > 순창군'),
  ((SELECT id FROM regions WHERE code='45'), '45370', '고창군',     2, '전북특별자치도 > 고창군'),
  ((SELECT id FROM regions WHERE code='45'), '45380', '부안군',     2, '전북특별자치도 > 부안군');

-- ■ 전라남도 (5시 17군 = 22)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='46'), '46010', '목포시',     2, '전라남도 > 목포시'),
  ((SELECT id FROM regions WHERE code='46'), '46020', '여수시',     2, '전라남도 > 여수시'),
  ((SELECT id FROM regions WHERE code='46'), '46030', '순천시',     2, '전라남도 > 순천시'),
  ((SELECT id FROM regions WHERE code='46'), '46040', '나주시',     2, '전라남도 > 나주시'),
  ((SELECT id FROM regions WHERE code='46'), '46050', '광양시',     2, '전라남도 > 광양시'),
  ((SELECT id FROM regions WHERE code='46'), '46310', '담양군',     2, '전라남도 > 담양군'),
  ((SELECT id FROM regions WHERE code='46'), '46320', '곡성군',     2, '전라남도 > 곡성군'),
  ((SELECT id FROM regions WHERE code='46'), '46330', '구례군',     2, '전라남도 > 구례군'),
  ((SELECT id FROM regions WHERE code='46'), '46340', '고흥군',     2, '전라남도 > 고흥군'),
  ((SELECT id FROM regions WHERE code='46'), '46350', '보성군',     2, '전라남도 > 보성군'),
  ((SELECT id FROM regions WHERE code='46'), '46360', '화순군',     2, '전라남도 > 화순군'),
  ((SELECT id FROM regions WHERE code='46'), '46370', '장흥군',     2, '전라남도 > 장흥군'),
  ((SELECT id FROM regions WHERE code='46'), '46380', '강진군',     2, '전라남도 > 강진군'),
  ((SELECT id FROM regions WHERE code='46'), '46390', '해남군',     2, '전라남도 > 해남군'),
  ((SELECT id FROM regions WHERE code='46'), '46400', '영암군',     2, '전라남도 > 영암군'),
  ((SELECT id FROM regions WHERE code='46'), '46410', '무안군',     2, '전라남도 > 무안군'),
  ((SELECT id FROM regions WHERE code='46'), '46420', '함평군',     2, '전라남도 > 함평군'),
  ((SELECT id FROM regions WHERE code='46'), '46430', '영광군',     2, '전라남도 > 영광군'),
  ((SELECT id FROM regions WHERE code='46'), '46440', '장성군',     2, '전라남도 > 장성군'),
  ((SELECT id FROM regions WHERE code='46'), '46450', '완도군',     2, '전라남도 > 완도군'),
  ((SELECT id FROM regions WHERE code='46'), '46460', '진도군',     2, '전라남도 > 진도군'),
  ((SELECT id FROM regions WHERE code='46'), '46470', '신안군',     2, '전라남도 > 신안군');

-- ■ 경상북도 (10시 12군 = 22) — 군위군은 대구로 편입
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='47'), '47010', '포항시',     2, '경상북도 > 포항시'),
  ((SELECT id FROM regions WHERE code='47'), '47020', '경주시',     2, '경상북도 > 경주시'),
  ((SELECT id FROM regions WHERE code='47'), '47030', '김천시',     2, '경상북도 > 김천시'),
  ((SELECT id FROM regions WHERE code='47'), '47040', '안동시',     2, '경상북도 > 안동시'),
  ((SELECT id FROM regions WHERE code='47'), '47050', '구미시',     2, '경상북도 > 구미시'),
  ((SELECT id FROM regions WHERE code='47'), '47060', '영주시',     2, '경상북도 > 영주시'),
  ((SELECT id FROM regions WHERE code='47'), '47070', '영천시',     2, '경상북도 > 영천시'),
  ((SELECT id FROM regions WHERE code='47'), '47080', '상주시',     2, '경상북도 > 상주시'),
  ((SELECT id FROM regions WHERE code='47'), '47090', '문경시',     2, '경상북도 > 문경시'),
  ((SELECT id FROM regions WHERE code='47'), '47100', '경산시',     2, '경상북도 > 경산시'),
  ((SELECT id FROM regions WHERE code='47'), '47310', '의성군',     2, '경상북도 > 의성군'),
  ((SELECT id FROM regions WHERE code='47'), '47320', '청송군',     2, '경상북도 > 청송군'),
  ((SELECT id FROM regions WHERE code='47'), '47330', '영양군',     2, '경상북도 > 영양군'),
  ((SELECT id FROM regions WHERE code='47'), '47340', '영덕군',     2, '경상북도 > 영덕군'),
  ((SELECT id FROM regions WHERE code='47'), '47350', '청도군',     2, '경상북도 > 청도군'),
  ((SELECT id FROM regions WHERE code='47'), '47360', '고령군',     2, '경상북도 > 고령군'),
  ((SELECT id FROM regions WHERE code='47'), '47370', '성주군',     2, '경상북도 > 성주군'),
  ((SELECT id FROM regions WHERE code='47'), '47380', '칠곡군',     2, '경상북도 > 칠곡군'),
  ((SELECT id FROM regions WHERE code='47'), '47390', '예천군',     2, '경상북도 > 예천군'),
  ((SELECT id FROM regions WHERE code='47'), '47400', '봉화군',     2, '경상북도 > 봉화군'),
  ((SELECT id FROM regions WHERE code='47'), '47410', '울진군',     2, '경상북도 > 울진군'),
  ((SELECT id FROM regions WHERE code='47'), '47420', '울릉군',     2, '경상북도 > 울릉군');

-- ■ 경상남도 (8시 10군 = 18)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='48'), '48010', '창원시',     2, '경상남도 > 창원시'),
  ((SELECT id FROM regions WHERE code='48'), '48020', '진주시',     2, '경상남도 > 진주시'),
  ((SELECT id FROM regions WHERE code='48'), '48030', '통영시',     2, '경상남도 > 통영시'),
  ((SELECT id FROM regions WHERE code='48'), '48040', '사천시',     2, '경상남도 > 사천시'),
  ((SELECT id FROM regions WHERE code='48'), '48050', '김해시',     2, '경상남도 > 김해시'),
  ((SELECT id FROM regions WHERE code='48'), '48060', '밀양시',     2, '경상남도 > 밀양시'),
  ((SELECT id FROM regions WHERE code='48'), '48070', '거제시',     2, '경상남도 > 거제시'),
  ((SELECT id FROM regions WHERE code='48'), '48080', '양산시',     2, '경상남도 > 양산시'),
  ((SELECT id FROM regions WHERE code='48'), '48310', '의령군',     2, '경상남도 > 의령군'),
  ((SELECT id FROM regions WHERE code='48'), '48320', '함안군',     2, '경상남도 > 함안군'),
  ((SELECT id FROM regions WHERE code='48'), '48330', '창녕군',     2, '경상남도 > 창녕군'),
  ((SELECT id FROM regions WHERE code='48'), '48340', '고성군',     2, '경상남도 > 고성군'),
  ((SELECT id FROM regions WHERE code='48'), '48350', '남해군',     2, '경상남도 > 남해군'),
  ((SELECT id FROM regions WHERE code='48'), '48360', '하동군',     2, '경상남도 > 하동군'),
  ((SELECT id FROM regions WHERE code='48'), '48370', '산청군',     2, '경상남도 > 산청군'),
  ((SELECT id FROM regions WHERE code='48'), '48380', '함양군',     2, '경상남도 > 함양군'),
  ((SELECT id FROM regions WHERE code='48'), '48390', '거창군',     2, '경상남도 > 거창군'),
  ((SELECT id FROM regions WHERE code='48'), '48400', '합천군',     2, '경상남도 > 합천군');

-- ■ 제주특별자치도 (2시)
INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
  ((SELECT id FROM regions WHERE code='50'), '50010', '제주시',     2, '제주특별자치도 > 제주시'),
  ((SELECT id FROM regions WHERE code='50'), '50020', '서귀포시',   2, '제주특별자치도 > 서귀포시');

COMMIT;

-- ── 검증 쿼리 ─────────────────────────────────
-- SELECT level, COUNT(*) FROM regions GROUP BY level ORDER BY level;
-- 결과: level 1 = 17, level 2 = 228, 합계 = 245
