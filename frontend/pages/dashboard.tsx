import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import ConditionForm from '@/components/ConditionForm';
import ListingCard from '@/components/ListingCard';
import { getMe, getConditions, createCondition, deleteCondition, getListings } from '@/lib/api';

export default function Dashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [conditions, setConditions] = useState<any[]>([]);
  const [listings, setListings] = useState<any[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [tab, setTab] = useState<'conditions' | 'listings'>('conditions');

  useEffect(() => {
    getMe()
      .then(u => {
        setUser(u);
        loadConditions();
        loadListings();
      })
      .catch(() => router.push('/login'));
  }, []);

  const loadConditions = async () => {
    try {
      const data = await getConditions();
      setConditions(data);
    } catch {}
  };

  const loadListings = async () => {
    try {
      const data = await getListings();
      setListings(data);
    } catch {}
  };

  const handleCreate = async (data: any) => {
    await createCondition(data);
    setShowForm(false);
    loadConditions();
  };

  const handleDelete = async (id: string) => {
    if (!confirm('이 알림 조건을 삭제하시겠습니까?')) return;
    await deleteCondition(id);
    loadConditions();
  };

  if (!user) return null;

  return (
    <Layout>
      <div className="container" style={{ padding: '40px 20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 32 }}>
          <div>
            <h1 style={{ fontSize: 28 }}>대시보드</h1>
            <p style={{ color: '#666' }}>
              {user.email} |{' '}
              <span className={`badge ${user.plan === 'premium' ? 'badge-blue' : 'badge-green'}`}>
                {user.plan.toUpperCase()}
              </span>
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 0, marginBottom: 24, borderBottom: '2px solid #eee' }}>
          {(['conditions', 'listings'] as const).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                padding: '12px 24px',
                background: 'none',
                borderRadius: 0,
                borderBottom: tab === t ? '2px solid #2E7D32' : '2px solid transparent',
                color: tab === t ? '#2E7D32' : '#999',
                fontWeight: tab === t ? 700 : 400,
                marginBottom: -2,
              }}
            >
              {t === 'conditions' ? `알림 조건 (${conditions.length})` : `최근 매물 (${listings.length})`}
            </button>
          ))}
        </div>

        {/* Conditions Tab */}
        {tab === 'conditions' && (
          <>
            <button className="btn-primary" onClick={() => setShowForm(!showForm)} style={{ marginBottom: 24 }}>
              {showForm ? '취소' : '+ 새 알림 조건'}
            </button>

            {showForm && <ConditionForm onSubmit={handleCreate} onCancel={() => setShowForm(false)} />}

            {conditions.length === 0 ? (
              <div className="card" style={{ textAlign: 'center', padding: 48, color: '#999' }}>
                <p style={{ fontSize: 18, marginBottom: 8 }}>등록된 알림 조건이 없습니다</p>
                <p>위 버튼을 눌러 첫 번째 알림 조건을 추가해보세요.</p>
              </div>
            ) : (
              conditions.map(c => (
                <div key={c.id} className="card" style={{ marginBottom: 12 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h3 style={{ fontSize: 16, marginBottom: 4 }}>{c.name || '이름 없는 조건'}</h3>
                      <p style={{ color: '#666', fontSize: 14 }}>
                        {[
                          c.sido_cd && `지역: ${c.sido_cd}`,
                          c.land_category && `지목: ${c.land_category}`,
                          c.trade_type && `거래: ${c.trade_type}`,
                          c.area_min && `면적 ${c.area_min}㎡~`,
                          c.area_max && `~${c.area_max}㎡`,
                          c.price_min && `금액 ${(c.price_min / 10000).toLocaleString()}만~`,
                          c.price_max && `~${(c.price_max / 10000).toLocaleString()}만`,
                        ].filter(Boolean).join(' | ') || '전체 매물'}
                      </p>
                    </div>
                    <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                      <span className={`badge ${c.is_active ? 'badge-green' : ''}`} style={!c.is_active ? { background: '#eee', color: '#999' } : {}}>
                        {c.is_active ? '활성' : '비활성'}
                      </span>
                      <button className="btn-danger" onClick={() => handleDelete(c.id)} style={{ padding: '6px 12px', fontSize: 13 }}>
                        삭제
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </>
        )}

        {/* Listings Tab */}
        {tab === 'listings' && (
          <>
            {listings.length === 0 ? (
              <div className="card" style={{ textAlign: 'center', padding: 48, color: '#999' }}>
                <p>아직 수집된 매물이 없습니다.</p>
              </div>
            ) : (
              listings.map(l => <ListingCard key={l.id} listing={l} />)
            )}
          </>
        )}
      </div>
    </Layout>
  );
}
