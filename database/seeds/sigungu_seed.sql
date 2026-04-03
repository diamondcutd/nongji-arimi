-- 전국 시군구 시드 데이터 (level=2)
-- 시도(level=1)가 이미 존재해야 함
-- 실행: psql -U postgres -d nongji -f sigungu_seed.sql

DO $$
DECLARE
  v_pid UUID;
BEGIN

  -- ── 서울특별시 ──
  SELECT id INTO v_pid FROM regions WHERE code = '11' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '11010', '종로구',   2, '서울특별시 > 종로구'),
      (v_pid, '11020', '중구',     2, '서울특별시 > 중구'),
      (v_pid, '11030', '용산구',   2, '서울특별시 > 용산구'),
      (v_pid, '11040', '성동구',   2, '서울특별시 > 성동구'),
      (v_pid, '11050', '광진구',   2, '서울특별시 > 광진구'),
      (v_pid, '11060', '동대문구', 2, '서울특별시 > 동대문구'),
      (v_pid, '11070', '중랑구',   2, '서울특별시 > 중랑구'),
      (v_pid, '11080', '성북구',   2, '서울특별시 > 성북구'),
      (v_pid, '11090', '강북구',   2, '서울특별시 > 강북구'),
      (v_pid, '11100', '도봉구',   2, '서울특별시 > 도봉구'),
      (v_pid, '11110', '노원구',   2, '서울특별시 > 노원구'),
      (v_pid, '11120', '은평구',   2, '서울특별시 > 은평구'),
      (v_pid, '11130', '서대문구', 2, '서울특별시 > 서대문구'),
      (v_pid, '11140', '마포구',   2, '서울특별시 > 마포구'),
      (v_pid, '11150', '양천구',   2, '서울특별시 > 양천구'),
      (v_pid, '11160', '강서구',   2, '서울특별시 > 강서구'),
      (v_pid, '11170', '구로구',   2, '서울특별시 > 구로구'),
      (v_pid, '11180', '금천구',   2, '서울특별시 > 금천구'),
      (v_pid, '11190', '영등포구', 2, '서울특별시 > 영등포구'),
      (v_pid, '11200', '동작구',   2, '서울특별시 > 동작구'),
      (v_pid, '11210', '관악구',   2, '서울특별시 > 관악구'),
      (v_pid, '11220', '서초구',   2, '서울특별시 > 서초구'),
      (v_pid, '11230', '강남구',   2, '서울특별시 > 강남구'),
      (v_pid, '11240', '송파구',   2, '서울특별시 > 송파구'),
      (v_pid, '11250', '강동구',   2, '서울특별시 > 강동구')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 부산광역시 ──
  SELECT id INTO v_pid FROM regions WHERE code = '21' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '21010', '중구',     2, '부산광역시 > 중구'),
      (v_pid, '21020', '서구',     2, '부산광역시 > 서구'),
      (v_pid, '21030', '동구',     2, '부산광역시 > 동구'),
      (v_pid, '21040', '영도구',   2, '부산광역시 > 영도구'),
      (v_pid, '21050', '부산진구', 2, '부산광역시 > 부산진구'),
      (v_pid, '21060', '동래구',   2, '부산광역시 > 동래구'),
      (v_pid, '21070', '남구',     2, '부산광역시 > 남구'),
      (v_pid, '21080', '북구',     2, '부산광역시 > 북구'),
      (v_pid, '21090', '해운대구', 2, '부산광역시 > 해운대구'),
      (v_pid, '21100', '사하구',   2, '부산광역시 > 사하구'),
      (v_pid, '21110', '금정구',   2, '부산광역시 > 금정구'),
      (v_pid, '21120', '강서구',   2, '부산광역시 > 강서구'),
      (v_pid, '21130', '연제구',   2, '부산광역시 > 연제구'),
      (v_pid, '21140', '수영구',   2, '부산광역시 > 수영구'),
      (v_pid, '21150', '사상구',   2, '부산광역시 > 사상구'),
      (v_pid, '21160', '기장군',   2, '부산광역시 > 기장군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 대구광역시 ──
  SELECT id INTO v_pid FROM regions WHERE code = '22' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '22010', '중구',   2, '대구광역시 > 중구'),
      (v_pid, '22020', '동구',   2, '대구광역시 > 동구'),
      (v_pid, '22030', '서구',   2, '대구광역시 > 서구'),
      (v_pid, '22040', '남구',   2, '대구광역시 > 남구'),
      (v_pid, '22050', '북구',   2, '대구광역시 > 북구'),
      (v_pid, '22060', '수성구', 2, '대구광역시 > 수성구'),
      (v_pid, '22070', '달서구', 2, '대구광역시 > 달서구'),
      (v_pid, '22080', '달성군', 2, '대구광역시 > 달성군'),
      (v_pid, '22090', '군위군', 2, '대구광역시 > 군위군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 인천광역시 ──
  SELECT id INTO v_pid FROM regions WHERE code = '23' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '23010', '중구',     2, '인천광역시 > 중구'),
      (v_pid, '23020', '동구',     2, '인천광역시 > 동구'),
      (v_pid, '23030', '미추홀구', 2, '인천광역시 > 미추홀구'),
      (v_pid, '23040', '연수구',   2, '인천광역시 > 연수구'),
      (v_pid, '23050', '남동구',   2, '인천광역시 > 남동구'),
      (v_pid, '23060', '부평구',   2, '인천광역시 > 부평구'),
      (v_pid, '23070', '계양구',   2, '인천광역시 > 계양구'),
      (v_pid, '23080', '서구',     2, '인천광역시 > 서구'),
      (v_pid, '23090', '강화군',   2, '인천광역시 > 강화군'),
      (v_pid, '23100', '옹진군',   2, '인천광역시 > 옹진군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 광주광역시 ──
  SELECT id INTO v_pid FROM regions WHERE code = '24' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '24010', '동구',   2, '광주광역시 > 동구'),
      (v_pid, '24020', '서구',   2, '광주광역시 > 서구'),
      (v_pid, '24030', '남구',   2, '광주광역시 > 남구'),
      (v_pid, '24040', '북구',   2, '광주광역시 > 북구'),
      (v_pid, '24050', '광산구', 2, '광주광역시 > 광산구')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 대전광역시 ──
  SELECT id INTO v_pid FROM regions WHERE code = '25' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '25010', '동구',   2, '대전광역시 > 동구'),
      (v_pid, '25020', '중구',   2, '대전광역시 > 중구'),
      (v_pid, '25030', '서구',   2, '대전광역시 > 서구'),
      (v_pid, '25040', '유성구', 2, '대전광역시 > 유성구'),
      (v_pid, '25050', '대덕구', 2, '대전광역시 > 대덕구')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 울산광역시 ──
  SELECT id INTO v_pid FROM regions WHERE code = '26' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '26010', '중구',   2, '울산광역시 > 중구'),
      (v_pid, '26020', '남구',   2, '울산광역시 > 남구'),
      (v_pid, '26030', '동구',   2, '울산광역시 > 동구'),
      (v_pid, '26040', '북구',   2, '울산광역시 > 북구'),
      (v_pid, '26050', '울주군', 2, '울산광역시 > 울주군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 세종특별자치시 ──
  SELECT id INTO v_pid FROM regions WHERE code = '29' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '29010', '세종시', 2, '세종특별자치시 > 세종시')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 경기도 ──
  SELECT id INTO v_pid FROM regions WHERE code = '31' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '31010', '수원시',   2, '경기도 > 수원시'),
      (v_pid, '31020', '성남시',   2, '경기도 > 성남시'),
      (v_pid, '31030', '의정부시', 2, '경기도 > 의정부시'),
      (v_pid, '31040', '안양시',   2, '경기도 > 안양시'),
      (v_pid, '31050', '부천시',   2, '경기도 > 부천시'),
      (v_pid, '31060', '광명시',   2, '경기도 > 광명시'),
      (v_pid, '31070', '평택시',   2, '경기도 > 평택시'),
      (v_pid, '31080', '동두천시', 2, '경기도 > 동두천시'),
      (v_pid, '31090', '안산시',   2, '경기도 > 안산시'),
      (v_pid, '31100', '고양시',   2, '경기도 > 고양시'),
      (v_pid, '31110', '과천시',   2, '경기도 > 과천시'),
      (v_pid, '31120', '구리시',   2, '경기도 > 구리시'),
      (v_pid, '31130', '남양주시', 2, '경기도 > 남양주시'),
      (v_pid, '31140', '오산시',   2, '경기도 > 오산시'),
      (v_pid, '31150', '시흥시',   2, '경기도 > 시흥시'),
      (v_pid, '31160', '군포시',   2, '경기도 > 군포시'),
      (v_pid, '31170', '의왕시',   2, '경기도 > 의왕시'),
      (v_pid, '31180', '하남시',   2, '경기도 > 하남시'),
      (v_pid, '31190', '용인시',   2, '경기도 > 용인시'),
      (v_pid, '31200', '파주시',   2, '경기도 > 파주시'),
      (v_pid, '31210', '이천시',   2, '경기도 > 이천시'),
      (v_pid, '31220', '안성시',   2, '경기도 > 안성시'),
      (v_pid, '31230', '김포시',   2, '경기도 > 김포시'),
      (v_pid, '31240', '화성시',   2, '경기도 > 화성시'),
      (v_pid, '31250', '광주시',   2, '경기도 > 광주시'),
      (v_pid, '31260', '양주시',   2, '경기도 > 양주시'),
      (v_pid, '31270', '포천시',   2, '경기도 > 포천시'),
      (v_pid, '31280', '여주시',   2, '경기도 > 여주시'),
      (v_pid, '31290', '연천군',   2, '경기도 > 연천군'),
      (v_pid, '31300', '가평군',   2, '경기도 > 가평군'),
      (v_pid, '31310', '양평군',   2, '경기도 > 양평군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 강원특별자치도 ──
  SELECT id INTO v_pid FROM regions WHERE code = '32' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '32010', '춘천시', 2, '강원특별자치도 > 춘천시'),
      (v_pid, '32020', '원주시', 2, '강원특별자치도 > 원주시'),
      (v_pid, '32030', '강릉시', 2, '강원특별자치도 > 강릉시'),
      (v_pid, '32040', '동해시', 2, '강원특별자치도 > 동해시'),
      (v_pid, '32050', '태백시', 2, '강원특별자치도 > 태백시'),
      (v_pid, '32060', '속초시', 2, '강원특별자치도 > 속초시'),
      (v_pid, '32070', '삼척시', 2, '강원특별자치도 > 삼척시'),
      (v_pid, '32080', '홍천군', 2, '강원특별자치도 > 홍천군'),
      (v_pid, '32090', '횡성군', 2, '강원특별자치도 > 횡성군'),
      (v_pid, '32100', '영월군', 2, '강원특별자치도 > 영월군'),
      (v_pid, '32110', '평창군', 2, '강원특별자치도 > 평창군'),
      (v_pid, '32120', '정선군', 2, '강원특별자치도 > 정선군'),
      (v_pid, '32130', '철원군', 2, '강원특별자치도 > 철원군'),
      (v_pid, '32140', '화천군', 2, '강원특별자치도 > 화천군'),
      (v_pid, '32150', '양구군', 2, '강원특별자치도 > 양구군'),
      (v_pid, '32160', '인제군', 2, '강원특별자치도 > 인제군'),
      (v_pid, '32170', '고성군', 2, '강원특별자치도 > 고성군'),
      (v_pid, '32180', '양양군', 2, '강원특별자치도 > 양양군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 충청북도 ──
  SELECT id INTO v_pid FROM regions WHERE code = '33' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '33010', '청주시', 2, '충청북도 > 청주시'),
      (v_pid, '33020', '충주시', 2, '충청북도 > 충주시'),
      (v_pid, '33030', '제천시', 2, '충청북도 > 제천시'),
      (v_pid, '33040', '보은군', 2, '충청북도 > 보은군'),
      (v_pid, '33050', '옥천군', 2, '충청북도 > 옥천군'),
      (v_pid, '33060', '영동군', 2, '충청북도 > 영동군'),
      (v_pid, '33070', '증평군', 2, '충청북도 > 증평군'),
      (v_pid, '33080', '진천군', 2, '충청북도 > 진천군'),
      (v_pid, '33090', '괴산군', 2, '충청북도 > 괴산군'),
      (v_pid, '33100', '음성군', 2, '충청북도 > 음성군'),
      (v_pid, '33110', '단양군', 2, '충청북도 > 단양군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 충청남도 ──
  SELECT id INTO v_pid FROM regions WHERE code = '34' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '34010', '천안시', 2, '충청남도 > 천안시'),
      (v_pid, '34020', '공주시', 2, '충청남도 > 공주시'),
      (v_pid, '34030', '보령시', 2, '충청남도 > 보령시'),
      (v_pid, '34040', '아산시', 2, '충청남도 > 아산시'),
      (v_pid, '34050', '서산시', 2, '충청남도 > 서산시'),
      (v_pid, '34060', '논산시', 2, '충청남도 > 논산시'),
      (v_pid, '34070', '계룡시', 2, '충청남도 > 계룡시'),
      (v_pid, '34080', '당진시', 2, '충청남도 > 당진시'),
      (v_pid, '34090', '금산군', 2, '충청남도 > 금산군'),
      (v_pid, '34100', '부여군', 2, '충청남도 > 부여군'),
      (v_pid, '34110', '서천군', 2, '충청남도 > 서천군'),
      (v_pid, '34120', '청양군', 2, '충청남도 > 청양군'),
      (v_pid, '34130', '홍성군', 2, '충청남도 > 홍성군'),
      (v_pid, '34140', '예산군', 2, '충청남도 > 예산군'),
      (v_pid, '34150', '태안군', 2, '충청남도 > 태안군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 전북특별자치도 ──
  SELECT id INTO v_pid FROM regions WHERE code = '35' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '35010', '전주시', 2, '전북특별자치도 > 전주시'),
      (v_pid, '35020', '군산시', 2, '전북특별자치도 > 군산시'),
      (v_pid, '35030', '익산시', 2, '전북특별자치도 > 익산시'),
      (v_pid, '35040', '정읍시', 2, '전북특별자치도 > 정읍시'),
      (v_pid, '35050', '남원시', 2, '전북특별자치도 > 남원시'),
      (v_pid, '35060', '김제시', 2, '전북특별자치도 > 김제시'),
      (v_pid, '35070', '완주군', 2, '전북특별자치도 > 완주군'),
      (v_pid, '35080', '진안군', 2, '전북특별자치도 > 진안군'),
      (v_pid, '35090', '무주군', 2, '전북특별자치도 > 무주군'),
      (v_pid, '35100', '장수군', 2, '전북특별자치도 > 장수군'),
      (v_pid, '35110', '임실군', 2, '전북특별자치도 > 임실군'),
      (v_pid, '35120', '순창군', 2, '전북특별자치도 > 순창군'),
      (v_pid, '35130', '고창군', 2, '전북특별자치도 > 고창군'),
      (v_pid, '35140', '부안군', 2, '전북특별자치도 > 부안군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 전라남도 ──
  SELECT id INTO v_pid FROM regions WHERE code = '36' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '36010', '목포시', 2, '전라남도 > 목포시'),
      (v_pid, '36020', '여수시', 2, '전라남도 > 여수시'),
      (v_pid, '36030', '순천시', 2, '전라남도 > 순천시'),
      (v_pid, '36040', '나주시', 2, '전라남도 > 나주시'),
      (v_pid, '36050', '광양시', 2, '전라남도 > 광양시'),
      (v_pid, '36060', '담양군', 2, '전라남도 > 담양군'),
      (v_pid, '36070', '곡성군', 2, '전라남도 > 곡성군'),
      (v_pid, '36080', '구례군', 2, '전라남도 > 구례군'),
      (v_pid, '36090', '고흥군', 2, '전라남도 > 고흥군'),
      (v_pid, '36100', '보성군', 2, '전라남도 > 보성군'),
      (v_pid, '36110', '화순군', 2, '전라남도 > 화순군'),
      (v_pid, '36120', '장흥군', 2, '전라남도 > 장흥군'),
      (v_pid, '36130', '강진군', 2, '전라남도 > 강진군'),
      (v_pid, '36140', '해남군', 2, '전라남도 > 해남군'),
      (v_pid, '36150', '영암군', 2, '전라남도 > 영암군'),
      (v_pid, '36160', '무안군', 2, '전라남도 > 무안군'),
      (v_pid, '36170', '함평군', 2, '전라남도 > 함평군'),
      (v_pid, '36180', '영광군', 2, '전라남도 > 영광군'),
      (v_pid, '36190', '장성군', 2, '전라남도 > 장성군'),
      (v_pid, '36200', '완도군', 2, '전라남도 > 완도군'),
      (v_pid, '36210', '진도군', 2, '전라남도 > 진도군'),
      (v_pid, '36220', '신안군', 2, '전라남도 > 신안군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 경상북도 ──
  SELECT id INTO v_pid FROM regions WHERE code = '37' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '37010', '포항시', 2, '경상북도 > 포항시'),
      (v_pid, '37020', '경주시', 2, '경상북도 > 경주시'),
      (v_pid, '37030', '김천시', 2, '경상북도 > 김천시'),
      (v_pid, '37040', '안동시', 2, '경상북도 > 안동시'),
      (v_pid, '37050', '구미시', 2, '경상북도 > 구미시'),
      (v_pid, '37060', '영주시', 2, '경상북도 > 영주시'),
      (v_pid, '37070', '영천시', 2, '경상북도 > 영천시'),
      (v_pid, '37080', '상주시', 2, '경상북도 > 상주시'),
      (v_pid, '37090', '문경시', 2, '경상북도 > 문경시'),
      (v_pid, '37100', '경산시', 2, '경상북도 > 경산시'),
      (v_pid, '37110', '의성군', 2, '경상북도 > 의성군'),
      (v_pid, '37120', '청송군', 2, '경상북도 > 청송군'),
      (v_pid, '37130', '영양군', 2, '경상북도 > 영양군'),
      (v_pid, '37140', '영덕군', 2, '경상북도 > 영덕군'),
      (v_pid, '37150', '청도군', 2, '경상북도 > 청도군'),
      (v_pid, '37160', '고령군', 2, '경상북도 > 고령군'),
      (v_pid, '37170', '성주군', 2, '경상북도 > 성주군'),
      (v_pid, '37180', '칠곡군', 2, '경상북도 > 칠곡군'),
      (v_pid, '37190', '예천군', 2, '경상북도 > 예천군'),
      (v_pid, '37200', '봉화군', 2, '경상북도 > 봉화군'),
      (v_pid, '37210', '울진군', 2, '경상북도 > 울진군'),
      (v_pid, '37220', '울릉군', 2, '경상북도 > 울릉군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 경상남도 ──
  SELECT id INTO v_pid FROM regions WHERE code = '38' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '38010', '창원시', 2, '경상남도 > 창원시'),
      (v_pid, '38020', '진주시', 2, '경상남도 > 진주시'),
      (v_pid, '38030', '통영시', 2, '경상남도 > 통영시'),
      (v_pid, '38040', '사천시', 2, '경상남도 > 사천시'),
      (v_pid, '38050', '김해시', 2, '경상남도 > 김해시'),
      (v_pid, '38060', '밀양시', 2, '경상남도 > 밀양시'),
      (v_pid, '38070', '거제시', 2, '경상남도 > 거제시'),
      (v_pid, '38080', '양산시', 2, '경상남도 > 양산시'),
      (v_pid, '38090', '의령군', 2, '경상남도 > 의령군'),
      (v_pid, '38100', '함안군', 2, '경상남도 > 함안군'),
      (v_pid, '38110', '창녕군', 2, '경상남도 > 창녕군'),
      (v_pid, '38120', '고성군', 2, '경상남도 > 고성군'),
      (v_pid, '38130', '남해군', 2, '경상남도 > 남해군'),
      (v_pid, '38140', '하동군', 2, '경상남도 > 하동군'),
      (v_pid, '38150', '산청군', 2, '경상남도 > 산청군'),
      (v_pid, '38160', '함양군', 2, '경상남도 > 함양군'),
      (v_pid, '38170', '거창군', 2, '경상남도 > 거창군'),
      (v_pid, '38180', '합천군', 2, '경상남도 > 합천군')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  -- ── 제주특별자치도 ──
  SELECT id INTO v_pid FROM regions WHERE code = '39' AND level = 1;
  IF v_pid IS NOT NULL THEN
    INSERT INTO regions (parent_id, code, name, level, full_path) VALUES
      (v_pid, '39010', '제주시',   2, '제주특별자치도 > 제주시'),
      (v_pid, '39020', '서귀포시', 2, '제주특별자치도 > 서귀포시')
    ON CONFLICT (code) DO NOTHING;
  END IF;

  RAISE NOTICE '시군구 INSERT 완료: % 건', (SELECT COUNT(*) FROM regions WHERE level = 2);

END $$;
