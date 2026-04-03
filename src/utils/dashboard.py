# ============================================================
# Progress Dashboard
# Printed in Colab output
# Shows live generation stats
# ============================================================

from datetime import datetime
from typing import Optional


class Dashboard:
    """
    Prints live progress dashboard in Colab output.
    Called every 50 samples and at session end.
    """

    def show(
        self,
        checkpoint,
        writer,
        session_start: datetime
    ):
        """
        Print full progress dashboard.

        Args:
            checkpoint    : CheckpointManager instance
            writer        : DataWriter instance
            session_start : When this session started
        """
        now          = datetime.now()
        elapsed      = now - session_start
        elapsed_mins = round(elapsed.total_seconds() / 60, 1)
        remaining_mins = max(0, round(240 - elapsed_mins, 1))

        # Get stats
        overall      = checkpoint.get_overall_progress()
        session      = writer.get_session_stats()
        cat_progress = checkpoint.get_category_progress()

        self._print_header(now)
        self._print_session_stats(
            session, elapsed_mins, remaining_mins
        )
        self._print_overall_stats(overall)
        self._print_category_table(cat_progress)
        self._print_footer(remaining_mins)

    # ─────────────────────────────────────────────
    # PRINT SECTIONS
    # ─────────────────────────────────────────────

    def _print_header(self, now: datetime):
        """Print dashboard header."""
        print("\n" + "="*62)
        print("  📊  BUSINESS AI DATASET GENERATOR - LIVE DASHBOARD")
        print(f"  🕐  {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*62)

    def _print_session_stats(
        self,
        session: dict,
        elapsed_mins: float,
        remaining_mins: float
    ):
        """Print current session statistics."""
        total    = session.get("session_total", 0)
        passed   = session.get("session_passed", 0)
        failed   = session.get("session_failed", 0)
        pass_rate = session.get("pass_rate", 0)

        # Estimate samples per hour
        if elapsed_mins > 0:
            rate_per_hour = round(total / elapsed_mins * 60, 0)
        else:
            rate_per_hour = 0

        # Estimate samples left before session ends
        est_remaining = round(
            rate_per_hour * remaining_mins / 60, 0
        )

        print("\n  ┌─────────────────────────────────────────────────┐")
        print("  │  THIS SESSION                                   │")
        print("  ├─────────────────────────────────────────────────┤")
        print(
            f"  │  Generated   : {str(total):<6} samples"
            f"                        │"
        )
        print(
            f"  │  Passed      : {str(passed):<6} "
            f"({pass_rate}% pass rate)"
            f"              │"
        )
        print(
            f"  │  Failed      : {str(failed):<6} samples"
            f"                        │"
        )
        print(
            f"  │  Time Elapsed: {str(elapsed_mins):<6} mins"
            f"                        │"
        )
        print(
            f"  │  Time Left   : {str(remaining_mins):<6} mins"
            f"  (Colab 4hr limit)    │"
        )
        print(
            f"  │  Rate        : {str(rate_per_hour):<6} samples/hour"
            f"                   │"
        )
        print(
            f"  │  Est. More   : ~{str(int(est_remaining)):<5} samples"
            f" before session ends   │"
        )
        print("  └─────────────────────────────────────────────────┘")

    def _print_overall_stats(self, overall: dict):
        """Print total dataset statistics across all sessions."""
        total      = overall.get("total_samples", 0)
        passed     = overall.get("passed", 0)
        failed     = overall.get("failed", 0)
        review     = overall.get("review", 0)
        categories = overall.get("categories_covered", 0)
        models     = overall.get("models_used", 0)

        # Target is 50K samples
        TARGET      = 50000
        pct_done    = round(total / TARGET * 100, 1)
        bar         = self._progress_bar(pct_done)

        # First and last generation times
        first = overall.get("first_generated")
        last  = overall.get("last_generated")

        first_str = (
            first.strftime("%d %b %H:%M")
            if first else "N/A"
        )
        last_str = (
            last.strftime("%d %b %H:%M")
            if last else "N/A"
        )

        print("\n  ┌─────────────────────────────────────────────────┐")
        print("  │  TOTAL DATASET (ALL SESSIONS)                   │")
        print("  ├─────────────────────────────────────────────────┤")
        print(
            f"  │  Total Samples   : {total:,}"
            f"  /  50,000 target"
            f"             │"
        )
        print(
            f"  │  Progress        : {bar} {pct_done}%"
            f"               │"
        )
        print(
            f"  │  Passed (PASS)   : {passed:,}"
            f"                              │"
        )
        print(
            f"  │  Review (REVIEW) : {review:,}"
            f"                              │"
        )
        print(
            f"  │  Failed (FAIL)   : {failed:,}"
            f"                              │"
        )
        print(
            f"  │  Categories Done : {categories} / 33"
            f"                          │"
        )
        print(
            f"  │  Models Used     : {models} / 3"
            f"                           │"
        )
        print(
            f"  │  First Sample    : {first_str}"
            f"                         │"
        )
        print(
            f"  │  Last Sample     : {last_str}"
            f"                         │"
        )
        print("  └─────────────────────────────────────────────────┘")

    def _print_category_table(self, cat_progress: list):
        """Print per-category progress table."""
        if not cat_progress:
            print("\n  No category data yet.")
            return

        # Category targets mapping
        TARGETS = {
            ("startup_validation",  "idea_testing"):        1500,
            ("startup_validation",  "pmf_analysis"):        1500,
            ("startup_validation",  "competitor_analysis"): 1200,
            ("startup_validation",  "customer_discovery"):  1200,
            ("gtm_strategy",        "launch_planning"):     1500,
            ("gtm_strategy",        "channel_selection"):   1500,
            ("gtm_strategy",        "partnership_strategy"):1200,
            ("gtm_strategy",        "market_entry"):        1200,
            ("marketing_strategy",  "brand_positioning"):   1500,
            ("marketing_strategy",  "content_marketing"):   1500,
            ("marketing_strategy",  "social_media"):        1500,
            ("marketing_strategy",  "influencer_marketing"):1000,
            ("marketing_strategy",  "seo_strategy"):        1000,
            ("pricing_models",      "subscription_pricing"):1500,
            ("pricing_models",      "freemium_strategy"):   1200,
            ("pricing_models",      "price_sensitivity"):   1200,
            ("pricing_models",      "competitive_pricing"): 1000,
            ("sales_communication", "cold_outreach"):       1500,
            ("sales_communication", "objection_handling"):  1500,
            ("sales_communication", "sales_copy"):          1200,
            ("sales_communication", "pitch_deck_advice"):   1000,
            ("growth_strategy",     "user_acquisition"):    1500,
            ("growth_strategy",     "retention_strategy"):  1500,
            ("growth_strategy",     "referral_programs"):   1200,
            ("growth_strategy",     "expansion_strategy"):  1200,
            ("customer_support",    "support_scripts"):     1500,
            ("customer_support",    "escalation_handling"): 1200,
            ("customer_support",    "refund_scenarios"):    1200,
            ("customer_support",    "onboarding_flows"):    1000,
            ("business_decisions",  "hiring_decisions"):    1200,
            ("business_decisions",  "pivot_analysis"):      1200,
            ("business_decisions",  "budget_allocation"):   1000,
            ("business_decisions",  "vendor_selection"):     800,
        }

        print("\n  ┌─────────────────────────────────────────────────────────────┐")
        print("  │  CATEGORY PROGRESS                                          │")
        print("  ├───────────────────────┬──────────────────┬───────┬──────────┤")
        print("  │  CATEGORY             │  SUBCATEGORY     │  DONE │  TARGET  │")
        print("  ├───────────────────────┼──────────────────┼───────┼──────────┤")

        # Sort by category name
        sorted_cats = sorted(
            cat_progress,
            key=lambda x: (
                x.get("category", ""),
                x.get("subcategory", "")
            )
        )

        for row in sorted_cats:
            cat    = row.get("category", "")
            subcat = row.get("subcategory", "")
            done   = row.get("total_generated", 0)
            target = TARGETS.get((cat, subcat), 1000)
            pct    = round(done / target * 100, 0) if target else 0

            # Status icon
            if pct >= 100:
                icon = "✅"
            elif pct >= 50:
                icon = "🔄"
            elif pct > 0:
                icon = "▶️ "
            else:
                icon = "⬜"

            # Truncate long names for table
            cat_display    = cat[:21].ljust(21)
            subcat_display = subcat[:16].ljust(16)

            print(
                f"  │  {cat_display} │  {subcat_display} │"
                f"  {str(done).rjust(4)} │"
                f"  {icon} {str(pct).rjust(3)}%  │"
            )

        print("  └───────────────────────┴──────────────────┴───────┴──────────┘")

    def _print_footer(self, remaining_mins: float):
        """Print footer with next action guidance."""
        print("\n  ┌─────────────────────────────────────────────────┐")
        print("  │  NEXT ACTIONS                                   │")
        print("  ├─────────────────────────────────────────────────┤")

        if remaining_mins < 30:
            print("  │  ⚠️  Less than 30 mins left in session          │")
            print("  │  Pipeline will auto-checkpoint and pause        │")
            print("  │  Start new Colab session to continue            │")
        elif remaining_mins < 60:
            print("  │  🕐  Less than 1 hour left                      │")
            print("  │  Continue generating, checkpoint is active      │")
        else:
            print("  │  ✅  Session running normally                   │")
            print("  │  Checkpoints saving every 10 samples            │")
            print("  │  Data is safe in GCP PostgreSQL                 │")

        print("  │                                                 │")
        print("  │  To resume after session ends:                  │")
        print("  │  1. Open new Colab session                      │")
        print("  │  2. Run all setup cells                         │")
        print("  │  3. Pipeline auto-resumes from checkpoint       │")
        print("  └─────────────────────────────────────────────────┘")
        print("="*62 + "\n")

    # ─────────────────────────────────────────────
    # UTILITIES
    # ─────────────────────────────────────────────

    def _progress_bar(
        self,
        percentage: float,
        width: int = 20
    ) -> str:
        """
        Generate ASCII progress bar.

        Example: [████████░░░░░░░░░░░░] 40%
        """
        filled = int(width * percentage / 100)
        empty  = width - filled
        bar    = "█" * filled + "░" * empty
        return f"[{bar}]"

    def print_sample_preview(self, sample: dict):
        """
        Print a quick preview of a generated sample.
        Called after every 25 samples.
        """
        print("\n  ── SAMPLE PREVIEW ──────────────────────────────")
        print(
            f"  ID       : {sample.get('sample_id', 'N/A')}"
        )
        print(
            f"  Category : {sample.get('category')} → "
            f"{sample.get('subcategory')}"
        )
        print(
            f"  Model    : {sample.get('source_model')}"
        )
        print(
            f"  Score    : {sample.get('quality_score')} "
            f"({sample.get('quality_flag')})"
        )
        print(
            f"  Words    : {sample.get('word_count')}"
        )
        print(
            f"  India    : {'✅' if sample.get('has_india_context') else '❌'}"
        )

        # Show first 200 chars of instruction
        instruction = sample.get("instruction", "")
        if instruction:
            preview = instruction[:200].replace("\n", " ")
            print(f"  Q        : {preview}...")

        # Show first 150 chars of breakdown
        breakdown = sample.get("problem_breakdown", "")
        if breakdown:
            preview = breakdown[:150].replace("\n", " ")
            print(f"  A        : {preview}...")

        print("  " + "─"*50)