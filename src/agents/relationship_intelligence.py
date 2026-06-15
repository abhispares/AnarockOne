from __future__ import annotations

import json
import re
from collections import Counter
from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator

from src.agents.llm_response import _content_to_text, _get_openai_llm


class RelationshipQueryInput(BaseModel):
    query: str = Field(..., min_length=1, description="Question to answer from account intelligence data")
    stakeholder_name: str | None = Field(default=None, description="Optional developer/account name filter")
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
    follow_up_questions: list[str] = Field(default_factory=list)


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

BUILDER_ACCOUNT_RENAMES: dict[str, str] = {
    "Abhishek": "Lodha Group",
    "Nidhi": "Prestige Group",
    "Jiwesh": "Godrej Properties",
    "Radhika": "DLF",
    "Manav": "Brigade Group",
    "Sneha": "Sobha Realty",
    "Arjun": "Hiranandani Group",
    "Kavya": "Mahindra Lifespaces",
    "Rahul": "Oberoi Realty",
    "Pooja": "Tata Realty",
    "Dev": "Embassy Group",
    "Meera": "Puravankara",
    "Samar": "Kolte-Patil Developers",
    "Tanya": "Runwal Group",
    "Vikrant": "Kalpataru Group",
}

BUILDER_COMPANY_RENAMES: dict[str, str] = {
    "NovaBuild Developers": "Lodha Group",
    "PropEdge Realty": "Prestige Group",
    "UrbanNest Housing": "Godrej Properties",
    "Skyline Estates": "DLF",
    "MetroNest Group": "Brigade Group",
    "Crescent Realty": "Sobha Realty",
    "PrimeHabitat": "Hiranandani Group",
    "HomeVista": "Mahindra Lifespaces",
    "EstateWorks": "Oberoi Realty",
    "GreenAxis Realty": "Tata Realty",
    "NorthStar Spaces": "Embassy Group",
    "BuildSphere": "Puravankara",
    "Sunrise Builders": "Kolte-Patil Developers",
    "UrbanLeaf Communities": "Runwal Group",
    "Legacy Infra": "Kalpataru Group",
}

ACCOUNT_PHRASE_REWRITES: dict[str, str] = {
    "relationship intelligence value": "account escalations and commercial status",
    "stakeholder context": "developer account context",
    "reduce cold outreach": "surface open escalations, pending collections, and account owners",
    "Relationship history": "Account history",
    "relationship history": "account history",
    "missed opportunity context": "missed commercial opportunity context",
    "preserving context across account transitions": "preserving escalation, collection, and conversation context across account transitions",
    "known preferences, prior commitments, and unresolved blockers": "known escalations, pending commitments, collections status, and unresolved blockers",
    "future BD and sales teams": "future management and account teams",
}

ACCOUNT_BRIEFS_BY_DEVELOPER: dict[str, dict[str, Any]] = {
    "Lodha Group": {
        "executive_status": "Amber",
        "escalations": [
            "Collections escalation open for overdue campaign invoices worth INR 1.8 crore.",
            "Leadership review requested because CRM adoption is lagging in the Mumbai region.",
            "Booking count is decreasing, and leads are reporting repeated Call Center and AI follow-up calls.",
        ],
        "pending_collections": "INR 1.8 crore pending; finance follow-up committed for 2026-06-18.",
        "ongoing_conversations": [
            "Commercial team is negotiating renewed mandate scope for two premium launches.",
            "Finance team asked for source-backed invoice reconciliation before releasing payment.",
        ],
        "management_focus": "Resolve payment blockage before discussing expanded launch support.",
        "next_actions": [
            "Rohan Shah to send reconciliation pack.",
            "Ananya Rao to schedule CFO-level review with clear collection ask.",
        ],
    },
    "Prestige Group": {
        "executive_status": "Green",
        "escalations": ["No critical escalation; data-access clarification is pending with technology team."],
        "pending_collections": "INR 42 lakh pending against two recent activation milestones.",
        "ongoing_conversations": [
            "Technology team is reviewing integration approach for lead and campaign reporting.",
            "Business team is discussing South India launch pipeline for Q3.",
        ],
        "management_focus": "Close integration concerns so commercial expansion is not delayed.",
        "next_actions": ["Meera Iyer to share architecture note.", "Karan Bedi to close open product questions."],
    },
    "Godrej Properties": {
        "executive_status": "Amber",
        "escalations": ["Procurement has held vendor clearance pending audit trail and retention answers."],
        "pending_collections": "INR 76 lakh pending; procurement approval required before payment release.",
        "ongoing_conversations": [
            "Legal and procurement are reviewing retention controls.",
            "Account team is pushing to unblock onboarding for a new project mandate.",
        ],
        "management_focus": "Unblock procurement approval and avoid losing the new mandate window.",
        "next_actions": ["Saurabh Jain to close legal note.", "Devika Nair to align procurement checklist."],
    },
    "DLF": {
        "executive_status": "Green",
        "escalations": [
            "Lead quality concern raised on one campaign; not yet escalated to CXO level.",
            "Regional sales team flagged booking count decline after prospects received repeated Call Center and AI follow-up calls.",
        ],
        "pending_collections": "INR 55 lakh pending, expected after campaign attribution sign-off.",
        "ongoing_conversations": [
            "Marketing team is reviewing attribution and lead quality.",
            "Partnerships team is discussing a joint campaign calendar.",
        ],
        "management_focus": "Show quality improvement before asking for larger media commitment.",
        "next_actions": ["Kabir Arora to share attribution snapshot.", "Pooja Menon to collect campaign feedback."],
    },
    "Brigade Group": {
        "executive_status": "Amber",
        "escalations": ["Regional adoption risk flagged by operations team."],
        "pending_collections": "INR 91 lakh pending across phased rollout milestones.",
        "ongoing_conversations": [
            "Operations team is discussing adoption cadence across cities.",
            "Product ops is preparing rollout governance for regional teams.",
        ],
        "management_focus": "Get operating cadence approved before additional rollout commitments.",
        "next_actions": ["Isha Kapoor to align COO review.", "Harsh Vyas to circulate adoption plan."],
    },
    "Sobha Realty": {
        "executive_status": "Green",
        "escalations": ["Account ownership overlap reported between regional sales teams."],
        "pending_collections": "INR 33 lakh pending; no payment dispute recorded.",
        "ongoing_conversations": [
            "Revenue ops is clarifying owner mapping.",
            "Sales team is reviewing enablement needs for launch managers.",
        ],
        "management_focus": "Clean up ownership before expanding account touchpoints.",
        "next_actions": ["Leena Rao to confirm owner map.", "Aarav Mehta to share enablement pack."],
    },
    "Hiranandani Group": {
        "executive_status": "Green",
        "escalations": ["Board-level ROI proof requested before a multi-project commitment."],
        "pending_collections": "INR 1.2 crore pending against annual commercial closure.",
        "ongoing_conversations": [
            "Executive relations team is preparing board-ready ROI narrative.",
            "Strategic accounts team is mapping decision owners for final approval.",
        ],
        "management_focus": "Make the ROI case crisp for promoter and board review.",
        "next_actions": ["Sana Qureshi to send executive brief.", "Vikram Sethi to validate decision map."],
    },
    "Mahindra Lifespaces": {
        "executive_status": "Amber",
        "escalations": ["Sustainability reporting requirement is delaying final scope approval."],
        "pending_collections": "INR 64 lakh pending; tied to scope freeze.",
        "ongoing_conversations": [
            "ESG and marketing teams are aligning reporting requirements.",
            "Account team is discussing pilot scope for two priority projects.",
        ],
        "management_focus": "Resolve reporting requirement and prevent pilot delay.",
        "next_actions": ["Ritika Paul to capture ESG asks.", "Naman Khanna to review compliance language."],
    },
    "Oberoi Realty": {
        "executive_status": "Red",
        "escalations": [
            "Integration delay escalated by digital team.",
            "Payment release is blocked until delivery timeline is reset.",
            "Bookings are trending down, and high-intent leads have complained about duplicate Call Center and AI follow-up calls.",
        ],
        "pending_collections": "INR 2.4 crore pending; highest collection risk in the POC data.",
        "ongoing_conversations": [
            "Product and digital teams are discussing integration checklist.",
            "BD team is negotiating revised timeline and commercial protection.",
        ],
        "management_focus": "Immediate senior intervention needed to reset timeline and unblock collections.",
        "next_actions": ["Aditi Nair to own integration checklist.", "Sonal Mehra to prepare escalation note."],
    },
    "Tata Realty": {
        "executive_status": "Amber",
        "escalations": ["Legal team has requested stronger consent and redaction controls."],
        "pending_collections": "INR 58 lakh pending; payment dependent on legal comfort.",
        "ongoing_conversations": [
            "Legal and compliance teams are reviewing data handling notes.",
            "Account management is trying to close governance objections.",
        ],
        "management_focus": "Resolve legal objections before any broader rollout discussion.",
        "next_actions": ["Saurabh Jain to send data processing note.", "Naman Khanna to close compliance comments."],
    },
    "Embassy Group": {
        "executive_status": "Green",
        "escalations": [
            "Forecast variance questioned by revenue leadership.",
            "Sales ops reported lead fatigue from repeated AI follow-up and Call Center calls.",
        ],
        "pending_collections": "INR 88 lakh pending, expected after pipeline dashboard validation.",
        "ongoing_conversations": [
            "Revenue ops is validating forecast assumptions.",
            "Enterprise sales is discussing expansion into two commercial assets.",
        ],
        "management_focus": "Validate forecast accuracy and convert expansion interest into committed scope.",
        "next_actions": ["Aman Verma to share pipeline dashboard.", "Kritika Bose to validate variance notes."],
    },
    "Puravankara": {
        "executive_status": "Amber",
        "escalations": ["Partner overlap creating duplicate outreach risk."],
        "pending_collections": "INR 47 lakh pending; no formal dispute.",
        "ongoing_conversations": [
            "Alliances team is mapping partner influence.",
            "Growth team is discussing shared launch ownership.",
        ],
        "management_focus": "Prevent duplicate outreach and settle partner ownership.",
        "next_actions": ["Nisha Menon to share partner influence map.", "Kabir Arora to confirm growth owner."],
    },
    "Kolte-Patil Developers": {
        "executive_status": "Amber",
        "escalations": ["Procurement was involved late and is asking for revised onboarding documents."],
        "pending_collections": "INR 39 lakh pending; vendor onboarding must clear first.",
        "ongoing_conversations": [
            "Procurement and account management are aligning onboarding checklist.",
            "Legal is reviewing vendor terms.",
        ],
        "management_focus": "Close procurement onboarding before the launch schedule slips.",
        "next_actions": ["Devika Nair to share vendor checklist.", "Saurabh Jain to close terms review."],
    },
    "Runwal Group": {
        "executive_status": "Green",
        "escalations": ["No commercial escalation; training adoption needs monitoring."],
        "pending_collections": "INR 29 lakh pending, expected after training sign-off.",
        "ongoing_conversations": [
            "People and product teams are discussing adoption and training.",
            "Customer success is collecting rollout feedback.",
        ],
        "management_focus": "Keep adoption on track so sign-off and collection do not slip.",
        "next_actions": ["Mitali Shah to share training plan.", "Pooja Menon to collect adoption feedback."],
    },
    "Kalpataru Group": {
        "executive_status": "Green",
        "escalations": ["Founder office asked for continuity after leadership changes."],
        "pending_collections": "INR 73 lakh pending; expected after founder narrative is approved.",
        "ongoing_conversations": [
            "Executive relations team is preparing founder-level narrative.",
            "Strategic accounts is documenting leadership transition context.",
        ],
        "management_focus": "Protect founder trust during transition and close pending approval.",
        "next_actions": ["Sana Qureshi to share founder narrative.", "Vikram Sethi to document transition context."],
    },
}

ESCALATION_SHOWCASE_UPDATES: dict[str, dict[str, Any]] = {
    "Lodha Group": {
        "executive_status": "Red",
        "escalations": [
            "Collections escalation open for overdue campaign invoices worth INR 1.8 crore.",
            "Booking count is decreasing across two Mumbai launches, and leads are reporting repeated Call Center and AI follow-up calls.",
            "Site sales head escalated that high-intent leads are being contacted by multiple Anarock touchpoints without a single owner.",
            "Developer has paused approval for the next digital burst until lead fatigue and duplicate calling are resolved.",
        ],
        "pending_collections": "INR 1.8 crore overdue for 47 days; finance wants invoice-level reconciliation before 2026-06-18.",
        "ongoing_conversations": [
            "CFO office is asking for a single collections owner and a written recovery plan.",
            "Mumbai launch team wants Call Center, AI follow-up, and sales callback rules rationalized before the next campaign.",
            "Commercial team is negotiating renewed mandate scope for two premium launches, but expansion is blocked by current service issues.",
        ],
        "management_focus": "Immediate senior intervention needed on collections, duplicate calling, and launch confidence before expansion is discussed.",
        "next_actions": [
            "Rohan Shah to send invoice reconciliation pack by 2026-06-18.",
            "Ananya Rao to schedule CFO-level review with clear payment ask.",
            "Leena Rao to produce lead-contact governance fix for Call Center and AI follow-up cadence.",
        ],
    },
    "Prestige Group": {
        "executive_status": "Amber",
        "escalations": [
            "South India regional team flagged delayed lead handover for two priority launches.",
            "Technology team has not approved data-access approach, delaying automated campaign reporting.",
            "Developer asked why campaign dashboards and sales-qualified lead counts do not reconcile.",
        ],
        "pending_collections": "INR 42 lakh pending against two activation milestones; payment likely after dashboard reconciliation.",
        "ongoing_conversations": [
            "Technology team is reviewing integration approach for lead and campaign reporting.",
            "Business team is discussing South India launch pipeline for Q3, conditional on reporting clarity.",
            "Finance team requested milestone evidence before releasing the pending amount.",
        ],
        "management_focus": "Close reporting reconciliation quickly so Q3 launch discussions are not delayed.",
        "next_actions": [
            "Meera Iyer to share architecture note.",
            "Karan Bedi to close open product questions.",
            "Kritika Bose to send activation evidence pack to finance.",
        ],
    },
    "Godrej Properties": {
        "executive_status": "Red",
        "escalations": [
            "Procurement has held vendor clearance pending audit trail and retention answers.",
            "Payment release is blocked because vendor onboarding documents do not match revised procurement format.",
            "Business sponsor warned that a new mandate window may move to another channel partner if onboarding slips further.",
        ],
        "pending_collections": "INR 76 lakh pending for 35 days; procurement approval required before payment release.",
        "ongoing_conversations": [
            "Legal and procurement are reviewing retention controls.",
            "Account team is pushing to unblock onboarding for a new project mandate.",
            "Procurement asked for a revised vendor checklist and audit-trail note.",
        ],
        "management_focus": "Unblock procurement approval this week and protect the new mandate window.",
        "next_actions": [
            "Saurabh Jain to close legal note.",
            "Devika Nair to align procurement checklist.",
            "Naman Khanna to send audit-trail response before the procurement review.",
        ],
    },
    "DLF": {
        "executive_status": "Amber",
        "escalations": [
            "Lead quality concern raised on one campaign; not yet escalated to CXO level.",
            "Regional sales team flagged booking count decline after prospects received repeated Call Center and AI follow-up calls.",
            "Marketing wants low-intent leads removed from billed performance reports before signing attribution.",
        ],
        "pending_collections": "INR 55 lakh pending; expected after campaign attribution and lead-quality sign-off.",
        "ongoing_conversations": [
            "Marketing team is reviewing attribution and lead quality.",
            "Partnerships team is discussing a joint campaign calendar.",
            "Customer success is collecting examples of duplicate follow-up complaints.",
        ],
        "management_focus": "Prove lead-quality correction and stop duplicate follow-ups before asking for larger media commitment.",
        "next_actions": [
            "Kabir Arora to share attribution snapshot.",
            "Pooja Menon to collect campaign feedback.",
            "Aarav Mehta to propose revised lead qualification rules.",
        ],
    },
    "Brigade Group": {
        "executive_status": "Amber",
        "escalations": [
            "Regional adoption risk flagged by operations team.",
            "Bengaluru team says sales managers are not using the agreed lead disposition workflow.",
            "Collections may slip because rollout milestone evidence is incomplete for two cities.",
        ],
        "pending_collections": "INR 91 lakh pending across phased rollout milestones; INR 36 lakh at risk if city evidence is not closed.",
        "ongoing_conversations": [
            "Operations team is discussing adoption cadence across cities.",
            "Product ops is preparing rollout governance for regional teams.",
            "Finance is asking for milestone completion evidence city-wise.",
        ],
        "management_focus": "Get operating cadence approved and close milestone evidence before collections slip.",
        "next_actions": [
            "Isha Kapoor to align COO review.",
            "Harsh Vyas to circulate adoption plan.",
            "Neel Shah to compile city-wise milestone evidence.",
        ],
    },
    "Oberoi Realty": {
        "executive_status": "Red",
        "escalations": [
            "Integration delay escalated by digital team.",
            "Payment release is blocked until delivery timeline is reset.",
            "Bookings are trending down, and high-intent leads have complained about duplicate Call Center and AI follow-up calls.",
            "Developer has asked for a commercial credit note if the revised integration date slips again.",
        ],
        "pending_collections": "INR 2.4 crore pending for 62 days; highest collection risk in the POC data.",
        "ongoing_conversations": [
            "Product and digital teams are discussing integration checklist.",
            "BD team is negotiating revised timeline and commercial protection.",
            "Finance team is holding payment release until delivery reset is accepted.",
            "Sales leadership wants a no-duplicate-contact commitment before the weekend campaign.",
        ],
        "management_focus": "Immediate senior intervention needed to reset timeline, stop duplicate outreach, and unblock collections.",
        "next_actions": [
            "Aditi Nair to own integration checklist.",
            "Sonal Mehra to prepare escalation note.",
            "Aman Verma to confirm commercial protection position before leadership review.",
        ],
    },
    "Tata Realty": {
        "executive_status": "Amber",
        "escalations": [
            "Legal team has requested stronger consent and redaction controls.",
            "Collection approval is on hold until data handling language is accepted.",
            "Account team reported that governance objections are delaying a broader rollout discussion.",
        ],
        "pending_collections": "INR 58 lakh pending; payment dependent on legal comfort and consent language approval.",
        "ongoing_conversations": [
            "Legal and compliance teams are reviewing data handling notes.",
            "Account management is trying to close governance objections.",
            "Finance asked whether redaction controls can be documented in the statement of work.",
        ],
        "management_focus": "Resolve legal objections before any broader rollout or collection closure.",
        "next_actions": [
            "Saurabh Jain to send data processing note.",
            "Naman Khanna to close compliance comments.",
            "Rhea Dutta to prepare revised SOW language.",
        ],
    },
    "Embassy Group": {
        "executive_status": "Amber",
        "escalations": [
            "Forecast variance questioned by revenue leadership.",
            "Sales ops reported lead fatigue from repeated AI follow-up and Call Center calls.",
            "Expansion into two commercial assets is paused until pipeline dashboard numbers are validated.",
        ],
        "pending_collections": "INR 88 lakh pending, expected after pipeline dashboard validation; INR 31 lakh may age beyond 45 days this week.",
        "ongoing_conversations": [
            "Revenue ops is validating forecast assumptions.",
            "Enterprise sales is discussing expansion into two commercial assets.",
            "Sales ops is asking for a revised lead-contact suppression rule.",
        ],
        "management_focus": "Validate forecast accuracy, fix lead fatigue, and convert expansion interest into committed scope.",
        "next_actions": [
            "Aman Verma to share pipeline dashboard.",
            "Kritika Bose to validate variance notes.",
            "Leena Rao to draft lead suppression rules for repeated follow-ups.",
        ],
    },
    "Puravankara": {
        "executive_status": "Amber",
        "escalations": [
            "Partner overlap creating duplicate outreach risk.",
            "Developer complained that two Anarock teams approached the same channel partner with different commercial terms.",
            "Collection approval is delayed until launch ownership is clarified.",
        ],
        "pending_collections": "INR 47 lakh pending; finance expects owner confirmation before release.",
        "ongoing_conversations": [
            "Alliances team is mapping partner influence.",
            "Growth team is discussing shared launch ownership.",
            "Commercial team is reconciling conflicting partner terms.",
        ],
        "management_focus": "Prevent duplicate outreach, settle partner ownership, and protect developer trust.",
        "next_actions": [
            "Nisha Menon to share partner influence map.",
            "Kabir Arora to confirm growth owner.",
            "Vikram Sethi to reconcile partner commercial terms.",
        ],
    },
    "Kolte-Patil Developers": {
        "executive_status": "Red",
        "escalations": [
            "Procurement was involved late and is asking for revised onboarding documents.",
            "Launch schedule is at risk because vendor onboarding is not cleared.",
            "Developer finance has held payment until procurement confirms revised terms.",
        ],
        "pending_collections": "INR 39 lakh pending; vendor onboarding must clear first and launch date is within two weeks.",
        "ongoing_conversations": [
            "Procurement and account management are aligning onboarding checklist.",
            "Legal is reviewing vendor terms.",
            "Launch team is asking whether Anarock can proceed at risk while onboarding closes.",
        ],
        "management_focus": "Close procurement onboarding immediately before the launch schedule slips.",
        "next_actions": [
            "Devika Nair to share vendor checklist.",
            "Saurabh Jain to close terms review.",
            "Riya Thomas to confirm launch dependency and escalation owner.",
        ],
    },
}


def _apply_escalation_showcase_updates() -> None:
    for account_name, update in ESCALATION_SHOWCASE_UPDATES.items():
        account_brief = ACCOUNT_BRIEFS_BY_DEVELOPER.get(account_name)
        if account_brief:
            account_brief.update(update)

    interaction_updates = {
        "Lodha Group": [
            {
                "date": "2026-06-14",
                "source": "Microsoft Teams meeting",
                "colleague": "Leena Rao, Revenue Ops",
                "summary": "Escalation review on falling bookings and repeated Call Center plus AI follow-up complaints for Lodha Group.",
                "discussion": "Lodha sales leadership said prospects are receiving duplicate calls from Call Center and AI workflows, creating lead fatigue and lowering booking conversion.",
                "decisions": "Anarock will pause duplicate follow-up paths for high-intent leads and create a single owner for each active lead.",
                "commitments": "Leena Rao will send revised contact-governance rules by 2026-06-17.",
                "outcome": "Escalation remains open; Lodha wants proof of correction before approving the next campaign burst.",
            },
            {
                "date": "2026-06-12",
                "source": "Outlook email",
                "colleague": "Rohan Shah, Business Development",
                "summary": "Collections follow-up for INR 1.8 crore overdue invoices at Lodha Group.",
                "discussion": "CFO office asked for invoice-level reconciliation and evidence of delivered campaign milestones.",
                "decisions": "Payment review will happen after reconciliation pack is shared.",
                "commitments": "Rohan Shah will send reconciliation pack by 2026-06-18.",
                "outcome": "Collection risk remains red until finance accepts the reconciliation.",
            },
        ],
        "Prestige Group": [
            {
                "date": "2026-06-13",
                "source": "BD Tracker update",
                "colleague": "Kritika Bose, RevOps",
                "summary": "Prestige Group raised dashboard reconciliation gap between campaign leads and sales-qualified leads.",
                "discussion": "Business team wants one version of lead counts before signing Q3 launch scope.",
                "decisions": "RevOps will reconcile activation evidence, campaign dashboard numbers, and sales-qualified lead counts.",
                "commitments": "Kritika Bose will send the reconciliation pack before the next Prestige commercial call.",
                "outcome": "Q3 expansion remains warm but delayed by reporting confidence.",
            },
        ],
        "Godrej Properties": [
            {
                "date": "2026-06-14",
                "source": "Outlook email",
                "colleague": "Naman Khanna, Compliance",
                "summary": "Godrej Properties procurement blocked payment and new mandate approval pending audit-trail answers.",
                "discussion": "Procurement asked for revised onboarding documents, retention controls, and audit evidence before vendor clearance.",
                "decisions": "Compliance and legal will send a combined response instead of separate notes.",
                "commitments": "Naman Khanna will send audit-trail response before procurement review.",
                "outcome": "Red escalation; new mandate window is at risk if clearance slips.",
            },
        ],
        "Oberoi Realty": [
            {
                "date": "2026-06-15",
                "source": "Microsoft Teams meeting",
                "colleague": "Aman Verma, Enterprise Sales",
                "summary": "Oberoi Realty senior escalation on integration delay, duplicate follow-ups, and INR 2.4 crore blocked collections.",
                "discussion": "Developer leadership asked for a delivery reset, commercial protection, and a no-duplicate-contact commitment for high-intent leads.",
                "decisions": "Anarock will send a revised integration date, collection recovery plan, and lead-contact suppression rule.",
                "commitments": "Aman Verma will confirm commercial protection position before leadership review.",
                "outcome": "Highest-risk escalation in the POC data; senior intervention required.",
            },
        ],
        "Embassy Group": [
            {
                "date": "2026-06-13",
                "source": "BD Tracker update",
                "colleague": "Leena Rao, Revenue Ops",
                "summary": "Embassy Group reported lead fatigue from repeated AI follow-up and Call Center calls.",
                "discussion": "Sales ops said forecast variance is partly driven by duplicate follow-up and inconsistent lead disposition.",
                "decisions": "Revenue ops will validate forecast assumptions and propose contact suppression rules.",
                "commitments": "Leena Rao will draft suppression rules for repeated follow-ups.",
                "outcome": "Expansion interest remains active, but dashboard validation is required before commercial closure.",
            },
        ],
        "Kolte-Patil Developers": [
            {
                "date": "2026-06-12",
                "source": "Microsoft Teams meeting",
                "colleague": "Riya Thomas, Customer Success",
                "summary": "Kolte-Patil Developers launch schedule at risk because procurement onboarding is still open.",
                "discussion": "Developer asked whether Anarock can support launch activity while revised vendor terms are still being reviewed.",
                "decisions": "Account team will not proceed at risk without procurement owner sign-off.",
                "commitments": "Riya Thomas will confirm launch dependency and escalation owner.",
                "outcome": "Red escalation; launch timeline and collections both depend on procurement closure.",
            },
        ],
    }

    for record in DUMMY_RELATIONSHIP_DATA:
        account_name = record["stakeholder"]["name"]
        record["interactions"].extend(interaction_updates.get(account_name, []))


CONTACT_SHOWCASE_UPDATES: dict[str, dict[str, Any]] = {
    "Lodha Group": {
        "developer_contacts": [
            "Abhishek Lodha, CFO Office, owns payment release and invoice reconciliation.",
            "Nidhi Shah, Head of Sales, owns Mumbai launch bookings and sales feedback.",
            "Jiwesh Mehta, Digital Marketing Lead, owns campaign performance and lead-quality review.",
            "Rohit Kulkarni, Site Sales Head, escalated duplicate Call Center and AI follow-up calls.",
        ],
        "engaged_internal_teams": [
            "Business Development: Rohan Shah owns commercial follow-up and renewal scope.",
            "Revenue Ops: Leena Rao owns lead-contact governance and Call Center plus AI follow-up cadence.",
            "Enterprise Sales: Ananya Rao owns CFO-level review and payment ask.",
            "Finance: Priya Menon owns invoice reconciliation support.",
            "Customer Success: Pooja Menon owns lead complaint evidence and campaign feedback.",
        ],
    },
    "Prestige Group": {
        "developer_contacts": [
            "Nidhi Menon, CTO Office, owns data-access and integration approvals.",
            "Abhishek Rao, South India Business Head, owns Q3 launch pipeline.",
            "Jiwesh Nair, Finance Controller, owns milestone payment release.",
        ],
        "engaged_internal_teams": [
            "Solutions Engineering: Meera Iyer owns architecture and integration note.",
            "Product: Karan Bedi owns product clarification and dashboard questions.",
            "Revenue Ops: Kritika Bose owns activation evidence and lead count reconciliation.",
            "Business Development: Rohan Shah owns commercial alignment.",
        ],
    },
    "Godrej Properties": {
        "developer_contacts": [
            "Jiwesh Desai, Procurement Head, owns vendor clearance.",
            "Nidhi Kapoor, Legal Counsel, owns retention and audit-trail comfort.",
            "Abhishek Jain, Business Sponsor, owns new mandate approval.",
        ],
        "engaged_internal_teams": [
            "Account Management: Devika Nair owns procurement checklist and mandate unblock.",
            "Legal: Saurabh Jain owns legal note and terms review.",
            "Compliance: Naman Khanna owns audit-trail response.",
            "Customer Success: Riya Thomas owns onboarding dependency tracking.",
        ],
    },
    "DLF": {
        "developer_contacts": [
            "Radhika Singh, CMO Office, owns campaign quality and attribution sign-off.",
            "Abhishek Bansal, Regional Sales Head, owns booking decline feedback.",
            "Nidhi Arora, Brand Lead, owns joint campaign calendar.",
        ],
        "engaged_internal_teams": [
            "Growth: Kabir Arora owns attribution snapshot.",
            "Customer Success: Pooja Menon owns lead-quality feedback.",
            "Enterprise Sales: Aarav Mehta owns revised qualification rules.",
            "Partnerships: Tanvi Desai owns joint campaign calendar.",
        ],
    },
    "Brigade Group": {
        "developer_contacts": [
            "Manav Reddy, COO Office, owns regional rollout approval.",
            "Nidhi Prakash, Bengaluru Sales Ops, owns lead disposition adoption.",
            "Abhishek Iyer, Finance Lead, owns milestone payment evidence.",
        ],
        "engaged_internal_teams": [
            "Strategic Accounts: Isha Kapoor owns COO review.",
            "Product Ops: Harsh Vyas owns adoption plan.",
            "BD Tracker: Neel Shah owns city-wise milestone evidence.",
            "Finance: Priya Menon owns collection evidence coordination.",
        ],
    },
    "Sobha Realty": {
        "developer_contacts": [
            "Sneha Rao, VP Sales, owns sales manager enablement.",
            "Jiwesh Thomas, Regional Sales Ops, owns ownership overlap resolution.",
            "Nidhi Shetty, Launch Manager, owns launch readiness feedback.",
        ],
        "engaged_internal_teams": [
            "Enterprise Sales: Aarav Mehta owns enablement pack.",
            "Revenue Ops: Leena Rao owns owner mapping.",
            "Alliances: Gaurav Sinha owns regional stakeholder coordination.",
        ],
    },
    "Hiranandani Group": {
        "developer_contacts": [
            "Arjun Hiranandani, Managing Director, owns board-level ROI review.",
            "Abhishek Shah, CFO Office, owns annual commercial closure.",
            "Nidhi Patel, Strategy Lead, owns decision-owner mapping.",
        ],
        "engaged_internal_teams": [
            "Executive Relations: Sana Qureshi owns board-ready brief.",
            "Strategic Accounts: Vikram Sethi owns decision map.",
            "Strategy: Ritika Paul owns executive narrative support.",
        ],
    },
    "Mahindra Lifespaces": {
        "developer_contacts": [
            "Kavya Nair, Sustainability Head, owns ESG reporting requirement.",
            "Abhishek Menon, Marketing Lead, owns pilot scope.",
            "Nidhi Kulkarni, Compliance Lead, owns reporting language.",
        ],
        "engaged_internal_teams": [
            "Strategy: Ritika Paul owns ESG asks.",
            "Compliance: Naman Khanna owns compliance language.",
            "Product: Mitali Shah owns pilot scope support.",
        ],
    },
    "Oberoi Realty": {
        "developer_contacts": [
            "Rahul Oberoi, Digital Head, owns integration delay escalation.",
            "Nidhi Mehra, Finance Controller, owns INR 2.4 crore payment release.",
            "Abhishek Narang, Sales Director, owns duplicate-contact complaints.",
            "Jiwesh Shah, Commercial Lead, owns credit note discussion.",
        ],
        "engaged_internal_teams": [
            "Enterprise Sales: Aman Verma owns senior escalation and commercial protection.",
            "Product: Aditi Nair owns integration checklist.",
            "Business Development: Sonal Mehra owns escalation note.",
            "Revenue Ops: Leena Rao owns lead-contact suppression rules.",
            "Finance: Priya Menon owns collection recovery support.",
        ],
    },
    "Tata Realty": {
        "developer_contacts": [
            "Pooja Sharma, Legal Counsel, owns consent and redaction approval.",
            "Nidhi Rao, Compliance Lead, owns data handling comfort.",
            "Abhishek Sinha, Finance Lead, owns collection release after legal approval.",
        ],
        "engaged_internal_teams": [
            "Legal: Saurabh Jain owns data processing note.",
            "Compliance: Naman Khanna owns compliance comments.",
            "Account Management: Rhea Dutta owns revised SOW language.",
        ],
    },
    "Embassy Group": {
        "developer_contacts": [
            "Dev Krishnan, CRO Office, owns forecast variance review.",
            "Nidhi Bhat, Sales Ops Head, owns lead fatigue and disposition issues.",
            "Abhishek Rao, Commercial Assets Lead, owns expansion discussion.",
        ],
        "engaged_internal_teams": [
            "Enterprise Sales: Aman Verma owns pipeline dashboard.",
            "Revenue Ops: Kritika Bose owns variance validation.",
            "Revenue Ops: Leena Rao owns lead suppression rules.",
            "Business Development: Rohan Shah owns expansion commercial scope.",
        ],
    },
    "Puravankara": {
        "developer_contacts": [
            "Meera Rao, Partnerships Head, owns partner influence and overlap.",
            "Jiwesh Shetty, Commercial Lead, owns conflicting partner terms.",
            "Nidhi Prabhu, Finance Lead, owns payment release after owner confirmation.",
        ],
        "engaged_internal_teams": [
            "Alliances: Nisha Menon owns partner influence map.",
            "Growth: Kabir Arora owns launch owner confirmation.",
            "Strategic Accounts: Vikram Sethi owns commercial term reconciliation.",
        ],
    },
    "Kolte-Patil Developers": {
        "developer_contacts": [
            "Samar Patil, Procurement Manager, owns vendor onboarding.",
            "Nidhi Joshi, Legal Lead, owns revised vendor terms.",
            "Abhishek Kulkarni, Launch Lead, owns launch date dependency.",
        ],
        "engaged_internal_teams": [
            "Account Management: Devika Nair owns vendor checklist.",
            "Legal: Saurabh Jain owns terms review.",
            "Customer Success: Riya Thomas owns launch dependency and escalation owner.",
        ],
    },
    "Runwal Group": {
        "developer_contacts": [
            "Tanya Shah, CPO Office, owns adoption and training sign-off.",
            "Nidhi Shah, HR Ops Lead, owns training attendance.",
            "Abhishek Mehta, Finance Lead, owns payment after sign-off.",
        ],
        "engaged_internal_teams": [
            "Product: Mitali Shah owns training plan.",
            "Customer Success: Pooja Menon owns adoption feedback.",
            "Product Ops: Harsh Vyas owns rollout governance.",
        ],
    },
    "Kalpataru Group": {
        "developer_contacts": [
            "Vikrant Mehta, Founder Office, owns relationship continuity.",
            "Nidhi Shah, Strategy Lead, owns leadership transition context.",
            "Abhishek Rao, Finance Lead, owns approval-linked payment release.",
        ],
        "engaged_internal_teams": [
            "Executive Relations: Sana Qureshi owns founder narrative.",
            "Strategic Accounts: Vikram Sethi owns transition context.",
            "Strategy: Ritika Paul owns leadership briefing.",
        ],
    },
}


def _apply_contact_showcase_updates() -> None:
    for account_name, update in CONTACT_SHOWCASE_UPDATES.items():
        account_brief = ACCOUNT_BRIEFS_BY_DEVELOPER.get(account_name)
        if account_brief:
            account_brief.update(update)


REFERENCE_SHOWCASE_UPDATES: dict[str, list[str]] = {
    "Lodha Group": [
        "2026-06-14: Leena Rao, Head of Revenue Ops, Anarock Digital, Mumbai, met Rohit Kulkarni, Site Sales Head, Lodha Group, on Teams about duplicate Call Center and AI follow-up calls. Useful reference for lead-contact governance.",
        "2026-06-12: Rohan Shah, Business Development Lead, Mumbai, emailed Abhishek Lodha, CFO Office, Lodha Group, about INR 1.8 crore invoice reconciliation. Useful reference for collections escalation.",
        "2026-06-07: Ananya Rao, Enterprise Sales Director, Mumbai, met Abhishek Lodha, CFO Office, Lodha Group, on Teams about renewal scope and CFO-level review. Useful reference for senior outreach.",
        "2026-06-05: Kabir Arora, VP Growth, Anarock Digital, Mumbai, met Jiwesh Mehta, Digital Marketing Lead, Lodha Group, about campaign performance and booking decline.",
    ],
    "Prestige Group": [
        "2026-06-13: Kritika Bose, RevOps Director, Bengaluru, updated Abhishek Rao, South India Business Head, Prestige Group, through BD Tracker on dashboard reconciliation. Useful reference for Q3 launch scope.",
        "2026-06-07: Meera Iyer, Solutions Engineering Head, Anarock Digital, Bengaluru, met Nidhi Menon, CTO Office, Prestige Group, on Teams about integration and data-access approvals.",
        "2026-06-06: Rohan Shah, Business Development Lead, Bengaluru, spoke with Jiwesh Nair, Finance Controller, Prestige Group, about activation milestone evidence.",
    ],
    "Godrej Properties": [
        "2026-06-14: Naman Khanna, Compliance Lead, Mumbai, emailed Jiwesh Desai, Procurement Head, Godrej Properties, about audit-trail and retention answers. Useful reference for procurement unblock.",
        "2026-06-07: Devika Nair, Account Management Lead, Mumbai, met Abhishek Jain, Business Sponsor, Godrej Properties, on Teams about the new mandate window.",
        "2026-06-06: Saurabh Jain, Legal Counsel, Mumbai, spoke with Nidhi Kapoor, Legal Counsel, Godrej Properties, about revised vendor terms.",
    ],
    "DLF": [
        "2026-06-12: Pooja Menon, Customer Success Head, NCR, met Abhishek Bansal, Regional Sales Head, DLF, about lead-quality complaints and duplicate follow-up examples.",
        "2026-06-07: Kabir Arora, VP Growth, Anarock Digital, NCR, met Radhika Singh, CMO Office, DLF, about campaign attribution and lead quality.",
        "2026-06-05: Tanvi Desai, Partnerships Lead, NCR, spoke with Nidhi Arora, Brand Lead, DLF, about joint campaign calendar.",
    ],
    "Brigade Group": [
        "2026-06-11: Isha Kapoor, Strategic Accounts Director, Bengaluru, met Manav Reddy, COO Office, Brigade Group, about city-wise rollout adoption. Useful reference for COO-level review.",
        "2026-06-09: Harsh Vyas, Product Ops Head, Bengaluru, met Nidhi Prakash, Bengaluru Sales Ops, Brigade Group, about lead disposition workflow.",
        "2026-06-06: Neel Shah, BD Tracker Owner, Bengaluru, spoke with Abhishek Iyer, Finance Lead, Brigade Group, about milestone evidence.",
    ],
    "Oberoi Realty": [
        "2026-06-15: Aman Verma, Enterprise Sales Director, Mumbai, met Rahul Oberoi, Digital Head, Oberoi Realty, on Teams about integration delay, duplicate follow-ups, and INR 2.4 crore blocked collections. Strongest recent reference.",
        "2026-06-14: Aditi Nair, Product Director, Anarock Digital, Mumbai, met Rahul Oberoi, Digital Head, Oberoi Realty, about the integration checklist and revised delivery date.",
        "2026-06-13: Sonal Mehra, Business Development Lead, Mumbai, spoke with Nidhi Mehra, Finance Controller, Oberoi Realty, about payment release conditions.",
        "2026-06-12: Leena Rao, Head of Revenue Ops, Mumbai, met Abhishek Narang, Sales Director, Oberoi Realty, about no-duplicate-contact rules for high-intent leads.",
    ],
    "Tata Realty": [
        "2026-06-10: Saurabh Jain, Legal Counsel, Mumbai, met Pooja Sharma, Legal Counsel, Tata Realty, about consent and redaction controls.",
        "2026-06-09: Naman Khanna, Compliance Lead, Mumbai, spoke with Nidhi Rao, Compliance Lead, Tata Realty, about data handling comfort.",
        "2026-06-06: Rhea Dutta, Account Management Lead, Mumbai, emailed Abhishek Sinha, Finance Lead, Tata Realty, about collection release after legal approval.",
    ],
    "Embassy Group": [
        "2026-06-13: Leena Rao, Head of Revenue Ops, Bengaluru, met Nidhi Bhat, Sales Ops Head, Embassy Group, through BD Tracker follow-up on lead fatigue and suppression rules.",
        "2026-06-12: Aman Verma, Enterprise Sales Director, Bengaluru, met Abhishek Rao, Commercial Assets Lead, Embassy Group, about expansion into two commercial assets.",
        "2026-06-10: Kritika Bose, RevOps Director, Bengaluru, met Dev Krishnan, CRO Office, Embassy Group, about forecast variance validation.",
    ],
    "Puravankara": [
        "2026-06-10: Nisha Menon, Alliances Director, Bengaluru, met Meera Rao, Partnerships Head, Puravankara, about partner influence and duplicate outreach risk.",
        "2026-06-08: Kabir Arora, VP Growth, Bengaluru, spoke with Nidhi Prabhu, Finance Lead, Puravankara, about owner confirmation before payment release.",
        "2026-06-07: Vikram Sethi, Strategic Accounts Lead, Bengaluru, met Jiwesh Shetty, Commercial Lead, Puravankara, about conflicting partner terms.",
    ],
    "Kolte-Patil Developers": [
        "2026-06-12: Riya Thomas, Customer Success Head, Pune, met Abhishek Kulkarni, Launch Lead, Kolte-Patil Developers, about launch dependency and procurement risk.",
        "2026-06-11: Devika Nair, Account Management Lead, Pune, met Samar Patil, Procurement Manager, Kolte-Patil Developers, about revised vendor checklist.",
        "2026-06-09: Saurabh Jain, Legal Counsel, Pune, spoke with Nidhi Joshi, Legal Lead, Kolte-Patil Developers, about revised vendor terms.",
    ],
    "Runwal Group": [
        "2026-06-08: Mitali Shah, Product Lead, Mumbai, met Tanya Shah, CPO Office, Runwal Group, about adoption and training sign-off.",
        "2026-06-07: Pooja Menon, Customer Success Head, Mumbai, spoke with Nidhi Shah, HR Ops Lead, Runwal Group, about training attendance.",
        "2026-06-05: Harsh Vyas, Product Ops Head, Mumbai, emailed Abhishek Mehta, Finance Lead, Runwal Group, about payment after sign-off.",
    ],
    "Kalpataru Group": [
        "2026-06-09: Sana Qureshi, Executive Relations Director, Mumbai, met Vikrant Mehta, Founder Office, Kalpataru Group, about leadership transition and founder narrative.",
        "2026-06-07: Vikram Sethi, Strategic Accounts Lead, Mumbai, met Nidhi Shah, Strategy Lead, Kalpataru Group, about transition context.",
        "2026-06-05: Ritika Paul, Consulting Director, Mumbai, spoke with Abhishek Rao, Finance Lead, Kalpataru Group, about approval-linked payment release.",
    ],
}


def _apply_reference_showcase_updates() -> None:
    for account_name, references in REFERENCE_SHOWCASE_UPDATES.items():
        account_brief = ACCOUNT_BRIEFS_BY_DEVELOPER.get(account_name)
        if account_brief:
            account_brief["recent_reference_contacts"] = references


def _replace_builder_names(value: Any) -> Any:
    if isinstance(value, str):
        replaced = value
        for original, builder in {**BUILDER_COMPANY_RENAMES, **BUILDER_ACCOUNT_RENAMES}.items():
            replaced = re.sub(rf"\b{re.escape(original)}\b", builder, replaced)
        for original, rewrite in ACCOUNT_PHRASE_REWRITES.items():
            replaced = replaced.replace(original, rewrite)
        return replaced

    if isinstance(value, list):
        return [_replace_builder_names(item) for item in value]

    if isinstance(value, dict):
        return {key: _replace_builder_names(item) for key, item in value.items()}

    return value


DUMMY_RELATIONSHIP_DATA = _replace_builder_names(DUMMY_RELATIONSHIP_DATA)
_apply_escalation_showcase_updates()
_apply_contact_showcase_updates()
_apply_reference_showcase_updates()


def _tokens(text: str) -> set[str]:
    return {
        token.strip(".,!?;:()[]{}\"'").lower()
        for token in text.split()
        if len(token.strip(".,!?;:()[]{}\"'")) > 2
    }


CONTACT_QUERY_TOKENS = {
    "contact",
    "contacts",
    "reference",
    "references",
    "referencing",
    "met",
    "meeting",
    "interacted",
    "interaction",
    "recent",
    "recently",
    "who",
    "team",
    "teams",
    "engaged",
    "city",
    "cities",
    "vertical",
    "verticals",
    "digital",
    "consulting",
}

HEALTH_QUERY_TOKENS = {
    "health",
    "status",
    "escalation",
    "escalations",
    "collection",
    "collections",
    "pending",
    "overdue",
    "risk",
    "risks",
    "red",
    "amber",
    "action",
    "actions",
    "actionable",
    "blocker",
    "blockers",
    "booking",
    "bookings",
}


def _query_mode(query: str) -> str:
    query_tokens = _tokens(query)
    has_contact_intent = bool(query_tokens & CONTACT_QUERY_TOKENS)
    has_health_intent = bool(query_tokens & HEALTH_QUERY_TOKENS)

    if has_contact_intent and has_health_intent:
        return "mixed"
    if has_contact_intent:
        return "contact_reference"
    if has_health_intent:
        return "health_check"
    return "general"


def _stakeholder_text(record: dict[str, Any]) -> str:
    stakeholder = record["stakeholder"]
    account_brief = ACCOUNT_BRIEFS_BY_DEVELOPER.get(stakeholder["name"], {})
    interaction_text = " ".join(
        " ".join(str(value) for value in interaction.values())
        for interaction in record["interactions"]
    )
    account_text = " ".join(
        [
            str(account_brief.get("executive_status", "")),
            " ".join(account_brief.get("escalations", [])),
            str(account_brief.get("pending_collections", "")),
            " ".join(account_brief.get("ongoing_conversations", [])),
            " ".join(account_brief.get("developer_contacts", [])),
            " ".join(account_brief.get("engaged_internal_teams", [])),
            " ".join(account_brief.get("recent_reference_contacts", [])),
            str(account_brief.get("management_focus", "")),
            " ".join(account_brief.get("next_actions", [])),
        ]
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
    return f"{profile_text} {account_text} {interaction_text}"


def _select_records(request: RelationshipQueryInput) -> list[dict[str, Any]]:
    query_tokens = _tokens(f"{request.query} {request.stakeholder_name or ''}")
    showcase_tokens = HEALTH_QUERY_TOKENS | CONTACT_QUERY_TOKENS | {
        "developer",
        "developers",
        "touchpoint",
        "touchpoints",
        "owner",
        "owners",
        "person",
        "people",
        "accounts",
        "lead",
        "leads",
    }
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
        return []

    record_limit = 6 if query_tokens & showcase_tokens and not request.stakeholder_name else 2
    return [record for score, record in scored_records if score > 0][:record_limit]


def _interaction_score(interaction: dict[str, str], query_tokens: set[str]) -> int:
    interaction_tokens = _tokens(" ".join(interaction.values()))
    return len(query_tokens & interaction_tokens)


def _build_context(request: RelationshipQueryInput, mode: str) -> tuple[str, list[str], list[RelationshipSource]]:
    records = _select_records(request)
    query_tokens = _tokens(request.query)
    context_blocks: list[str] = []
    stakeholders: list[str] = []
    sources: list[RelationshipSource] = []

    for record in records:
        stakeholder = record["stakeholder"]
        account_brief = ACCOUNT_BRIEFS_BY_DEVELOPER.get(stakeholder["name"], {})
        stakeholders.append(f"{stakeholder['name']} ({stakeholder['title']}, {stakeholder['company']})")

        interactions = sorted(
            record["interactions"],
            key=lambda item: (item["date"], _interaction_score(item, query_tokens)),
            reverse=True,
        )[: request.max_interactions]

        source_counter = Counter(interaction["source"] for interaction in interactions)
        if mode == "contact_reference":
            context_lines = [
                f"Developer account: {stakeholder['name']}",
                f"Developer-side contacts: {'; '.join(account_brief.get('developer_contacts', [])) or 'Not available'}",
                f"Anarock references and teams engaged: {'; '.join(account_brief.get('engaged_internal_teams', [])) or 'Not available'}",
                f"Recent Anarock reference meetings: {'; '.join(account_brief.get('recent_reference_contacts', [])) or 'Not available'}",
                f"Available source mix: {dict(source_counter)}",
            ]
        elif mode == "health_check":
            context_lines = [
                f"Developer account: {stakeholder['name']}",
                f"Executive status: {account_brief.get('executive_status', 'Not available')}",
                f"Pending escalations: {'; '.join(account_brief.get('escalations', [])) or 'None recorded'}",
                f"Pending collections: {account_brief.get('pending_collections', 'Not available')}",
                f"Actionable items: {'; '.join(account_brief.get('next_actions', [])) or 'Not available'}",
                f"Management focus: {account_brief.get('management_focus', 'Not available')}",
                f"Available source mix: {dict(source_counter)}",
            ]
        else:
            context_lines = [
                f"Developer account: {stakeholder['name']}",
                f"Executive status: {account_brief.get('executive_status', 'Not available')}",
                f"Pending escalations: {'; '.join(account_brief.get('escalations', [])) or 'None recorded'}",
                f"Pending collections: {account_brief.get('pending_collections', 'Not available')}",
                f"Actionable items: {'; '.join(account_brief.get('next_actions', [])) or 'Not available'}",
            ]

        context_blocks.append("\n".join(context_lines))

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
            if mode == "contact_reference":
                context_blocks.append(
                    "\n".join(
                        [
                            f"Reference interaction date: {interaction['date']}",
                            f"Source: {interaction['source']}",
                            f"Anarock employee/reference: {interaction['colleague']}",
                            f"Contact/reference summary: {interaction['summary']}",
                        ]
                    )
                )
            elif mode == "health_check":
                context_blocks.append(
                    "\n".join(
                        [
                            f"Health-check source date: {interaction['date']}",
                            f"Source: {interaction['source']}",
                            f"Owner: {interaction['colleague']}",
                            f"Escalation/collection/action summary: {interaction['summary']}",
                            f"Key decisions: {interaction['decisions']}",
                            f"Commitments/action items: {interaction['commitments']}",
                            f"Outcome/risk: {interaction['outcome']}",
                        ]
                    )
                )

    return "\n\n---\n\n".join(context_blocks), stakeholders, sources


def _build_prompt(query: str, context: str, mode: str, today: date | None = None) -> str:
    current_date = (today or date.today()).isoformat()
    return f"""You are AnarockOne, an executive account intelligence assistant for senior management.
Answer the user's question using only the dummy account context below.

Rules:
- Do not invent developers, meetings, emails, escalations, collections, commitments, or outcomes.
- If the context does not contain enough evidence, say what is missing.
- If the user only greets or asks a non-account question, do not pick any developer account. Briefly greet the user and ask what account, escalation, collection, or conversation they want to review.
- Current answer mode: {mode}.
- There are only two business question types. Do not merge them in one answer.
- Contact/reference mode: only give developer-side contacts, Anarock references, internal teams/verticals/cities, and who recently met top developer officials. Do not include executive status, pending escalations, collections, commercial blockers, or action items.
- Health-check mode: only give pending escalations, pending collections, risks/blockers, management focus, and actionable items. Do not include developer-side contact lists, Anarock references, teams engaged, or who met whom.
- Mixed mode: if the user asks both contact/reference and health-check in the same query, politely ask them to run one query for contacts/references and one query for health check. Do not answer both.
- For contact/reference mode, include Anarock employee name, vertical/team, city, developer official met, meeting date, meeting channel when available, and why that employee is a useful reference. Sort recent meetings by most recent first.
- Do not lead with relationship score, relationship strength, warm introductions, stakeholder preferences, or generic relationship history unless the user explicitly asks for them.
- For health-check mode, use short sections such as Pending Escalations, Collections, Risks, and Actionable Items.
- For contact/reference mode, use short sections such as Developer Contacts, Anarock References, and Recent Meetings.
- Keep the answer concise and useful for upper management reviewing developer accounts.
- Return only valid JSON with this shape:
  {{"answer":"markdown answer text","follow_up_questions":["question 1","question 2","question 3"]}}
- The follow_up_questions must be generated from the same dummy account context and should help upper management continue the review.
- The current user is Anuj Puri. Write follow_up_questions directly to the user using "I" or neutral phrasing; do not ask "What should Anuj Puri..." or refer to Anuj in third person.
- follow_up_questions are clickable suggested queries that the user can run directly. Phrase them as user intents or commands, not as the assistant asking the user a question.
- In contact/reference mode, follow_up_questions must stay contact/reference-only.
- In health-check mode, follow_up_questions must stay health-check-only.
- Good contact/reference follow_up_questions examples: "Show recent Anarock references for this account", "List internal teams engaged with this developer".
- Good health-check follow_up_questions examples: "Show accounts with open escalations", "Summarize pending collections by account".
- Bad follow_up_questions examples: "Which account would you like to discuss?", "Do you have any collections in mind?", "Can you tell me which escalation?".
- Do not wrap the JSON in markdown fences.
- Today is {current_date}.

Dummy account context:
{context or "No matching dummy relationship records were found."}

User question:
{query}
"""


def _parse_llm_json_response(raw_output: str) -> tuple[str, list[str]]:
    cleaned_output = raw_output.strip()
    if cleaned_output.startswith("```"):
        cleaned_output = re.sub(r"^```(?:json)?\s*", "", cleaned_output)
        cleaned_output = re.sub(r"\s*```$", "", cleaned_output)

    try:
        payload = json.loads(cleaned_output)
    except json.JSONDecodeError:
        return raw_output.strip(), []

    answer = str(payload.get("answer") or "").strip()
    raw_follow_ups = payload.get("follow_up_questions") or []
    follow_up_questions = [
        str(question).strip()
        for question in raw_follow_ups
        if str(question).strip()
    ][:3]

    return answer or raw_output.strip(), follow_up_questions


def answer_relationship_query(
    body: RelationshipQueryInput | dict[str, Any],
) -> RelationshipQueryOutput:
    request = body if isinstance(body, RelationshipQueryInput) else RelationshipQueryInput(**body)
    mode = _query_mode(request.query)
    records = _select_records(request)
    context, stakeholders, sources = _build_context(request, mode)
    prompt = _build_prompt(request.query.strip(), context, mode)
    response = _get_openai_llm().invoke(prompt)
    raw_answer = _content_to_text(getattr(response, "content", response)).strip()
    answer, follow_up_questions = _parse_llm_json_response(raw_answer)

    return RelationshipQueryOutput(
        query=request.query.strip(),
        answer=answer,
        stakeholders=stakeholders,
        sources=sources,
        follow_up_questions=follow_up_questions,
    )
