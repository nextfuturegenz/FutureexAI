# ============================================================
# Category Taxonomy + Priority Configuration
# ============================================================

# Priority order for generation
# Lower number = generate first
CATEGORY_PRIORITY = [
    # ─────────────────────────────────────────────
    # TIER 1: STARTUP VALIDATION (Priority 1-4)
    # Foundation of all business reasoning
    # Generate these first
    # ─────────────────────────────────────────────
    {
        "priority":   1,
        "category":   "startup_validation",
        "subcategory": "idea_testing",
        "target":     1500,
        "model_preference": "qwen",       # Complex reasoning needed
        "prompt_types": ["structured", "critique"],
        "description": "Testing startup ideas before building"
    },
    {
        "priority":   2,
        "category":   "startup_validation",
        "subcategory": "pmf_analysis",
        "target":     1500,
        "model_preference": "deepseek",   # Chain of thought needed
        "prompt_types": ["structured", "critique"],
        "description": "Product market fit measurement and analysis"
    },
    {
        "priority":   3,
        "category":   "startup_validation",
        "subcategory": "competitor_analysis",
        "target":     1200,
        "model_preference": "qwen",
        "prompt_types": ["structured", "critique"],
        "description": "Competitive landscape analysis for Indian market"
    },
    {
        "priority":   4,
        "category":   "startup_validation",
        "subcategory": "customer_discovery",
        "target":     1200,
        "model_preference": "deepseek",
        "prompt_types": ["structured", "simulation"],
        "description": "Customer interview and discovery frameworks"
    },

    # ─────────────────────────────────────────────
    # TIER 2: GTM STRATEGY (Priority 5-8)
    # Most asked by founders
    # ─────────────────────────────────────────────
    {
        "priority":   5,
        "category":   "gtm_strategy",
        "subcategory": "launch_planning",
        "target":     1500,
        "model_preference": "qwen",
        "prompt_types": ["structured", "critique"],
        "description": "90-day launch planning for Indian startups"
    },
    {
        "priority":   6,
        "category":   "gtm_strategy",
        "subcategory": "channel_selection",
        "target":     1500,
        "model_preference": "qwen",
        "prompt_types": ["structured", "critique"],
        "description": "Acquisition channel selection and prioritization"
    },
    {
        "priority":   7,
        "category":   "gtm_strategy",
        "subcategory": "partnership_strategy",
        "target":     1200,
        "model_preference": "deepseek",
        "prompt_types": ["structured", "simulation"],
        "description": "Strategic partnerships for Indian market entry"
    },
    {
        "priority":   8,
        "category":   "gtm_strategy",
        "subcategory": "market_entry",
        "target":     1200,
        "model_preference": "qwen",
        "prompt_types": ["structured", "critique"],
        "description": "New market entry strategy Tier 2 and Tier 3 India"
    },

    # ─────────────────────────────────────────────
    # TIER 3: MARKETING STRATEGY (Priority 9-13)
    # High volume and diverse scenarios
    # ─────────────────────────────────────────────
    {
        "priority":   9,
        "category":   "marketing_strategy",
        "subcategory": "brand_positioning",
        "target":     1500,
        "model_preference": "qwen",
        "prompt_types": ["structured", "critique"],
        "description": "Brand positioning in crowded Indian markets"
    },
    {
        "priority":   10,
        "category":   "marketing_strategy",
        "subcategory": "content_marketing",
        "target":     1500,
        "model_preference": "phi",        # High volume simple samples
        "prompt_types": ["structured", "simulation"],
        "description": "Content strategy for Indian audiences"
    },
    {
        "priority":   11,
        "category":   "marketing_strategy",
        "subcategory": "social_media",
        "target":     1500,
        "model_preference": "phi",
        "prompt_types": ["structured", "simulation"],
        "description": "Social media strategy WhatsApp Instagram YouTube"
    },
    {
        "priority":   12,
        "category":   "marketing_strategy",
        "subcategory": "influencer_marketing",
        "target":     1000,
        "model_preference": "phi",
        "prompt_types": ["structured", "critique"],
        "description": "Influencer and creator marketing for Indian brands"
    },
    {
        "priority":   13,
        "category":   "marketing_strategy",
        "subcategory": "seo_strategy",
        "target":     1000,
        "model_preference": "phi",
        "prompt_types": ["structured", "critique"],
        "description": "SEO and organic growth for Indian startups"
    },

    # ─────────────────────────────────────────────
    # TIER 4: PRICING MODELS (Priority 14-17)
    # High value reasoning samples
    # ─────────────────────────────────────────────
    {
        "priority":   14,
        "category":   "pricing_models",
        "subcategory": "subscription_pricing",
        "target":     1500,
        "model_preference": "deepseek",
        "prompt_types": ["structured", "critique"],
        "description": "SaaS subscription pricing for Indian market"
    },
    {
        "priority":   15,
        "category":   "pricing_models",
        "subcategory": "freemium_strategy",
        "target":     1200,
        "model_preference": "deepseek",
        "prompt_types": ["structured", "critique"],
        "description": "Freemium to paid conversion strategy India"
    },
    {
        "priority":   16,
        "category":   "pricing_models",
        "subcategory": "price_sensitivity",
        "target":     1200,
        "model_preference": "deepseek",
        "prompt_types": ["structured", "critique"],
        "description": "Price sensitivity analysis Indian customer segments"
    },
    {
        "priority":   17,
        "category":   "pricing_models",
        "subcategory": "competitive_pricing",
        "target":     1000,
        "model_preference": "qwen",
        "prompt_types": ["structured", "critique"],
        "description": "Competitive pricing decisions and responses"
    },

    # ─────────────────────────────────────────────
    # TIER 5: SALES COMMUNICATION (Priority 18-21)
    # Dialogue diversity
    # ─────────────────────────────────────────────
    {
        "priority":   18,
        "category":   "sales_communication",
        "subcategory": "cold_outreach",
        "target":     1500,
        "model_preference": "qwen",
        "prompt_types": ["structured", "simulation"],
        "description": "Cold outreach scripts for Indian B2B sales"
    },
    {
        "priority":   19,
        "category":   "sales_communication",
        "subcategory": "objection_handling",
        "target":     1500,
        "model_preference": "deepseek",
        "prompt_types": ["structured", "simulation"],
        "description": "Sales objection handling for Indian buyers"
    },
    {
        "priority":   20,
        "category":   "sales_communication",
        "subcategory": "sales_copy",
        "target":     1200,
        "model_preference": "phi",
        "prompt_types": ["structured", "critique"],
        "description": "Sales copy and messaging for Indian market"
    },
    {
        "priority":   21,
        "category":   "sales_communication",
        "subcategory": "pitch_deck_advice",
        "target":     1000,
        "model_preference": "qwen",
        "prompt_types": ["structured", "critique"],
        "description": "Pitch deck structure and investor messaging India"
    },

    # ─────────────────────────────────────────────
    # TIER 6: GROWTH STRATEGY (Priority 22-25)
    # Builds on startup and GTM categories
    # ─────────────────────────────────────────────
    {
        "priority":   22,
        "category":   "growth_strategy",
        "subcategory": "user_acquisition",
        "target":     1500,
        "model_preference": "qwen",
        "prompt_types": ["structured", "critique"],
        "description": "User acquisition playbooks for Indian startups"
    },
    {
        "priority":   23,
        "category":   "growth_strategy",
        "subcategory": "retention_strategy",
        "target":     1500,
        "model_preference": "deepseek",
        "prompt_types": ["structured", "critique"],
        "description": "Customer retention and churn reduction India"
    },
    {
        "priority":   24,
        "category":   "growth_strategy",
        "subcategory": "referral_programs",
        "target":     1200,
        "model_preference": "phi",
        "prompt_types": ["structured", "simulation"],
        "description": "Referral program design for Indian consumer behavior"
    },
    {
        "priority":   25,
        "category":   "growth_strategy",
        "subcategory": "expansion_strategy",
        "target":     1200,
        "model_preference": "qwen",
        "prompt_types": ["structured", "critique"],
        "description": "Geographic and segment expansion within India"
    },

    # ─────────────────────────────────────────────
    # TIER 7: CUSTOMER SUPPORT (Priority 26-29)
    # High volume simpler scenarios
    # ─────────────────────────────────────────────
    {
        "priority":   26,
        "category":   "customer_support",
        "subcategory": "support_scripts",
        "target":     1500,
        "model_preference": "phi",
        "prompt_types": ["structured", "simulation"],
        "description": "Customer support conversation scripts India"
    },
    {
        "priority":   27,
        "category":   "customer_support",
        "subcategory": "escalation_handling",
        "target":     1200,
        "model_preference": "phi",
        "prompt_types": ["structured", "simulation"],
        "description": "Escalation handling and angry customer management"
    },
    {
        "priority":   28,
        "category":   "customer_support",
        "subcategory": "refund_scenarios",
        "target":     1200,
        "model_preference": "phi",
        "prompt_types": ["structured", "simulation"],
        "description": "Refund request handling and retention scripts"
    },
    {
        "priority":   29,
        "category":   "customer_support",
        "subcategory": "onboarding_flows",
        "target":     1000,
        "model_preference": "phi",
        "prompt_types": ["structured", "simulation"],
        "description": "Customer onboarding conversation flows"
    },

    # ─────────────────────────────────────────────
    # TIER 8: BUSINESS DECISIONS (Priority 30-33)
    # Complex reasoning saved for last
    # Uses best models only
    # ─────────────────────────────────────────────
    {
        "priority":   30,
        "category":   "business_decisions",
        "subcategory": "hiring_decisions",
        "target":     1200,
        "model_preference": "deepseek",
        "prompt_types": ["structured", "critique"],
        "description": "First hire and team building decisions India"
    },
    {
        "priority":   31,
        "category":   "business_decisions",
        "subcategory": "pivot_analysis",
        "target":     1200,
        "model_preference": "deepseek",
        "prompt_types": ["structured", "critique"],
        "description": "Pivot vs persist decision frameworks"
    },
    {
        "priority":   32,
        "category":   "business_decisions",
        "subcategory": "budget_allocation",
        "target":     1000,
        "model_preference": "deepseek",
        "prompt_types": ["structured", "critique"],
        "description": "Budget allocation for Indian startups limited runway"
    },
    {
        "priority":   33,
        "category":   "business_decisions",
        "subcategory": "vendor_selection",
        "target":     800,
        "model_preference": "phi",
        "prompt_types": ["structured", "simulation"],
        "description": "Vendor and tool selection for Indian startups"
    },
]


# ============================================================
# COMPUTED TOTALS
# ============================================================

TOTAL_TARGET_SAMPLES = sum(
    item["target"] for item in CATEGORY_PRIORITY
)

CATEGORY_TOTALS = {}
for item in CATEGORY_PRIORITY:
    cat = item["category"]
    if cat not in CATEGORY_TOTALS:
        CATEGORY_TOTALS[cat] = 0
    CATEGORY_TOTALS[cat] += item["target"]


# ============================================================
# MODEL ASSIGNMENT
# Which categories go to which model
# ============================================================

MODEL_ASSIGNMENTS = {
    "qwen": [
        item for item in CATEGORY_PRIORITY
        if item["model_preference"] == "qwen"
    ],
    "deepseek": [
        item for item in CATEGORY_PRIORITY
        if item["model_preference"] == "deepseek"
    ],
    "phi": [
        item for item in CATEGORY_PRIORITY
        if item["model_preference"] == "phi"
    ],
}

MODEL_TARGETS = {
    model: sum(item["target"] for item in items)
    for model, items in MODEL_ASSIGNMENTS.items()
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_priority_list() -> list:
    """
    Return categories sorted by priority.
    Used by orchestrator to decide what to generate next.
    """
    return sorted(
        CATEGORY_PRIORITY,
        key=lambda x: x["priority"]
    )


def get_categories_for_model(model_name: str) -> list:
    """
    Get all categories assigned to a specific model.
    Used when running single-model sessions.

    Args:
        model_name: 'qwen' | 'deepseek' | 'phi'
    """
    return MODEL_ASSIGNMENTS.get(model_name, [])


def get_next_underfilled_category(
    current_counts: dict,
    model_filter: str = None
) -> dict:
    """
    Find the highest priority category that
    has not yet reached its target count.

    Args:
        current_counts: {category_subcategory: count}
        model_filter:   Only return categories for this model

    Returns:
        Category config dict or None if all targets met
    """
    source = (
        get_categories_for_model(model_filter)
        if model_filter
        else get_priority_list()
    )

    for item in sorted(source, key=lambda x: x["priority"]):
        key = f"{item['category']}_{item['subcategory']}"
        current = current_counts.get(key, 0)

        if current < item["target"]:
            return {
                **item,
                "current_count": current,
                "remaining": item["target"] - current,
                "completion_pct": round(
                    current / item["target"] * 100, 1
                )
            }

    return None  # All targets met


def get_category_summary() -> dict:
    """
    Return summary of all categories.
    Used for dashboard display.
    """
    return {
        "total_categories":    len(CATEGORY_PRIORITY),
        "total_target":        TOTAL_TARGET_SAMPLES,
        "category_breakdown":  CATEGORY_TOTALS,
        "model_targets":       MODEL_TARGETS,
        "categories": [
            {
                "priority":    item["priority"],
                "category":    item["category"],
                "subcategory": item["subcategory"],
                "target":      item["target"],
                "model":       item["model_preference"],
                "description": item["description"]
            }
            for item in get_priority_list()
        ]
    }


def print_category_plan():
    """
    Print the full generation plan.
    Call this at session start to see the plan.
    """
    summary = get_category_summary()

    print("\n" + "="*60)
    print("  DATASET GENERATION PLAN")
    print("="*60)
    print(f"  Total Categories : {summary['total_categories']}")
    print(f"  Total Target     : {summary['total_target']:,} samples")
    print()

    print("  MODEL ASSIGNMENTS:")
    print("  " + "-"*40)
    for model, target in summary['model_targets'].items():
        cats = len(MODEL_ASSIGNMENTS[model])
        print(
            f"  {model.upper():<12} "
            f"{target:>6,} samples  "
            f"({cats} subcategories)"
        )

    print()
    print("  CATEGORY BREAKDOWN:")
    print("  " + "-"*40)
    for cat, total in summary['category_breakdown'].items():
        print(f"  {cat:<30} {total:>6,}")

    print()
    print("  FULL PRIORITY LIST:")
    print("  " + "-"*40)
    print(
        f"  {'P':<4} {'CATEGORY':<25} "
        f"{'SUBCATEGORY':<25} "
        f"{'TARGET':>6} "
        f"{'MODEL':<10}"
    )
    print("  " + "-"*75)

    for item in summary['categories']:
        print(
            f"  {item['priority']:<4} "
            f"{item['category']:<25} "
            f"{item['subcategory']:<25} "
            f"{item['target']:>6,} "
            f"{item['model']:<10}"
        )

    print("="*60 + "\n")