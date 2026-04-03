# ============================================================
# Prompt Templates
# 3 types per category
# India context injection built in
# ============================================================

from typing import Dict, List
import random


# ============================================================
# INDIA CONTEXT VARIABLES
# Injected into prompts to force India-specific outputs
# ============================================================

INDIA_CONTEXTS = {
    "metro": {
        "cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
        "budget_range": "₹2,00,000 - ₹10,00,000/month",
        "channels": ["LinkedIn", "Instagram", "Google Ads", "Email"],
        "payment": "Razorpay, UPI, Credit Cards",
        "customer_type": "Urban professionals, tech-savvy SMBs"
    },
    "tier2": {
        "cities": ["Jaipur", "Surat", "Lucknow", "Nagpur", "Indore"],
        "budget_range": "₹20,000 - ₹1,00,000/month",
        "channels": ["WhatsApp", "Facebook", "YouTube", "Local events"],
        "payment": "UPI, Cash on Delivery, EMI",
        "customer_type": "Traditional business owners, first-gen entrepreneurs"
    },
    "tier3": {
        "cities": ["Jodhpur", "Varanasi", "Mysore", "Coimbatore", "Amritsar"],
        "budget_range": "₹5,000 - ₹30,000/month",
        "channels": ["WhatsApp", "Word of mouth", "Local dealers"],
        "payment": "UPI, Cash",
        "customer_type": "Small traders, farmers, local service providers"
    }
}

INDIA_INDUSTRIES = [
    "B2B SaaS for Indian SMBs",
    "D2C brand targeting Indian millennials",
    "Edtech for Tier 2 Indian cities",
    "Fintech for underbanked rural India",
    "Agritech for Indian farmers",
    "Logistics for Indian ecommerce",
    "Healthtech for Indian clinics",
    "HR tech for Indian manufacturing",
]

INDIA_STAGES = [
    "bootstrapped founder with ₹5 lakh savings",
    "pre-seed startup with ₹50 lakh angel funding",
    "seed-stage startup with ₹2 crore funding",
    "Series A startup scaling across India",
    "profitable bootstrapped SaaS at ₹10 lakh MRR"
]


def get_india_context(tier: str = None) -> Dict[str, str]:
    """Get random India context variables for prompt injection."""
    if tier is None:
        tier = random.choice(["metro", "tier2", "tier3"])
    
    ctx = INDIA_CONTEXTS[tier].copy()
    ctx['tier'] = tier
    ctx['city'] = random.choice(ctx['cities'])
    ctx['industry'] = random.choice(INDIA_INDUSTRIES)
    ctx['stage'] = random.choice(INDIA_STAGES)
    return ctx


# ============================================================
# PROMPT TYPE 1: STRUCTURED REASONING
# Forces the 5-section business framework output
# ============================================================

STRUCTURED_REASONING_PROMPTS = {

    "startup_validation": {
        "idea_testing": [
            """You are a senior business strategist with 15 years experience in Indian startups.

A {stage} asks:
"I want to build {industry}. How do I test if this idea is worth pursuing before spending money?"

Context:
- Target city: {city} ({tier} market)
- Available budget for testing: Part of {budget_range}
- Primary channel for reaching customers: {channels}

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[What is actually being tested? What are the core assumptions that need validation?]

**STRATEGIC OPTIONS**
[Option 1: Name + description + tradeoffs]
[Option 2: Name + description + tradeoffs]
[Option 3: Name + description + tradeoffs]

**RECOMMENDED DECISION**
[Choose ONE option. Justify with specific reasoning for this market.]

**EXECUTION PLAN**
[Step 1: Specific action with timeline]
[Step 2: Specific action with timeline]
[Step 3: Specific action with timeline]
[Step 4: Specific action with timeline]
[Step 5: Specific action with timeline]

**RISKS AND MITIGATION**
[Risk 1: What could go wrong + exact mitigation]
[Risk 2: What could go wrong + exact mitigation]
[Risk 3: What could go wrong + exact mitigation]

Be specific. Use INR numbers. Reference Indian market realities. No generic advice.""",

            """You are advising a {stage} building {industry}.

They have done zero validation and want to know:
"What are the 3 most dangerous assumptions I am making about my business idea?"

Market context:
- Geography: {city}, {tier} India
- Customer acquisition budget: {budget_range}
- Customer payment behavior: {payment}

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[Identify the 3 core assumptions buried in this business idea]

**STRATEGIC OPTIONS**
[How to test assumption 1 - with tradeoffs]
[How to test assumption 2 - with tradeoffs]  
[How to test assumption 3 - with tradeoffs]

**RECOMMENDED DECISION**
[Which assumption is most dangerous to leave untested? Why?]

**EXECUTION PLAN**
[Exact steps to test the most dangerous assumption first]
[Timeline: 2-week sprint format]
[Budget: Specific INR amounts]

**RISKS AND MITIGATION**
[What if all 3 assumptions are wrong?]
[How to pivot without losing everything]
[Minimum viable validation threshold]

Be precise. Indian market context required.""",
        ],
        
        "pmf_analysis": [
            """You are a growth advisor for Indian startups.

Situation: {stage} running {industry} in {city}.
They have 50 paying customers but are not sure if they have product-market fit.
Monthly revenue: somewhere between ₹50,000 - ₹3,00,000.

Question: "How do I know if I have real PMF or just early adopter luck?"

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[What does PMF actually mean in this specific context?]
[What signals matter vs what signals are misleading?]

**STRATEGIC OPTIONS**
[Option 1: Retention-based PMF measurement]
[Option 2: Survey-based PMF measurement (Sean Ellis method)]
[Option 3: Revenue-based PMF measurement]
[Include tradeoffs for each]

**RECOMMENDED DECISION**
[Which method fits this stage and market best? Why?]

**EXECUTION PLAN**
[Specific steps with exact metrics to track]
[Timeline for each step]
[What number = PMF confirmed vs PMF not found]

**RISKS AND MITIGATION**
[False positive PMF signals to watch for]
[What to do if PMF is NOT found at this stage]
[How to communicate PMF status to investors]

Use specific metrics. Real thresholds. Indian startup context.""",
        ],
    },

    "gtm_strategy": {
        "launch_planning": [
            """You are a GTM strategist specializing in Indian market launches.

Client: {stage} launching {industry}
Launch market: {city} ({tier} tier)
Available launch budget: {budget_range}
Primary acquisition channels: {channels}
Customer payment preference: {payment}

Question: "Design my go-to-market strategy for the first 90 days."

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[What does a successful 90-day launch look like for this specific product in this market?]
[What are the key variables that will determine success?]

**STRATEGIC OPTIONS**
[Option 1: Community-led launch - details + tradeoffs]
[Option 2: Paid acquisition launch - details + tradeoffs]
[Option 3: Partnership-led launch - details + tradeoffs]

**RECOMMENDED DECISION**
[Choose the best approach for this specific context]
[Justify with market and budget reasoning]

**EXECUTION PLAN**
[Days 1-30: Specific actions with targets]
[Days 31-60: Specific actions with targets]
[Days 61-90: Specific actions with targets]
[Budget breakdown in INR]
[Success metrics for each phase]

**RISKS AND MITIGATION**
[Top 3 launch risks with exact mitigation steps]
[Plan B if primary channel fails]
[Early warning signals to watch]

Be specific to Indian {tier} market dynamics.""",
        ],

        "channel_selection": [
            """You are a digital marketing strategist for Indian B2B and B2C startups.

Startup: {stage} | Product: {industry}
Target customer: {customer_type} in {city}
Monthly marketing budget: Part of {budget_range}

Question: "Which acquisition channels should I focus on and in what order?"

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[What does the customer journey look like for this specific buyer?]
[Where do they actually spend time? Where do they make decisions?]

**STRATEGIC OPTIONS**
[Channel 1: {channels[0]} - cost, reach, conversion potential, effort]
[Channel 2: Alternative channel - same breakdown]
[Channel 3: Alternative channel - same breakdown]

**RECOMMENDED DECISION**
[Primary channel + secondary channel]
[Budget split recommendation with INR numbers]
[Timeline to see ROI from each]

**EXECUTION PLAN**
[Week 1-2: Setup and initial test]
[Week 3-4: Measure and optimize]
[Month 2: Scale what works]
[Exact metrics: CAC target, CTR benchmark, conversion rate goal]

**RISKS AND MITIGATION**
[Channel dependency risk]
[Budget burn without results - when to stop]
[Competition on same channels]""",
        ],
    },

    "pricing_models": {
        "subscription_pricing": [
            """You are a SaaS pricing strategist with deep India market experience.

Company: {stage} building {industry}
Target segment: {customer_type} in {city} ({tier} market)
Current pricing consideration: monthly subscription model
Competitor context: International tools pricing in USD, local alternatives exist

Question: "How should I price my subscription product for the Indian market?"

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[What are the real pricing constraints in this market?]
[Price sensitivity level + willingness to pay range + payment behavior]

**STRATEGIC OPTIONS**
[Option 1: Value-based pricing - tiers + INR amounts + rationale]
[Option 2: Competitor-based pricing - analysis + positioning]
[Option 3: Usage-based pricing - structure + INR amounts]

**RECOMMENDED DECISION**
[Exact pricing tiers with INR amounts]
[Starter / Growth / Scale tier names and prices]
[What each tier includes and why]

**EXECUTION PLAN**
[Step 1: Validate price points with 10 prospects]
[Step 2: Build pricing page]
[Step 3: A/B test pricing]
[Step 4: Annual discount strategy]
[Revenue projection at each tier]

**RISKS AND MITIGATION**
[Race to bottom pricing war]
[Customer asking for discounts]
[International competitor undercutting]
[How to raise prices later without losing customers]

Use real INR numbers. Reference Indian SMB budget realities.""",
        ],
    },

    "sales_communication": {
        "cold_outreach": [
            """You are a B2B sales trainer specializing in Indian market outreach.

Salesperson context: {stage} selling {industry}
Target prospect: {customer_type} in {city}
Outreach channel: {channels}
Deal size target: Part of {budget_range}

Question: "Write me a cold outreach message that actually gets responses in India."

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[Why do most cold messages fail in Indian B2B context?]
[What does this specific buyer care about most?]

**STRATEGIC OPTIONS**
[Option 1: Problem-first approach - full message draft]
[Option 2: Social proof approach - full message draft]
[Option 3: Direct ROI approach - full message draft]

**RECOMMENDED DECISION**
[Choose best approach for this buyer type]
[Final polished message - ready to send]
[Subject line / opening line options]

**EXECUTION PLAN**
[Day 1: Send initial message]
[Day 3: First follow-up - what to say]
[Day 7: Second follow-up - what to say]
[Day 14: Final follow-up or close the sequence]
[Response handling scripts for common replies]

**RISKS AND MITIGATION**
[Being marked as spam]
[Ghosting after initial interest]
[Price objection in first response]
[How to handle "we have a vendor already"]""",
        ],

        "objection_handling": [
            """You are a sales coach training a team at {stage} selling {industry}.

Sales scenario: Prospect in {city} ({tier} market) shows interest but raises objections.
Deal value: Within {budget_range}
Payment preference: {payment}

The prospect says: "Your product looks good but it is too expensive for us right now."

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[Is this a real budget objection or a value objection? How to tell?]
[What is the prospect actually saying vs what they mean?]

**STRATEGIC OPTIONS**
[Option 1: ROI reframing response - exact script]
[Option 2: Flexible payment response - exact script]
[Option 3: Start small response - exact script]

**RECOMMENDED DECISION**
[Best response for this specific context]
[Complete script - word for word]
[Tone and delivery guidance for Indian buyer]

**EXECUTION PLAN**
[Immediate response to objection]
[Follow-up within 24 hours]
[Proposal adjustment if needed]
[Final closing attempt]

**RISKS AND MITIGATION**
[Over-discounting and losing margin]
[Prospect using objection as polite rejection]
[Losing deal to cheaper competitor]
[How to know when to walk away]""",
        ],
    },

    "marketing_strategy": {
        "brand_positioning": [
            """You are a brand strategist working with Indian consumer and B2B startups.

Brand context: {stage} building {industry}
Target market: {customer_type} in {city} ({tier} India)
Budget for brand building: Part of {budget_range}
Primary channels: {channels}

Question: "How do I position my brand to stand out in a crowded Indian market?"

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[What does the current competitive landscape look like?]
[What positioning spaces are available vs already occupied?]

**STRATEGIC OPTIONS**
[Option 1: Premium differentiation positioning]
[Option 2: Local/desi challenger positioning]
[Option 3: Category creation positioning]
[Each with: tagline example, key message, proof points]

**RECOMMENDED DECISION**
[Recommended positioning with clear rationale]
[Brand voice and tone guidelines]
[3 core messages for this market]

**EXECUTION PLAN**
[Step 1: Define positioning statement]
[Step 2: Create brand assets]
[Step 3: Test messaging with target audience]
[Step 4: Rollout across channels]
[Month-by-month brand building plan]

**RISKS AND MITIGATION**
[Brand confusion with established players]
[Positioning not resonating with target segment]
[Budget constraints limiting brand visibility]
[How to measure brand strength progress]""",
        ],
    },

    "growth_strategy": {
        "user_acquisition": [
            """You are a growth hacker who has scaled multiple Indian startups.

Startup: {stage} | Product: {industry}
Current users: Early stage, under 1000 users
Target market: {customer_type} in {city}
Growth budget: {budget_range}
Working channels: {channels}

Question: "How do I get my first 1000 paying customers without burning cash?"

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[What is the most efficient path to 1000 customers for this specific product?]
[What does the unit economics need to look like at this stage?]

**STRATEGIC OPTIONS**
[Option 1: Community + content led growth - steps + cost]
[Option 2: Referral program driven growth - steps + cost]
[Option 3: Direct sales hustle approach - steps + cost]

**RECOMMENDED DECISION**
[Best approach with CAC target in INR]
[Expected timeline to 1000 customers]
[LTV:CAC ratio goal]

**EXECUTION PLAN**
[Week 1-2: Foundation actions]
[Week 3-4: First acquisition push]
[Month 2: Scale what worked]
[Month 3: Optimize and systematize]
[Budget allocation in INR per channel]

**RISKS AND MITIGATION**
[High CAC burning through budget]
[Low retention making acquisition pointless]
[Channel saturation]
[Competitor copying your acquisition strategy]""",
        ],
    },

    "customer_support": {
        "support_scripts": [
            """You are a customer success manager at {stage} running {industry}.

Support scenario: Customer in {city} contacts via {channels}
Customer issue: They paid {payment} but cannot access their account after signup.
Customer tone: Frustrated, threatening to ask for refund.

Question: "Write the complete customer support script for this situation."

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[What is the customer actually experiencing? What do they need?]
[Technical issue vs trust issue vs billing issue?]

**STRATEGIC OPTIONS**
[Response approach 1: Immediate resolution focus]
[Response approach 2: Empathy-first then resolve]
[Response approach 3: Escalation to technical team]

**RECOMMENDED DECISION**
[Best approach for this customer situation]

**EXECUTION PLAN**
[Message 1 - Immediate acknowledgment: Exact script]
[Message 2 - Status update within 30 mins: Exact script]
[Message 3 - Resolution confirmation: Exact script]
[Message 4 - Follow-up satisfaction check: Exact script]
[Escalation script if not resolved in 2 hours]

**RISKS AND MITIGATION**
[Customer posting negative review]
[Refund request management]
[Same issue happening to other customers]
[How to turn frustrated customer into advocate]""",
        ],
    },

    "business_decisions": {
        "pivot_analysis": [
            """You are a startup advisor working with {stage} building {industry}.

Situation: The startup has been running for 8 months.
Current state:
- Revenue: Stagnant, not growing past ₹2,00,000/month
- Customer complaints: Product solves problem but not urgent enough
- Team: 4 people, runway: 6 months
- Market: {city} ({tier} tier)

Question: "Should we pivot? And if yes, how do we decide what to pivot to?"

Respond with this EXACT structure:

**PROBLEM BREAKDOWN**
[Is this a pivot situation or an execution problem?]
[What signals indicate real PMF failure vs early-stage struggle?]

**STRATEGIC OPTIONS**
[Option 1: Stay the course - what would need to change]
[Option 2: Product pivot - keep customers, change product]
[Option 3: Market pivot - keep product, change customer]
[Option 4: Full pivot - new direction entirely]

**RECOMMENDED DECISION**
[Based on the signals given, what should they do?]
[Decision framework with specific criteria]

**EXECUTION PLAN**
[If pivoting: 30-day pivot planning sprint]
[If staying: 30-day turnaround sprint]
[How to involve team in decision]
[How to communicate with existing customers]
[Runway management during transition]

**RISKS AND MITIGATION**
[Pivot regret - switching too early]
[Team morale during uncertainty]
[Customer churn during pivot]
[Running out of runway before new direction works]""",
        ],
    },
}


# ============================================================
# PROMPT TYPE 2: CRITIQUE AND IMPROVEMENT
# Forces model to critique then improve an answer
# Generates higher quality reasoning data
# ============================================================

CRITIQUE_IMPROVEMENT_TEMPLATE = """You are a senior business strategy reviewer.

Below is a business advice response that was given to a founder.
Your job: First critique it harshly, then rewrite it to be 10x better.

ORIGINAL QUESTION:
{instruction}

ORIGINAL RESPONSE:
{original_response}

Now respond with this EXACT structure:

**CRITIQUE**
[What is wrong with this response?]
[What is missing?]
[What is generic or unhelpful?]
[What India-specific context is missing?]
[Score: X/10 with specific reason]

**IMPROVED RESPONSE**

**PROBLEM BREAKDOWN**
[Better version with specific details]

**STRATEGIC OPTIONS**
[Better version with real tradeoffs and India context]

**RECOMMENDED DECISION**  
[Clear, specific, justified decision]

**EXECUTION PLAN**
[Actionable steps with INR numbers and timelines]

**RISKS AND MITIGATION**
[Specific risks with concrete mitigation]

The improved response must be dramatically better than the original.
Use real numbers. Name real Indian tools, platforms, and market realities."""


# ============================================================
# PROMPT TYPE 3: SIMULATION / DIALOGUE
# Generates realistic business conversation flows
# Good for customer support and sales training data
# ============================================================

SIMULATION_DIALOGUE_TEMPLATE = """You are simulating a realistic business conversation.

Context: {context}
Participants: {participants}
Situation: {situation}

Generate a realistic dialogue that shows:
1. How the conversation actually unfolds in Indian business context
2. Realistic objections, concerns, and responses
3. The strategic thinking behind each response
4. A clear resolution or next step

Format:
[SPEAKER]: [What they say]
[THINKING]: [Why they said it / strategic reasoning]

Then after the dialogue:

**KEY LESSONS**
[What worked in this conversation]
[What could have been done better]
[Applicable framework for similar situations]"""


# ============================================================
# TEMPLATE SELECTOR
# ============================================================

class PromptSelector:
    """
    Selects and formats the right prompt for each generation.
    Injects India context automatically.
    """
    
    def get_structured_prompt(
        self, 
        category: str, 
        subcategory: str,
        tier: str = None
    ) -> tuple[str, dict]:
        """
        Get a structured reasoning prompt.
        Returns: (formatted_prompt, metadata)
        """
        ctx = get_india_context(tier)
        
        templates = STRUCTURED_REASONING_PROMPTS.get(
            category, {}
        ).get(subcategory, [])
        
        if not templates:
            # Fallback generic template
            template = self._get_fallback_template(category, subcategory)
        else:
            template = random.choice(templates)
        
        # Format with India context
        try:
            formatted = template.format(**ctx)
        except KeyError:
            formatted = template
        
        metadata = {
            'category': category,
            'subcategory': subcategory,
            'geography': f"india_{ctx['tier']}",
            'industry': ctx['industry'],
            'business_stage': ctx['stage'],
            'has_india_context': True,
            'prompt_type': 'structured_reasoning'
        }
        
        return formatted, metadata
    
    def get_critique_prompt(
        self,
        instruction: str,
        original_response: str
    ) -> str:
        """Get critique and improvement prompt."""
        return CRITIQUE_IMPROVEMENT_TEMPLATE.format(
            instruction=instruction,
            original_response=original_response
        )
    
    def _get_fallback_template(
        self, 
        category: str, 
        subcategory: str
    ) -> str:
        """Generic fallback when specific template not found."""
        return f"""You are a senior business strategist specializing in Indian startups.

A {{stage}} working on {{industry}} in {{city}} ({{tier}} market) asks a question about {subcategory} in the context of {category}.

Create a realistic, specific business question they might ask, then answer it.

Use this EXACT structure:

**PROBLEM BREAKDOWN**
[Clear breakdown of the business problem]

**STRATEGIC OPTIONS**
[2-3 real options with tradeoffs]

**RECOMMENDED DECISION**
[One clear recommendation with justification]

**EXECUTION PLAN**
[Step by step actions with INR numbers and timelines]

**RISKS AND MITIGATION**
[Specific risks with concrete mitigations]

India context required. No generic advice. Use real numbers."""