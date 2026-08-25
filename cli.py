"""
CLI for LI-RADS Liver Imaging Agent: ACR LI-RADS v2018 categorization tool.
"""
import argparse
import json
import sys
from li_rads_liver_imaging_agent.models import LiverObservation, LIRADSCategory, Modality
from li_rads_liver_imaging_agent.engine import categorize, CATEGORY_INFO


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="li-rads-liver-imaging-agent",
        description="LI-RADS v2018 liver observation categorization tool.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # categorize command
    p_cat = subparsers.add_parser("categorize", help="Categorize a liver observation")
    p_cat.add_argument("--size", type=float, required=True, help="Observation size in mm")
    p_cat.add_argument("--modality", choices=["CT", "MRI", "US"], default="CT", help="Imaging modality")
    p_cat.add_argument("--ahe", action="store_true", help="Arterial hyperenhancement present")
    p_cat.add_argument("--washout", action="store_true", help="Non-peripheral washout present")
    p_cat.add_argument("--capsule", action="store_true", help="Enhancing capsule present")
    p_cat.add_argument("--growth", action="store_true", help="Threshold growth (>=50% in <=6 months)")
    p_cat.add_argument("--prior-size", type=float, default=None, help="Prior size in mm")
    p_cat.add_argument("--prior-months", type=float, default=None, help="Months since prior scan")
    p_cat.add_argument("--tumor-in-vein", action="store_true", help="Tumor in vein present")
    p_cat.add_argument("--definitely-benign", action="store_true", help="Observation is definitely benign")
    p_cat.add_argument("--malignancy-not-hcc", action="store_true", help="Features suggest malignancy not HCC")
    p_cat.add_argument("--no-risk-liver", action="store_true", help="No at-risk liver factors")
    p_cat.add_argument("--json", action="store_true", help="Output as JSON")

    # info command
    p_info = subparsers.add_parser("info", help="Show LI-RADS category information")
    p_info.add_argument("category", nargs="?", default=None, help="Category (1, 2, 3, 4, 5, M, TIV, NC)")

    args = parser.parse_args(argv)

    if args.command == "categorize":
        modality = Modality(args.modality)
        obs = LiverObservation(
            observation_id="obs_1",
            size_mm=args.size,
            modality=modality,
            arterial_hyperenhancement=args.ahe,
            non_peripheral_washout=args.washout,
            enhancing_capsule=args.capsule,
            threshold_growth=args.growth,
            prior_size_mm=args.prior_size,
            prior_months=args.prior_months,
            has_tumor_in_vein=args.tumor_in_vein,
            is_definitely_benign=args.definitely_benign,
            has_malignancy_not_hcc=args.malignancy_not_hcc,
            has_at_risk_liver=not args.no_risk_liver,
        )
        result = categorize(obs)
        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print("=" * 60)
            print(f"  LI-RADS Assessment")
            print("=" * 60)
            print(f"  Category:     {result.category.value} - {result.category_label}")
            print(f"  Size:         {result.size_mm}mm")
            print(f"  Description:  {result.description}")
            print(f"  Treatment:    {result.treatment_note}")
            print(f"  Eligible:     {'Yes' if result.treatment_eligible else 'No'}")
            print(f"\n  Major Features:")
            for feat, present in result.major_features.items():
                status = "YES" if present else "no"
                print(f"    {feat}: {status}")
            if result.ancillary_malignancy:
                print(f"\n  Ancillary (favoring malignancy): {', '.join(result.ancillary_malignancy)}")
            if result.ancillary_benignity:
                print(f"\n  Ancillary (favoring benignity): {', '.join(result.ancillary_benignity)}")
            if result.notes:
                print(f"\n  Notes:")
                for note in result.notes:
                    print(f"    - {note}")
            print("=" * 60)
        return 0

    elif args.command == "info":
        if args.category:
            cat_map = {
                "NC": LIRADSCategory.LR_NC,
                "1": LIRADSCategory.LR_1,
                "2": LIRADSCategory.LR_2,
                "3": LIRADSCategory.LR_3,
                "4": LIRADSCategory.LR_4,
                "5": LIRADSCategory.LR_5,
                "M": LIRADSCategory.LR_M,
                "TIV": LIRADSCategory.LR_TIV,
            }
            cat = cat_map.get(args.category.upper())
            if cat is None:
                print(f"Unknown category: {args.category}", file=sys.stderr)
                return 1
            info = CATEGORY_INFO[cat]
            print(f"{cat.value}: {info['label']}")
            print(f"  {info['description']}")
        else:
            for cat in LIRADSCategory:
                info = CATEGORY_INFO[cat]
                print(f"{cat.value}: {info['label']}")
                print(f"  {info['description']}")
                print()
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
