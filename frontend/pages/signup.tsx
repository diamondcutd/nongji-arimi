import { useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import Link from 'next/link';
import { register } from '@/lib/api';

export default function Signup() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await register(email, password, phone || undefined);
      router.push('/login?registered=1');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div style={{ maxWidth: 440, margin: '80px auto', padding: '0 20px' }}>
        <div className="card">
          <h1 style={{ fontSize: 24, marginBottom: 8 }}>회원가입</h1>
          <p style={{ color: '#666', marginBottom: 32 }}>농지알리미에 가입하고 매물 알림을 받아보세요.</p>

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>이메일</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="example@email.com" />
            </div>
            <div className="form-group">
              <label>비밀번호</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required minLength={6} placeholder="6자 이상" />
            </div>
            <div className="form-group">
              <label>전화번호 (선택)</label>
              <input type="tel" value={phone} onChange={e => setPhone(e.target.value)} placeholder="010-1234-5678" />
            </div>

            {error && <p className="error-msg">{error}</p>}

            <button type="submit" className="btn-primary" disabled={loading} style={{ width: '100%', marginTop: 8 }}>
              {loading ? '가입 중...' : '가입하기'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: 24, color: '#666', fontSize: 14 }}>
            이미 계정이 있으신가요? <Link href="/login" style={{ fontWeight: 600 }}>로그인</Link>
          </p>
        </div>
      </div>
    </Layout>
  );
}
