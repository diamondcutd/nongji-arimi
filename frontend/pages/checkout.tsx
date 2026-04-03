import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import { getMe, createCheckout } from '@/lib/api';

export default function Checkout() {
  const router = useRouter();
  const { plan } = router.query;
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    getMe().then(setUser).catch(() => router.push('/login'));
  }, []);

  const handleCheckout = async () => {
    if (!plan || typeof plan !== 'string') return;
    setLoading(true);
    setError('');

    try {
      const data = await createCheckout(plan);

      // 토스페이먼츠 SDK 결제 위젯 호출
      // @ts-ignore
      const tossPayments = await loadTossPayments(data.clientKey);
      await tossPayments.requestPayment('카드', {
        amount: data.amount,
        orderId: data.orderId,
        orderName: data.orderName,
        customerEmail: data.customerEmail,
        successUrl: `${window.location.origin}/checkout/success`,
        failUrl: `${window.location.origin}/checkout/fail`,
      });
    } catch (err: any) {
      setError(err.message || '결제 요청 실패');
    } finally {
      setLoading(false);
    }
  };

  const planInfo = plan === 'premium'
    ? { name: 'Premium', price: '19,900', features: ['무제한 알림 조건', '이메일+카카오+SMS', '즉시 알림'] }
    : { name: 'Basic', price: '9,900', features: ['5개 알림 조건', '이메일 알림', '매일 1회 알림'] };

  return (
    <Layout>
      {/* 토스페이먼츠 SDK */}
      <script src="https://js.tosspayments.com/v1/payment" />

      <div style={{ maxWidth: 500, margin: '80px auto', padding: '0 20px' }}>
        <div className="card">
          <h1 style={{ fontSize: 24, marginBottom: 24 }}>구독 결제</h1>

          <div style={{ background: '#F5F5F5', borderRadius: 8, padding: 20, marginBottom: 24 }}>
            <h2 style={{ fontSize: 20, marginBottom: 8 }}>{planInfo.name} 플랜</h2>
            <p style={{ fontSize: 28, fontWeight: 800, marginBottom: 12 }}>
              {planInfo.price}<span style={{ fontSize: 16, fontWeight: 400, color: '#666' }}>원/월</span>
            </p>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {planInfo.features.map((f, i) => (
                <li key={i} style={{ padding: '4px 0', fontSize: 14, color: '#666' }}>✓ {f}</li>
              ))}
            </ul>
          </div>

          {error && <p className="error-msg" style={{ marginBottom: 16 }}>{error}</p>}

          <button
            className="btn-primary"
            onClick={handleCheckout}
            disabled={loading}
            style={{ width: '100%', padding: '14px 0', fontSize: 16 }}
          >
            {loading ? '처리 중...' : `월 ${planInfo.price}원 결제하기`}
          </button>

          <p style={{ textAlign: 'center', marginTop: 16, color: '#999', fontSize: 13 }}>
            결제는 토스페이먼츠를 통해 안전하게 처리됩니다.
          </p>
        </div>
      </div>
    </Layout>
  );
}

// 토스페이먼츠 SDK 로드 헬퍼
function loadTossPayments(clientKey: string): Promise<any> {
  return new Promise((resolve, reject) => {
    // @ts-ignore
    if (window.TossPayments) {
      // @ts-ignore
      resolve(window.TossPayments(clientKey));
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://js.tosspayments.com/v1/payment';
    script.onload = () => {
      // @ts-ignore
      resolve(window.TossPayments(clientKey));
    };
    script.onerror = () => reject(new Error('결제 모듈 로드 실패'));
    document.head.appendChild(script);
  });
}
