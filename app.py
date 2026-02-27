#!/usr/bin/env python3
"""
SEO Article Generation Tool - Web App
Flask backend with streaming support
Based on DIAL Agents SEO Best Practice Guides
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, Response, jsonify, stream_with_context
import anthropic

app = Flask(__name__)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"

# ─────────────────────────────────────────────
# Best Practice Guides (from your PDFs)
# ─────────────────────────────────────────────

SEMANTIC_KEYWORDS_GUIDE = """
SEO SEMANTIC KEYWORDS BEST PRACTICE GUIDE (LSI):
Objective: Enhance webpage relevancy using Latent Semantic Indexing (LSI) keywords.

Instructions:
1. Identify the primary keyword as the focal point.
2. Generate 10-15 LSI keywords semantically related to it.
3. Maintain topical relevance — keywords must establish page authority on the subject.
4. Assign estimated monthly search volume to each keyword.
5. Identify keyword intent: informational, commercial, or both.

Tips:
- Clearly identify primary vs secondary keywords.
- Indicate low confidence where uncertain.
- Estimate search volumes based on typical industry patterns.
- Focus on keywords that will genuinely improve topical authority.
"""

CATEGORY_TAGGING_GUIDE = """
SEO CATEGORY TAGGING BEST PRACTICE GUIDE:
Objective: Tag keywords by intent and category for grouping and performance tracking.

Steps:
1. Tag 1 - Keyword Intent:
   - Commercial: Direct, purchase-focused, typically ≤4 words.
   - Informational: Usually >4 words, questions or comparisons.
   - Tag as: informational, commercial, or both.
2. Tags 2-4 - Category Hierarchy:
   - Tag 2: Top-level category
   - Tag 3: Sub-category of Tag 2
   - Tag 4: Sub-category of Tag 3
3. Tags 5+ - Specific differentiation: features, material, colour, size, gender, etc.
4. Mark uncertain keywords as [untagged].

Key Considerations:
- Understand full context before creating categories.
- Do not invent information if unsure.
- Avoid rude or explicit terms.
"""

CONTENT_RESEARCH_GUIDE = """
SEO CONTENT RESEARCH BEST PRACTICE GUIDE:
Steps:
1. Understand the topic and what the article should comprehensively cover.
2. Understand the target audience — their needs, questions, and search behaviour.
3. Brainstorm content angles not commonly covered.
4. Ensure relevance to primary keyword and audience intent.
5. For each content angle, identify 2-3 supporting keywords with search volumes.

Key Considerations:
- Be knowledgeable and useful above all else.
- Ensure topical relevance throughout.
- Indicate low confidence where uncertain.
- Search volumes should reflect monthly data.
"""

ARTICLE_COPY_GUIDE = """
SEO ARTICLE COPYWRITING BEST PRACTICE GUIDE:

GENERAL GUIDELINES:
1. Readability: Flesch-Kincaid score of 50-60. For complex terms scoring below 50,
   provide a definitions glossary at the bottom of the article with clear referencing.
2. Expert Tone: Write as a subject-matter expert. Comprehensive and clearly structured.
3. FAQs: Include a FAQ section at the bottom with 4-5 questions and answers.
4. Structure:
   - H1 (#): Article title
   - H2 (##), H3 (###), H4 (####): Nested headings — H3 goes deeper than H2, H4 deeper than H3.
   - Maximum 4 heading levels.

CONTENT REQUIREMENTS:
1. Keywords: Use LSI keywords naturally in copy and headings. No keyword stuffing.
2. Word Count: 800–2000 words total. Each section: 120–300 words.
3. Title Tag: Must contain primary keyword. Max 60 characters.
4. Meta Description: 150–160 characters, includes primary keyword, compelling and clickable.

BEST PRACTICES:
- Readability is paramount — short paragraphs (2–4 sentences).
- Answer common questions and solve real problems.
- Use emotional trigger words where appropriate.
- Use numbers, statistics, and data points — cite sources where possible.
- Avoid false claims; indicate uncertainty clearly.
- Hook readers immediately in the introduction.
- Strong conclusion with a clear takeaway or call to action.

NEIL PATEL PRINCIPLES:
- Write for humans first, search engines second.
- Use the primary keyword in: title, first paragraph, 2+ subheadings, conclusion.
- Match search intent: informational, navigational, commercial, or transactional.
- Use bucket brigades (transitional phrases) to keep readers engaged.
- Use power words to drive emotion and action.
"""

OUTPUT_FORMAT = """
OUTPUT FORMAT — use these exact section delimiters:

---KEYWORDS---
[comma-separated list of all keywords used]

---TITLETAG---
[Title tag - max 60 characters, must include primary keyword]

---METADESC---
[Meta description - 150-160 characters, includes primary keyword, compelling]

---ARTICLETITLE---
[H1 main title of the article]

---ARTICLECOPY---
[Full article body in Markdown using # ## ### #### headings]
[Minimum 800 words. Each section 120-300 words.]
[End with a Definitions section if complex terms were used]

---FAQS---
Q1: [Question]
A1: [Answer — 2-4 sentences]

Q2: [Question]
A2: [Answer]

Q3: [Question]
A3: [Answer]

Q4: [Question]
A4: [Answer]

Q5: [Question]
A5: [Answer]

---END---
"""


# ─────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/keywords", methods=["POST"])
def generate_keywords():
    """Step 2: Generate LSI keywords."""
    data = request.json
    primary_keyword = data.get("primary_keyword", "")
    industry = data.get("industry", "General")
    target_audience = data.get("target_audience", "General audience")

    prompt = f"""
{SEMANTIC_KEYWORDS_GUIDE}

PRIMARY KEYWORD: "{primary_keyword}"
INDUSTRY/NICHE: {industry}
TARGET AUDIENCE: {target_audience}

Following the SEO Semantic Keywords Best Practice Guide, generate a comprehensive LSI keyword list.

Output in this EXACT format (use the pipe-separated table):

PRIMARY KEYWORD: {primary_keyword}

KEYWORD INTENT: [informational / commercial / both] — [brief explanation of why]

BEST CONTENT ANGLE: [1-2 sentences on the best angle to take for this keyword]

LSI KEYWORDS TABLE:
| Keyword | Est. Monthly Searches | Intent |
|---|---|---|
[10-15 rows]

TOP 5 KEYWORDS TO WEAVE INTO ARTICLE:
1. [keyword] — [why it matters for this topic]
2. [keyword] — [why]
3. [keyword] — [why]
4. [keyword] — [why]
5. [keyword] — [why]

Note: Search volume estimates are indicative — verify with Google Keyword Planner or Ahrefs.
"""

    def generate():
        with client.messages.stream(
            model=MODEL,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/api/brief", methods=["POST"])
def generate_brief():
    """Step 3: Generate content angle and article brief."""
    data = request.json
    primary_keyword = data.get("primary_keyword", "")
    industry = data.get("industry", "General")
    target_audience = data.get("target_audience", "General audience")
    keywords_output = data.get("keywords_output", "")

    prompt = f"""
{CONTENT_RESEARCH_GUIDE}

PRIMARY KEYWORD: "{primary_keyword}"
INDUSTRY: {industry}
TARGET AUDIENCE: {target_audience}

KEYWORD RESEARCH COMPLETED:
{keywords_output}

Based on the SEO Content Research Best Practice Guide, produce a concise article brief.

Output in this EXACT format:

SEARCH INTENT: [informational / commercial / navigational / transactional]
USER PROBLEM: [What problem is the user trying to solve with this search?]

RECOMMENDED ARTICLE TITLE (H1):
[Compelling title containing primary keyword]

TITLE TAG (max 60 chars):
[Title tag]

META DESCRIPTION (150-160 chars):
[Meta description — include primary keyword, make it clickable]

TARGET WORD COUNT: [specific number between 800-2000]

ARTICLE OUTLINE:
## [H2 Heading 1] — [brief note on what this section covers, which LSI keywords to use]
### [H3 sub-heading if needed]
## [H2 Heading 2] — [note]
## [H2 Heading 3] — [note]
## [H2 Heading 4] — [note]
## [H2 Heading 5 — optional]
## Frequently Asked Questions
## [Definitions if complex terms expected]

FAQ SUGGESTIONS (5 questions a real reader would ask):
1. [Question]
2. [Question]
3. [Question]
4. [Question]
5. [Question]
"""

    def generate():
        with client.messages.stream(
            model=MODEL,
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/api/article", methods=["POST"])
def generate_article():
    """Step 4: Generate full SEO article."""
    data = request.json
    primary_keyword = data.get("primary_keyword", "")
    industry = data.get("industry", "General")
    target_audience = data.get("target_audience", "General audience")
    tone = data.get("tone", "expert, informative, conversational")
    brand = data.get("brand_name", "")
    keywords_output = data.get("keywords_output", "")
    brief_output = data.get("brief_output", "")
    user_notes = data.get("user_notes", "")

    system = (
        "You are a world-class SEO copywriter who strictly follows best practice guidelines. "
        "Always produce the article in the exact output format requested. "
        "Never truncate or summarise — write the full article."
    )

    prompt = f"""
{ARTICLE_COPY_GUIDE}

You are writing a complete, publish-ready SEO article. Follow ALL guidelines above precisely.

INPUTS:
- Primary Keyword: "{primary_keyword}"
- Industry/Niche: {industry}
- Target Audience: {target_audience}
- Tone of Voice: {tone}
- Brand/Website: {brand if brand else "Not specified"}
- Additional Notes from User: {user_notes if user_notes else "None"}

KEYWORD RESEARCH:
{keywords_output}

ARTICLE BRIEF & OUTLINE:
{brief_output}

CRITICAL REQUIREMENTS CHECKLIST:
✅ Flesch-Kincaid readability: AIM FOR 50-60 (short sentences, plain language)
✅ Total word count: 800–2000 words
✅ Each section: 120–300 words
✅ Primary keyword in: H1 title, first paragraph, at least 2 subheadings, conclusion
✅ LSI keywords woven naturally — NO keyword stuffing
✅ Short paragraphs: 2–4 sentences max
✅ Use numbers, statistics, examples where relevant
✅ Emotional trigger words where appropriate
✅ Include Definitions section at bottom if complex terms are used
✅ Strong hook in the introduction (first 2 sentences must grab attention)
✅ Strong conclusion with a clear takeaway or CTA
✅ 5 FAQs with full answers at the end

{OUTPUT_FORMAT}
"""

    def generate():
        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            system=system,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/api/refine", methods=["POST"])
def refine_article():
    """Refine the article based on user instruction."""
    data = request.json
    current_article = data.get("current_article", "")
    refinement = data.get("refinement", "")
    primary_keyword = data.get("primary_keyword", "")

    prompt = f"""
Here is the current SEO article:

{current_article}

REFINEMENT REQUEST: {refinement}

Apply ONLY the requested refinement. Maintain all SEO best practices:
- Primary keyword: "{primary_keyword}"
- Keep the exact same output format (---KEYWORDS--- ... ---END---)
- Maintain Flesch-Kincaid 50-60 readability
- Keep word count 800-2000 words
- Preserve all section delimiters exactly as they are

Output the complete refined article in the same format.
"""

    def generate():
        with client.messages.stream(
            model=MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": prompt}]
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@app.route("/api/save", methods=["POST"])
def save_article():
    """Parse and save the final article."""
    data = request.json
    raw = data.get("raw_article", "")
    context = data.get("context", {})

    def extract(raw, start, end):
        try:
            s = raw.index(start) + len(start)
            e = raw.index(end, s)
            return raw[s:e].strip()
        except ValueError:
            return ""

    sections = {
        "keywords": extract(raw, "---KEYWORDS---", "---TITLETAG---"),
        "title_tag": extract(raw, "---TITLETAG---", "---METADESC---"),
        "meta_desc": extract(raw, "---METADESC---", "---ARTICLETITLE---"),
        "article_title": extract(raw, "---ARTICLETITLE---", "---ARTICLECOPY---"),
        "article_copy": extract(raw, "---ARTICLECOPY---", "---FAQS---"),
        "faqs": extract(raw, "---FAQS---", "---END---"),
    }

    output_dir = os.path.expanduser("~/Desktop/SEO Articles")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_kw = context.get("primary_keyword", "article").replace(" ", "_").replace("/", "-")[:30]
    base = f"{safe_kw}_{timestamp}"

    # Markdown
    md = f"""# SEO ARTICLE OUTPUT

**Primary Keyword:** {context.get('primary_keyword', '')}
**Generated:** {datetime.now().strftime('%d %B %Y, %H:%M')}

---

## SEO META DATA

**Title Tag:** {sections['title_tag']}

**Meta Description:** {sections['meta_desc']}

**Keywords Used:** {sections['keywords']}

---

## ARTICLE

{sections['article_copy']}

---

## FREQUENTLY ASKED QUESTIONS

{sections['faqs']}

---

## KEYWORD RESEARCH NOTES

{context.get('keywords_output', 'N/A')}

---
*Generated by DIAL Agents SEO Article Tool*
"""
    md_path = os.path.join(output_dir, f"{base}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)

    # JSON
    json_data = {
        "generated_at": datetime.now().isoformat(),
        **context,
        **sections,
    }
    json_path = os.path.join(output_dir, f"{base}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    return jsonify({
        "success": True,
        "md_path": md_path,
        "json_path": json_path,
        "sections": sections,
    })


if __name__ == "__main__":
    print("\n" + "=" * 55)
    print("  DIAL Agents — SEO Article Generation Tool")
    print("=" * 55)
    print("  Open your browser at: http://127.0.0.1:5000")
    print("  Press Ctrl+C to stop the server")
    print("=" * 55 + "\n")
    app.run(debug=False, port=5000)
