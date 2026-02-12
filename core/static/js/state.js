/**
 * Client-side State Management using localStorage
 */

const StateManager = {
  // Storage keys
  KEYS: {
    USER: 'rba_user',
    RESUME: 'rba_resume',
    PREFERENCES: 'rba_preferences',
    ANALYSIS: 'rba_analysis',
    JOBS: 'rba_jobs',
    METRICS: 'rba_metrics'
  },

  // Initialize state
  init() {
    // Set default user if not exists
    if (!this.getUser()) {
      this.setUser({
        name: '',
        email: '',
        createdAt: new Date().toISOString()
      });
    }

    // Set default preferences if not exists
    if (!this.getPreferences()) {
      this.setPreferences({
        jobTitle: '',
        location: '',
        remote: false,
        salaryRange: '',
        experienceLevel: '',
        industries: [],
        skills: []
      });
    }

    // Initialize metrics if not exists
    if (!this.getMetrics()) {
      this.setMetrics({
        lastAnalysisDate: null,
        totalAnalyses: 0,
        averageATSScore: 0,
        jobsFound: 0,
        resumeUploaded: false
      });
    }
  },

  // Hydrate state from server data
  hydrate(data) {
    if (!data) return;

    // Update Resume info with all fields needed by analysis page
    if (data.resumeName || data.atsScore !== undefined) {
      const resumeData = {
        name: data.resumeName,
        fileName: data.resumeName,
        uploadedAt: data.uploadedAt,
        atsScore: data.atsScore,
        atsBreakdown: data.atsBreakdown,
        skills: data.skills,
        missingKeywords: data.atsBreakdown?.missing_keywords || [],
        professionalSummary: data.atsBreakdown?.professional_summary || ''
      };
      this.setResume(resumeData);
    }

    // Update Analysis info (Store raw data, let UI handle display)
    if (data.atsScore !== undefined) {
      const analysisData = {
        atsScore: data.atsScore,
        breakdown: data.atsBreakdown,
        skills: data.skills,
        analyzedAt: data.uploadedAt
      };
      this.setAnalysis(analysisData);

      // Also ensure skills are in preferences for job matching
      const prefs = this.getPreferences();
      // Merge unique skills
      const newSkills = [...new Set([...(prefs.skills || []), ...data.skills])];
      this.updatePreferences({ skills: newSkills });
    }
  },

  // User management
  getUser() {
    const user = localStorage.getItem(this.KEYS.USER);
    return user ? JSON.parse(user) : null;
  },

  setUser(user) {
    localStorage.setItem(this.KEYS.USER, JSON.stringify(user));
    this.dispatchEvent('userUpdated', user);
  },

  updateUser(updates) {
    const user = this.getUser();
    const updated = { ...user, ...updates };
    this.setUser(updated);
    return updated;
  },

  // Resume management
  getResume() {
    const resume = localStorage.getItem(this.KEYS.RESUME);
    return resume ? JSON.parse(resume) : null;
  },

  setResume(resume) {
    localStorage.setItem(this.KEYS.RESUME, JSON.stringify(resume));
    this.dispatchEvent('resumeUpdated', resume);

    // Update metrics
    const metrics = this.getMetrics();
    metrics.resumeUploaded = true;
    this.setMetrics(metrics);
  },

  // Preferences management
  getPreferences() {
    const prefs = localStorage.getItem(this.KEYS.PREFERENCES);
    return prefs ? JSON.parse(prefs) : null;
  },

  setPreferences(preferences) {
    localStorage.setItem(this.KEYS.PREFERENCES, JSON.stringify(preferences));
    this.dispatchEvent('preferencesUpdated', preferences);
  },

  updatePreferences(updates) {
    const prefs = this.getPreferences();
    const updated = { ...prefs, ...updates };
    this.setPreferences(updated);
    return updated;
  },

  // Analysis management
  getAnalysis() {
    const analysis = localStorage.getItem(this.KEYS.ANALYSIS);
    return analysis ? JSON.parse(analysis) : null;
  },

  setAnalysis(analysis) {
    localStorage.setItem(this.KEYS.ANALYSIS, JSON.stringify(analysis));
    this.dispatchEvent('analysisUpdated', analysis);

    // Update metrics
    const metrics = this.getMetrics();
    metrics.lastAnalysisDate = new Date().toISOString();
    metrics.totalAnalyses += 1;
    if (analysis.atsScore) {
      const currentAvg = metrics.averageATSScore;
      const total = metrics.totalAnalyses;
      metrics.averageATSScore = ((currentAvg * (total - 1)) + analysis.atsScore) / total;
    }
    this.setMetrics(metrics);
  },

  // Jobs management
  getJobs() {
    const jobs = localStorage.getItem(this.KEYS.JOBS);
    return jobs ? JSON.parse(jobs) : [];
  },

  setJobs(jobs) {
    localStorage.setItem(this.KEYS.JOBS, JSON.stringify(jobs));
    this.dispatchEvent('jobsUpdated', jobs);

    // Update metrics
    const metrics = this.getMetrics();
    metrics.jobsFound = jobs.length;
    this.setMetrics(metrics);
  },

  addJob(job) {
    const jobs = this.getJobs();
    // Check if job already exists (by id or title+company)
    const exists = jobs.some(j =>
      (job.id && j.id === job.id) ||
      (j.title === job.title && j.company === job.company)
    );
    if (!exists) {
      jobs.push(job);
      this.setJobs(jobs);
    }
  },

  // Metrics management
  getMetrics() {
    const metrics = localStorage.getItem(this.KEYS.METRICS);
    return metrics ? JSON.parse(metrics) : null;
  },

  setMetrics(metrics) {
    localStorage.setItem(this.KEYS.METRICS, JSON.stringify(metrics));
    this.dispatchEvent('metricsUpdated', metrics);
  },

  // Event system for state changes
  listeners: {},

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  },

  off(event, callback) {
    if (this.listeners[event]) {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  },

  dispatchEvent(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${event}:`, error);
        }
      });
    }
  },

  // Clear all data (for testing/logout)
  clearAll() {
    Object.values(this.KEYS).forEach(key => {
      localStorage.removeItem(key);
    });
    this.listeners = {};
  }
};

// Initialize on load
if (typeof window !== 'undefined') {
  StateManager.init();
}
