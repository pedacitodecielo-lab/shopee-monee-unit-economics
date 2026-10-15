# Data checks

## 1. Reported YoY vs computed YoY

| period | metric | reported % | computed % | allowed gap | ok |
|---|---|---|---|---|---|
| 2020Q1 | gmv_usd_bn | 74.3 | 77.1 | 4.1 | yes |
| 2020Q1 | gross_orders_bn | 111.2 | 111.2 | 0.3 | yes |
| 2020Q2 | gmv_usd_bn | 109.9 | 110.5 | 4.3 | yes |
| 2020Q2 | gross_orders_bn | 150.1 | 150.1 | 0.3 | yes |
| 2020Q3 | gmv_usd_bn | 102.7 | 102.2 | 3.5 | yes |
| 2020Q3 | gross_orders_bn | 130.7 | 130.7 | 0.3 | yes |
| 2020Q4 | gmv_usd_bn | 112.5 | 112.5 | 3.0 | yes |
| 2020Q4 | gross_orders_bn | 134.6 | 127.0 | 38.6 | yes |
| 2021Q1 | gmv_usd_bn | 103.2 | 103.2 | 2.6 | yes |
| 2021Q1 | gross_orders_bn | 153.0 | 155.9 | 41.1 | yes |
| 2021Q2 | gmv_usd_bn | 87.5 | 87.5 | 2.0 | yes |
| 2021Q2 | gross_orders_bn | 127.4 | 127.3 | 26.8 | yes |
| 2021Q3 | gmv_usd_bn | 80.6 | 80.6 | 1.7 | yes |
| 2021Q3 | gross_orders_bn | 123.2 | 129.2 | 21.8 | yes |
| 2021Q4 | gmv_usd_bn | 52.7 | 52.9 | 1.3 | yes |
| 2021Q4 | gross_orders_bn | 90.1 | 100.0 | 14.5 | yes |
| 2022Q1 | gmv_usd_bn | 38.7 | 38.1 | 1.1 | yes |
| 2022Q1 | gross_orders_bn | 71.3 | 72.7 | 12.5 | yes |
| 2022Q2 | gmv_usd_bn | 27.2 | 26.7 | 1.0 | yes |
| 2022Q2 | gross_orders_bn | 41.6 | 42.9 | 8.8 | yes |
| 2022Q3 | gmv_usd_bn | 13.5 | 13.7 | 0.8 | yes |
| 2022Q3 | gross_orders_bn | 19.2 | 17.6 | 6.7 | yes |
| 2023Q3 | gmv_usd_bn | 5.1 | 5.2 | 0.7 | yes |
| 2023Q3 | gross_orders_bn | 13.2 | 10.0 | 5.6 | yes |
| 2023Q4 | gmv_usd_bn | 28.6 | 28.3 | 0.8 | yes |
| 2023Q4 | gross_orders_bn | 46.0 | 47.1 | 7.4 | yes |
| 2024Q1 | gmv_usd_bn | 36.3 | 36.3 | 0.9 | yes |
| 2024Q1 | gross_orders_bn | 56.8 | 56.8 | 7.9 | yes |
| 2024Q2 | gmv_usd_bn | 29.1 | 29.1 | 0.8 | yes |
| 2024Q2 | gross_orders_bn | 40.3 | 40.3 | 6.9 | yes |
| 2024Q3 | gmv_usd_bn | 25.2 | 24.9 | 0.8 | yes |
| 2024Q3 | gross_orders_bn | 24.2 | 27.3 | 5.2 | yes |
| 2024Q4 | gmv_usd_bn | 23.5 | 23.8 | 0.7 | yes |
| 2024Q4 | gross_orders_bn | 20.1 | 20.0 | 4.6 | yes |
| 2025Q1 | gmv_usd_bn | 21.5 | 21.2 | 0.7 | yes |
| 2025Q1 | gross_orders_bn | 20.5 | 19.2 | 4.5 | yes |
| 2025Q2 | gmv_usd_bn | 28.2 | 27.9 | 0.7 | yes |
| 2025Q2 | gross_orders_bn | 28.6 | 32.0 | 4.7 | yes |
| 2025Q3 | gmv_usd_bn | 28.4 | 28.3 | 0.7 | yes |
| 2025Q3 | gross_orders_bn | 28.4 | 28.6 | 4.3 | yes |
| 2025Q4 | gmv_usd_bn | 28.6 | 28.3 | 0.6 | yes |
| 2025Q4 | gross_orders_bn | 30.5 | 33.3 | 4.0 | yes |
| 2026Q1 | gmv_usd_bn | 30.2 | 30.4 | 0.6 | yes |
| 2026Q1 | gross_orders_bn | 29.3 | 29.0 | 3.9 | yes |
| 2026Q2 | gmv_usd_bn | 28.4 | 28.5 | 0.6 | yes |
| 2026Q2 | gross_orders_bn | 27.5 | 27.3 | 3.6 | yes |

Failures: 0

## 2. Adjusted EBITDA: prior-year figure in later release vs first reported

| period | segment | first reported (US$ m) | shown a year later | difference |
|---|---|---|---|---|
| 2020Q1 | shopee | -260.0 | -264.1 | -4.1 |
| 2020Q1 | monee | -101.6 | -93.1 | +8.5 |
| 2020Q2 | shopee | -305.5 | -313.7 | -8.3 |
| 2020Q2 | monee | -110.1 | -97.5 | +12.6 |

Rows above are restatements by Sea (e.g. segment re-allocations). The model uses first-reported values.

## 3. Sum of quarters vs full-year figure

| year | metric | full year | sum of quarters | gap % |
|---|---|---|---|---|
| 2019 | gmv_usd_bn | 17.6 | 17.50 | -0.6 |
| 2019 | gross_orders_bn | not printed | | |
| 2020 | gmv_usd_bn | 35.4 | 35.40 | +0.0 |
| 2020 | gross_orders_bn | 2.8 | 2.79 | -0.5 |
| 2021 | gmv_usd_bn | 62.5 | 62.60 | +0.2 |
| 2021 | gross_orders_bn | 6.1 | 6.20 | +1.6 |
| 2022 | gmv_usd_bn | 73.5 | 73.50 | +0.0 |
| 2022 | gross_orders_bn | 7.6 | 7.60 | +0.0 |
| 2023 | gmv_usd_bn | 78.5 | 78.56 (includes derived 2023Q1-Q2) | +0.1 |
| 2023 | gross_orders_bn | 8.2 | 8.14 (includes derived 2023Q1-Q2) | -0.7 |
| 2024 | gmv_usd_bn | 100.5 | 100.60 | +0.1 |
| 2024 | gross_orders_bn | 10.9 | 10.90 | -0.0 |
| 2025 | gmv_usd_bn | 127.4 | 127.30 | -0.1 |
| 2025 | gross_orders_bn | 13.9 | 14.00 | +0.7 |

Gaps within about 3% come from Sea printing quarters rounded to 0.1 bn.

## 5. Exact core marketplace revenue vs reported core YoY

| period | reported % | computed % | ok |
|---|---|---|---|
| 2025Q1 | 39.2 | 39.2 | yes |
| 2025Q2 | 46.2 | 46.2 | yes |
| 2025Q3 | 52.8 | 52.8 | yes |
| 2025Q4 | 50.2 | 50.2 | yes |
| 2026Q1 | 61.0 | 61.0 | yes |
| 2026Q2 | 65.6 | 65.6 | yes |

## 4. Remaining gaps

