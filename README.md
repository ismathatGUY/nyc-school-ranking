# NYC School Ranking

A project that ranks NYC district schools using state test results. It cleans the data, adjusts for small schools, scores each school with z-scores, estimates how certain each rank is, and shows the results in a dashboard.

Live dashboard: https://ismathatguy.github.io/nyc-school-ranking/

By Ismael Kabore. I built it with help from AI tools (Claude and Cursor) and checked the results myself.

## What is in this repo

1. pipeline.py: cleans the data, runs the checks, scores and ranks schools
2. school_rankings_2026.csv: the ranked list with rank ranges
3. index.html: interactive page with search, borough filter, sortable table and scatter plot
4. qa_log.txt: output of the data checks
5. executive_summary.md: one page summary for leaders

## Data

NYC Public Schools grades 3 to 8 ELA and Math results, school level files, from the NYC Public Schools InfoHub test results page. The files are not included here. Download the two school level Excel files, put them in a folder called data, and keep the file names:

1. school-ela-results-public.xlsx
2. school-math-results-public.xlsx

I used the "ELA - All" and "Math - All" sheets and only 2023 to 2026, because the state changed the tests in 2023.

## How to run it

1. Install the tools: pip install pandas numpy scipy openpyxl
2. Put the two Excel files in the data folder
3. Run: python pipeline.py
4. Open index.html in a browser

## Method

1. Keep the "All Grades" row for each school and year from 2023 to 2026.
2. Convert suppressed values to blanks and drop schools with fewer than 20 tested students in either subject.
3. Check the data: no duplicates, level counts match number tested, recalculated proficiency matches reported proficiency.
4. Merge ELA and Math. 1,104 schools have both in 2026.
5. Adjust each school's proficiency rate toward the citywide rate, more strongly when fewer students were tested.
6. Convert to z-scores and average ELA and Math equally.
7. Rank schools by the combined score.
8. Simulate the test results to find a 90% rank range for each school.
9. Re-run the ranking with different choices to see if the results change.

## Main results

1. Top 10 schools have a typical rank range of about 10 places. Schools ranked 500 to 900 have about 186. Only 11% of schools have a range of 50 or less.
2. Changing weights or skipping the small school adjustment barely changes the ranking.
3. Median scores by borough: Staten Island +0.37, Queens +0.24, Brooklyn +0.04, Manhattan -0.29, Bronx -0.68.

## Limits

1. Charter schools and District 75 students are not in the source file.
2. The ranking is not adjusted for student demographics.
3. The rank ranges come from a simulation that treats year-to-year differences as random.