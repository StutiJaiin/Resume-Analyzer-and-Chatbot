/* ═══════════════════════════════════════════════════════════════════
   ResumeIQ — Job Profiles (COMMENTED OUT — Python Backend Mode)
   File: js/jobs.js

   ★ ALL JOB PROFILE LOGIC NOW RUNS ON THE PYTHON BACKEND:
     backend/job_profiles.py

   This file is kept for reference. The Python implementation mirrors
   every profile and the getJobProfile() function. To restore client-side
   job matching, uncomment this file and update app.js.

   Python equivalents:
     JOB_PROFILES     → job_profiles.py → JOB_PROFILES (dict)
     getJobProfile()  → job_profiles.py → get_job_profile()
═══════════════════════════════════════════════════════════════════ */

/*
// ─────────────────────────────────────────────────────────────
//  EVERYTHING BELOW IS COMMENTED OUT — Python backend handles jobs
// ─────────────────────────────────────────────────────────────

const JOB_PROFILES = {
  'ml engineer': {
    description: `machine learning engineer python tensorflow pytorch sklearn deep learning neural networks
      model deployment mlops docker kubernetes aws sagemaker gcp azure data pipeline
      feature engineering model evaluation a/b testing statistics linear algebra probability
      gradient descent backpropagation convolutional recurrent transformer bert gpt
      sql nosql spark hadoop distributed computing api flask fastapi git ci/cd
      hypothesis testing regression classification clustering computer vision nlp
      reinforcement learning hyperparameter tuning model monitoring data versioning dvc`,
    skills: ['Python','TensorFlow','PyTorch','scikit-learn','MLOps','Docker',
             'AWS','Statistics','Linear Algebra','SQL','Git','Feature Engineering',
             'Deep Learning','NLP','Computer Vision'],
    sources: [
      { icon: '💼', title: 'ML Engineer — Google Careers', url: 'careers.google.com/jobs/ml-engineer',
        insight: 'Requires 3+ years Python, TensorFlow, and distributed training experience' },
      { icon: '🔗', title: 'LinkedIn: ML Engineer Job Trends 2024', url: 'linkedin.com/jobs/machine-learning-engineer',
        insight: '42% of postings require PyTorch; MLOps skills increasingly demanded' },
      { icon: '📊', title: 'Levels.fyi: ML Engineer Salary & Skills', url: 'levels.fyi/ml-engineer',
        insight: 'Top skills: Python, model serving APIs, distributed training' }
    ]
  },

  // ... (all other profiles: data scientist, software engineer, ai researcher,
  //      full stack developer, product manager, data analyst)
  // See backend/job_profiles.py for the full Python version.
};

function getJobProfile(jobTitle) {
  const j = jobTitle.toLowerCase().trim();
  for (const key of Object.keys(JOB_PROFILES)) {
    if (j.includes(key) || key.includes(j)) {
      return { ...JOB_PROFILES[key], role: key };
    }
  }
  // ... alias matching and generic fallback
  // See backend/job_profiles.py → get_job_profile() for full logic.
}

*/
