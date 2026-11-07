# NYC School Ranking: Executive Summary

Ismael Kabore
Data: NYC Public Schools grades 3 to 8 ELA and Math state test results, 2023 to 2026

## Bottom line

We can reliably identify the strongest and weakest schools, but we cannot reliably put the middle schools in order. I recommend reporting schools in tiers instead of exact ranks, and pairing any ranking with a view that accounts for student demographics.

## What I did

I ranked 1,104 district schools using their 2026 ELA and Math results. For each school I used the share of students scoring proficient (Level 3 or 4). Because schools with few test takers can swing a lot from one year to the next, I adjusted their rates toward the citywide average. I then put ELA and Math on the same scale using z-scores and averaged them equally. I used 2023 to 2026 data only, because the state changed the tests in 2023 and earlier years are not comparable. I excluded schools with fewer than 20 tested students in either subject.

## Key findings

1. Ranks are firm only at the top. The top 10 schools have a typical 90% rank range of about 10 places. Schools ranked 500 to 900 have a range of about 186 places. Only 11% of schools have a range of 50 places or less. A school ranked 600th could reasonably be 500th or 700th.

2. The ranking holds up when I change my choices. Weighting ELA or Math more heavily, or skipping the small school adjustment, barely changes the results. Rank correlation stayed between 0.998 and 1.000, and 97 to 99 of the top 100 schools stayed in the top 100.

3. There are large gaps between boroughs. Median scores were Staten Island +0.37, Queens +0.24, Brooklyn +0.04, Manhattan -0.29 and Bronx -0.68. Manhattan has 39 of the top 100 schools and the Bronx has 5, but the boroughs are different sizes (Manhattan 179 schools, Bronx 249), so the medians are the better comparison.

## Data quality

I checked the data before using it. There were no duplicate school-year rows, the level counts matched the number tested, and the proficiency rates I recalculated matched the reported rates exactly. Suppressed small-group values (38 ELA rows and 142 Math rows from 2023 to 2026) were excluded.

## Limits

1. Charter schools and District 75 students are not in this data file.
2. The ranking is not adjusted for demographics, so it reflects who enrolls as well as what the school adds.
3. Rank ranges come from a simulation that treats year-to-year differences as random, which is an approximation.
4. Some grades moved to computer-based testing in 2024 and 2025, which may affect year-to-year comparisons.

