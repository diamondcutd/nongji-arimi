import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';

export default function CheckoutSuccess() {
  const router = useRouter();
  const { paymentKey, orderId, amount } = router.query;
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');

  useEffect(() => {
    if (!paymentKey || !orderId || !amount) return;

    // 백엔드 웹훅 호출하여 결제 확인
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/subscriptions/webhook`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ paymentKey, orderId, amount: Number(amount) }),
    })
      .then(res => {
        if (res.ok) setStatus('success');
        else setStatus('error');
      })
      .catch(() => setStatus('error'));
  }, [paymentKey, orderId, amount]);

  return (
    <Layout>
      <div style={{ maxWidth: 500, margin: '120px auto', textAlign: 'center', padding: '0 20px' }}>
        {status === 'loading' && (
          <div className="card" style={{ padding: 48 }}>
            <p style={{ fontSize: 18 }}>결제 확인 중...</p>
          </div>
        )}
        {status === 'success' && (
          <div className="card" style={{ padding: 48 }}>
            <div style={{ fontSize: 64, marginBottom: 16 }}>✅</div>
            <h1 style={{ fontSize: 24, marginBottom: 12 }}>결제 완료!</h1>
            <p style={{ color: '#666', marginBottom: 32 }}>구독이 활성화되었습니다.</p>
            <button className="btn-primary" onClick={() => router.push('/dashboard')}>
              대시보드로 이동
            </button>
          </div>
        )}
        {status === 'error' && (
          <div className="card" style={{ padding: 48 }}>
            <div style={{ fontSize: 64, marginBottom: 16 }}>❌</div>
            <h1 style={{ fontSize: 24, marginBottom: 12 }}>결제 실패</h1>
            <p style={{ color: '#666', marginBottom: 32 }}>문제가 발생했습니다. 다시 시도해주세요.</p>
            <button className="btn-primary" onClick={() => router.push('/pricing')}>
              요금제 페이지로
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}
