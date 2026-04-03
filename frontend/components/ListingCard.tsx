interface Listing {
  id: string;
  address: string;
  land_category: string | null;
  trade_type: string | null;
  biz_type: string | null;
  total_area: number | null;
  price: number | null;
  deadline: string | null;
  applicant_count: number | null;
  detail_url: string | null;
}

function formatPrice(price: number | null): string {
  if (price === null) return '미정';
  if (price >= 100000000) {
    const eok = Math.floor(price / 100000000);
    const man = Math.floor((price % 100000000) / 10000);
    return man > 0 ? `${eok}억 ${man.toLocaleString()}만원` : `${eok}억원`;
  }
  if (price >= 10000) {
    return `${Math.floor(price / 10000).toLocaleString()}만원`;
  }
  return `${price.toLocaleString()}원`;
}

export default function ListingCard({ listing }: { listing: Listing }) {
  const area = listing.total_area;
  const pyeong = area ? (area / 3.3058).toFixed(1) : '-';

  return (
    <div className="card" style={{ marginBottom: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <p style={{ fontWeight: 700, fontSize: 16, marginBottom: 8 }}>
            {listing.address || '주소 미상'}
          </p>
          <div style={{ display: 'flex', gap: 8, marginBottom: 8 }}>
            {listing.trade_type && (
              <span className={`badge ${listing.trade_type === '매도' ? 'badge-blue' : 'badge-green'}`}>
                {listing.trade_type}
              </span>
            )}
            {listing.biz_type && <span className="badge badge-orange">{listing.biz_type}</span>}
            {listing.land_category && <span className="badge badge-green">{listing.land_category}</span>}
          </div>
          <p style={{ color: '#666', fontSize: 14 }}>
            면적: {area ? `${area.toLocaleString()}㎡ (${pyeong}평)` : '-'} |
            희망가: {formatPrice(listing.price)}
          </p>
          <p style={{ color: '#999', fontSize: 13 }}>
            신청기한: {listing.deadline || '-'} | 신청자: {listing.applicant_count ?? 0}명
          </p>
        </div>
        {listing.detail_url && (
          <a href={listing.detail_url} target="_blank" rel="noopener noreferrer">
            <button className="btn-outline" style={{ whiteSpace: 'nowrap', fontSize: 13, padding: '8px 14px' }}>
              상세보기
            </button>
          </a>
        )}
      </div>
    </div>
  );
}
