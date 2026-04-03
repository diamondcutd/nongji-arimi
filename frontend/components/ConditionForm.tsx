import { useState } from 'react';
import RegionSelector from './RegionSelector';

interface ConditionFormProps {
  initial?: any;
  onSubmit: (data: any) => Promise<void>;
  onCancel?: () => void;
}

export default function ConditionForm({ initial, onSubmit, onCancel }: ConditionFormProps) {
  const [name, setName] = useState(initial?.name || '');
  const [sidoCd, setSidoCd] = useState(initial?.sido_cd || '');
  const [sigunCd, setSigunCd] = useState(initial?.sigun_cd || '');
  const [landCategory, setLandCategory] = useState(initial?.land_category || '');
  const [tradeType, setTradeType] = useState(initial?.trade_type || '');
  const [areaMin, setAreaMin] = useState(initial?.area_min || '');
  const [areaMax, setAreaMax] = useState(initial?.area_max || '');
  const [priceMin, setPriceMin] = useState(initial?.price_min || '');
  const [priceMax, setPriceMax] = useState(initial?.price_max || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await onSubmit({
        name: name || null,
        sido_cd: sidoCd || null,
        sigun_cd: sigunCd || null,
        land_category: landCategory || null,
        trade_type: tradeType || null,
        area_min: areaMin ? Number(areaMin) : null,
        area_max: areaMax ? Number(areaMax) : null,
        price_min: priceMin ? Number(priceMin) : null,
        price_max: priceMax ? Number(priceMax) : null,
      });
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card" style={{ marginBottom: 24 }}>
      <div className="form-group">
        <label>조건 이름</label>
        <input value={name} onChange={e => setName(e.target.value)} placeholder="예: 함안군 논 찾기" />
      </div>

      <RegionSelector sidoCd={sidoCd} sigunCd={sigunCd} onSidoChange={setSidoCd} onSigunChange={setSigunCd} />

      <div className="form-row">
        <div className="form-group">
          <label>지목</label>
          <select value={landCategory} onChange={e => setLandCategory(e.target.value)}>
            <option value="">전체</option>
            <option value="전">전 (밭)</option>
            <option value="답">답 (논)</option>
            <option value="과수원">과수원</option>
          </select>
        </div>
        <div className="form-group">
          <label>거래유형</label>
          <select value={tradeType} onChange={e => setTradeType(e.target.value)}>
            <option value="">전체</option>
            <option value="매도">매도</option>
            <option value="임대">임대</option>
          </select>
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>최소 면적 (㎡)</label>
          <input type="number" value={areaMin} onChange={e => setAreaMin(e.target.value)} placeholder="0" />
        </div>
        <div className="form-group">
          <label>최대 면적 (㎡)</label>
          <input type="number" value={areaMax} onChange={e => setAreaMax(e.target.value)} placeholder="제한 없음" />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>최소 금액 (원)</label>
          <input type="number" value={priceMin} onChange={e => setPriceMin(e.target.value)} placeholder="0" />
        </div>
        <div className="form-group">
          <label>최대 금액 (원)</label>
          <input type="number" value={priceMax} onChange={e => setPriceMax(e.target.value)} placeholder="제한 없음" />
        </div>
      </div>

      {error && <p className="error-msg">{error}</p>}

      <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? '저장 중...' : initial ? '수정' : '조건 추가'}
        </button>
        {onCancel && (
          <button type="button" className="btn-outline" onClick={onCancel}>취소</button>
        )}
      </div>
    </form>
  );
}
