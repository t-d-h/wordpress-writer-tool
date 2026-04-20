export default function News() {
  const newsItems = [
    {
      id: 1,
      date: 'April 19, 2026',
      title: 'New Feature: AI Content Generation',
      content: 'We\'ve added powerful AI content generation capabilities to help you create engaging articles faster. Choose from multiple AI providers including OpenAI, Gemini, and Anthropic.',
      tags: ['Feature', 'AI']
    },
    {
      id: 2,
      date: 'April 15, 2026',
      title: 'WordPress Site Validation',
      content: 'Before saving your WordPress site configuration, we now validate connectivity and credentials. This ensures you know immediately if your site is configured correctly.',
      tags: ['Improvement', 'WordPress']
    },
    {
      id: 3,
      date: 'April 10, 2026',
      title: 'Enhanced Dashboard Statistics',
      content: 'The dashboard now provides real-time statistics on all your jobs across projects. Track running, pending, completed, and failed tasks at a glance.',
      tags: ['Dashboard', 'Statistics']
    },
    {
      id: 4,
      date: 'April 5, 2026',
      title: 'Multi-Provider AI Support',
      content: 'You can now configure multiple AI providers and set default models for different content generation tasks. Switch between providers seamlessly.',
      tags: ['AI', 'Configuration']
    },
    {
      id: 5,
      date: 'March 28, 2026',
      title: 'Project Management Improvements',
      content: 'Create and manage projects with ease. Each project can have multiple posts with their own content generation pipelines.',
      tags: ['Projects', 'Management']
    }
  ]

  return (
    <div className="page-enter">
      <div className="page-header">
        <h1 className="page-title">News</h1>
        <p className="page-description">Latest updates and announcements</p>
      </div>

      <div className="news-list">
        {newsItems.map(item => (
          <div key={item.id} className="news-card">
            <div className="news-date">{item.date}</div>
            <h3 className="news-title">{item.title}</h3>
            <p className="news-content">{item.content}</p>
            <div className="news-tags">
              {item.tags.map(tag => (
                <span key={tag} className="news-tag">{tag}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
