import Layout from '@/components/Layout';
import Link from 'next/link';

export default function Home() {
  return (
    <Layout>
      {/* Hero */}
      <section style={{
        background: 'linear-gradient(135deg, #1B5E20 0%, #2E7D32 50%, #4CAF50 100%)',
        color: 'white',
        padding: '100px 0',
        textAlign: 'center',
      }}>
        <div className="container">
          <h1 style={{ fontSize: 48, fontWeight: 800, marginBottom: 20 }}>
            농지 매물, 놓치지 마세요
          </h1>
          <p style={{ fontSize: 20, opacity: 0.9, marginBottom: 40, maxWidth: 600, margin: '0 auto 40px' }}>
            농지은행에 올라오는 매물을 자동으로 감시하고,<br />
            원하는 조건의 매물이 등록되면 즉시 알려드립니다.
          </p>
          <div style={{ display: 'flex', gap: 16, justifyContent: 'center' }}>
            <Link href="/signup">
              <button className="btn-primary" style={{ padding: '14px 32px', fontSize: 18, background: 'white', color: '#2E7D32' }}>
                무료로 시작하기
              </button>
            </Link>
            <Link href="/pricing">
              <button className="btn-outline" style={{ padding: '14px 32px', fontSize: 18, borderColor: 'white', color: 'white' }}>
                요금제 보기
              </button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: '80px 0' }}>
        <div className="container">
          <h2 style={{ textAlign: 'center', fontSize: 32, marginBottom: 60 }}>
            농지은행 공식 알림보다 강력한 기능
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 32 }}>
            {[
              { icon: '🔍', title: '복합 필터', desc: '지역 + 지목 + 면적 + 금액을 조합한 정밀한 조건 설정. 공식 알림은 읍면동 지역만 가능합니다.' },
              { icon: '⚡', title: '즉시 알림', desc: 'Premium은 매물 등록 후 1시간 내 알림. 공식 서비스는 다음날 오전 10시에만 보냅니다.' },
              { icon: '📱', title: '다채널 알림', desc: '이메일 + 카카오톡 + SMS. 어디서든 매물 소식을 받아보세요.' },
            ].map((f, i) => (
              <div key={i} className="card" style={{ textAlign: 'center', padding: 32 }}>
                <div style={{ fontSize: 48, marginBottom: 16 }}>{f.icon}</div>
                <h3 style={{ fontSize: 20, marginBottom: 12 }}>{f.title}</h3>
                <p style={{ color: '#666' }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Comparison */}
      <section style={{ padding: '60px 0', background: '#F5F5F5' }}>
        <div className="container">
          <h2 style={{ textAlign: 'center', fontSize: 28, marginBottom: 40 }}>
            농지은행 공식 vs 농지알리미
          </h2>
          <div style={{ maxWidth: 700, margin: '0 auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', background: 'white', borderRadius: 12, overflow: 'hidden' }}>
              <thead>
                <tr style={{ background: '#E8F5E9' }}>
                  <th style={{ padding: 14, textAlign: 'left' }}>기능</th>
                  <th style={{ padding: 14, textAlign: 'center' }}>농지은행 공식</th>
                  <th style={{ padding: 14, textAlign: 'center', color: '#2E7D32' }}>농지알리미</th>
                </tr>
              </thead>
              <tbody>
                {[
                  ['관심 지역', '최대 3개', 'Basic 5개 / Premium 무제한'],
                  ['필터 조건', '읍면동만', '지역+지목+면적+금액'],
                  ['알림 채널', '카카오+문자', '이메일+카카오+SMS'],
                  ['알림 시점', '다음날 10시', '즉시 (Premium)'],
                ].map(([label, official, ours], i) => (
                  <tr key={i} style={{ borderTop: '1px solid #eee' }}>
                    <td style={{ padding: 14, fontWeight: 600 }}>{label}</td>
                    <td style={{ padding: 14, textAlign: 'center', color: '#999' }}>{official}</td>
                    <td style={{ padding: 14, textAlign: 'center', color: '#2E7D32', fontWeight: 600 }}>{ours}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: '80px 0', textAlign: 'center' }}>
        <div className="container">
          <h2 style={{ fontSize: 32, marginBottom: 16 }}>지금 시작하세요</h2>
          <p style={{ color: '#666', marginBottom: 32 }}>원하는 조건만 설정하면, 나머지는 농지알리미가 알아서 합니다.</p>
          <Link href="/signup">
            <button className="btn-primary" style={{ padding: '14px 40px', fontSize: 18 }}>
              회원가입
            </button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid #eee', padding: '40px 0', color: '#999', textAlign: 'center', fontSize: 14 }}>
        <div className="container">
          <p>© 2025 농지알리미. 농지은행(fbo.or.kr)의 공개 정보를 활용한 서비스입니다.</p>
        </div>
      </footer>
    </Layout>
  );
}
