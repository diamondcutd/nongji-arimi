import { useState, useEffect } from 'react';
import { getSido, getSigun } from '@/lib/api';

interface RegionSelectorProps {
  sidoCd: string;
  sigunCd: string;
  onSidoChange: (code: string) => void;
  onSigunChange: (code: string) => void;
}

export default function RegionSelector({ sidoCd, sigunCd, onSidoChange, onSigunChange }: RegionSelectorProps) {
  const [sidoList, setSidoList] = useState<{ code: string; name: string }[]>([]);
  const [sigunList, setSigunList] = useState<{ code: string; name: string }[]>([]);

  useEffect(() => {
    getSido().then(setSidoList).catch(() => {});
  }, []);

  useEffect(() => {
    if (sidoCd) {
      getSigun(sidoCd).then(setSigunList).catch(() => setSigunList([]));
    } else {
      setSigunList([]);
    }
  }, [sidoCd]);

  return (
    <div className="form-row">
      <div className="form-group">
        <label>시도</label>
        <select value={sidoCd} onChange={e => { onSidoChange(e.target.value); onSigunChange(''); }}>
          <option value="">전체</option>
          {sidoList.map(s => (
            <option key={s.code} value={s.code}>{s.name}</option>
          ))}
        </select>
      </div>
      <div className="form-group">
        <label>시군구</label>
        <select value={sigunCd} onChange={e => onSigunChange(e.target.value)} disabled={!sidoCd}>
          <option value="">전체</option>
          {sigunList.map(s => (
            <option key={s.code} value={s.code}>{s.name}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
