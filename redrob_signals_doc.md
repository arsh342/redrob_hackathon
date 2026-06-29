## **Redrob Behavioral Signals — Reference** 

This document explains the 23 behavioral signals embedded in each candidate's redrob_signals object, how they relate to candidate quality, and how they're constructed in the synthetic dataset. 

## **What are Redrob signals?** 

In a real recruiting platform, candidates generate observable behavior beyond what they list in their profile: 

- Do they actually respond to recruiter messages? 

- Have they logged in recently? 

- Did they complete the assessments they started? 

- Are recruiters saving their profile? 

- Have they completed previous interview cycles? 

These behavioral signals are often **more predictive** of whether a candidate can actually be hired than their static profile. A perfect-on-paper candidate who hasn't logged in for 6 months and has a 5% response rate is, for hiring purposes, not actually available. 

This dataset includes these signals so that ranking systems can incorporate them as a multiplier or modifier on top of skill-match scoring. 

## **The 23 signals** 

|**The 23 signals**||||
|---|---|---|---|
|**#**|**Signal**|**Range / type**|**What it measures**|
|1|profle_completeness_<br>score|0-100|How much of the<br>profle they've flled in|
|2|signup_date|date string|When they signed up<br>on Redrob|
|3|last_actve_date|date string|When they last logged<br>in|
|4|open_to_work_fag|bool|Have they marked<br>themselves available|
|5|profle_views_received<br>_30d|integer >= 0|How ofen their profle<br>has been viewed by<br>recruiters in last 30|



||||days|
|---|---|---|---|
|6|applicatons_submited<br>_30d|integer >= 0|How many roles<br>they've applied to<br>recently|
|7|recruiter_response_rat<br>e|0.0-1.0|What fracton of<br>recruiter messages<br>they reply to|
|8|avg_response_tme_ho<br>urs|number >= 0|Median tme to<br>respond to a recruiter<br>message|
|9|skill_assessment_score<br>s|dict[str, 0-100]|Per-skill Redrob<br>assessment scores|
|10|connecton_count|integer >= 0|Number of Redrob<br>connectons|
|11|endorsements_receive<br>d|integer >= 0|Total skill<br>endorsements received|
|12|notce_period_days|0-180|Their stated notce<br>period|
|13|expected_salary_range<br>_inr_lpa.min / .max|number >= 0|Salary expectatons in<br>INR lakhs per annum|
|14|preferred_work_mode|onsite/hybrid/<br>remote/fexible|Their stated work-<br>mode preference|
|15|willing_to_relocate|bool|Will they relocate if<br>needed|
|16|github_actvity_score|-1 to 100|GitHub<br>commits/contributons<br>score (-1 if no GitHub<br>linked)|
|17|search_appearance_30<br>d|integer >= 0|How ofen they show<br>up in recruiter searches|
|18|saved_by_recruiters_3<br>0d|integer >= 0|How many recruiters<br>bookmarked them in<br>last 30 days|
|19|interview_completon_<br>rate|0.0-1.0|What fracton of<br>interviews they've|



||||actually atended|
|---|---|---|---|
|20|ofer_acceptance_rate|-1 to 1.0|What fracton of ofers<br>they accepted (-1 if no<br>prior ofers)|
|21|verifed_email|bool|Whether their email<br>address is verifed|
|22|verifed_phone|bool|Whether their phone<br>number is verifed|
|23|linkedin_connected|bool|Whether their LinkedIn<br>account is connected|



