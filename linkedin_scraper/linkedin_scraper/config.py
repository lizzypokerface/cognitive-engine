LINKEDIN_SEARCH_BASE = "https://www.linkedin.com/jobs/search-results/?keywords={keywords}&geoId=102454443&distance=0.0"

# Search terms for LinkedIn job research in Singapore.
# Grouped by fit and relevance to CV.
# The groupings also double as a priority signal —
# if you're running searches sequentially, work top to bottom.

SEARCH_TERMS = [
    # Core identity — your clearest differentiators
    "ai engineer",            # Your primary positioning; agentic systems, LLM pipelines, production AI
    "agentic engineer",       # Emerging title that matches your desktop-agent and cognitive-engine work exactly
    "ml engineer",            # Bridges AI and backend; common SG title that catches AI-adjacent roles

    # Solutions & delivery — suits your end-to-end ownership and business-facing communication style
    "solutions engineer",     # Client-facing, cross-functional; fits your Nike and Horangi delivery patterns
    "ai solutions engineer",  # Growing SG title; your AI depth + delivery experience is a strong match

    # Backend & software — your foundations, two actual job titles
    "backend engineer",       # Your job title at Zendesk and Horangi; strong resume signal match
    "software engineer",      # Broad catch-all; captures generalist roles that value your full-stack range

    # Infrastructure & ops — supported by your portfolio and AWS experience
    "platform engineer",      # Kubernetes, AWS CDK, CI/CD; your Horangi infra work backs this up
    "cloud engineer",         # AWS cert + CDK experience; catches cloud-focused infra postings
    "devops engineer",        # noteflow-devops-pipeline covers this end to end
    "site reliability engineer", # Overlaps with DevOps; targets reliability-focused infra roles
    "infrastructure engineer",   # Broader than SRE/platform; captures a different slice of postings

    # Domain-specific — real experience, not just adjacent
    "automation engineer",    # Nike contract maps directly; ETL, workflow automation, AI-assisted delivery
    "security engineer",      # Horangi/Bitdefender tenure gives genuine cybersecurity domain credibility

    # Borderline — weakest fit, drop first if trimming
    "data engineer",          # Nike ETL work is adjacent but not your core identity; catches pipeline roles
]

OUTPUT_DIR = "output"
AUTH_FILE = "auth.json"
RESEARCH_NOTES_FILE = "research_notes.txt"

LLM_CONFIG = {"provider": "poe", "model": "gemini-3.1-flash-lite"}
