import { ReactNode, useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { getMe, logout } from '@/lib/api';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    getMe().then(setUser).catch(() => setUser(null));
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/');
  };

  return (
    <>
      <nav className="nav">
        <div className="container">
          <Link href="/" className="nav-logo">
            🌾 농지알리미
          </Link>
          <div className="nav-links">
            {user ? (
              <>
                <Link href="/dashboard">대시보드</Link>
                <Link href="/pricing">요금제</Link>
                <span style={{ color: '#666', fontSize: 14 }}>
                  {user.email} ({user.plan})
                </span>
                <button className="btn-outline" onClick={handleLogout} style={{ padding: '6px 14px', fontSize: 13 }}>
                  로그아웃
                </button>
              </>
            ) : (
              <>
                <Link href="/pricing">요금제</Link>
                <Link href="/signup">회원가입</Link>
                <Link href="/login">
                  <button className="btn-primary" style={{ padding: '6px 14px', fontSize: 13 }}>
                    로그인
                  </button>
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>
      <main>{children}</main>
    </>
  );
}
