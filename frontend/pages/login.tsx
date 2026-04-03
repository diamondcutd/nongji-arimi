import { useState } from 'react';
import { useRouter } from 'next/router';
import Layout from '@/components/Layout';
import Link from 'next/link';
import { login } from '@/lib/api';

export default function Login() {
  const router = useRouter();
  const registered = router.query.registered;
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      router.push('/dashboard');
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
          <h1 style={{ fontSize: 24, marginBottom: 8 }}>로그인</h1>

          {registered && (
            <p style={{ color: '#388E3C', background: '#E8F5E9', padding: '10px 14px', borderRadius: 8, marginBottom: 16, fontSize: 14 }}>
              가입이 완료되었습니다. 로그인해주세요.
            </p>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label>이메일</label>
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required placeholder="example@email.com" />
            </div>
            <div className="form-group">
              <label>비밀번호</label>
              <input type="password" value={password} onChange={e => setPassword(e.target.value)} required />
            </div>

            {error && <p className="error-msg">{error}</p>}

            <button type="submit" className="btn-primary" disabled={loading} style={{ width: '100%', marginTop: 8 }}>
              {loading ? '로그인 중...' : '로그인'}
            </button>
          </form>

          <p style={{ textAlign: 'center', marginTop: 24, color: '#666', fontSize: 14 }}>
            계정이 없으신가요? <Link href="/signup" style={{ fontWeight: 600 }}>회원가입</Link>
          </p>
        </div>
      </div>
    </Layout>
  );
}
