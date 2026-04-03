import Layout from '@/components/Layout';
import Link from 'next/link';

const plans = [
  {
    name: 'Basic',
    price: '9,900',
    features: [
      '알림 조건 5개',
      '이메일 알림',
      '매일 1회 알림',
      '최근 7일 매물 조회',
      '지역 + 지목 필터',
    ],
    highlight: false,
  },
  {
    name: 'Premium',
    price: '19,900',
    features: [
      '알림 조건 무제한',
      '이메일 + 카카오톡 + SMS',
      '즉시 알림 (1시간 내)',
      '최근 90일 매물 조회',
      '지역 + 지목 + 면적 + 금액 전체 필터',
    ],
    highlight: true,
  },
];

export default function Pricing() {
  return (
    <Layout>
      <div style={{ padding: '80px 0', textAlign: 'center' }}>
        <div className="container">
          <h1 style={{ fontSize: 36, marginBottom: 12 }}>요금제</h1>
          <p style={{ color: '#666', marginBottom: 60, fontSize: 18 }}>
            필요에 맞는 플랜을 선택하세요
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 32, maxWidth: 800, margin: '0 auto' }}>
            {plans.map(plan => (
              <div
                key={plan.name}
                className="card"
                style={{
                  padding: 40,
                  border: plan.highlight ? '2px solid #2E7D32' : '1px solid #e0e0e0',
                  position: 'relative',
                }}
              >
                {plan.highlight && (
                  <div style={{
                    position: 'absolute',
                    top: -14,
                    left: '50%',
                    transform: 'translateX(-50%)',
                    background: '#2E7D32',
                    color: 'white',
                    padding: '4px 16px',
                    borderRadius: 20,
                    fontSize: 13,
                    fontWeight: 600,
                  }}>
                    추천
                  </div>
                )}

                <h2 style={{ fontSize: 24, marginBottom: 8 }}>{plan.name}</h2>
                <div style={{ marginBottom: 24 }}>
                  <span style={{ fontSize: 36, fontWeight: 800 }}>{plan.price}</span>
                  <span style={{ color: '#666' }}>원/월</span>
                </div>

                <ul style={{ listStyle: 'none', padding: 0, marginBottom: 32, textAlign: 'left' }}>
                  {plan.features.map((f, i) => (
                    <li key={i} style={{ padding: '8px 0', borderBottom: '1px solid #f5f5f5', fontSize: 15 }}>
                      ✓ {f}
                    </li>
                  ))}
                </ul>

                <Link href="/signup">
                  <button
                    className={plan.highlight ? 'btn-primary' : 'btn-outline'}
                    style={{ width: '100%', padding: '12px 0' }}
                  >
                    시작하기
                  </button>
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>
    </Layout>
  );
}
