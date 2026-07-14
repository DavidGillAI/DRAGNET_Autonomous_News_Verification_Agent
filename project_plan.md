## Project Title

# DRAGNET: Autonomous News Research & Verification Agent

**Digital Research Agent Gathering News Evidence Transparently**

*Just the facts, ma’am.*

This document is the build plan for the main DRAGNET project and should be used as the reference point for scope, technical decisions and MVP boundaries.

## 1. Use Case

### Use Case Description

This project will create an autonomous news research agent that investigates a current news story across multiple sources, compares and contrasts the available reporting, identifies framing, opinion, speculation and unsupported claims, and returns a fact-focused summary with sources.

The system will not begin with pre-assigned political labels or assumptions about a publication's bias. Every article will be assessed using the same criteria, regardless of the publication.

The intended workflow is simple:

**Query in → autonomous research and verification → report out**

### Problem Statement

News coverage is often shaped by the political outlook, editorial stance and personal interpretation of the publication or journalist. This makes it difficult for readers to distinguish verified facts from framing, emphasis and opinion.

The agent will compare reporting from multiple sources, identify points of agreement and contradiction, and separate well-supported facts from commentary, speculation or unsupported claims.

### Target Users

The target users are:

- members of the general public who want to stay informed without being steered by a publication's political or editorial position;
- sceptical readers who want to test contested claims against stronger evidence;
- journalists and researchers who need a quick, structured comparison of sources before developing or publishing their own coverage.

### Current Manual Process

A person would currently need to:

- find and read coverage from multiple sources;
- identify exaggerated, dismissive, minimising or emotionally loaded language;
- compare how each publication presents the same events;
- identify duplicated, syndicated or paraphrased reporting;
- separate directly supported facts from speculation and interpretation;
- research unsupported claims independently;
- compare contradictory evidence;
- reach a cautious overall understanding of the story.

### Success Criteria

The agent is successful when it:

- accepts a clearly defined news story or query;
- researches the story across multiple relevant and independent sources;
- compares and contrasts the coverage;
- removes duplicated or irrelevant information;
- separates verified facts from opinion, speculation and framing;
- cites the sources used in the final summary;
- clearly identifies uncertainty and unresolved claims;
- completes the workflow without human intervention;
- returns a final report within a maximum of 10 research iterations.

A report may still be successful when no definitive conclusion can be reached, provided the agent clearly explains why the evidence remains inconclusive.

---

## 2. Technology Stack

### Core LLM

**OpenAI**

OpenAI will be used as the core language model because access is already available through Ironhack, it has been used successfully in previous labs, and it integrates well with LangChain, LangGraph and n8n.

### Agent Framework

**LangGraph** will be used as the main workflow engine.

It is suitable because the agent requires:

- structured stages;
- shared state;
- conditional routing;
- repeated research loops;
- a stopping rule;
- error handling;
- self-review before final output.

**LangChain** will support:

- model calls;
- prompt handling;
- tool integration;
- document retrieval.

### RAG Components

**Pinecone** will be used as the vector database.

Pinecone will not search live news. It will store a small reference collection containing:

- source-evaluation criteria;
- fact-checking rules;
- media-framing concepts;
- guidance for distinguishing fact, opinion and speculation;
- known satire and parody sources;
- the report structure;
- the agent's verification checklist.

OpenAI embeddings will be used to store and retrieve this reference material.

### Orchestration

**n8n** will be used to:

- receive the user's query;
- trigger the autonomous agent;
- manage the workflow;
- handle failures and retries;
- return the completed report.

The normal user experience should not require manually running PowerShell commands.

### User Interface

A **Telegram bot** will be used for:

- submitting a news story or query;
- receiving clarification options when the query is ambiguous;
- receiving the final report.

### External Tools and Integrations

The initial toolset will include:

1. **News-search API**
   - Finds current coverage from a range of publications.

2. **General web-search API**
   - Finds additional reporting, specific publications, primary documents and official statements.

3. **Official-source or fact-checking search tool**
   - Helps verify important factual claims.

The final API choices will depend on:

- free-tier availability;
- source coverage;
- rate limits;
- ease of integration;
- access to article URLs and publication dates.

### Why These Technologies Were Chosen

The selected stack matches the needs of the project:

- OpenAI provides the reasoning and language capabilities.
- LangGraph manages the iterative autonomous workflow.
- LangChain supports tools and retrieval.
- Pinecone stores reusable verification guidance.
- n8n handles orchestration and delivery.
- Telegram provides a simple query-in, report-out interface.
- News and web-search APIs provide current external information.

### Alternatives Considered

- **Simple LangChain agent:** rejected because the project requires structured loops, state and conditional stopping.
- **Streamlit or other external UI** excluded from the MVP because it would require deployment.
- **LLM knowledge only:** unsuitable because the project focuses on trending and current stories.
- **Using Pinecone for live news search:** unsuitable because Pinecone is for stored reference material, not current web retrieval.
- **Pre-labelled left/right source lists:** rejected because every article should be assessed using the same neutral criteria.

---

## 3. MVP Scope

### Must-Have Features

The MVP must:

- accept one news story or query at a time;
- identify the intended story automatically when the query is clear;
- return a short list of possible stories when the query is ambiguous;
- search for up to 10 suitable and genuinely independent sources;
- continue with fewer than 10 sources when sufficient strong evidence is available;
- detect duplicated, syndicated and paraphrased reporting;
- treat repeated coverage from one original source as one evidence chain;
- apply the same analysis criteria to every article;
- identify factual claims, evidence, framing, opinion and speculation;
- independently research uncited factual claims;
- prioritise evidence quality over source quantity;
- generate a draft summary;
- review the draft against the verification criteria;
- research further and rewrite when the draft fails;
- complete at least 3 and no more than 10 iterations;
- perform a final recency check;
- return a fact-focused report with sources;
- return an inconclusive report when evidence is insufficient.

### Source Rules

#### Neutral Article Assessment

The agent will not assume that a publication is left-wing, right-wing or centrist before analysing it.

Every article will be assessed using the same criteria:

- factual claims;
- direct evidence;
- identifiable sources;
- emotionally loaded language;
- speculation;
- unsupported conclusions;
- omissions;
- corrections or updates.

#### Source Weighting

Sources will not be treated equally.

Greater weight will be given to:

- direct evidence;
- primary documents;
- independently verifiable records;
- well-supported reporting;
- multiple independent confirmations.

However, primary or official sources will not be treated as automatically neutral or truthful.

A company, government, police force, campaign group or other interested organisation may have a reason to minimise, exaggerate or frame events in its own favour.

The agent must distinguish between:

- what an organisation claims;
- what can be independently verified;
- what remains disputed.

#### Duplicate Coverage

Duplicated, syndicated, paraphrased or cited articles will be logged internally but treated as one piece of evidence when they rely on the same original source.

#### Anonymous Sources

Anonymous sources may be used when directly relevant, such as whistleblower cases or situations where identification could create risk.

Anonymous claims must:

- be clearly labelled;
- be treated cautiously;
- be checked for corroboration;
- not be presented as established fact without supporting evidence.

If stronger evidence contradicts the anonymous claim, that conflict must be stated.

#### Satire, Parody and Opinion

Clearly labelled satire and parody will be excluded.

A reference list of known satirical publications will be supplied to the agent.

Opinion pieces may be consulted when they:

- contain relevant factual claims;
- cite or link to original evidence.

The agent should follow the citation and use the original source in the final report rather than the opinion article.

Unsupported opinion will not be used as factual evidence.

#### Unsupported Claims

When a source makes a factual claim without citing evidence, the agent will research the claim independently.

If corroborated, the stronger original or supporting source will be cited.

If the claim cannot be verified, it will not be included as fact.

#### Social Media

The MVP may use relevant text-based social media posts only from identifiable and directly relevant accounts, such as:

- official organisations;
- public authorities;
- verified individuals involved in the story;
- recognised journalists with first-hand reporting;
- recognised subject-matter experts.

Fan accounts, parody accounts, anonymous reposting pages, unofficial channels and unrelated commentary will be excluded.

Social media posts will be treated as claims to verify, not automatically as facts.

### Research Iteration and Stopping Rules

The agent will complete:

- a minimum of 3 research iterations;
- a maximum of 10 research iterations.

It may stop before the tenth iteration only when:

- the key claims are supported by multiple independent sources;
- major contradictions have been resolved or clearly explained;
- source quality is sufficient;
- the summary passes the verification checks;
- a final search confirms that no important newer update has appeared.

If the evidence remains incomplete after 10 iterations, the agent will return an inconclusive report.

### Final Report Requirements

The final report will include:

1. **Fact-focused summary**
2. **Bullet-pointed timeline**, where dates are important
3. **Disputed or unresolved claims**
4. **Confidence score**
5. **Research iterations completed**
6. **Major limitations**
7. **What would clarify the story**, when relevant
8. **Source list with links**

The report will distinguish between:

- confirmed claims;
- strongly supported claims;
- disputed claims;
- unsupported claims;
- disproven claims;
- unresolved claims.

When no evidence is found, the report should say:

> No supporting evidence was found during this investigation.

It must not automatically say that the claim is false.

### Confidence Score

The report will include a confidence score from 0% to 100%.

The score will reflect:

- source quality;
- source independence;
- access to primary evidence;
- level of corroboration;
- unresolved contradictions;
- failed tools or inaccessible sources;
- the proportion of claims that could be verified.

The percentage is a confidence estimate, not a scientific probability.

The report must briefly explain the score.

### Source List

Only sources that directly support, corroborate, contradict or materially inform the final summary will appear in the user-facing source list.

Each source should include, where possible:

- publication name;
- article title;
- publication date;
- access date;
- clickable link;
- a short note explaining what the source supports or contradicts.

Older sources must be clearly identified as older and potentially less relevant to the current state of the story.

Corrections and retractions must be reflected in the summary and timeline, with a footnote beside the relevant source.

### Corrected Articles

A corrected article may still be used when the amended version is reliable and the correction is clearly disclosed.

Publishing a correction may strengthen confidence because it demonstrates transparency and a willingness to amend inaccurate information.

The corrected version will be used, not the superseded claim.

### Publication Track Record

Each article will be judged primarily on its own evidence and sourcing.

A publication's wider correction or retraction history may be used as a secondary reliability factor, but it will not automatically disqualify a well-supported article.

### Included in the MVP

- English-language sources;
- text-based news articles;
- selected relevant social media posts;
- one investigation at a time;
- current web research;
- iterative self-review;
- Telegram input and output;
- n8n orchestration;
- Pinecone reference retrieval;
- up to 10 research iterations;
- transparent source-backed reporting.

### Excluded from the MVP

- multilingual research;
- video analysis;
- podcast or audio analysis;
- permanent memory of previous queries;
- dashboards;
- real-time monitoring;
- mobile applications;
- a separately deployed Streamlit interface or other UI;
- automatic political labelling of publications;
- detailed display of the agent's internal reasoning;
- analysing every possible source on the internet.


## Dependencies and Budget Considerations

The project depends on access to OpenAI, Pinecone, n8n, Telegram and suitable news or web-search APIs. API authentication, rate limits and free-tier restrictions may affect development and testing.

Free-tier services will be used wherever possible. Any paid API will only be considered if no suitable free alternative exists, and expected costs will be documented before use. The main technical dependency is completing and testing the core Python agent before beginning the n8n and Telegram integrations.


### Future Enhancements

Possible later features include:

- multilingual research;
- persistent query history;
- saved reports;
- reuse of previous research;
- video and audio analysis;
- broader social media analysis;
- real-time monitoring;
- dashboards;
- user accounts;
- custom publication preferences.

---



## 4. Risk Assessment

### Risk 1: Hallucination

- **Probability:** Medium
- **Impact:** High

**Description:**  
The model may invent claims, sources, citations or links.

**Mitigation:**

- require every factual claim to be traceable to a retrieved source;
- prohibit invented citations;
- validate links before including them;
- run a final verification stage;
- return an inconclusive report when evidence cannot be verified.

### Risk 2: Misclassification

- **Probability:** Medium
- **Impact:** High

**Description:**  
The agent may incorrectly classify opinion, speculation, satire or interpretation as factual reporting.

**Mitigation:**

- apply the same structured criteria to every source;
- check page labels, author information and article type;
- compare claims across multiple independent sources;
- separate fact, opinion, speculation and uncertainty;
- use the Pinecone reference material as a verification guide.

### Risk 3: Poor-Quality Sources

- **Probability:** Medium
- **Impact:** High

**Description:**  
The agent may retrieve unreliable, low-quality or misleading material.

**Mitigation:**

- prioritise identifiable and reputable sources;
- assess evidence quality rather than publication reputation alone;
- exclude anonymous reposting pages and unofficial channels;
- corroborate important claims;
- reject unsupported claims from the final factual summary.

### Risk 4: Paywalls and Inaccessible Sources

- **Probability:** High
- **Impact:** Medium

**Description:**  
Important reporting may be inaccessible.

**Mitigation:**

- search for alternative coverage;
- use syndicated versions where legitimate;
- look for official documents or primary evidence;
- state the limitation in the final report;
- avoid pretending inaccessible material was fully reviewed.

### Risk 5: API Limits and Failures

- **Probability:** Medium
- **Impact:** Medium

**Description:**  
An API may fail, return incomplete results or reach its request limit.

**Mitigation:**

- log the failed API or tool;
- continue with remaining tools where possible;
- retry temporary failures;
- include the limitation in the final report;
- return an inconclusive report when too many critical tools fail.

### Risk 6: Duplicate or Syndicated Reporting

- **Probability:** High
- **Impact:** High

**Description:**  
Multiple articles may repeat the same original report, creating false confirmation.

**Mitigation:**

- detect copied, syndicated or paraphrased material;
- trace claims to the earliest available source;
- treat repeated reporting from one origin as one evidence chain;
- log duplicates internally.

### Risk 7: Contradictory Sources

- **Probability:** Medium
- **Impact:** High

**Description:**  
Independent sources may directly contradict each other.

**Mitigation:**

- compare the quality of evidence;
- prioritise direct and verifiable evidence;
- consider the wider independent consensus;
- clearly identify conflicting claims;
- state when the conclusion is based on the weight of evidence rather than certainty.

### Risk 8: User Distrust

- **Probability:** Medium
- **Impact:** High

**Description:**  
Repeated inaccuracies may cause users to stop trusting the agent.

**Mitigation:**

- provide links;
- signpost uncertainty;
- explain confidence scores;
- disclose failed tools and limitations;
- never force a conclusion;
- keep the report transparent.

### Risk 9: Insufficient Evidence

- **Probability:** Medium
- **Impact:** Medium

**Description:**  
Some stories may remain unresolved despite extensive searching.

**Mitigation:**

- permit an inconclusive outcome;
- explain why the evidence is insufficient;
- identify what evidence would clarify the story;
- do not present speculation as truth.

### Risk 10: Scope Creep

- **Probability:** Low
- **Impact:** Medium

**Description:**  
Additional features may be added before the core workflow works.

**Mitigation:**

- keep the agreed MVP boundaries fixed;
- defer multilingual support, multimedia, dashboards and persistent memory;
- complete the core autonomous workflow before considering enhancements.

---

## 5. Implementation Plan

### Phase 1: Setup and Research Preparation

Phase 1 will establish the project foundation.

Tasks:

- create the project folder;
- initialise Git and GitHub;
- create the Python environment;
- install required packages;
- create a secure `.env` file;
- identify suitable news, web-search and verification APIs;
- compare API coverage, limits and costs;
- test each API independently;
- define the source-selection rules;
- define the evidence-evaluation rules;
- prepare the Pinecone reference collection;
- create the Pinecone index;
- test retrieval quality;
- define the user input format;
- define the final report structure.

### Phase 2: Core Agent Development

The first working agent will:

- accept one clearly defined news query;
- search for up to 10 suitable independent sources;
- avoid relying only on the first search results;
- detect duplicated and syndicated coverage;
- extract factual claims;
- compare evidence across sources;
- identify framing and unsupported material;
- produce a first fact-focused summary;
- include source links.

### Phase 3: Autonomous Review and Iteration

The agent will:

- read its draft summary;
- check every factual claim against the evidence;
- check that duplicated coverage is not treated as independent;
- check that opinion, speculation and loaded language have been removed;
- check that contradictions are acknowledged;
- check that the source list supports the report;
- check that no unsupported information has been introduced;
- search for additional evidence when a check fails;
- rewrite the summary;
- repeat until the criteria are met or 10 iterations are reached;
- perform a final recency search;
- return an inconclusive result when necessary.

### Phase 4: n8n and Telegram Integration

The completed agent will be connected to n8n and Telegram.

The workflow will:

- receive the user's message through Telegram;
- identify whether the story is clear;
- ask the user to choose when several stories match;
- trigger the Python agent;
- manage errors and retries;
- receive the finished report;
- return the report to the same Telegram chat.

Testing will include:

- clear queries;
- vague queries;
- failed API calls;
- paywalled sources;
- duplicated coverage;
- contradictory evidence;
- inconclusive investigations;
- source links;
- long Telegram messages;
- report delivery failures.

---

## 6. Timeline

The project officially begins on **Tuesday, 14 July 2026** and must be ready for submission by **Saturday, 1 August 2026**.

The submission day will not be counted as working time.

Approximately 32 scheduled class hours are available before the deadline:

- Tuesdays: 3 hours;
- Thursdays: 3 hours;
- Saturdays: approximately 7 hours, including lunch.

Additional work may be completed outside class if necessary.

### 14 to 18 July: Phase 1

- repository and environment setup;
- API research;
- source and evidence rules;
- Pinecone reference preparation;
- report and input design.

### 21 to 25 July: Phases 2 and 3

- core research agent;
- source collection;
- deduplication;
- claim extraction;
- evidence comparison;
- draft summary generation;
- iterative review loop;
- stopping rules.

### 28 to 30 July: Phase 4 and Finalisation

- n8n integration;
- Telegram integration;
- end-to-end testing;
- error handling;
- sample reports;
- README;
- project plan;
- workflow documentation;
- final presentation or demonstration materials.

Telegram integration will only be attempted after the core agent is working.

---

## 7. Resources Needed

The project will require:

- OpenAI API access;
- Pinecone account and index;
- n8n access;
- Telegram bot access;
- news-search API;
- general web-search API;
- official-source or fact-checking search tool;
- Python;
- LangChain;
- LangGraph;
- Git and GitHub;
- VS Code;
- course materials;
- official technical documentation;
- instructor support if authentication or API access blocks progress.

No additional team members are required.

---

## 8. Final Output Structure

The intended report structure is:

# Story Title

## Fact-Focused Summary

A concise summary based only on supported evidence.

## Timeline

- Date: event, statement, correction or update
- Date: event, statement, correction or update

## Disputed or Unresolved Claims

Claims that remain disputed, unsupported or unresolved.

## Overall Assessment

A cautious explanation of what the weight of evidence currently supports.

When evidence is inconclusive, the agent may describe the simplest interpretation consistent with the available facts, but it must clearly label this as an assessment rather than established truth.

## Confidence Score

A percentage with a brief explanation.

## Research Transparency

- number of iterations completed;
- source limitations;
- failed APIs;
- inaccessible pages;
- English-only limitation;
- other relevant constraints.

## What Would Clarify the Story

Included only when the result is inconclusive.

## Sources

Each source will include:

- publication;
- title;
- publication date;
- access date;
- link;
- what it supports or contradicts;
- correction or retraction footnote where relevant.

---

## 9. Definition of Done

The MVP is complete when:

- a user can submit a query through Telegram;
- n8n triggers the workflow;
- the agent searches current sources;
- the agent gathers and compares independent evidence;
- duplicate reporting is detected;
- unsupported claims are excluded;
- the agent reviews and revises its own summary;
- the workflow stops according to the agreed rules;
- a factual or inconclusive report is returned;
- the report contains source links and transparency information;
- the complete workflow runs without human intervention.
