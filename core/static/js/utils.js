/**
 * Utility Functions
 */

const Utils = {
  // Format date
  formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  },

  // Format date relative (e.g., "2 days ago")
  formatDateRelative(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
  },

  // Format file size
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  },

  // Get cookie by name
  getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  },

  // Validate email
  validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  },

  // Validate file type
  validateFileType(file, allowedTypes) {
    const fileType = file.type || '';
    const fileName = file.name || '';
    const extension = fileName.split('.').pop().toLowerCase();

    return allowedTypes.some(type => {
      if (type.startsWith('.')) {
        return extension === type.substring(1);
      }
      return fileType.includes(type);
    });
  },

  // Validate file size
  validateFileSize(file, maxSizeMB) {
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxSizeBytes;
  },

  // Get score color class
  getScoreColor(score) {
    if (score >= 80) return 'score-circle-high';
    if (score >= 60) return 'score-circle-medium';
    return 'score-circle-low';
  },

  // Get score label
  getScoreLabel(score) {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Needs Improvement';
  },

  // Calculate match percentage (improved)
  calculateMatchPercentage(job, resume, preferences) {
    let score = 0;
    let factors = 0;

    // Use resume skills if available, otherwise fall back to preferences
    const userSkills = (resume && resume.skills && resume.skills.length > 0)
      ? resume.skills
      : (preferences && preferences.skills) || [];

    // Skills match (most important - 40 points)
    if (userSkills.length > 0 && job.skills && job.skills.length > 0) {
      const matchingSkills = job.skills.filter(jobSkill =>
        userSkills.some(userSkill =>
          jobSkill.toLowerCase().includes(userSkill.toLowerCase()) ||
          userSkill.toLowerCase().includes(jobSkill.toLowerCase())
        )
      ).length;

      const skillMatchRatio = matchingSkills / job.skills.length;
      score += skillMatchRatio * 40;
      factors++;
    }

    // Job title match (30 points)
    if (preferences && preferences.jobTitle && job.title) {
      const titleMatch = job.title.toLowerCase().includes(preferences.jobTitle.toLowerCase()) ||
        preferences.jobTitle.toLowerCase().includes(job.title.toLowerCase());
      score += titleMatch ? 30 : 0;
      factors++;
    }

    // Location match (15 points)
    if (preferences && preferences.location && job.location) {
      const locationMatch = job.location.toLowerCase().includes(preferences.location.toLowerCase()) ||
        preferences.location.toLowerCase().includes(job.location.toLowerCase());
      score += locationMatch ? 15 : 0;
      factors++;
    }

    // Remote match (10 points)
    if (preferences && preferences.remote !== undefined && job.remote !== undefined) {
      if (preferences.remote === job.remote) {
        score += 10;
      }
      factors++;
    }

    // Experience level match (5 points)
    if (preferences && preferences.experienceLevel && job.experienceLevel) {
      if (preferences.experienceLevel === job.experienceLevel) {
        score += 5;
      }
      factors++;
    }

    // If we have skills, give a baseline score
    if (factors === 0 && userSkills.length > 0) {
      // Give 60-80% match if we have skills but no other factors
      return Math.floor(Math.random() * 20 + 60);
    }

    // If no factors at all, give moderate score
    if (factors === 0) {
      return Math.floor(Math.random() * 30 + 50); // 50-80%
    }

    return Math.min(100, Math.max(0, Math.round(score)));
  },

  // Debounce function
  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  },

  // Show notification (simple implementation)
  showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    // Set colors based on type
    let borderColor = 'var(--border-color)';
    let bgColor = 'var(--bg-secondary)';
    if (type === 'success') {
      borderColor = 'var(--accent-success)';
      bgColor = 'rgba(16, 185, 129, 0.1)';
    } else if (type === 'error') {
      borderColor = 'var(--accent-error)';
      bgColor = 'rgba(239, 68, 68, 0.1)';
    } else if (type === 'warning') {
      borderColor = 'var(--accent-warning)';
      bgColor = 'rgba(245, 158, 11, 0.1)';
    }

    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background-color: ${bgColor};
      border: 1px solid ${borderColor};
      border-radius: var(--radius-md);
      padding: var(--spacing-md) var(--spacing-lg);
      box-shadow: var(--shadow-lg);
      z-index: 1000;
      animation: slideIn 0.3s ease;
      color: var(--text-primary);
      max-width: 400px;
    `;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
      notification.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => {
        if (document.body.contains(notification)) {
          document.body.removeChild(notification);
        }
      }, 300);
    }, 3000);
  },

  // Simulate API delay
  async simulateDelay(ms = 1000) {
    return new Promise(resolve => setTimeout(resolve, ms));
  },

  // Read file as text
  readFileAsText(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(e);
      reader.readAsText(file);
    });
  },

  // Generate unique ID
  generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  },

  // Generate Analysis (Simulated)
  generateAnalysis(resume, preferences) {
    // Generate ATS score (60-95 range, weighted towards preferences)
    const baseScore = 65 + Math.random() * 25;
    const atsScore = Math.round(baseScore);

    // Generate strengths
    const allStrengths = [
      'Clear and concise formatting',
      'Strong action verbs used throughout',
      'Quantifiable achievements included',
      'Relevant keywords present',
      'Professional summary well-written',
      'Education section properly formatted',
      'Work experience clearly detailed',
      'Skills section comprehensive',
      'Contact information complete',
      'Consistent formatting style'
    ];
    const strengths = allStrengths.sort(() => 0.5 - Math.random()).slice(0, 5);

    // Generate weaknesses
    const allWeaknesses = [
      'Could benefit from more industry-specific keywords',
      'Some sections lack quantifiable metrics',
      'Professional summary could be more compelling',
      'Missing some relevant technical skills',
      'Work experience descriptions could be more detailed',
      'Consider adding certifications or awards',
      'Some formatting inconsistencies detected',
      'Could highlight leadership experience more'
    ];
    const weaknesses = allWeaknesses.sort(() => 0.5 - Math.random()).slice(0, 4);

    // Generate missing keywords based on preferences
    const keywordTemplates = {
      'Software Engineer': ['JavaScript', 'React', 'Node.js', 'API', 'Git', 'Agile', 'CI/CD', 'Docker', 'AWS'],
      'Product Manager': ['Agile', 'Scrum', 'Stakeholder', 'Roadmap', 'KPIs', 'User Stories', 'A/B Testing', 'Analytics'],
      'Data Scientist': ['Python', 'Machine Learning', 'SQL', 'Pandas', 'TensorFlow', 'Statistics', 'Data Visualization'],
      'Marketing Manager': ['SEO', 'SEM', 'Content Marketing', 'Analytics', 'Campaign Management', 'ROI', 'Brand Awareness']
    };

    let missingKeywords = [];
    if (preferences && preferences.jobTitle) {
      const jobTitle = preferences.jobTitle.toLowerCase();
      for (const [key, keywords] of Object.entries(keywordTemplates)) {
        if (jobTitle.includes(key.toLowerCase()) || key.toLowerCase().includes(jobTitle.split(' ')[0])) {
          missingKeywords = keywords.sort(() => 0.5 - Math.random()).slice(0, 6);
          break;
        }
      }
    }

    if (missingKeywords.length === 0) {
      missingKeywords = ['Leadership', 'Project Management', 'Communication', 'Problem Solving', 'Team Collaboration', 'Analytics'];
    }

    // Generate professional summary
    const summary = `Experienced professional with a strong track record of delivering results. Proven expertise in ${preferences?.jobTitle || 'your field'} with demonstrated success in driving innovation and achieving organizational goals. Skilled in ${preferences?.skills?.slice(0, 3).join(', ') || 'key competencies'} with a passion for continuous learning and professional development.`;

    return {
      atsScore,
      strengths,
      weaknesses,
      missingKeywords,
      professionalSummary: summary,
      generatedAt: new Date().toISOString()
    };
  }
};

// Add CSS animations for notifications
if (typeof document !== 'undefined') {
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from {
        transform: translateX(100%);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }
    @keyframes slideOut {
      from {
        transform: translateX(0);
        opacity: 1;
      }
      to {
        transform: translateX(100%);
        opacity: 0;
      }
    }
  `;
  document.head.appendChild(style);
}
