import { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { HiOutlineGlobeAlt, HiOutlineClock, HiOutlineDocumentText } from 'react-icons/hi2';
import { getSiteInfo } from '../../api/client';

export default function WpSiteInfoCard({ siteId }) {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!siteId) return;

    const loadInfo = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await getSiteInfo(siteId);
        setInfo(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load WordPress site information');
      } finally {
        setLoading(false);
      }
    };

    loadInfo();
  }, [siteId]);

  if (loading) {
    return (
      <div className="card" style={{ marginBottom: 20 }}>
        <h3 className="card-title">WordPress Site Info</h3>
        <div style={{ padding: '20px 0', color: 'var(--text-muted)' }}>Loading site information...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card" style={{ marginBottom: 20 }}>
        <h3 className="card-title">WordPress Site Info</h3>
        <div style={{ padding: '20px 0', color: 'var(--danger)' }}>{error}</div>
      </div>
    );
  }

  if (!info) return null;

  return (
    <div className="card" style={{ marginBottom: 20 }}>
      <h3 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <HiOutlineGlobeAlt />
        WordPress Site Info
      </h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 20, marginTop: 16 }}>
        <div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 4 }}>Site Name</div>
          <div style={{ fontWeight: 500 }}>{info.name}</div>
        </div>
        <div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 4 }}>Tagline</div>
          <div style={{ fontWeight: 500 }}>{info.description || '-'}</div>
        </div>
        <div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 4 }}>URL</div>
          <div style={{ fontWeight: 500 }}>
            <a href={info.url} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--accent-primary)', textDecoration: 'none' }}>
              {info.url}
            </a>
          </div>
        </div>
        <div>
          <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 4, display: 'flex', alignItems: 'center', gap: 4 }}>
            <HiOutlineClock /> Timezone
          </div>
          <div style={{ fontWeight: 500 }}>{info.timezone_string || 'Default'}</div>
        </div>
      </div>

      <div style={{ marginTop: 24, paddingTop: 16, borderTop: '1px solid var(--border-color)' }}>
        <h4 style={{ fontSize: 14, color: 'var(--text-muted)', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
          <HiOutlineDocumentText /> Post Statistics
        </h4>
        <div style={{ display: 'flex', gap: 24 }}>
          <div>
            <div style={{ fontSize: 24, fontWeight: 600 }}>{info.posts?.total || 0}</div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Total Posts</div>
          </div>
          <div>
            <div style={{ fontSize: 24, fontWeight: 600, color: 'var(--success)' }}>{info.posts?.published || 0}</div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Published</div>
          </div>
          <div>
            <div style={{ fontSize: 24, fontWeight: 600, color: 'var(--warning)' }}>{info.posts?.draft || 0}</div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>Drafts</div>
          </div>
        </div>
      </div>
    </div>
  );
}

WpSiteInfoCard.propTypes = {
  siteId: PropTypes.string.isRequired,
};
