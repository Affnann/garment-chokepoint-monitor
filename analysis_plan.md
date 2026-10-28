# Analysis plan: Who Paid for the Red Sea Crisis?

Written October 28, 2026, before any comparison between the EU and Japan was computed.
Changes after this date are listed at the bottom with the reason.

## Question
After container lines diverted Asia–Europe ships away from the Red Sea in December 2023,
did the price per kilo of Bangladeshi garments arriving in the EU rise relative to the
same goods arriving in Japan, whose shipping route does not pass through the Red Sea?

## Data (importer-recorded only)
- EU-27 imports from Bangladesh, HS chapters 61 and 62, monthly, value (EUR) and weight.
  Eurostat Comext DS-045409 (all modes) and DS-059334 (by mode of transport).
- Japan imports from Bangladesh, HS 61 and 62, monthly, value (USD, CIF) and weight,
  built from HS 6-digit lines in UN Comtrade.
- Monthly average USD per EUR, Eurostat ert_bil_eur_m, to put EU values in US dollars.
- Bangladesh's own export figures (EPB) are not used: Bangladesh Bank found them
  overstated for garments from FY2022 to FY2024.

## Outcomes
1. Unit value: US dollars per kilogram (import value / net weight).
2. Volume: kilograms imported.
3. EU only: share of kilograms arriving by air.

## Comparison
- Pre window: December 2022 to November 2023. Post window: December 2023 to November 2024.
  Same calendar months in both, so seasonal patterns cancel.
- Main estimate: the change in log unit value for the EU minus the change for Japan
  (difference in differences), for HS 61 and HS 62 separately and combined.
- Inference: regress the monthly EU-minus-Japan gap in log unit value on a post-period
  dummy, with Newey-West standard errors (3 lags).

## Checks fixed in advance
- EU sea-only unit value instead of all modes (air shipments carry higher-value goods,
  so a shift to air raises the average price without any price change).
- Post window starting January 2024 instead of December 2023.
- Euro values converted at the monthly rate versus a fixed 2023 average rate.

## What the result cannot show
Import values include freight and insurance to the border (CIF). A relative rise in EU
unit values is consistent with buyers paying the higher freight; it does not show how
much of the cost exporters absorbed. Unit value per kilo also moves when the product
mix changes. The paper will say this plainly.

## Changes after writing
- October 28, 2026, after seeing the main results: added a placebo test (shock moved to
  December 2022; before = January to November 2022) to check whether EU unit values were
  already falling relative to Japan before the diversions. Not in the original plan; the
  paper reports it as an added check. Code: code/03_extra_checks.py.
- The main results came out with the opposite sign to the "buyers pay the freight" reading
  in the Question above (EU unit values fell relative to Japan). The analysis itself was not
  changed; only the interpretation in the paper follows the result.
- October 28, 2026, after release v1.0.0: the heading's working title ("Paper 4 (short
  version)") was replaced with the paper's title. Nothing else in the plan was changed.
