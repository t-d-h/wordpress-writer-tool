/**
 * Date utilities for consistent GMT+7 (Asia/Bangkok) formatting.
 */

const TIME_ZONE = 'Asia/Bangkok';
const LOCALE = 'en-GB'; // Use GB for DD/MM/YYYY format or US for MM/DD/YYYY. User's OS is linux.

export const formatDateTime = (dateString) => {
  if (!dateString) return '—';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '—';
    
    return date.toLocaleString(LOCALE, {
      timeZone: TIME_ZONE,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false
    });
  } catch (e) {
    return '—';
  }
};

export const formatDateOnly = (dateString) => {
  if (!dateString) return '—';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return '—';
    
    return date.toLocaleDateString(LOCALE, {
      timeZone: TIME_ZONE,
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    });
  } catch (e) {
    return '—';
  }
};
