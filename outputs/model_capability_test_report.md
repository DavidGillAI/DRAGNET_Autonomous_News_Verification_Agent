# DRAGNET Model Capability Test Report

## Purpose

This report records three early tests carried out to assess whether the chosen language model can support the core reasoning required for DRAGNET: comparing multiple news sources, separating confirmed facts from unsupported claims, identifying framing, and producing cautious conclusions.

These tests were conducted before building the full autonomous LangGraph workflow, in order to reduce project risk and check whether the model is capable of the main verification task.

## Project Context

DRAGNET stands for:

**Digital Research Agent Gathering News Evidence Transparently**

The project aims to create an autonomous news research and verification agent. The agent should search for news sources, compare reporting, identify supported and unsupported claims, and produce a cautious fact-focused report rather than overclaiming certainty.

## Test 1: Controlled Contradiction Test

### Aim

The first test checked whether the model could handle a deliberately controlled contradiction between article summaries.

The test used three fictional but realistic article snippets about a city centre incident. Two sources stated that police were investigating and that no arrests had been made. A third source claimed that a man had been arrested, but without police or official confirmation.

### Expected Behaviour

The model should not accept the stronger arrest claim as confirmed. It should identify the incident and investigation as supported, while treating the arrest claim as disputed or unsupported.

### Outcome

The model correctly identified the confirmed facts: an incident occurred, police were investigating, the investigation was ongoing, and police appealed for witnesses.

It also correctly marked the arrest claim from Outlet B as unsupported because it was not confirmed by police or an official source.

The model compared the sources appropriately and concluded that the arrest claim remained unclear.

Saved output: `outputs/llm_comparison_test_1.txt`

### Consistency Note

Before saving the hard-copy output, the same test was run multiple times in the terminal. Across three runs, the model reached the same core conclusion each time: the incident and investigation were supported, but the arrest claim was not confirmed.

### Result

**Pass.**

The model showed stable reasoning across repeated runs and did not overclaim from a single unsupported source.

## Test 2: Real GNews Snippet Comparison

### Aim

The second test used live GNews results to check whether the model could reason over messy real-world article snippets.

The search query related to Brexit and the UK economy. Unlike Test 1, the articles were not controlled examples. They came from live search results and covered different aspects of Brexit.

### Expected Behaviour

The model should recognise whether the articles were about one specific event or a broader mixed topic. It should also avoid treating snippets as full evidence.

### Outcome

The model correctly identified that the articles were not about one single event, but covered different facets of Brexit and its long-term effects.

It identified several reported economic claims and separated them from more opinion-based or unclear political claims.

The model also included an appropriate limitation, stating that snippets are not full articles and therefore restrict the strength of any conclusion.

Saved output: `outputs/llm_real_gnews_test_2.txt`

### Result

**Pass, with useful prompt refinement.**

The model handled real snippets cautiously and recognised that the sources covered a broad topic rather than one single event. Future prompts should continue to require careful wording around studies, estimates and counterfactual claims.

## Test 3: DRAGNET Report Format Test

### Aim

The third test checked whether the model could produce output in the intended DRAGNET report structure, using real GNews snippets.

The query related to the Folarin Balogun situation involving FIFA, Donald Trump and claims around a reversed suspension.

### Expected Behaviour

The model should produce the planned DRAGNET format:

- Story title
- Fact-Focused Summary
- Timeline, if dates matter
- Confirmed / Strongly Supported Facts
- Disputed / Unsupported / Unresolved Claims
- Overall Assessment
- Confidence Score
- Research Transparency
- What Would Clarify the Story
- Sources

It should also avoid assuming bias in advance and should not conclude that Trump directly influenced FIFA unless the snippets clearly supported that claim.

### Outcome

The model produced the intended DRAGNET-style report structure. It summarised the story as a controversy around FIFA’s reversal of Balogun’s suspension and claims of Trump’s involvement.

It identified key claims, including the red card, the suspension reversal, Infantino receiving a call from Trump, and a complaint filed with the IOC.

Most importantly, it did not conclude that Trump directly influenced FIFA’s decision. It correctly marked that causal claim as unresolved and unsupported by the snippets alone.

The model gave a cautious confidence score of 5/10 and explained that the available snippets did not provide definitive evidence.

Saved output: `outputs/dragnet_report_test_3.txt`

### Weakness Identified

The Sources section listed publication names but did not include article titles, publication dates or URLs.

This is a formatting issue rather than a reasoning failure. The prompt should be updated so that the final DRAGNET report requires source names, titles, publication dates and URLs.

### Result

**Pass, with formatting improvement needed.**

The model produced the intended report structure and handled the central unresolved claim cautiously. The main improvement is to make the Sources section more complete.

## Overall Conclusion

Across the three tests, the model demonstrated that it can support the core reasoning required for DRAGNET.

The tests showed that the model can:

1. identify confirmed facts;
2. flag unsupported or disputed claims;
3. avoid overclaiming from a single source;
4. handle real article snippets cautiously;
5. recognise when articles are about mixed topics;
6. produce a structured DRAGNET-style report;
7. explain limitations and uncertainty.

The model is not perfect and still needs guardrails. In particular, prompts should require careful attribution of reported claims, cautious treatment of studies and estimates, and full source metadata including URLs.

However, the test results suggest that the DRAGNET concept is feasible as an MVP, especially if the final system is designed around cautious evidence classification rather than asking the model to declare absolute truth.

## Implications for the MVP

The tests support continuing with the DRAGNET MVP, but the final system should include clear guardrails.

The report prompt should require full source metadata, including source name, article title, publication date, URL, and what each source was used for.

The model should remain focused on evidence comparison rather than declaring absolute truth. Where evidence is limited to snippets, the report should say so clearly.

The next build step is to connect the existing components into a simple MVP flow: user query, GNews retrieval, DRAGNET report generation, and saved output.