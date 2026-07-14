# Verification Rules for DRAGNET

## Purpose

These rules guide how DRAGNET evaluates news sources, extracts factual claims, and separates evidence from opinion, speculation and framing.

The agent must apply the same criteria to every article, regardless of the publication.

## Core Principle

Do not assume a claim is true because it appears in a news article.

A claim should be treated as factual only when it is supported by identifiable evidence, corroborated by independent sources, or directly supported by primary material.

## Source Types

### Stronger Evidence

Greater weight should be given to:

- primary documents;
- direct quotes with clear attribution;
- official records;
- court documents;
- published datasets;
- first-hand reporting;
- independently corroborated reporting;
- corrected articles where the correction is clearly disclosed.

### Weaker Evidence

Lower weight should be given to:

- anonymous claims without corroboration;
- opinion pieces;
- articles that cite no original evidence;
- commentary presented as reporting;
- social media posts that cannot be verified;
- duplicated, syndicated or paraphrased articles relying on the same original source.

## Official Sources

Official sources are important, but not automatically neutral.

Statements from governments, companies, police forces, campaign groups or public figures may reflect self-interest, reputation management or incomplete information.

The agent must distinguish between:

- what an organisation claims;
- what can be independently verified;
- what remains disputed or uncertain.

## Opinion and Framing

The agent should identify and reduce:

- emotionally loaded language;
- exaggeration;
- minimising language;
- dismissive language;
- unsupported interpretation;
- speculation;
- claims about motive without evidence;
- conclusions that go beyond the evidence.

## Unsupported Claims

If a source makes a factual claim without evidence, the agent should research the claim independently.

If corroborated by stronger sources, cite the stronger sources.

If not corroborated, do not include the claim as fact.

## Contradictory Claims

When sources contradict each other, the agent should compare:

- evidence quality;
- source independence;
- access to primary material;
- recency;
- whether later corrections or updates exist.

The final report must clearly state unresolved contradictions.

## Duplicate Coverage

Multiple articles repeating the same original report should not be counted as multiple independent confirmations.

Duplicated or syndicated coverage should be treated as one evidence chain.

## Anonymous Sources

Anonymous sources may be included only when directly relevant.

They must be labelled clearly and treated cautiously.

Anonymous claims should not be presented as established fact without corroboration.

## Satire and Parody

Clearly labelled satire and parody must not be used as factual evidence.

Known satire sources should be excluded from factual analysis.

## Social Media

Social media may be used only from relevant and identifiable sources, such as:

- official organisations;
- public authorities;
- verified people directly involved;
- journalists with first-hand reporting;
- recognised subject-matter experts.

Fan accounts, anonymous reposting pages, parody accounts and unrelated commentary should be excluded.

Social media posts should be treated as claims to verify, not as confirmed facts.

## Final Output Rules

The final report should separate:

- confirmed facts;
- strongly supported claims;
- disputed claims;
- unsupported claims;
- disproven claims;
- unresolved claims.

When no supporting evidence is found, say:

> No supporting evidence was found during this investigation.

Do not automatically describe unsupported claims as false.

## Confidence

Confidence should be based on:

- source quality;
- source independence;
- amount of corroboration;
- access to primary evidence;
- unresolved contradictions;
- failed tools or inaccessible sources;
- whether the final summary is fully source-supported.