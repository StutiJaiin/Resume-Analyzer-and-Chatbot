# ═══════════════════════════════════════════════════════════════════
#  ResumeIQ — Job Profiles (Python)
#  File: backend/job_profiles.py
#
#  Mirrors js/jobs.js — contains job description profiles
#  simulating a web-scraped corpus.
#
#  Each profile contains:
#    description  — representative JD text (TF-IDF corpus)
#    skills       — canonical skill list for overlap scoring
#    sources      — web sources that informed this profile
#
#  [ML-HOOK] In future, replace with:
#    - Live API calls to LinkedIn/Indeed/Glassdoor
#    - A trained classifier that auto-generates JD profiles
#    - Vector DB embeddings for semantic job matching
# ═══════════════════════════════════════════════════════════════════

from typing import Dict, List, Optional


# ─── Job profile data structure (matches js/jobs.js exactly) ───
JOB_PROFILES: Dict[str, Dict] = {
    'ml engineer': {
        'description': (
            'machine learning engineer python tensorflow pytorch sklearn deep learning neural networks '
            'model deployment mlops docker kubernetes aws sagemaker gcp azure data pipeline '
            'feature engineering model evaluation a/b testing statistics linear algebra probability '
            'gradient descent backpropagation convolutional recurrent transformer bert gpt '
            'sql nosql spark hadoop distributed computing api flask fastapi git ci/cd '
            'hypothesis testing regression classification clustering computer vision nlp '
            'reinforcement learning hyperparameter tuning model monitoring data versioning dvc'
        ),
        'skills': [
            'Python', 'TensorFlow', 'PyTorch', 'scikit-learn', 'MLOps', 'Docker',
            'AWS', 'Statistics', 'Linear Algebra', 'SQL', 'Git', 'Feature Engineering',
            'Deep Learning', 'NLP', 'Computer Vision'
        ],
        'sources': [
            {'icon': '💼', 'title': 'ML Engineer — Google Careers', 'url': 'careers.google.com/jobs/ml-engineer',
             'insight': 'Requires 3+ years Python, TensorFlow, and distributed training experience'},
            {'icon': '🔗', 'title': 'LinkedIn: ML Engineer Job Trends 2024', 'url': 'linkedin.com/jobs/machine-learning-engineer',
             'insight': '42% of postings require PyTorch; MLOps skills increasingly demanded'},
            {'icon': '📊', 'title': 'Levels.fyi: ML Engineer Salary & Skills', 'url': 'levels.fyi/ml-engineer',
             'insight': 'Top skills: Python, model serving APIs, distributed training'}
        ]
    },

    'data scientist': {
        'description': (
            'data scientist python r statistics machine learning pandas numpy matplotlib seaborn '
            'scikit-learn sql tableau power bi a/b testing hypothesis testing regression classification '
            'clustering feature engineering exploratory data analysis eda visualization business analytics '
            'predictive modeling causal inference time series forecasting nlp text analysis '
            'bayesian statistics experimental design data wrangling spark hadoop aws azure gcp '
            'jupyter notebook git communication storytelling stakeholder management'
        ),
        'skills': [
            'Python', 'R', 'Statistics', 'SQL', 'Pandas', 'scikit-learn', 'Tableau',
            'A/B Testing', 'Data Visualization', 'Hypothesis Testing', 'Machine Learning',
            'Communication', 'Spark', 'Git'
        ],
        'sources': [
            {'icon': '📈', 'title': 'Data Scientist — Meta Careers', 'url': 'metacareers.com/data-scientist',
             'insight': 'Focus on experimentation, causal inference, and large-scale analytics'},
            {'icon': '🔗', 'title': 'Kaggle: Data Science Survey 2024', 'url': 'kaggle.com/survey',
             'insight': 'Python is top language; SQL and visualization highly valued'},
            {'icon': '🎓', 'title': 'Towards Data Science: Role Guide', 'url': 'towardsdatascience.com/role-guide',
             'insight': 'Statistical thinking and communication are top differentiators'}
        ]
    },

    'software engineer': {
        'description': (
            'software engineer java python javascript typescript react nodejs spring boot '
            'rest api microservices docker kubernetes git ci/cd agile data structures algorithms '
            'system design sql nosql cloud aws azure gcp object oriented programming design patterns '
            'testing unit integration tdd bdd code review git github debugging performance optimization '
            'linux bash scripting concurrency multithreading distributed systems scalability'
        ),
        'skills': [
            'Python / Java', 'JavaScript', 'TypeScript', 'React', 'System Design',
            'REST APIs', 'Docker', 'Git', 'Algorithms', 'SQL', 'Microservices',
            'Testing', 'Cloud (AWS/GCP/Azure)'
        ],
        'sources': [
            {'icon': '💻', 'title': 'SWE — Amazon Jobs', 'url': 'amazon.jobs/software-engineer',
             'insight': 'Emphasis on data structures, system design, and leadership principles'},
            {'icon': '🔗', 'title': 'LinkedIn: Top SWE Skills 2024', 'url': 'linkedin.com/jobs/software-engineer-skills',
             'insight': 'TypeScript and cloud experience are most in-demand additions'},
            {'icon': '📊', 'title': 'Stack Overflow Dev Survey 2024', 'url': 'survey.stackoverflow.co/2024',
             'insight': 'JavaScript is #1 language; React is most wanted framework'}
        ]
    },

    'ai researcher': {
        'description': (
            'ai researcher deep learning natural language processing nlp computer vision '
            'reinforcement learning transformers bert gpt llm large language models pytorch tensorflow '
            'research publications arxiv mathematics optimization gradient descent backpropagation '
            'statistics probability theory generative models diffusion models attention mechanism '
            'self supervised learning contrastive learning few shot zero shot prompting fine tuning '
            'rlhf alignment safety interpretability mechanistic evaluation benchmarking phd'
        ),
        'skills': [
            'Deep Learning', 'NLP', 'PyTorch', 'Mathematics', 'Research Writing',
            'Publications', 'Transformers', 'Reinforcement Learning', 'Statistics',
            'Generative Models', 'Python', 'Linear Algebra'
        ],
        'sources': [
            {'icon': '🔬', 'title': 'AI Researcher — Anthropic Careers', 'url': 'anthropic.com/careers',
             'insight': 'Strong ML theory, publication record, and safety orientation valued'},
            {'icon': '📄', 'title': 'Google Scholar: AI Research Trends', 'url': 'scholar.google.com/ai-trends',
             'insight': 'Transformers, diffusion models, and RLHF are dominant 2024 topics'},
            {'icon': '🧠', 'title': 'Papers with Code: Research Landscape', 'url': 'paperswithcode.com/sota',
             'insight': 'Open-source contributions and reproducible research highly valued'}
        ]
    },

    'full stack developer': {
        'description': (
            'full stack developer html css javascript react vue angular nodejs express '
            'python django flask ruby rails php laravel sql mysql postgresql mongodb redis '
            'rest graphql api docker kubernetes aws gcp azure git ci/cd webpack vite typescript '
            'responsive design ui ux tailwind bootstrap testing jest cypress agile scrum'
        ),
        'skills': [
            'HTML/CSS', 'JavaScript', 'React/Vue', 'Node.js', 'Python', 'SQL',
            'MongoDB', 'REST/GraphQL', 'Docker', 'AWS', 'Git', 'TypeScript', 'Testing'
        ],
        'sources': [
            {'icon': '🌐', 'title': 'Full Stack — Stripe Engineering', 'url': 'stripe.com/jobs/engineering',
             'insight': 'Strong focus on TypeScript, React, and API design'},
            {'icon': '🔗', 'title': 'LinkedIn: Full Stack Trends', 'url': 'linkedin.com/jobs/full-stack-developer',
             'insight': 'React + Node.js most requested combo in 2024'},
            {'icon': '📊', 'title': 'State of JS Survey 2024', 'url': 'stateofjs.com/2024',
             'insight': 'TypeScript adoption over 90%; Next.js dominant framework'}
        ]
    },

    'product manager': {
        'description': (
            'product manager product strategy roadmap stakeholder management user research '
            'ux design agile scrum sprint planning jira confluence prioritization okr kpi '
            'market analysis competitive analysis go to market launch metrics data analysis '
            'a/b testing sql tableau figma wireframe prototyping cross functional collaboration '
            'communication presentation leadership customer discovery jobs to be done'
        ),
        'skills': [
            'Product Strategy', 'Roadmapping', 'User Research', 'Agile/Scrum',
            'Data Analysis', 'SQL', 'Stakeholder Management', 'A/B Testing',
            'Figma', 'Communication', 'OKRs', 'Jira'
        ],
        'sources': [
            {'icon': '📋', 'title': 'PM — Airbnb Careers', 'url': 'careers.airbnb.com/product',
             'insight': 'Emphasis on customer obsession, data fluency, and cross-team leadership'},
            {'icon': '🔗', 'title': 'LinkedIn: PM Job Trends 2024', 'url': 'linkedin.com/jobs/product-manager',
             'insight': 'Technical PMs with SQL/analytics skills 40% more in demand'},
            {'icon': '📊', 'title': 'Product School: PM Skills Report', 'url': 'productschool.com/report',
             'insight': 'AI product knowledge now top-3 must-have skill'}
        ]
    },

    'data analyst': {
        'description': (
            'data analyst sql python r excel tableau power bi data visualization dashboard '
            'reporting metrics kpi business intelligence etl data pipeline statistics descriptive '
            'analysis trend analysis cohort analysis funnel analysis hypothesis testing a/b testing '
            'stakeholder communication storytelling data cleaning wrangling google analytics '
            'looker dbt snowflake bigquery presentation problem solving'
        ),
        'skills': [
            'SQL', 'Python / R', 'Excel', 'Tableau / Power BI', 'Data Visualization',
            'Statistics', 'Business Intelligence', 'ETL', 'A/B Testing',
            'Communication', 'Dashboards', 'Google Analytics'
        ],
        'sources': [
            {'icon': '📊', 'title': 'Data Analyst — Netflix Jobs', 'url': 'jobs.netflix.com/data-analyst',
             'insight': 'Heavy emphasis on SQL, storytelling with data, and A/B testing'},
            {'icon': '🔗', 'title': 'LinkedIn: Data Analyst Trends', 'url': 'linkedin.com/jobs/data-analyst',
             'insight': 'dbt and Snowflake now expected in modern analytics stacks'},
            {'icon': '📈', 'title': 'Mode: Analytics Skills Report', 'url': 'mode.com/analytics-report',
             'insight': 'Python overtaking R; Tableau + SQL still the core combo'}
        ]
    }
}

# ─── Aliases for fuzzy job matching (mirrors js/jobs.js) ───
JOB_ALIASES: Dict[str, str] = {
    'mle': 'ml engineer',
    'machine learning': 'ml engineer',
    'ds': 'data scientist',
    'swe': 'software engineer',
    'sde': 'software engineer',
    'backend': 'software engineer',
    'frontend': 'full stack developer',
    'fullstack': 'full stack developer',
    'pm': 'product manager',
    'da': 'data analyst',
}


def get_job_profile(job_title: str) -> Dict:
    """
    Fuzzy-match user input to stored job profiles.
    Falls back to a generic profile for unknown roles.

    Parameters:
        job_title (str): User-entered job title

    Returns:
        Dict with description, skills, sources, and role
    """
    j = job_title.lower().strip()

    # Exact or partial key match
    for key in JOB_PROFILES:
        if j in key or key in j:
            return {**JOB_PROFILES[key], 'role': key}

    # Alias matching
    for alias, key in JOB_ALIASES.items():
        if alias in j:
            return {**JOB_PROFILES[key], 'role': key}

    # Generic fallback
    return {
        'description': (
            f'{job_title} skills experience technical analytical problem solving '
            'communication teamwork leadership python programming project management '
            'data analysis research documentation agile collaboration'
        ),
        'skills': [
            'Problem Solving', 'Communication', 'Technical Skills',
            'Python', 'Project Management', 'Research', 'Collaboration'
        ],
        'sources': [
            {'icon': '🔗', 'title': f'{job_title} — LinkedIn Jobs',
             'url': f'linkedin.com/jobs/{job_title.replace(" ", "-")}',
             'insight': 'Browse active listings for current skill requirements'},
            {'icon': '💼', 'title': f'{job_title} — Indeed',
             'url': f'indeed.com/jobs?q={job_title.replace(" ", "+")}',
             'insight': 'Compare salaries and required qualifications'},
            {'icon': '📊', 'title': 'Glassdoor: Role Insights',
             'url': f'glassdoor.com/jobs/{job_title.replace(" ", "-")}',
             'insight': 'Interview questions and company culture insights'}
        ],
        'role': job_title.lower()
    }
