
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { getPost, validateWordCount } from '../api/client';

export default function PostView() {
  const { id } = useParams();
  const [post, setPost] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [validationResult, setValidationResult] = useState(null);
  const [validating, setValidating] = useState(false);

  useEffect(() => {
    setLoading(true);
    getPost(id)
      .then(response => {
        setPost(response.data);
      })
      .catch(err => {
        setError(err.response?.data?.detail || err.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [id]);

  const handleValidate = () => {
    setValidating(true);
    setValidationResult(null);
    validateWordCount(id)
      .then(response => {
        setValidationResult(response.data);
      })
      .catch(err => {
        alert('Error: ' + (err.response?.data?.detail || err.message));
      })
      .finally(() => {
        setValidating(false);
      });
  };

  if (loading) return <div className="loading-page">Loading post...</div>;
  if (error) return <div className="error-message">Error: {error}</div>;
  if (!post) return <div className="empty-state">Post not found.</div>;

  return (
    <div className="post-view">
      <h1>{post.title}</h1>
      <div className="post-content" dangerouslySetInnerHTML={{ __html: post.content }} />
      
      <div className="word-count-validation">
        <button onClick={handleValidate} disabled={validating}>
          {validating ? 'Validating...' : 'Validate Word Count'}
        </button>
        {validationResult && (
          <div className={`validation-result ${validationResult.is_valid ? 'valid' : 'invalid'}`}>
            <p>Word Count: {validationResult.word_count}</p>
            <p>Status: {validationResult.is_valid ? 'Valid' : 'Invalid'}</p>
            {!validationResult.is_valid && <p>Message: {validationResult.message}</p>}
          </div>
        )}
      </div>
    </div>
  );
}
