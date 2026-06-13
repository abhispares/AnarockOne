from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.agents.llm_response import _content_to_text, _get_openai_llm


class RelationshipQueryInput(BaseModel):
    query: str = Field(..., min_length=1, description="Question to answer from relationship intelligence data")
    stakeholder_name: str | None = Field(default=None, description="Optional stakeholder name filter")
    max_interactions: int = Field(default=6, ge=1, le=10, description="Maximum interactions to include")

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("query must not be empty")
        return value


class RelationshipSource(BaseModel):
    stakeholder: str
    source: str
    date: str
    colleague: str
    summary: str


class RelationshipQueryOutput(BaseModel):
    query: str
    answer: str
    stakeholders: list[str]
    sources: list[RelationshipSource]


DUMMY_RELATIONSHIP_DATA: list[dict[str, Any]] = [
    {
        "stakeholder": {
            "name": 'Abhishek',
            "title": 'Chief Financial Officer',
            "company": 'NovaBuild Developers',
            "relationship_strength": 'Strong',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand NovaBuild Developers'],
            "concerns": ['budget governance and data privacy', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Abhishek was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Ananya Rao, Enterprise Sales', 'summary': 'Recent strategy discussion with Abhishek on relationship intelligence value for NovaBuild Developers.', 'discussion': 'Abhishek asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'NovaBuild Developers agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Ananya Rao will share a finance-facing ROI model before the next review.', 'outcome': 'Positive; Abhishek saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Rohan Shah, Business Development', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Abhishek.', 'discussion': 'Abhishek requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Rohan Shah will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Vikram Sethi, Strategic Accounts', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Abhishek.', 'discussion': 'Abhishek is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Vikram Sethi will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Nidhi',
            "title": 'Chief Technology Officer',
            "company": 'PropEdge Realty',
            "relationship_strength": 'Medium',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand PropEdge Realty'],
            "concerns": ['tenant isolation and source citations', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Nidhi was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Meera Iyer, Solutions Engineering', 'summary': 'Recent strategy discussion with Nidhi on relationship intelligence value for PropEdge Realty.', 'discussion': 'Nidhi asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'PropEdge Realty agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Meera Iyer will share a architecture diagram with cited responses before the next review.', 'outcome': 'Positive; Nidhi saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Karan Bedi, Product', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Nidhi.', 'discussion': 'Nidhi requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Karan Bedi will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Nisha Menon, Alliances', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Nidhi.', 'discussion': 'Nidhi is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Nisha Menon will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Jiwesh',
            "title": 'Head of Procurement',
            "company": 'UrbanNest Housing',
            "relationship_strength": 'Weak but improving',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand UrbanNest Housing'],
            "concerns": ['audit trails and retention controls', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Jiwesh was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Devika Nair, Account Management', 'summary': 'Recent strategy discussion with Jiwesh on relationship intelligence value for UrbanNest Housing.', 'discussion': 'Jiwesh asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'UrbanNest Housing agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Devika Nair will share a risk and retention summary before the next review.', 'outcome': 'Positive; Jiwesh saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Saurabh Jain, Legal', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Jiwesh.', 'discussion': 'Jiwesh requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Saurabh Jain will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Riya Thomas, Customer Success', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Jiwesh.', 'discussion': 'Jiwesh is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Riya Thomas will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Radhika',
            "title": 'Chief Marketing Officer',
            "company": 'Skyline Estates',
            "relationship_strength": 'Strong',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand Skyline Estates'],
            "concerns": ['brand safety and lead quality', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Radhika was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Kabir Arora, Growth', 'summary': 'Recent strategy discussion with Radhika on relationship intelligence value for Skyline Estates.', 'discussion': 'Radhika asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'Skyline Estates agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Kabir Arora will share a campaign attribution snapshot before the next review.', 'outcome': 'Positive; Radhika saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Pooja Menon, Customer Success', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Radhika.', 'discussion': 'Radhika requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Pooja Menon will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Tanvi Desai, Partnerships', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Radhika.', 'discussion': 'Radhika is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Tanvi Desai will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Manav',
            "title": 'Chief Operating Officer',
            "company": 'MetroNest Group',
            "relationship_strength": 'Medium-strong',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand MetroNest Group'],
            "concerns": ['change management and regional adoption', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Manav was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Isha Kapoor, Strategic Accounts', 'summary': 'Recent strategy discussion with Manav on relationship intelligence value for MetroNest Group.', 'discussion': 'Manav asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'MetroNest Group agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Isha Kapoor will share a operations rollout plan before the next review.', 'outcome': 'Positive; Manav saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Harsh Vyas, Product Ops', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Manav.', 'discussion': 'Manav requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Harsh Vyas will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Neel Shah, BD Tracker Owner', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Manav.', 'discussion': 'Manav is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Neel Shah will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Sneha',
            "title": 'VP Sales',
            "company": 'Crescent Realty',
            "relationship_strength": 'Medium',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand Crescent Realty'],
            "concerns": ['visibility into account ownership', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Sneha was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Aarav Mehta, Enterprise Sales', 'summary': 'Recent strategy discussion with Sneha on relationship intelligence value for Crescent Realty.', 'discussion': 'Sneha asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'Crescent Realty agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Aarav Mehta will share a sales manager enablement pack before the next review.', 'outcome': 'Positive; Sneha saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Leena Rao, Revenue Ops', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Sneha.', 'discussion': 'Sneha requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Leena Rao will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Gaurav Sinha, Alliances', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Sneha.', 'discussion': 'Sneha is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Gaurav Sinha will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Arjun',
            "title": 'Managing Director',
            "company": 'PrimeHabitat',
            "relationship_strength": 'Strong',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand PrimeHabitat'],
            "concerns": ['board-level ROI and continuity', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Arjun was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Sana Qureshi, Executive Relations', 'summary': 'Recent strategy discussion with Arjun on relationship intelligence value for PrimeHabitat.', 'discussion': 'Arjun asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'PrimeHabitat agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Sana Qureshi will share a executive briefing note before the next review.', 'outcome': 'Positive; Arjun saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Mohit Jain, Business Development', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Arjun.', 'discussion': 'Arjun requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Mohit Jain will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Ritika Paul, Strategy', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Arjun.', 'discussion': 'Arjun is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Ritika Paul will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Kavya',
            "title": 'Head of Customer Experience',
            "company": 'HomeVista',
            "relationship_strength": 'Medium',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand HomeVista'],
            "concerns": ['handoff quality and complaint history', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Kavya was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Dhruv Bansal, Customer Success', 'summary': 'Recent strategy discussion with Kavya on relationship intelligence value for HomeVista.', 'discussion': 'Kavya asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'HomeVista agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Dhruv Bansal will share a customer journey map before the next review.', 'outcome': 'Positive; Kavya saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Mitali Shah, Product', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Kavya.', 'discussion': 'Kavya requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Mitali Shah will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Parth Joshi, Support Ops', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Kavya.', 'discussion': 'Kavya is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Parth Joshi will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Rahul',
            "title": 'Director of Digital Transformation',
            "company": 'EstateWorks',
            "relationship_strength": 'Early-stage',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand EstateWorks'],
            "concerns": ['Microsoft Graph permission boundaries', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Rahul was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Aditi Nair, Solutions Engineering', 'summary': 'Recent strategy discussion with Rahul on relationship intelligence value for EstateWorks.', 'discussion': 'Rahul asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'EstateWorks agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Aditi Nair will share a integration checklist before the next review.', 'outcome': 'Positive; Rahul saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Yash Agarwal, Product', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Rahul.', 'discussion': 'Rahul requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Yash Agarwal will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Sonal Mehra, BD', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Rahul.', 'discussion': 'Rahul is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Sonal Mehra will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Pooja',
            "title": 'Legal Counsel',
            "company": 'GreenAxis Realty',
            "relationship_strength": 'Cautious',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand GreenAxis Realty'],
            "concerns": ['consent, redaction, and audit logs', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Pooja was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Saurabh Jain, Legal', 'summary': 'Recent strategy discussion with Pooja on relationship intelligence value for GreenAxis Realty.', 'discussion': 'Pooja asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'GreenAxis Realty agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Saurabh Jain will share a data processing note before the next review.', 'outcome': 'Positive; Pooja saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Naman Khanna, Compliance', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Pooja.', 'discussion': 'Pooja requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Naman Khanna will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Rhea Dutta, Account Management', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Pooja.', 'discussion': 'Pooja is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Rhea Dutta will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Dev',
            "title": 'Chief Revenue Officer',
            "company": 'NorthStar Spaces',
            "relationship_strength": 'Strong',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand NorthStar Spaces'],
            "concerns": ['forecast accuracy and account transitions', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Dev was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Aman Verma, Enterprise Sales', 'summary': 'Recent strategy discussion with Dev on relationship intelligence value for NorthStar Spaces.', 'discussion': 'Dev asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'NorthStar Spaces agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Aman Verma will share a pipeline risk dashboard sample before the next review.', 'outcome': 'Positive; Dev saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Kritika Bose, RevOps', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Dev.', 'discussion': 'Dev requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Kritika Bose will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Rohan Shah, Business Development', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Dev.', 'discussion': 'Dev is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Rohan Shah will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Meera',
            "title": 'Head of Partnerships',
            "company": 'BuildSphere',
            "relationship_strength": 'Medium',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand BuildSphere'],
            "concerns": ['partner overlap and duplicate outreach', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Meera was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Nisha Menon, Alliances', 'summary': 'Recent strategy discussion with Meera on relationship intelligence value for BuildSphere.', 'discussion': 'Meera asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'BuildSphere agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Nisha Menon will share a partner influence map before the next review.', 'outcome': 'Positive; Meera saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Kabir Arora, Growth', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Meera.', 'discussion': 'Meera requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Kabir Arora will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Ananya Rao, Enterprise Sales', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Meera.', 'discussion': 'Meera is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Ananya Rao will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Samar',
            "title": 'Procurement Manager',
            "company": 'Sunrise Builders',
            "relationship_strength": 'Weak',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand Sunrise Builders'],
            "concerns": ['late procurement involvement', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Samar was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Devika Nair, Account Management', 'summary': 'Recent strategy discussion with Samar on relationship intelligence value for Sunrise Builders.', 'discussion': 'Samar asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'Sunrise Builders agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Devika Nair will share a vendor onboarding checklist before the next review.', 'outcome': 'Positive; Samar saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Saurabh Jain, Legal', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Samar.', 'discussion': 'Samar requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Saurabh Jain will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Riya Thomas, Customer Success', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Samar.', 'discussion': 'Samar is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Riya Thomas will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Tanya',
            "title": 'Chief People Officer',
            "company": 'UrbanLeaf Communities',
            "relationship_strength": 'Medium',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand UrbanLeaf Communities'],
            "concerns": ['team adoption and privacy expectations', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Tanya was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Mitali Shah, Product', 'summary': 'Recent strategy discussion with Tanya on relationship intelligence value for UrbanLeaf Communities.', 'discussion': 'Tanya asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'UrbanLeaf Communities agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Mitali Shah will share a training and adoption plan before the next review.', 'outcome': 'Positive; Tanya saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Harsh Vyas, Product Ops', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Tanya.', 'discussion': 'Tanya requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Harsh Vyas will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Pooja Menon, Customer Success', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Tanya.', 'discussion': 'Tanya is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Pooja Menon will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    },
    {
        "stakeholder": {
            "name": 'Vikrant',
            "title": 'Founder',
            "company": 'Legacy Infra',
            "relationship_strength": 'Strong but informal',
            "preferences": ['Prefers concise context before outreach and clear next steps', 'Responds best when internal history is summarized with source references', 'Values warm introductions from colleagues who already understand Legacy Infra'],
            "concerns": ['trust continuity after leadership changes', 'Avoiding repeated discovery calls with different Anarock teams', 'Ensuring sensitive relationship notes are visible only to the right users'],
            "missed_opportunities": ['A previous opportunity slowed because Vikrant was approached without full context from earlier conversations', 'The account team missed a follow-up window when commitments were not carried into the next planning cycle'],
        },
        "interactions": [{'date': '2026-06-07', 'source': 'Microsoft Teams meeting', 'colleague': 'Sana Qureshi, Executive Relations', 'summary': 'Recent strategy discussion with Vikrant on relationship intelligence value for Legacy Infra.', 'discussion': 'Vikrant asked how AnarockOne can reveal colleagues with recent stakeholder context and reduce cold outreach.', 'decisions': 'Legacy Infra agreed to review a POC workflow using dummy Teams, Outlook, and BD Tracker data.', 'commitments': 'Sana Qureshi will share a founder-level narrative before the next review.', 'outcome': 'Positive; Vikrant saw value in preserving context across account transitions.'}, {'date': '2026-05-29', 'source': 'Outlook email', 'colleague': 'Vikram Sethi, Strategic Accounts', 'summary': 'Email follow-up covering prerequisites, risks, and open questions for Vikrant.', 'discussion': 'Vikrant requested clarity on access controls, cited summaries, and what information future teams can view.', 'decisions': 'Demo should show source-backed answers and clear separation between summary and raw communication history.', 'commitments': 'Vikram Sethi will document risk notes and send a concise follow-up before the next call.', 'outcome': 'Warm but dependent on proof that the platform handles sensitive context responsibly.'}, {'date': '2026-04-18', 'source': 'BD Tracker update', 'colleague': 'Ritika Paul, Strategy', 'summary': 'BD Tracker note capturing relationship history and missed opportunity context for Vikrant.', 'discussion': 'Vikrant is influenced by internal sponsors and expects Anarock to remember prior concerns rather than restart discovery.', 'decisions': 'Future outreach should begin with known preferences, prior commitments, and unresolved blockers.', 'commitments': 'Ritika Paul will keep the stakeholder map updated after every meaningful interaction.', 'outcome': 'Useful relationship intelligence captured for future BD and sales teams.'}],
    }
]


def _tokens(text: str) -> set[str]:
    return {
        token.strip(".,!?;:()[]{}\"'").lower()
        for token in text.split()
        if len(token.strip(".,!?;:()[]{}\"'")) > 2
    }


def _stakeholder_text(record: dict[str, Any]) -> str:
    stakeholder = record["stakeholder"]
    interaction_text = " ".join(
        " ".join(str(value) for value in interaction.values())
        for interaction in record["interactions"]
    )
    profile_text = " ".join(
        [
            stakeholder["name"],
            stakeholder["title"],
            stakeholder["company"],
            stakeholder["relationship_strength"],
            " ".join(stakeholder["preferences"]),
            " ".join(stakeholder["concerns"]),
            " ".join(stakeholder["missed_opportunities"]),
        ]
    )
    return f"{profile_text} {interaction_text}"


def _select_records(request: RelationshipQueryInput) -> list[dict[str, Any]]:
    query_tokens = _tokens(f"{request.query} {request.stakeholder_name or ''}")
    scored_records = []

    for record in DUMMY_RELATIONSHIP_DATA:
        stakeholder_name = record["stakeholder"]["name"].lower()
        if request.stakeholder_name and request.stakeholder_name.lower() not in stakeholder_name:
            continue

        record_tokens = _tokens(_stakeholder_text(record))
        score = len(query_tokens & record_tokens)
        if request.stakeholder_name and request.stakeholder_name.lower() in stakeholder_name:
            score += 20
        scored_records.append((score, record))

    if not scored_records:
        return []

    scored_records.sort(key=lambda item: item[0], reverse=True)
    top_score = scored_records[0][0]
    if top_score == 0 and not request.stakeholder_name:
        return DUMMY_RELATIONSHIP_DATA

    return [record for score, record in scored_records if score > 0][:2]


def _interaction_score(interaction: dict[str, str], query_tokens: set[str]) -> int:
    interaction_tokens = _tokens(" ".join(interaction.values()))
    return len(query_tokens & interaction_tokens)


def _build_context(request: RelationshipQueryInput) -> tuple[str, list[str], list[RelationshipSource]]:
    records = _select_records(request)
    query_tokens = _tokens(request.query)
    context_blocks: list[str] = []
    stakeholders: list[str] = []
    sources: list[RelationshipSource] = []

    for record in records:
        stakeholder = record["stakeholder"]
        stakeholders.append(f"{stakeholder['name']} ({stakeholder['title']}, {stakeholder['company']})")

        interactions = sorted(
            record["interactions"],
            key=lambda item: (item["date"], _interaction_score(item, query_tokens)),
            reverse=True,
        )[: request.max_interactions]

        source_counter = Counter(interaction["source"] for interaction in interactions)
        context_blocks.append(
            "\n".join(
                [
                    f"Stakeholder: {stakeholder['name']}",
                    f"Role/company: {stakeholder['title']}, {stakeholder['company']}",
                    f"Relationship strength: {stakeholder['relationship_strength']}",
                    f"Preferences: {'; '.join(stakeholder['preferences'])}",
                    f"Concerns: {'; '.join(stakeholder['concerns'])}",
                    f"Missed opportunities/context: {'; '.join(stakeholder['missed_opportunities'])}",
                    f"Available source mix: {dict(source_counter)}",
                ]
            )
        )

        for interaction in interactions:
            sources.append(
                RelationshipSource(
                    stakeholder=stakeholder["name"],
                    source=interaction["source"],
                    date=interaction["date"],
                    colleague=interaction["colleague"],
                    summary=interaction["summary"],
                )
            )
            context_blocks.append(
                "\n".join(
                    [
                        f"Interaction date: {interaction['date']}",
                        f"Source: {interaction['source']}",
                        f"Internal colleague: {interaction['colleague']}",
                        f"Summary: {interaction['summary']}",
                        f"What was discussed: {interaction['discussion']}",
                        f"Key decisions: {interaction['decisions']}",
                        f"Commitments: {interaction['commitments']}",
                        f"Outcome: {interaction['outcome']}",
                    ]
                )
            )

    return "\n\n---\n\n".join(context_blocks), stakeholders, sources


def _build_prompt(query: str, context: str, today: date | None = None) -> str:
    current_date = (today or date.today()).isoformat()
    return f"""You are the Relationship Intelligence assistant for a hackathon POC.
Answer the user's question using only the dummy relationship intelligence context below.

Rules:
- Do not invent stakeholders, meetings, emails, commitments, or outcomes.
- If the context does not contain enough evidence, say what is missing.
- Mention the internal colleagues who have warm context.
- Include recent interactions, decisions, commitments, relationship strength, preferences, concerns, and missed-opportunity context when relevant.
- Keep the answer concise and useful for a BD or sales user preparing outreach.
- Today is {current_date}.

Dummy relationship intelligence context:
{context or "No matching dummy relationship records were found."}

User question:
{query}
"""


def answer_relationship_query(
    body: RelationshipQueryInput | dict[str, Any],
) -> RelationshipQueryOutput:
    request = body if isinstance(body, RelationshipQueryInput) else RelationshipQueryInput(**body)
    context, stakeholders, sources = _build_context(request)
    prompt = _build_prompt(request.query.strip(), context)
    response = _get_openai_llm().invoke(prompt)
    answer = _content_to_text(getattr(response, "content", response)).strip()

    return RelationshipQueryOutput(
        query=request.query.strip(),
        answer=answer,
        stakeholders=stakeholders,
        sources=sources,
    )
