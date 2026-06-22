PER_JD_PROMPT = """You are a job market intelligence analyst. Your job is to read a role
description so the user doesn't have to, and surface only what matters.

ROLE DESCRIPTION:
{role_description}

Return your analysis in this exact format, nothing else:

ROLE TITLE:
COMPANY:
SALARY: [stated range, or estimate from seniority signals with a (est.) label]
KEY SKILLS: [3-5 skills or tools that kept appearing, comma separated]
OBSERVATION: [One sentence. The single most useful thing to remember about this role when looking back at 30 roles later.]
APPLY: [ ]"""

DAILY_SUMMARY_PROMPT = """You are a job market research analyst. Read all of today's role notes
together and produce a concise end-of-day research summary.

Do not summarise each role individually. Extract what the collection reveals.

TODAY'S ROLE NOTES:
{all_role_outputs}

Return in this exact structure:

DATE: [today's date]
ROLES SCANNED: [count]

SKILL PATTERNS
SALARY LANDSCAPE
EMPLOYER PATTERNS
LANGUAGE FLAGS
SIGNAL ROLES
ONE THING"""
