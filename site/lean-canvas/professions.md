# Professions: who gains from each way of working with agents (layer b)

Every occupation of O*NET 31.0, judged against each way of working with agents (`future-work.md`) by
`collateral-role-bridge` and ranked from greatest beneficiary to least (`crafts/chronicle/rules/collateral.md` §5). The
table below is generated; never edited by hand. It shows the future hypothesis's applicability to today and never gates
a target (d-work #696, entry 32).

- **Sources.** Tasks, task importance (IM) and consequence of error (work context 4.C.3.a.1, CX): O*NET 31.0 Database,
  U.S. Department of Labor, Employment and Training Administration (USDOL/ETA), used under the CC BY 4.0 licence.
  Exposure: Eloundou, Manning, Mishkin and Rock, "GPTs are GPTs" (2023), occupation-level human ratings, β, MIT licence,
  **H**: it moves only the order within an outcome.
- **Reading.** The verbs and objects that decide "stated" are a reading (H), made once, in the script's data
  (`crafts/chronicle/scripts/role_bridge_rules.txt`). `demanded` is broad, so within it the score does most of the
  ranking. `drifting` is empty: it needs two taxonomy versions, and one was read.
- **Regenerate.** `python3 crafts/chronicle/scripts/role_bridge.py rank <O*NET 31.0 CSV folder> --version 31.0
  --exposure-source "GPTs are GPTs (2023), human β"`, with `exposure.csv` (code, value) built from the exposure file.

Ranked by `crafts/chronicle/scripts/role_bridge.py` from O*NET 31.0 and the exposure index "GPTs are GPTs" (2023), human β; never edited by hand. 1016 occupations.

| outcome | overall | intent-specification | decision-framing | evaluation | oversight | orchestration |
|---|---|---|---|---|---|---|
| `demanded` | 856 | 606 | 394 | 702 | 563 | 421 |
| `emerging` | 5 | 49 | 95 | 35 | 76 | 106 |
| `drifting` | 0 | 0 | 0 | 0 | 0 | 0 |
| `net-cost` | 19 | 137 | 256 | 77 | 135 | 212 |
| `absent` | 43 | 131 | 178 | 109 | 149 | 184 |
| `unsourced` | 93 | 93 | 93 | 93 | 93 | 93 |

| rank | occupation | code | outcome | best way | score | intent-specification rank | decision-framing rank | evaluation rank | oversight rank | orchestration rank |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Transportation Planners | 19-3099.01 | `demanded` | intent-specification | 0.267 | 1 | 4 | 2 | 221 | 430 |
| 2 | Video Game Designers | 15-1255.01 | `demanded` | intent-specification | 0.264 | 2 | 413 | 45 | 115 | 65 |
| 3 | Operations Research Analysts | 15-2031.00 | `demanded` | evaluation | 0.219 | 8 | 69 | 1 | 51 | 51 |
| 4 | Interior Designers | 27-1025.00 | `demanded` | intent-specification | 0.214 | 3 | 158 | 238 | 627 | 197 |
| 5 | Urban and Regional Planners | 19-3051.00 | `demanded` | intent-specification | 0.207 | 4 | 28 | 36 | 231 | 33 |
| 6 | Emergency Management Directors | 11-9161.00 | `demanded` | intent-specification | 0.203 | 5 | 427 | 139 | 591 | 183 |
| 7 | Sociologists | 19-3041.00 | `demanded` | evaluation | 0.199 | 181 | 403 | 3 | 40 | 434 |
| 8 | Water/Wastewater Engineers | 17-2051.02 | `demanded` | intent-specification | 0.190 | 6 | 186 | 94 | 43 | 458 |
| 9 | Software Quality Assurance Analysts and Testers | 15-1253.00 | `demanded` | evaluation | 0.187 | 99 | 54 | 4 | 61 | 135 |
| 10 | Personal Financial Advisors | 13-2052.00 | `demanded` | intent-specification | 0.174 | 7 | 13 | 213 | 288 | 466 |
| 11 | Environmental Restoration Planners | 19-2041.02 | `demanded` | intent-specification | 0.171 | 9 | 408 | 190 | 8 | 144 |
| 12 | Statisticians | 15-2041.00 | `demanded` | evaluation | 0.169 | 72 | 74 | 5 | 241 | 439 |
| 13 | Architectural and Civil Drafters | 17-3011.00 | `demanded` | intent-specification | 0.168 | 10 | 447 | 213 | 195 | 224 |
| 14 | Budget Analysts | 13-2031.00 | `demanded` | evaluation | 0.165 | 624 | 60 | 6 | 6 | 457 |
| 15 | Landscape Architects | 17-1012.00 | `demanded` | intent-specification | 0.162 | 11 | 213 | 182 | 320 | 71 |
| 16 | Credit Analysts | 13-2041.00 | `demanded` | evaluation | 0.155 | 220 | 14 | 7 | 597 | 461 |
| 17 | Conservation Scientists | 19-1031.00 | `demanded` | intent-specification | 0.154 | 12 | 22 | 175 | 96 | 87 |
| 18 | Dispatchers, Except Police, Fire, and Ambulance | 43-5032.00 | `demanded` | orchestration | 0.153 | 614 | 411 | 196 | 89 | 1 |
| 19 | Financial Examiners | 13-2061.00 | `demanded` | evaluation | 0.150 | 242 | 9 | 8 | 2 | 14 |
| 20 | Fashion Designers | 27-1022.00 | `demanded` | intent-specification | 0.149 | 13 | 450 | 258 | 143 | 101 |
| 21 | Commercial and Industrial Designers | 27-1021.00 | `demanded` | intent-specification | 0.145 | 14 | 512 | 268 | 91 | 232 |
| 22 | Survey Researchers | 19-3022.00 | `demanded` | evaluation | 0.145 | 24 | 407 | 9 | 30 | 96 |
| 23 | Accountants and Auditors | 13-2011.00 | `demanded` | evaluation | 0.139 | 219 | 118 | 10 | 138 | 486 |
| 24 | Order Clerks | 43-4151.00 | `demanded` | evaluation | 0.138 | 223 | 72 | 11 | 155 | 431 |
| 25 | Mechanical Drafters | 17-3013.00 | `demanded` | intent-specification | 0.136 | 15 | 145 | 263 | 126 | 206 |
| 26 | Human Factors Engineers and Ergonomists | 17-2112.01 | `demanded` | evaluation | 0.136 | 56 | 180 | 12 | 290 | 234 |
| 27 | Civil Engineering Technologists and Technicians | 17-3022.00 | `demanded` | evaluation | 0.134 | 16 | 108 | 13 | 609 | 482 |
| 28 | Data Warehousing Specialists | 15-1243.01 | `demanded` | intent-specification | 0.134 | 17 | 77 | 24 | 573 | 113 |
| 29 | Training and Development Managers | 11-3131.00 | `demanded` | evaluation | 0.133 | 97 | 39 | 14 | 583 | 137 |
| 30 | Soil and Plant Scientists | 19-1013.00 | `demanded` | intent-specification | 0.131 | 18 | 132 | 400 | 183 | 454 |
| 31 | Clinical Data Managers | 15-2051.02 | `demanded` | oversight | 0.130 | 52 | 31 | 21 | 1 | 158 |
| 32 | Business Continuity Planners | 13-1199.04 | `demanded` | intent-specification | 0.130 | 19 | 140 | 46 | 135 | 462 |
| 33 | Instructional Coordinators | 25-9031.00 | `demanded` | intent-specification | 0.128 | 20 | 2 | 40 | 212 | 230 |
| 34 | Aerospace Engineers | 17-2011.00 | `demanded` | intent-specification | 0.126 | 21 | 493 | 15 | 99 | 80 |
| 35 | Climate Change Policy Analysts | 19-2041.01 | `demanded` | evaluation | 0.125 | 607 | 26 | 16 | 565 | 423 |
| 36 | Credit Counselors | 13-2071.00 | `demanded` | intent-specification | 0.123 | 22 | 3 | 165 | 577 | 438 |
| 37 | Government Property Inspectors and Investigators | 13-1041.04 | `demanded` | evaluation | 0.120 | 650 | 94 | 17 | 273 | 516 |
| 38 | Dietitians and Nutritionists | 29-1031.00 | `demanded` | intent-specification | 0.120 | 23 | 40 | 143 | 198 | 480 |
| 39 | Logistics Engineers | 13-1081.01 | `demanded` | intent-specification | 0.119 | 25 | 419 | 39 | 163 | 226 |
| 40 | Statistical Assistants | 43-9111.00 | `demanded` | evaluation | 0.118 | 612 | 75 | 18 | 136 | 98 |
| 41 | Biostatisticians | 15-2041.01 | `demanded` | intent-specification | 0.118 | 26 | 33 | 19 | 14 | 185 |
| 41 | Architects, Except Landscape and Naval | 17-1011.00 | `demanded` | intent-specification | 0.118 | 26 | 510 | 744 | 147 | 273 |
| 43 | Web and Digital Interface Designers | 15-1255.00 | `demanded` | intent-specification | 0.117 | 28 | 29 | 107 | 285 | 101 |
| 44 | Electrical and Electronics Drafters | 17-3012.00 | `demanded` | intent-specification | 0.106 | 29 | 140 | 80 | 212 | 234 |
| 45 | Environmental Compliance Inspectors | 13-1041.01 | `demanded` | evaluation | 0.105 | 627 | 41 | 20 | 80 | 98 |
| 45 | Automotive Engineers | 17-2141.02 | `demanded` | intent-specification | 0.105 | 30 | 429 | 74 | 10 | 237 |
| 47 | Energy Auditors | 47-4011.01 | `demanded` | evaluation | 0.104 | 371 | 186 | 22 | 644 | 531 |
| 48 | Editors | 27-3041.00 | `demanded` | oversight | 0.104 | 276 | 41 | 340 | 3 | 16 |
| 48 | Recreational Therapists | 29-1125.00 | `demanded` | intent-specification | 0.104 | 31 | 500 | 42 | 64 | 150 |
| 50 | Appraisers and Assessors of Real Estate | 13-2023.00 | `demanded` | evaluation | 0.104 | 367 | 433 | 23 | 604 | 469 |
| 51 | Art Directors | 27-1011.00 | `demanded` | intent-specification | 0.103 | 32 | 95 | 181 | 63 | 147 |
| 51 | Set and Exhibit Designers | 27-1027.00 | `demanded` | intent-specification | 0.103 | 32 | 481 | 359 | 223 | 116 |
| 53 | Health Informatics Specialists | 15-1211.01 | `demanded` | evaluation | 0.102 | 39 | 101 | 25 | 596 | 460 |
| 54 | Market Research Analysts and Marketing Specialists | 13-1161.00 | `demanded` | evaluation | 0.102 | 201 | 417 | 26 | 145 | 444 |
| 55 | Claims Adjusters, Examiners, and Investigators | 13-1031.00 | `demanded` | evaluation | 0.102 | 394 | 32 | 27 | 347 | 498 |
| 56 | Nuclear Engineers | 17-2161.00 | `demanded` | intent-specification | 0.101 | 34 | 143 | 156 | 33 | 571 |
| 56 | Epidemiologists | 19-1041.00 | `demanded` | intent-specification | 0.101 | 34 | 76 | 313 | 13 | 448 |
| 58 | Curators | 25-4012.00 | `demanded` | intent-specification | 0.101 | 36 | 24 | 304 | 25 | 12 |
| 59 | Public Relations Specialists | 27-3031.00 | `demanded` | intent-specification | 0.100 | 37 | 414 | 322 | 154 | 442 |
| 60 | Legal Secretaries and Administrative Assistants | 43-6012.00 | `demanded` | evaluation | 0.100 | 206 | 402 | 28 | 572 | 9 |
| 61 | Hydrologic Technicians | 19-4044.00 | `demanded` | intent-specification | 0.100 | 38 | 46 | 29 | 108 | 427 |
| 62 | Microsystems Engineers | 17-2199.06 | `demanded` | intent-specification | 0.099 | 40 | 433 | 96 | 29 | 49 |
| 63 | Fuel Cell Engineers | 17-2141.01 | `demanded` | intent-specification | 0.099 | 41 | 240 | 31 | 337 | 188 |
| 64 | Validation Engineers | 17-2112.02 | `demanded` | evaluation | 0.099 | 166 | 171 | 30 | 331 | 530 |
| 65 | Electronics Engineers, Except Computer | 17-2072.00 | `demanded` | intent-specification | 0.099 | 42 | 68 | 34 | 133 | 37 |
| 66 | Fire-Prevention and Protection Engineers | 17-2111.02 | `demanded` | evaluation | 0.096 | 43 | 438 | 32 | 194 | 128 |
| 67 | Wind Energy Development Managers | 11-9199.10 | `demanded` | evaluation | 0.095 | 48 | 85 | 33 | 44 | 8 |
| 68 | Bioengineers and Biomedical Engineers | 17-2031.00 | `demanded` | intent-specification | 0.094 | 44 | 248 | 433 | 117 | 247 |
| 68 | Hydrologists | 19-2043.00 | `demanded` | intent-specification | 0.094 | 44 | 30 | 76 | 18 | 207 |
| 70 | Media Programming Directors | 27-2012.03 | `demanded` | orchestration | 0.094 | 248 | 65 | 125 | 4 | 2 |
| 71 | Compensation and Benefits Managers | 11-3111.00 | `demanded` | intent-specification | 0.093 | 46 | 78 | 55 | 67 | 226 |
| 72 | Brownfield Redevelopment Specialists and Site Managers | 11-9199.11 | `demanded` | intent-specification | 0.093 | 47 | 457 | 215 | 617 | 212 |
| 73 | Environmental Economists | 19-3011.01 | `demanded` | decision-framing | 0.093 | 227 | 1 | 221 | 91 | 94 |
| 74 | Web Administrators | 15-1299.01 | `demanded` | evaluation | 0.091 | 163 | 38 | 35 | 72 | 165 |
| 75 | Agricultural Engineers | 17-2021.00 | `demanded` | intent-specification | 0.090 | 49 | 547 | 418 | 36 | 569 |
| 76 | Natural Sciences Managers | 11-9121.00 | `demanded` | intent-specification | 0.090 | 50 | 145 | 37 | 39 | 170 |
| 77 | Training and Development Specialists | 13-1151.00 | `demanded` | orchestration | 0.090 | 127 | 412 | 146 | 17 | 3 |
| 78 | Software Developers | 15-1252.00 | `demanded` | intent-specification | 0.089 | 51 | 152 | 100 | 28 | 108 |
| 78 | Production, Planning, and Expediting Clerks | 43-5061.00 | `demanded` | orchestration | 0.089 | 208 | 495 | 265 | 76 | 4 |
| 80 | Political Scientists | 19-3094.00 | `demanded` | evaluation | 0.088 | 325 | 12 | 38 | 584 | 445 |
| 81 | Geodetic Surveyors | 17-1022.01 | `demanded` | oversight | 0.087 | 184 | 459 | 63 | 5 | 75 |
| 82 | Blockchain Engineers | 15-1299.07 | `demanded` | intent-specification | 0.086 | 53 | 517 | 284 | 657 | 247 |
| 82 | Law Teachers, Postsecondary | 25-1112.00 | `demanded` | orchestration | 0.086 | 256 | 90 | 147 | 248 | 5 |
| 84 | Environmental Scientists and Specialists, Including Health | 19-2041.00 | `demanded` | evaluation | 0.086 | 115 | 410 | 41 | 12 | 440 |
| 85 | Rehabilitation Counselors | 21-1015.00 | `demanded` | intent-specification | 0.085 | 54 | 428 | 176 | 68 | 142 |
| 86 | Economists | 19-3011.00 | `demanded` | evaluation | 0.085 | 256 | 27 | 43 | 186 | 483 |
| 87 | Tax Examiners and Collectors, and Revenue Agents | 13-2081.00 | `demanded` | evaluation | 0.084 | 623 | 49 | 44 | 241 | 456 |
| 88 | Chief Sustainability Officers | 11-1011.03 | `demanded` | oversight | 0.084 | 309 | 161 | 90 | 7 | 203 |
| 89 | Petroleum Engineers | 17-2171.00 | `demanded` | intent-specification | 0.084 | 55 | 92 | 87 | 107 | 152 |
| 90 | Range Managers | 19-1031.02 | `demanded` | intent-specification | 0.083 | 56 | 503 | 295 | 96 | 239 |
| 91 | Solar Energy Systems Engineers | 17-2199.11 | `demanded` | intent-specification | 0.082 | 58 | 201 | 136 | 156 | 122 |
| 92 | Security Management Specialists | 13-1199.07 | `demanded` | intent-specification | 0.081 | 59 | 125 | 183 | 118 | 290 |
| 93 | Mechanical Engineers | 17-2141.00 | `demanded` | intent-specification | 0.081 | 60 | 101 | 188 | 111 | 163 |
| 94 | Telephone Operators | 43-2021.00 | `demanded` | oversight | 0.081 | 242 | 423 | 286 | 9 | 452 |
| 95 | Foreign Language and Literature Teachers, Postsecondary | 25-1124.00 | `demanded` | orchestration | 0.081 | 283 | 104 | 174 | 98 | 6 |
| 96 | Computer Programmers | 15-1251.00 | `demanded` | oversight | 0.081 | 239 | 81 | 127 | 11 | 146 |
| 97 | Public Relations Managers | 11-2032.00 | `demanded` | intent-specification | 0.081 | 61 | 437 | 382 | 124 | 473 |
| 98 | Computer Network Architects | 15-1241.00 | `demanded` | intent-specification | 0.080 | 62 | 100 | 232 | 162 | 176 |
| 99 | Mechatronics Engineers | 17-2199.05 | `demanded` | intent-specification | 0.080 | 63 | 304 | 359 | 48 | 600 |
| 100 | Document Management Specialists | 15-1299.03 | `demanded` | evaluation | 0.079 | 327 | 151 | 47 | 104 | 451 |
| 101 | Sustainability Specialists | 13-1199.05 | `demanded` | evaluation | 0.079 | 152 | 397 | 48 | 567 | 425 |
| 102 | Fire Inspectors and Investigators | 33-2021.00 | `demanded` | evaluation | 0.079 | 320 | 210 | 49 | 241 | 325 |
| 103 | Information Security Engineers | 15-1299.05 | `demanded` | evaluation | 0.079 | 344 | 148 | 50 | 22 | 38 |
| 104 | Customer Service Representatives | 43-4051.00 | `demanded` | intent-specification | 0.079 | 64 | 6 | 61 | 571 | 432 |
| 105 | Manufacturing Engineers | 17-2112.03 | `demanded` | intent-specification | 0.079 | 65 | 244 | 275 | 340 | 272 |
| 106 | Industrial Ecologists | 19-2041.03 | `demanded` | evaluation | 0.079 | 80 | 399 | 51 | 175 | 428 |
| 107 | Special Effects Artists and Animators | 27-1014.00 | `demanded` | intent-specification | 0.078 | 66 | 509 | 742 | 34 | 539 |
| 108 | Quality Control Systems Managers | 11-3051.01 | `demanded` | evaluation | 0.078 | 228 | 272 | 52 | 27 | 508 |
| 108 | Desktop Publishers | 43-9031.00 | `demanded` | intent-specification | 0.078 | 67 | 105 | 711 | 209 | 191 |
| 110 | Financial Risk Specialists | 13-2054.00 | `demanded` | intent-specification | 0.078 | 68 | 107 | 108 | 78 | 422 |
| 111 | Purchasing Agents, Except Wholesale, Retail, and Farm Products | 13-1023.00 | `demanded` | evaluation | 0.077 | 276 | 204 | 53 | 331 | 549 |
| 111 | Actuaries | 15-2011.00 | `demanded` | evaluation | 0.077 | 123 | 436 | 53 | 606 | 472 |
| 113 | Music Therapists | 29-1129.02 | `demanded` | intent-specification | 0.077 | 69 | 93 | 250 | 151 | 244 |
| 114 | Insurance Underwriters | 13-2053.00 | `demanded` | evaluation | 0.077 | 175 | 41 | 56 | 620 | 509 |
| 115 | Mathematical Science Teachers, Postsecondary | 25-1022.00 | `demanded` | orchestration | 0.076 | 288 | 130 | 189 | 276 | 7 |
| 116 | Architectural and Engineering Managers | 11-9041.00 | `demanded` | evaluation | 0.076 | 158 | 60 | 57 | 44 | 247 |
| 117 | Wind Energy Engineers | 17-2199.10 | `demanded` | oversight | 0.076 | 106 | 440 | 130 | 15 | 478 |
| 118 | Transportation Engineers | 17-2051.01 | `demanded` | evaluation | 0.075 | 90 | 528 | 58 | 86 | 200 |
| 119 | Executive Secretaries and Executive Administrative Assistants | 43-6011.00 | `demanded` | oversight | 0.075 | 239 | 98 | 160 | 16 | 27 |
| 120 | Industrial Engineers | 17-2112.00 | `demanded` | intent-specification | 0.074 | 70 | 206 | 59 | 49 | 47 |
| 121 | Computer and Information Systems Managers | 11-3021.00 | `demanded` | evaluation | 0.073 | 390 | 103 | 60 | 115 | 143 |
| 122 | Management Analysts | 13-1111.00 | `demanded` | evaluation | 0.072 | 77 | 7 | 62 | 158 | 26 |
| 123 | Financial Managers | 11-3031.00 | `demanded` | evaluation | 0.072 | 232 | 198 | 64 | 23 | 221 |
| 124 | Web Developers | 15-1254.00 | `demanded` | intent-specification | 0.072 | 71 | 22 | 101 | 158 | 225 |
| 125 | Information Technology Project Managers | 15-1299.09 | `demanded` | orchestration | 0.071 | 127 | 17 | 310 | 95 | 10 |
| 126 | Penetration Testers | 15-1299.04 | `demanded` | evaluation | 0.071 | 432 | 255 | 65 | 667 | 556 |
| 127 | Healthcare Social Workers | 21-1022.00 | `demanded` | intent-specification | 0.071 | 73 | 138 | 262 | 73 | 207 |
| 128 | Cost Estimators | 13-1051.00 | `demanded` | evaluation | 0.071 | 131 | 5 | 66 | 21 | 471 |
| 129 | Geoscientists, Except Hydrologists and Geographers | 19-2042.00 | `demanded` | evaluation | 0.071 | 162 | 256 | 67 | 367 | 494 |
| 129 | Human Resources Assistants, Except Payroll and Timekeeping | 43-4161.00 | `demanded` | evaluation | 0.071 | 320 | 48 | 67 | 605 | 470 |
| 131 | Family and Consumer Sciences Teachers, Postsecondary | 25-1192.00 | `demanded` | orchestration | 0.071 | 248 | 95 | 140 | 192 | 11 |
| 132 | Regulatory Affairs Specialists | 13-1041.07 | `demanded` | evaluation | 0.070 | 406 | 227 | 69 | 188 | 129 |
| 132 | Procurement Clerks | 43-3061.00 | `demanded` | evaluation | 0.070 | 628 | 45 | 69 | 101 | 179 |
| 134 | Mining and Geological Engineers, Including Mining Safety Engineers | 17-2151.00 | `demanded` | intent-specification | 0.070 | 74 | 150 | 120 | 75 | 103 |
| 135 | Agricultural Sciences Teachers, Postsecondary | 25-1041.00 | `demanded` | orchestration | 0.070 | 181 | 145 | 225 | 94 | 13 |
| 136 | Energy Engineers, Except Wind and Solar | 17-2199.03 | `demanded` | evaluation | 0.070 | 89 | 182 | 71 | 42 | 502 |
| 137 | Credit Authorizers, Checkers, and Clerks | 43-4041.00 | `demanded` | evaluation | 0.070 | 647 | 16 | 72 | 267 | 507 |
| 138 | Billing and Posting Clerks | 43-3021.00 | `demanded` | evaluation | 0.069 | 640 | 210 | 73 | 616 | 497 |
| 139 | Treasurers and Controllers | 11-3031.01 | `demanded` | oversight | 0.069 | 332 | 256 | 469 | 19 | 185 |
| 140 | Equal Opportunity Representatives and Officers | 13-1041.03 | `demanded` | evaluation | 0.068 | 392 | 122 | 75 | 246 | 189 |
| 140 | Database Architects | 15-1243.00 | `demanded` | intent-specification | 0.068 | 75 | 237 | 184 | 347 | 260 |
| 142 | Fundraising Managers | 11-2033.00 | `demanded` | intent-specification | 0.068 | 76 | 463 | 373 | 83 | 501 |
| 143 | Health and Safety Engineers, Except Mining Safety Engineers and Inspectors | 17-2111.00 | `demanded` | evaluation | 0.067 | 156 | 119 | 77 | 353 | 274 |
| 144 | School Psychologists | 19-3034.00 | `demanded` | evaluation | 0.067 | 211 | 448 | 78 | 613 | 489 |
| 145 | Telecommunications Engineering Specialists | 15-1241.01 | `demanded` | evaluation | 0.067 | 275 | 472 | 79 | 206 | 262 |
| 146 | Advertising and Promotions Managers | 11-2011.00 | `demanded` | intent-specification | 0.067 | 78 | 195 | 134 | 83 | 59 |
| 147 | Physicists | 19-2012.00 | `demanded` | evaluation | 0.066 | 98 | 431 | 81 | 598 | 463 |
| 147 | Health Information Technologists and Medical Registrars | 29-9021.00 | `demanded` | intent-specification | 0.066 | 79 | 8 | 81 | 20 | 85 |
| 149 | English Language and Literature Teachers, Postsecondary | 25-1123.00 | `demanded` | orchestration | 0.066 | 320 | 161 | 151 | 284 | 15 |
| 150 | Social Science Research Assistants | 19-4061.00 | `demanded` | evaluation | 0.066 | 138 | 404 | 83 | 24 | 138 |
| 151 | Medical and Health Services Managers | 11-9111.00 | `demanded` | intent-specification | 0.066 | 81 | 480 | 276 | 276 | 60 |
| 152 | Graphic Designers | 27-1024.00 | `demanded` | intent-specification | 0.065 | 82 | 117 | 714 | 608 | 481 |
| 152 | Producers and Directors | 27-2012.00 | `demanded` | intent-specification | 0.065 | 82 | 284 | 281 | 53 | 262 |
| 154 | Robotics Engineers | 17-2199.08 | `demanded` | intent-specification | 0.065 | 84 | 270 | 313 | 269 | 562 |
| 154 | Bioinformatics Scientists | 19-1029.01 | `demanded` | evaluation | 0.065 | 279 | 36 | 84 | 77 | 446 |
| 156 | Supply Chain Managers | 11-3071.04 | `demanded` | intent-specification | 0.065 | 85 | 105 | 135 | 26 | 474 |
| 157 | Office Clerks, General | 43-9061.00 | `demanded` | evaluation | 0.065 | 630 | 432 | 85 | 263 | 203 |
| 158 | Biologists | 19-1029.04 | `demanded` | intent-specification | 0.065 | 86 | 514 | 252 | 347 | 544 |
| 159 | Chemists | 19-2031.00 | `demanded` | evaluation | 0.064 | 684 | 550 | 86 | 318 | 239 |
| 160 | Zoologists and Wildlife Biologists | 19-1023.00 | `demanded` | intent-specification | 0.064 | 87 | 89 | 726 | 223 | 171 |
| 161 | Sales Representatives, Wholesale and Manufacturing, Except Technical and Scientific Products | 41-4012.00 | `demanded` | decision-framing | 0.064 | 192 | 10 | 704 | 566 | 424 |
| 162 | Search Marketing Strategists | 13-1161.01 | `demanded` | evaluation | 0.064 | 185 | 232 | 88 | 158 | 450 |
| 162 | First-Line Supervisors of Retail Sales Workers | 41-1011.00 | `demanded` | intent-specification | 0.064 | 88 | 152 | 245 | 593 | 87 |
| 164 | Quality Control Analysts | 19-4099.01 | `demanded` | evaluation | 0.063 | 682 | 173 | 89 | 113 | 329 |
| 165 | Environmental Engineers | 17-2081.00 | `demanded` | intent-specification | 0.063 | 91 | 271 | 193 | 168 | 289 |
| 166 | First-Line Supervisors of Mechanics, Installers, and Repairers | 49-1011.00 | `demanded` | evaluation | 0.062 | 445 | 277 | 91 | 74 | 141 |
| 167 | Computer and Information Research Scientists | 15-1221.00 | `demanded` | evaluation | 0.062 | 148 | 138 | 92 | 38 | 150 |
| 168 | Orthopedic Surgeons, Except Pediatric | 29-1242.00 | `demanded` | evaluation | 0.062 | 348 | 485 | 93 | 634 | 520 |
| 169 | Loan Officers | 13-2072.00 | `demanded` | decision-framing | 0.062 | 305 | 11 | 329 | 602 | 260 |
| 169 | Database Administrators | 15-1242.00 | `demanded` | evaluation | 0.062 | 104 | 70 | 94 | 85 | 155 |
| 171 | Psychiatrists | 29-1223.00 | `demanded` | evaluation | 0.062 | 144 | 491 | 97 | 642 | 529 |
| 172 | Technical Writers | 27-3042.00 | `demanded` | orchestration | 0.061 | 221 | 58 | 123 | 173 | 17 |
| 172 | Intelligence Analysts | 33-3021.06 | `demanded` | evaluation | 0.061 | 196 | 479 | 98 | 629 | 130 |
| 174 | Computer Hardware Engineers | 17-2061.00 | `demanded` | intent-specification | 0.061 | 92 | 70 | 124 | 143 | 244 |
| 174 | Anthropologists and Archeologists | 19-3091.00 | `demanded` | intent-specification | 0.061 | 92 | 215 | 199 | 294 | 455 |
| 176 | Project Management Specialists | 13-1082.00 | `demanded` | orchestration | 0.061 | 178 | 44 | 141 | 54 | 18 |
| 176 | Molecular and Cellular Biologists | 19-1029.02 | `demanded` | evaluation | 0.061 | 124 | 497 | 99 | 59 | 174 |
| 178 | Writers and Authors | 27-3043.00 | `demanded` | intent-specification | 0.060 | 94 | 396 | 328 | 202 | 109 |
| 179 | History Teachers, Postsecondary | 25-1125.00 | `demanded` | orchestration | 0.060 | 289 | 112 | 190 | 230 | 19 |
| 180 | Nanosystems Engineers | 17-2199.09 | `demanded` | intent-specification | 0.060 | 95 | 263 | 301 | 241 | 298 |
| 180 | Merchandise Displayers and Window Trimmers | 27-1026.00 | `demanded` | intent-specification | 0.060 | 95 | 487 | 735 | 637 | 524 |
| 182 | Business Intelligence Analysts | 15-2051.01 | `demanded` | evaluation | 0.060 | 171 | 115 | 102 | 600 | 464 |
| 182 | Industrial-Organizational Psychologists | 19-3032.00 | `demanded` | evaluation | 0.060 | 273 | 58 | 102 | 295 | 477 |
| 182 | Medical Secretaries and Administrative Assistants | 43-6013.00 | `demanded` | orchestration | 0.060 | 613 | 53 | 268 | 578 | 20 |
| 185 | Tax Preparers | 13-2082.00 | `demanded` | evaluation | 0.059 | 214 | 426 | 104 | 590 | 125 |
| 186 | Historians | 19-3093.00 | `demanded` | orchestration | 0.059 | 619 | 420 | 334 | 585 | 21 |
| 187 | Mental Health and Substance Abuse Social Workers | 21-1023.00 | `demanded` | intent-specification | 0.059 | 100 | 533 | 157 | 122 | 199 |
| 187 | Insurance Claims and Policy Processing Clerks | 43-9041.00 | `demanded` | evaluation | 0.059 | 625 | 166 | 105 | 592 | 126 |
| 189 | Education Administrators, Kindergarten through Secondary | 11-9032.00 | `demanded` | intent-specification | 0.059 | 101 | 67 | 154 | 60 | 41 |
| 190 | Compliance Managers | 11-9199.02 | `demanded` | oversight | 0.059 | 415 | 237 | 227 | 31 | 293 |
| 190 | Data Entry Keyers | 43-9021.00 | `demanded` | evaluation | 0.059 | 657 | 15 | 106 | 643 | 111 |
| 192 | Sales Managers | 11-2022.00 | `demanded` | oversight | 0.059 | 139 | 95 | 179 | 32 | 56 |
| 192 | Floral Designers | 27-1023.00 | `demanded` | intent-specification | 0.059 | 102 | 49 | 734 | 635 | 522 |
| 194 | Philosophy and Religion Teachers, Postsecondary | 25-1126.00 | `demanded` | orchestration | 0.058 | 319 | 125 | 202 | 245 | 22 |
| 195 | Directors, Religious Activities and Education | 21-2021.00 | `demanded` | intent-specification | 0.058 | 103 | 78 | 329 | 172 | 139 |
| 196 | Environmental Engineering Technologists and Technicians | 17-3025.00 | `demanded` | evaluation | 0.058 | 216 | 508 | 109 | 651 | 268 |
| 197 | Switchboard Operators, Including Answering Service | 43-2011.00 | `demanded` | oversight | 0.058 | 622 | 425 | 355 | 35 | 182 |
| 197 | Correspondence Clerks | 43-4021.00 | `demanded` | evaluation | 0.058 | 609 | 62 | 110 | 123 | 435 |
| 199 | Bioinformatics Technicians | 15-2099.01 | `demanded` | evaluation | 0.058 | 285 | 421 | 111 | 208 | 449 |
| 200 | Human Resources Specialists | 13-1071.00 | `demanded` | evaluation | 0.057 | 234 | 240 | 112 | 329 | 73 |
| 201 | Education Administrators, Postsecondary | 11-9033.00 | `demanded` | intent-specification | 0.057 | 105 | 240 | 307 | 57 | 148 |
| 202 | Information Security Analysts | 15-1212.00 | `demanded` | evaluation | 0.057 | 158 | 520 | 113 | 80 | 172 |
| 203 | Tutors | 25-3041.00 | `demanded` | evaluation | 0.057 | 116 | 193 | 114 | 594 | 62 |
| 204 | Purchasing Managers | 11-3061.00 | `demanded` | evaluation | 0.057 | 291 | 37 | 115 | 220 | 459 |
| 205 | Cartographers and Photogrammetrists | 17-1021.00 | `demanded` | oversight | 0.057 | 140 | 454 | 222 | 37 | 495 |
| 205 | Art, Drama, and Music Teachers, Postsecondary | 25-1121.00 | `demanded` | orchestration | 0.057 | 298 | 125 | 197 | 231 | 23 |
| 207 | Health Education Specialists | 21-1091.00 | `demanded` | intent-specification | 0.056 | 106 | 435 | 211 | 205 | 168 |
| 208 | Political Science Teachers, Postsecondary | 25-1065.00 | `demanded` | orchestration | 0.056 | 291 | 134 | 197 | 229 | 24 |
| 209 | Geographic Information Systems Technologists and Technicians | 15-1299.02 | `demanded` | intent-specification | 0.056 | 108 | 51 | 145 | 599 | 42 |
| 210 | Precision Agriculture Technicians | 19-4012.01 | `demanded` | evaluation | 0.056 | 269 | 232 | 116 | 186 | 259 |
| 211 | Cardiologists | 29-1212.00 | `demanded` | evaluation | 0.055 | 299 | 256 | 117 | 223 | 521 |
| 212 | Geothermal Production Managers | 11-3051.02 | `demanded` | intent-specification | 0.055 | 109 | 310 | 378 | 129 | 333 |
| 213 | Talent Directors | 27-2012.04 | `demanded` | evaluation | 0.055 | 309 | 121 | 118 | 264 | 512 |
| 214 | Communications Teachers, Postsecondary | 25-1122.00 | `demanded` | orchestration | 0.055 | 309 | 134 | 206 | 137 | 25 |
| 215 | Computer Systems Analysts | 15-1211.00 | `demanded` | evaluation | 0.055 | 147 | 250 | 119 | 56 | 133 |
| 216 | Interviewers, Except Eligibility and Loan | 43-4111.00 | `demanded` | evaluation | 0.054 | 639 | 456 | 120 | 615 | 496 |
| 217 | Mechanical Engineering Technologists and Technicians | 17-3027.00 | `demanded` | evaluation | 0.054 | 114 | 277 | 122 | 447 | 299 |
| 217 | Self-Enrichment Teachers | 25-3021.00 | `demanded` | intent-specification | 0.054 | 110 | 115 | 446 | 133 | 91 |
| 219 | General and Operations Managers | 11-1021.00 | `demanded` | oversight | 0.054 | 230 | 482 | 371 | 41 | 100 |
| 220 | Civil Engineers | 17-2051.00 | `demanded` | intent-specification | 0.054 | 111 | 556 | 279 | 202 | 579 |
| 221 | Secretaries and Administrative Assistants, Except Legal, Medical, and Executive | 43-6014.00 | `demanded` | orchestration | 0.054 | 618 | 186 | 409 | 304 | 28 |
| 222 | Clinical and Counseling Psychologists | 19-3033.00 | `demanded` | intent-specification | 0.054 | 112 | 182 | 249 | 351 | 563 |
| 222 | Career/Technical Education Teachers, Postsecondary | 25-1194.00 | `demanded` | intent-specification | 0.054 | 112 | 161 | 274 | 130 | 112 |
| 224 | Court, Municipal, and License Clerks | 43-4031.00 | `demanded` | evaluation | 0.053 | 385 | 204 | 126 | 192 | 154 |
| 225 | Education and Childcare Administrators, Preschool and Daycare | 11-9031.00 | `demanded` | evaluation | 0.052 | 161 | 64 | 127 | 88 | 126 |
| 226 | Data Scientists | 15-2051.00 | `demanded` | evaluation | 0.052 | 309 | 17 | 129 | 587 | 453 |
| 227 | Architecture Teachers, Postsecondary | 25-1031.00 | `demanded` | intent-specification | 0.051 | 117 | 173 | 230 | 273 | 92 |
| 228 | Farm and Home Management Educators | 25-9021.00 | `demanded` | evaluation | 0.051 | 119 | 422 | 131 | 586 | 131 |
| 229 | Dietetic Technicians | 29-2051.00 | `demanded` | oversight | 0.051 | 118 | 55 | 363 | 46 | 94 |
| 230 | Radio Frequency Identification Device Specialists | 17-2072.01 | `demanded` | evaluation | 0.051 | 265 | 57 | 132 | 653 | 255 |
| 230 | Park Naturalists | 19-1031.03 | `demanded` | orchestration | 0.051 | 129 | 441 | 715 | 250 | 29 |
| 230 | Receptionists and Information Clerks | 43-4171.00 | `demanded` | evaluation | 0.051 | 271 | 409 | 132 | 579 | 32 |
| 233 | Construction Managers | 11-9021.00 | `demanded` | oversight | 0.050 | 142 | 295 | 303 | 47 | 221 |
| 233 | Postmasters and Mail Superintendents | 11-9131.00 | `demanded` | orchestration | 0.050 | 245 | 452 | 720 | 164 | 30 |
| 235 | Geneticists | 19-1029.03 | `demanded` | intent-specification | 0.050 | 120 | 169 | 209 | 290 | 268 |
| 236 | Computer Systems Engineers/Architects | 15-1299.08 | `demanded` | intent-specification | 0.050 | 121 | 87 | 171 | 130 | 305 |
| 236 | Geography Teachers, Postsecondary | 25-1064.00 | `demanded` | orchestration | 0.050 | 344 | 200 | 237 | 126 | 31 |
| 238 | Photonics Engineers | 17-2199.07 | `demanded` | intent-specification | 0.049 | 122 | 581 | 318 | 686 | 314 |
| 239 | Solar Sales Representatives and Assessors | 41-4011.07 | `demanded` | evaluation | 0.049 | 136 | 65 | 137 | 603 | 467 |
| 239 | Payroll and Timekeeping Clerks | 43-3051.00 | `demanded` | evaluation | 0.049 | 130 | 430 | 137 | 595 | 255 |
| 241 | First-Line Supervisors of Non-Retail Sales Workers | 41-1012.00 | `demanded` | orchestration | 0.049 | 125 | 442 | 716 | 610 | 33 |
| 242 | Economics Teachers, Postsecondary | 25-1063.00 | `demanded` | orchestration | 0.049 | 327 | 158 | 228 | 266 | 35 |
| 242 | First-Line Supervisors of Office and Administrative Support Workers | 43-1011.00 | `demanded` | orchestration | 0.049 | 187 | 99 | 260 | 185 | 35 |
| 244 | Computer User Support Specialists | 15-1232.00 | `demanded` | oversight | 0.049 | 195 | 46 | 251 | 50 | 511 |
| 245 | Anthropology and Archeology Teachers, Postsecondary | 25-1061.00 | `demanded` | evaluation | 0.048 | 373 | 221 | 141 | 157 | 68 |
| 246 | Atmospheric and Space Scientists | 19-2021.00 | `demanded` | intent-specification | 0.048 | 126 | 416 | 256 | 249 | 219 |
| 247 | Weighers, Measurers, Checkers, and Samplers, Recordkeeping | 43-5111.00 | `demanded` | evaluation | 0.048 | 689 | 565 | 143 | 394 | 592 |
| 248 | News Analysts, Reporters, and Journalists | 27-3023.00 | `demanded` | evaluation | 0.048 | 610 | 133 | 147 | 575 | 45 |
| 249 | Administrative Law Judges, Adjudicators, and Hearing Officers | 23-1021.00 | `demanded` | evaluation | 0.047 | 662 | 19 | 149 | 654 | 216 |
| 250 | Automotive Engineering Technicians | 17-3027.01 | `demanded` | evaluation | 0.047 | 408 | 250 | 150 | 440 | 636 |
| 251 | Logistics Analysts | 13-1081.02 | `demanded` | evaluation | 0.047 | 233 | 172 | 152 | 79 | 115 |
| 252 | Electrical Engineers | 17-2071.00 | `demanded` | oversight | 0.047 | 135 | 526 | 345 | 52 | 176 |
| 253 | Computer Network Support Specialists | 15-1231.00 | `demanded` | evaluation | 0.047 | 658 | 499 | 153 | 365 | 533 |
| 254 | Logisticians | 13-1081.00 | `demanded` | intent-specification | 0.047 | 132 | 223 | 219 | 89 | 74 |
| 254 | Remote Sensing Scientists and Technologists | 19-2099.01 | `demanded` | evaluation | 0.047 | 380 | 227 | 154 | 65 | 120 |
| 256 | Recreation and Fitness Studies Teachers, Postsecondary | 25-1193.00 | `demanded` | orchestration | 0.046 | 342 | 193 | 243 | 273 | 39 |
| 257 | Transportation, Storage, and Distribution Managers | 11-3071.00 | `demanded` | intent-specification | 0.046 | 133 | 136 | 193 | 70 | 64 |
| 257 | Criminal Justice and Law Enforcement Teachers, Postsecondary | 25-1111.00 | `demanded` | orchestration | 0.046 | 354 | 186 | 258 | 298 | 40 |
| 259 | Facilities Managers | 11-3013.00 | `demanded` | oversight | 0.046 | 210 | 553 | 400 | 55 | 221 |
| 259 | Materials Engineers | 17-2131.00 | `demanded` | intent-specification | 0.046 | 134 | 266 | 186 | 269 | 574 |
| 261 | Remote Sensing Technicians | 19-4099.03 | `demanded` | evaluation | 0.045 | 191 | 128 | 158 | 141 | 92 |
| 262 | Archivists | 25-4011.00 | `demanded` | orchestration | 0.045 | 641 | 136 | 721 | 180 | 43 |
| 263 | Eligibility Interviewers, Government Programs | 43-4061.00 | `demanded` | evaluation | 0.045 | 621 | 82 | 159 | 228 | 49 |
| 264 | Patient Representatives | 29-2099.08 | `demanded` | decision-framing | 0.045 | 631 | 20 | 713 | 607 | 479 |
| 265 | Social and Community Service Managers | 11-9151.00 | `demanded` | evaluation | 0.045 | 369 | 498 | 161 | 126 | 532 |
| 265 | Business Teachers, Postsecondary | 25-1011.00 | `demanded` | orchestration | 0.045 | 351 | 185 | 256 | 334 | 44 |
| 267 | Insurance Appraisers, Auto Damage | 13-1032.00 | `demanded` | evaluation | 0.045 | 635 | 21 | 162 | 614 | 492 |
| 267 | Medical Records Specialists | 29-2072.00 | `demanded` | evaluation | 0.045 | 626 | 87 | 162 | 188 | 60 |
| 269 | Private Detectives and Investigators | 33-9021.00 | `demanded` | evaluation | 0.045 | 664 | 518 | 164 | 267 | 547 |
| 270 | Regulatory Affairs Managers | 11-9199.01 | `demanded` | intent-specification | 0.044 | 137 | 458 | 223 | 110 | 265 |
| 270 | Area, Ethnic, and Cultural Studies Teachers, Postsecondary | 25-1062.00 | `demanded` | orchestration | 0.044 | 362 | 192 | 263 | 320 | 45 |
| 272 | Security Managers | 11-3013.01 | `demanded` | oversight | 0.044 | 172 | 266 | 305 | 58 | 174 |
| 272 | Paralegals and Legal Assistants | 23-2011.00 | `demanded` | evaluation | 0.044 | 346 | 496 | 165 | 646 | 135 |
| 274 | Reservation and Transportation Ticket Agents and Travel Clerks | 43-4181.00 | `demanded` | orchestration | 0.044 | 398 | 215 | 422 | 380 | 48 |
| 275 | Aerospace Engineering and Operations Technologists and Technicians | 17-3021.00 | `demanded` | evaluation | 0.044 | 291 | 650 | 167 | 724 | 660 |
| 276 | Compensation, Benefits, and Job Analysis Specialists | 13-1141.00 | `demanded` | evaluation | 0.044 | 183 | 83 | 168 | 342 | 513 |
| 276 | Librarians and Media Collections Specialists | 25-4022.00 | `demanded` | evaluation | 0.044 | 143 | 158 | 168 | 140 | 447 |
| 278 | Clinical Research Coordinators | 11-9121.01 | `demanded` | evaluation | 0.044 | 327 | 466 | 170 | 236 | 181 |
| 279 | Animal Scientists | 19-1011.00 | `demanded` | decision-framing | 0.044 | 615 | 25 | 709 | 62 | 441 |
| 279 | Advertising Sales Agents | 41-3011.00 | `demanded` | intent-specification | 0.044 | 141 | 91 | 708 | 580 | 153 |
| 281 | Fraud Examiners, Investigators and Analysts | 13-2099.04 | `demanded` | evaluation | 0.043 | 357 | 152 | 172 | 600 | 464 |
| 282 | Loss Prevention Managers | 11-9199.08 | `demanded` | evaluation | 0.043 | 669 | 156 | 173 | 91 | 551 |
| 283 | Sociology Teachers, Postsecondary | 25-1067.00 | `demanded` | orchestration | 0.042 | 366 | 203 | 273 | 165 | 52 |
| 284 | Water Resource Specialists | 11-9121.02 | `demanded` | oversight | 0.042 | 204 | 177 | 245 | 66 | 487 |
| 285 | Biomass Power Plant Managers | 11-3051.04 | `demanded` | intent-specification | 0.042 | 145 | 612 | 319 | 204 | 325 |
| 285 | Financial Quantitative Analysts | 13-2099.01 | `demanded` | evaluation | 0.042 | 333 | 130 | 176 | 318 | 491 |
| 287 | Library Science Teachers, Postsecondary | 25-1082.00 | `demanded` | orchestration | 0.042 | 353 | 167 | 260 | 296 | 53 |
| 288 | Title Examiners, Abstractors, and Searchers | 23-2093.00 | `demanded` | evaluation | 0.042 | 439 | 169 | 178 | 391 | 300 |
| 288 | Adult Basic Education, Adult Secondary Education, and English as a Second Language Instructors | 25-3011.00 | `demanded` | orchestration | 0.042 | 150 | 51 | 281 | 149 | 54 |
| 290 | Meeting, Convention, and Event Planners | 13-1121.00 | `demanded` | evaluation | 0.042 | 170 | 167 | 179 | 309 | 209 |
| 291 | Social Work Teachers, Postsecondary | 25-1113.00 | `demanded` | orchestration | 0.041 | 365 | 199 | 277 | 145 | 55 |
| 292 | Orthodontists | 29-1023.00 | `demanded` | intent-specification | 0.041 | 146 | 590 | 767 | 691 | 607 |
| 293 | Media Technical Directors/Managers | 27-2012.05 | `demanded` | oversight | 0.041 | 416 | 551 | 756 | 68 | 160 |
| 294 | Recycling Coordinators | 53-1042.01 | `demanded` | oversight | 0.041 | 318 | 501 | 438 | 71 | 162 |
| 295 | Fabric and Apparel Patternmakers | 51-6092.00 | `demanded` | intent-specification | 0.041 | 148 | 635 | 538 | 718 | 650 |
| 296 | Speech-Language Pathologists | 29-1127.00 | `demanded` | intent-specification | 0.041 | 151 | 266 | 292 | 401 | 560 |
| 297 | Bill and Account Collectors | 43-3011.00 | `demanded` | evaluation | 0.040 | 667 | 524 | 185 | 280 | 120 |
| 298 | Astronomers | 19-2011.00 | `demanded` | evaluation | 0.040 | 380 | 439 | 186 | 118 | 476 |
| 298 | Computer Science Teachers, Postsecondary | 25-1021.00 | `demanded` | orchestration | 0.040 | 225 | 215 | 289 | 82 | 56 |
| 300 | Poets, Lyricists and Creative Writers | 27-3043.05 | `demanded` | intent-specification | 0.040 | 153 | 395 | 703 | 564 | 58 |
| 300 | Occupational Therapists | 29-1122.00 | `demanded` | intent-specification | 0.040 | 153 | 33 | 278 | 658 | 118 |
| 302 | Investment Fund Managers | 11-3031.03 | `demanded` | evaluation | 0.040 | 428 | 543 | 192 | 383 | 565 |
| 303 | Marine Engineers and Naval Architects | 17-2121.00 | `demanded` | intent-specification | 0.039 | 155 | 328 | 233 | 236 | 232 |
| 304 | Foresters | 19-1032.00 | `demanded` | intent-specification | 0.039 | 156 | 295 | 755 | 112 | 572 |
| 305 | Marketing Managers | 11-2021.00 | `demanded` | intent-specification | 0.039 | 158 | 223 | 298 | 153 | 84 |
| 306 | Proofreaders and Copy Markers | 43-9081.00 | `demanded` | evaluation | 0.039 | 616 | 414 | 195 | 581 | 442 |
| 307 | Spa Managers | 11-9179.02 | `demanded` | orchestration | 0.039 | 380 | 468 | 289 | 170 | 63 |
| 308 | Medical Transcriptionists | 31-9094.00 | `demanded` | evaluation | 0.039 | 687 | 264 | 199 | 682 | 276 |
| 309 | Financial and Investment Analysts | 13-2051.00 | `demanded` | intent-specification | 0.038 | 164 | 401 | 344 | 215 | 433 |
| 309 | Sales Engineers | 41-9031.00 | `demanded` | intent-specification | 0.038 | 164 | 191 | 406 | 269 | 475 |
| 311 | Food Science Technicians | 19-4013.00 | `demanded` | evaluation | 0.038 | 423 | 231 | 201 | 363 | 580 |
| 312 | Teaching Assistants, Postsecondary | 25-9044.00 | `demanded` | orchestration | 0.038 | 651 | 483 | 384 | 632 | 66 |
| 313 | Wholesale and Retail Buyers, Except Farm Products | 13-1022.00 | `demanded` | evaluation | 0.038 | 633 | 110 | 202 | 215 | 488 |
| 313 | Broadcast Announcers and Radio Disc Jockeys | 27-3011.00 | `demanded` | decision-framing | 0.038 | 661 | 35 | 743 | 652 | 541 |
| 315 | Library Technicians | 25-4031.00 | `demanded` | evaluation | 0.038 | 166 | 186 | 204 | 316 | 238 |
| 316 | Occupational Health and Safety Technicians | 19-5012.00 | `demanded` | evaluation | 0.038 | 421 | 213 | 205 | 694 | 616 |
| 316 | Education Teachers, Postsecondary | 25-1081.00 | `demanded` | orchestration | 0.038 | 374 | 227 | 298 | 309 | 67 |
| 318 | Elementary School Teachers, Except Special Education | 25-2021.00 | `demanded` | intent-specification | 0.038 | 168 | 210 | 517 | 223 | 71 |
| 319 | Environmental Science and Protection Technicians, Including Health | 19-4042.00 | `demanded` | evaluation | 0.038 | 336 | 264 | 206 | 106 | 540 |
| 319 | Physics Teachers, Postsecondary | 25-1054.00 | `demanded` | orchestration | 0.038 | 384 | 247 | 302 | 177 | 69 |
| 319 | Bookkeeping, Accounting, and Auditing Clerks | 43-3031.00 | `demanded` | evaluation | 0.038 | 668 | 525 | 206 | 662 | 550 |
| 322 | Human Resources Managers | 11-3121.00 | `demanded` | intent-specification | 0.037 | 169 | 56 | 220 | 212 | 163 |
| 323 | Brokerage Clerks | 43-4011.00 | `demanded` | orchestration | 0.037 | 620 | 424 | 218 | 588 | 70 |
| 324 | Traffic Technicians | 53-6041.00 | `demanded` | oversight | 0.037 | 197 | 577 | 305 | 86 | 599 |
| 325 | Pediatric Surgeons | 29-1243.00 | `demanded` | evaluation | 0.037 | 374 | 486 | 209 | 636 | 523 |
| 326 | Genetic Counselors | 29-9092.00 | `demanded` | evaluation | 0.036 | 282 | 521 | 212 | 659 | 253 |
| 327 | Buyers and Purchasing Agents, Farm Products | 13-1021.00 | `demanded` | evaluation | 0.036 | 677 | 541 | 216 | 231 | 178 |
| 327 | Library Assistants, Clerical | 43-4121.00 | `demanded` | intent-specification | 0.036 | 173 | 227 | 324 | 329 | 253 |
| 329 | Non-Destructive Testing Specialists | 17-3029.01 | `demanded` | evaluation | 0.036 | 720 | 626 | 217 | 408 | 639 |
| 330 | Forest and Conservation Technicians | 19-4071.00 | `demanded` | intent-specification | 0.036 | 174 | 206 | 517 | 113 | 606 |
| 331 | Atmospheric, Earth, Marine, and Space Sciences Teachers, Postsecondary | 25-1051.00 | `demanded` | orchestration | 0.035 | 377 | 240 | 238 | 184 | 75 |
| 332 | Middle School Teachers, Except Special and Career/Technical Education | 25-2022.00 | `demanded` | intent-specification | 0.035 | 176 | 180 | 500 | 196 | 117 |
| 332 | Model Makers, Wood | 51-7031.00 | `demanded` | intent-specification | 0.035 | 176 | 619 | 482 | 708 | 633 |
| 334 | Fitness and Wellness Coordinators | 11-9179.01 | `demanded` | oversight | 0.035 | 408 | 110 | 283 | 99 | 107 |
| 334 | Engineering Teachers, Postsecondary | 25-1032.00 | `demanded` | orchestration | 0.035 | 390 | 244 | 245 | 173 | 77 |
| 336 | Entertainment and Recreation Managers, Except Gambling | 11-9072.00 | `demanded` | intent-specification | 0.035 | 179 | 226 | 749 | 666 | 81 |
| 337 | Orthoptists | 29-1299.02 | `demanded` | intent-specification | 0.035 | 180 | 476 | 349 | 625 | 515 |
| 338 | Audiologists | 29-1181.00 | `demanded` | oversight | 0.035 | 252 | 464 | 292 | 102 | 503 |
| 338 | Emergency Medical Technicians | 29-2042.00 | `demanded` | oversight | 0.035 | 653 | 123 | 356 | 102 | 183 |
| 340 | Property, Real Estate, and Community Association Managers | 11-9141.00 | `demanded` | evaluation | 0.035 | 316 | 503 | 224 | 358 | 167 |
| 340 | Forestry and Conservation Science Teachers, Postsecondary | 25-1043.00 | `demanded` | orchestration | 0.035 | 388 | 261 | 316 | 177 | 78 |
| 342 | New Accounts Clerks | 43-4141.00 | `demanded` | evaluation | 0.035 | 637 | 453 | 225 | 196 | 209 |
| 343 | First-Line Supervisors of Helpers, Laborers, and Material Movers, Hand | 53-1042.00 | `demanded` | evaluation | 0.034 | 327 | 527 | 228 | 168 | 194 |
| 344 | Electrical and Electronic Engineering Technologists and Technicians | 17-3023.00 | `demanded` | intent-specification | 0.034 | 185 | 113 | 307 | 158 | 209 |
| 344 | Food Scientists and Technologists | 19-1012.00 | `demanded` | evaluation | 0.034 | 309 | 119 | 230 | 650 | 537 |
| 344 | Environmental Science Teachers, Postsecondary | 25-1053.00 | `demanded` | orchestration | 0.034 | 388 | 244 | 243 | 180 | 79 |
| 347 | Psychology Teachers, Postsecondary | 25-1066.00 | `demanded` | oversight | 0.034 | 392 | 254 | 319 | 104 | 81 |
| 348 | First-Line Supervisors of Entertainment and Recreation Workers, Except Gambling Services | 39-1014.00 | `demanded` | orchestration | 0.034 | 258 | 221 | 271 | 118 | 81 |
| 349 | Industrial Engineering Technologists and Technicians | 17-3026.00 | `demanded` | evaluation | 0.034 | 309 | 310 | 234 | 677 | 342 |
| 349 | Inspectors, Testers, Sorters, Samplers, and Weighers | 51-9061.00 | `demanded` | evaluation | 0.034 | 704 | 225 | 234 | 456 | 614 |
| 351 | Biofuels/Biodiesel Technology and Product Development Managers | 11-9041.01 | `demanded` | intent-specification | 0.033 | 188 | 554 | 449 | 234 | 576 |
| 352 | Administrative Services Managers | 11-3012.00 | `demanded` | intent-specification | 0.033 | 189 | 143 | 236 | 108 | 89 |
| 353 | Biological Science Teachers, Postsecondary | 25-1042.00 | `demanded` | orchestration | 0.033 | 387 | 253 | 312 | 190 | 86 |
| 354 | Kindergarten Teachers, Except Special Education | 25-2012.00 | `demanded` | intent-specification | 0.033 | 190 | 232 | 534 | 261 | 113 |
| 355 | Geological Technicians, Except Hydrologic Technicians | 19-4043.00 | `demanded` | evaluation | 0.033 | 399 | 306 | 238 | 326 | 575 |
| 355 | Lawyers | 23-1011.00 | `demanded` | evaluation | 0.033 | 290 | 562 | 238 | 679 | 586 |
| 355 | Judicial Law Clerks | 23-1012.00 | `demanded` | evaluation | 0.033 | 291 | 108 | 238 | 622 | 239 |
| 358 | Career/Technical Education Teachers, Secondary School | 25-2032.00 | `demanded` | intent-specification | 0.032 | 193 | 248 | 752 | 254 | 262 |
| 359 | Art Therapists | 29-1129.01 | `demanded` | intent-specification | 0.032 | 194 | 292 | 335 | 370 | 296 |
| 360 | Tellers | 43-3071.00 | `demanded` | evaluation | 0.032 | 336 | 310 | 248 | 675 | 577 |
| 361 | Geothermal Technicians | 49-9099.01 | `demanded` | intent-specification | 0.032 | 197 | 325 | 779 | 201 | 350 |
| 362 | Farmers, Ranchers, and Other Agricultural Managers | 11-9013.00 | `demanded` | intent-specification | 0.032 | 199 | 587 | 550 | 171 | 278 |
| 362 | Real Estate Brokers | 41-9021.00 | `demanded` | oversight | 0.032 | 634 | 448 | 374 | 118 | 489 |
| 364 | Computer Numerically Controlled Tool Programmers | 51-9162.00 | `demanded` | evaluation | 0.031 | 274 | 86 | 252 | 130 | 270 |
| 365 | Food Service Managers | 11-9051.00 | `demanded` | evaluation | 0.031 | 437 | 140 | 254 | 179 | 97 |
| 365 | Taxi Drivers | 53-3054.00 | `demanded` | orchestration | 0.031 | 649 | 475 | 729 | 624 | 90 |
| 367 | Probation Officers and Correctional Treatment Specialists | 21-1092.00 | `demanded` | evaluation | 0.031 | 336 | 177 | 255 | 370 | 200 |
| 367 | Special Education Teachers, Elementary School | 25-2056.00 | `demanded` | intent-specification | 0.031 | 200 | 298 | 405 | 227 | 243 |
| 369 | Fundraisers | 13-1131.00 | `demanded` | intent-specification | 0.031 | 201 | 443 | 717 | 124 | 484 |
| 370 | Advanced Practice Psychiatric Nurses | 29-1141.02 | `demanded` | intent-specification | 0.031 | 203 | 545 | 289 | 673 | 568 |
| 371 | Concierges | 39-6012.00 | `demanded` | intent-specification | 0.030 | 205 | 398 | 705 | 568 | 426 |
| 372 | Secondary School Teachers, Except Special and Career/Technical Education | 25-2031.00 | `demanded` | intent-specification | 0.030 | 206 | 179 | 732 | 283 | 145 |
| 373 | Agents and Business Managers of Artists, Performers, and Athletes | 13-1011.00 | `demanded` | evaluation | 0.029 | 666 | 522 | 266 | 661 | 215 |
| 373 | Calibration Technologists and Technicians | 17-3028.00 | `demanded` | evaluation | 0.029 | 367 | 614 | 266 | 707 | 630 |
| 375 | Travel Agents | 41-3041.00 | `demanded` | intent-specification | 0.029 | 209 | 503 | 740 | 648 | 535 |
| 375 | Public Safety Telecommunicators | 43-5031.00 | `demanded` | oversight | 0.029 | 675 | 540 | 459 | 138 | 561 |
| 377 | Telemarketers | 41-9041.00 | `demanded` | orchestration | 0.029 | 617 | 418 | 710 | 582 | 104 |
| 378 | Health Specialties Teachers, Postsecondary | 25-1071.00 | `demanded` | orchestration | 0.029 | 408 | 259 | 342 | 351 | 105 |
| 379 | Lodging Managers | 11-9081.00 | `demanded` | orchestration | 0.029 | 403 | 502 | 739 | 345 | 106 |
| 379 | Travel Guides | 39-7012.00 | `demanded` | evaluation | 0.029 | 343 | 474 | 268 | 623 | 214 |
| 381 | Chief Executives | 11-1011.00 | `demanded` | oversight | 0.029 | 317 | 62 | 364 | 141 | 247 |
| 381 | Insurance Sales Agents | 41-3021.00 | `demanded` | intent-specification | 0.029 | 212 | 73 | 382 | 148 | 506 |
| 383 | Mathematicians | 15-2021.00 | `demanded` | intent-specification | 0.029 | 213 | 405 | 272 | 574 | 436 |
| 384 | Geographers | 19-3092.00 | `demanded` | orchestration | 0.028 | 276 | 446 | 719 | 612 | 109 |
| 385 | Hotel, Motel, and Resort Desk Clerks | 43-4081.00 | `demanded` | intent-specification | 0.028 | 215 | 445 | 718 | 307 | 226 |
| 386 | Substance Abuse and Behavioral Disorder Counselors | 21-1011.00 | `demanded` | intent-specification | 0.028 | 216 | 581 | 368 | 414 | 318 |
| 386 | Cooks, Private Household | 35-2013.00 | `demanded` | intent-specification | 0.028 | 216 | 537 | 753 | 297 | 559 |
| 388 | Low Vision Therapists, Orientation and Mobility Specialists, and Vision Rehabilitation Therapists | 29-1122.01 | `demanded` | evaluation | 0.028 | 226 | 165 | 279 | 394 | 587 |
| 389 | Gambling Surveillance Officers and Gambling Investigators | 33-9031.00 | `demanded` | oversight | 0.027 | 706 | 598 | 398 | 150 | 617 |
| 390 | Audio and Video Technicians | 27-4011.00 | `demanded` | intent-specification | 0.027 | 222 | 157 | 500 | 660 | 160 |
| 390 | Preventive Medicine Physicians | 29-1229.05 | `demanded` | oversight | 0.027 | 331 | 272 | 365 | 152 | 189 |
| 392 | Craft Artists | 27-1012.00 | `demanded` | intent-specification | 0.027 | 223 | 164 | 736 | 638 | 526 |
| 393 | Electrical and Electronics Repairers, Commercial and Industrial Equipment | 49-2094.00 | `demanded` | evaluation | 0.027 | 466 | 309 | 284 | 704 | 265 |
| 394 | Word Processors and Typists | 43-9022.00 | `demanded` | evaluation | 0.027 | 252 | 492 | 286 | 645 | 239 |
| 395 | Compliance Officers | 13-1041.00 | `demanded` | evaluation | 0.026 | 659 | 148 | 288 | 647 | 534 |
| 395 | Solar Energy Installation Managers | 47-1011.03 | `demanded` | orchestration | 0.026 | 285 | 620 | 296 | 303 | 118 |
| 397 | Special Education Teachers, Middle School | 25-2057.00 | `demanded` | intent-specification | 0.026 | 229 | 277 | 454 | 246 | 191 |
| 398 | Agricultural Inspectors | 45-2011.00 | `demanded` | evaluation | 0.026 | 234 | 182 | 294 | 218 | 591 |
| 399 | Industrial Production Managers | 11-3051.00 | `demanded` | orchestration | 0.026 | 417 | 129 | 351 | 175 | 123 |
| 400 | Chemistry Teachers, Postsecondary | 25-1052.00 | `demanded` | orchestration | 0.025 | 420 | 290 | 358 | 240 | 124 |
| 400 | Costume Attendants | 39-3092.00 | `demanded` | intent-specification | 0.025 | 231 | 173 | 366 | 190 | 284 |
| 402 | Coroners | 13-1041.06 | `demanded` | oversight | 0.025 | 683 | 549 | 754 | 165 | 570 |
| 402 | Network and Computer Systems Administrators | 15-1244.00 | `demanded` | oversight | 0.025 | 300 | 80 | 319 | 165 | 166 |
| 402 | Opticians, Dispensing | 29-2081.00 | `demanded` | evaluation | 0.025 | 680 | 544 | 297 | 377 | 566 |
| 405 | Labor Relations Specialists | 13-1075.00 | `demanded` | evaluation | 0.025 | 307 | 282 | 298 | 257 | 286 |
| 406 | Jewelers and Precious Stone and Metal Workers | 51-9071.00 | `demanded` | intent-specification | 0.025 | 236 | 335 | 530 | 721 | 653 |
| 407 | Surveying and Mapping Technicians | 17-3031.00 | `demanded` | intent-specification | 0.024 | 237 | 494 | 378 | 257 | 285 |
| 407 | Occupational Therapy Assistants | 31-2011.00 | `demanded` | intent-specification | 0.024 | 237 | 575 | 512 | 314 | 597 |
| 409 | Digital Forensics Analysts | 15-1299.06 | `demanded` | evaluation | 0.024 | 380 | 113 | 307 | 631 | 518 |
| 410 | Special Education Teachers, Kindergarten | 25-2055.00 | `demanded` | intent-specification | 0.024 | 239 | 538 | 412 | 252 | 252 |
| 410 | First-Line Supervisors of Construction Trades and Extraction Workers | 47-1011.00 | `demanded` | orchestration | 0.024 | 377 | 206 | 413 | 399 | 132 |
| 412 | First-Line Supervisors of Material-Moving Machine and Vehicle Operators | 53-1043.00 | `demanded` | orchestration | 0.024 | 434 | 195 | 367 | 386 | 133 |
| 413 | Medical and Clinical Laboratory Technologists | 29-2011.00 | `demanded` | evaluation | 0.024 | 751 | 319 | 311 | 322 | 685 |
| 414 | Social and Human Service Assistants | 21-1093.00 | `demanded` | intent-specification | 0.024 | 242 | 513 | 410 | 655 | 543 |
| 415 | Online Merchants | 13-1199.06 | `demanded` | intent-specification | 0.024 | 245 | 201 | 433 | 299 | 244 |
| 415 | Nanotechnology Engineering Technologists and Technicians | 17-3026.01 | `demanded` | evaluation | 0.024 | 421 | 530 | 313 | 254 | 552 |
| 415 | Educational, Guidance, and Career Counselors and Advisors | 21-1012.00 | `demanded` | intent-specification | 0.024 | 245 | 215 | 372 | 367 | 343 |
| 418 | Sales Representatives of Services, Except Advertising, Insurance, Financial Services, and Travel | 41-3091.00 | `demanded` | decision-framing | 0.023 | 629 | 84 | 712 | 200 | 467 |
| 419 | Career/Technical Education Teachers, Middle School | 25-2023.00 | `demanded` | intent-specification | 0.023 | 250 | 215 | 750 | 323 | 179 |
| 419 | Exercise Physiologists | 29-1128.00 | `demanded` | evaluation | 0.023 | 396 | 314 | 317 | 680 | 588 |
| 419 | Models | 41-9012.00 | `demanded` | oversight | 0.023 | 643 | 461 | 723 | 182 | 139 |
| 422 | Arbitrators, Mediators, and Conciliators | 23-1022.00 | `demanded` | intent-specification | 0.023 | 251 | 232 | 414 | 630 | 279 |
| 423 | Umpires, Referees, and Other Sports Officials | 27-2023.00 | `demanded` | evaluation | 0.023 | 700 | 277 | 322 | 690 | 300 |
| 424 | Funeral Home Managers | 11-9171.00 | `demanded` | intent-specification | 0.023 | 254 | 259 | 341 | 250 | 200 |
| 425 | Biochemists and Biophysicists | 19-1021.00 | `demanded` | intent-specification | 0.023 | 255 | 276 | 494 | 236 | 558 |
| 426 | Special Education Teachers, Preschool | 25-2051.00 | `demanded` | intent-specification | 0.022 | 258 | 523 | 425 | 339 | 325 |
| 427 | Shipping, Receiving, and Inventory Clerks | 43-5071.00 | `demanded` | evaluation | 0.022 | 660 | 506 | 325 | 649 | 536 |
| 428 | Pediatricians, General | 29-1221.00 | `demanded` | evaluation | 0.022 | 370 | 584 | 326 | 424 | 603 |
| 428 | Makeup Artists, Theatrical and Performance | 39-5091.00 | `demanded` | evaluation | 0.022 | 264 | 552 | 326 | 674 | 573 |
| 428 | Hydroelectric Plant Technicians | 51-8013.04 | `demanded` | intent-specification | 0.022 | 260 | 780 | 577 | 477 | 775 |
| 431 | Patternmakers, Wood | 51-7032.00 | `demanded` | intent-specification | 0.022 | 261 | 558 | 757 | 676 | 582 |
| 432 | Sales Representatives, Wholesale and Manufacturing, Technical and Scientific Products | 41-4011.00 | `demanded` | orchestration | 0.022 | 265 | 215 | 429 | 589 | 148 |
| 433 | Mental Health Counselors | 21-1014.00 | `demanded` | intent-specification | 0.022 | 262 | 611 | 376 | 487 | 311 |
| 434 | Orthotists and Prosthetists | 29-2091.00 | `demanded` | intent-specification | 0.021 | 263 | 284 | 773 | 702 | 625 |
| 435 | Surveyors | 17-1022.00 | `demanded` | oversight | 0.021 | 307 | 547 | 331 | 198 | 304 |
| 435 | Preschool Teachers, Except Special Education | 25-2011.00 | `demanded` | intent-specification | 0.021 | 265 | 272 | 558 | 316 | 191 |
| 435 | Special Education Teachers, Secondary School | 25-2058.00 | `demanded` | intent-specification | 0.021 | 265 | 288 | 538 | 323 | 282 |
| 438 | Hydroelectric Production Managers | 11-3051.06 | `demanded` | intent-specification | 0.021 | 269 | 637 | 465 | 309 | 279 |
| 439 | Gambling and Sports Book Writers and Runners | 39-3012.00 | `demanded` | evaluation | 0.021 | 678 | 542 | 331 | 671 | 564 |
| 440 | Appraisers of Personal and Business Property | 13-2022.00 | `demanded` | intent-specification | 0.021 | 271 | 471 | 728 | 621 | 510 |
| 441 | Marriage and Family Therapists | 21-1013.00 | `demanded` | evaluation | 0.021 | 346 | 152 | 333 | 688 | 297 |
| 442 | Parking Enforcement Workers | 33-3041.00 | `demanded` | evaluation | 0.021 | 685 | 266 | 335 | 380 | 333 |
| 443 | Construction and Building Inspectors | 47-4011.00 | `demanded` | evaluation | 0.020 | 394 | 322 | 337 | 464 | 689 |
| 443 | Security and Fire Alarm Systems Installers | 49-2098.00 | `demanded` | evaluation | 0.020 | 423 | 325 | 337 | 733 | 675 |
| 445 | First-Line Supervisors of Food Preparation and Serving Workers | 35-1012.00 | `demanded` | intent-specification | 0.020 | 280 | 310 | 339 | 264 | 156 |
| 446 | Chemical Technicians | 19-4031.00 | `demanded` | intent-specification | 0.020 | 281 | 591 | 479 | 290 | 608 |
| 447 | Nannies | 39-9011.01 | `demanded` | orchestration | 0.020 | 690 | 566 | 759 | 406 | 157 |
| 448 | Occupational Health and Safety Specialists | 19-5011.00 | `demanded` | oversight | 0.020 | 360 | 275 | 395 | 207 | 309 |
| 448 | Chefs and Head Cooks | 35-1011.00 | `demanded` | orchestration | 0.020 | 305 | 572 | 488 | 299 | 159 |
| 448 | Light Truck Drivers | 53-3033.00 | `demanded` | evaluation | 0.020 | 417 | 587 | 342 | 689 | 605 |
| 451 | Medical Dosimetrists | 29-2036.00 | `demanded` | intent-specification | 0.020 | 283 | 713 | 614 | 758 | 715 |
| 452 | Biofuels Production Managers | 11-3051.03 | `demanded` | intent-specification | 0.020 | 285 | 293 | 568 | 389 | 705 |
| 452 | Bartenders | 35-3011.00 | `demanded` | oversight | 0.020 | 300 | 489 | 488 | 209 | 306 |
| 452 | Commercial Pilots | 53-2012.00 | `demanded` | oversight | 0.020 | 339 | 660 | 400 | 209 | 229 |
| 455 | Biological Technicians | 19-4021.00 | `demanded` | oversight | 0.019 | 442 | 595 | 406 | 215 | 612 |
| 456 | Loan Interviewers and Clerks | 43-4131.00 | `demanded` | evaluation | 0.019 | 679 | 250 | 346 | 672 | 173 |
| 456 | Computer Numerically Controlled Tool Operators | 51-9161.00 | `demanded` | oversight | 0.019 | 732 | 341 | 514 | 219 | 657 |
| 458 | Electro-Mechanical and Mechatronics Technologists and Technicians | 17-3024.00 | `demanded` | evaluation | 0.019 | 334 | 308 | 347 | 431 | 367 |
| 458 | Community Health Workers | 21-1094.00 | `demanded` | intent-specification | 0.019 | 291 | 477 | 730 | 626 | 300 |
| 458 | Farmworkers and Laborers, Crop, Nursery, and Greenhouse | 45-2092.00 | `demanded` | intent-specification | 0.019 | 291 | 332 | 630 | 464 | 754 |
| 461 | Nursing Instructors and Teachers, Postsecondary | 25-1072.00 | `demanded` | orchestration | 0.019 | 472 | 318 | 444 | 353 | 169 |
| 461 | Personal Care Aides | 31-1122.00 | `demanded` | intent-specification | 0.019 | 297 | 605 | 444 | 700 | 622 |
| 463 | Chemical Engineers | 17-2041.00 | `demanded` | oversight | 0.019 | 304 | 627 | 403 | 222 | 640 |
| 464 | Gambling Managers | 11-9071.00 | `demanded` | evaluation | 0.018 | 674 | 539 | 348 | 669 | 274 |
| 465 | Agricultural Technicians | 19-4012.00 | `demanded` | intent-specification | 0.018 | 300 | 330 | 587 | 299 | 356 |
| 465 | Clinical Nurse Specialists | 29-1141.04 | `demanded` | intent-specification | 0.018 | 300 | 621 | 449 | 342 | 356 |
| 467 | Interpreters and Translators | 27-3091.00 | `demanded` | evaluation | 0.018 | 632 | 444 | 349 | 611 | 485 |
| 468 | Freight Forwarders | 43-5011.01 | `demanded` | evaluation | 0.018 | 636 | 451 | 351 | 353 | 493 |
| 469 | Neurodiagnostic Technologists | 29-2099.01 | `demanded` | evaluation | 0.018 | 756 | 677 | 353 | 457 | 691 |
| 470 | Physical Therapists | 29-1123.00 | `demanded` | intent-specification | 0.018 | 309 | 600 | 385 | 696 | 618 |
| 471 | Lighting Technicians | 27-4015.00 | `demanded` | oversight | 0.018 | 454 | 746 | 815 | 234 | 740 |
| 471 | Obstetricians and Gynecologists | 29-1218.00 | `demanded` | evaluation | 0.018 | 474 | 629 | 354 | 436 | 644 |
| 473 | Microbiologists | 19-1022.00 | `demanded` | intent-specification | 0.017 | 320 | 295 | 488 | 312 | 641 |
| 473 | Medical Scientists, Except Epidemiologists | 19-1042.00 | `demanded` | intent-specification | 0.017 | 320 | 507 | 741 | 239 | 538 |
| 473 | Materials Scientists | 19-2032.00 | `demanded` | evaluation | 0.017 | 334 | 473 | 356 | 261 | 514 |
| 476 | Legislators | 11-1031.00 | `demanded` | intent-specification | 0.017 | 325 | 124 | 359 | 570 | 185 |
| 476 | Photonics Technicians | 17-3029.08 | `demanded` | evaluation | 0.017 | 351 | 322 | 359 | 386 | 634 |
| 478 | Broadcast Technicians | 27-4012.00 | `demanded` | orchestration | 0.017 | 459 | 299 | 512 | 397 | 195 |
| 478 | First-Line Supervisors of Production and Operating Workers | 51-1011.00 | `demanded` | orchestration | 0.017 | 407 | 307 | 517 | 414 | 195 |
| 480 | Amusement and Recreation Attendants | 39-3091.00 | `demanded` | oversight | 0.016 | 648 | 470 | 727 | 253 | 220 |
| 481 | Wind Energy Operations Managers | 11-9199.09 | `demanded` | oversight | 0.016 | 746 | 284 | 479 | 254 | 678 |
| 481 | First-Line Supervisors of Landscaping, Lawn Service, and Groundskeeping Workers | 37-1012.00 | `demanded` | orchestration | 0.016 | 372 | 299 | 403 | 257 | 198 |
| 483 | First-Line Supervisors of Housekeeping and Janitorial Workers | 37-1011.00 | `demanded` | evaluation | 0.016 | 460 | 232 | 369 | 414 | 321 |
| 483 | Exercise Trainers and Group Fitness Instructors | 39-9031.00 | `demanded` | oversight | 0.016 | 339 | 555 | 459 | 257 | 578 |
| 485 | Fine Artists, Including Painters, Sculptors, and Illustrators | 27-1013.00 | `demanded` | intent-specification | 0.016 | 339 | 515 | 745 | 281 | 545 |
| 485 | Baggage Porters and Bellhops | 39-6011.00 | `demanded` | evaluation | 0.016 | 688 | 564 | 370 | 361 | 590 |
| 487 | Disc Jockeys, Except Radio | 27-2091.00 | `demanded` | orchestration | 0.016 | 646 | 467 | 376 | 304 | 205 |
| 487 | Acupuncturists | 29-1291.00 | `demanded` | intent-specification | 0.016 | 348 | 578 | 486 | 370 | 601 |
| 489 | Meter Readers, Utilities | 43-5041.00 | `demanded` | evaluation | 0.015 | 663 | 516 | 374 | 656 | 546 |
| 490 | Registered Nurses | 29-1141.00 | `demanded` | intent-specification | 0.015 | 350 | 322 | 421 | 375 | 290 |
| 490 | Residential Advisors | 39-9041.00 | `demanded` | oversight | 0.015 | 435 | 600 | 557 | 269 | 349 |
| 492 | Neuropsychologists | 19-3039.02 | `demanded` | evaluation | 0.015 | 374 | 535 | 380 | 276 | 557 |
| 492 | Forest Fire Inspectors and Prevention Specialists | 33-2022.00 | `demanded` | oversight | 0.015 | 702 | 593 | 769 | 276 | 610 |
| 492 | Recreational Vehicle Service Technicians | 49-3092.00 | `demanded` | evaluation | 0.015 | 504 | 754 | 380 | 780 | 746 |
| 495 | Tour Guides and Escorts | 39-7011.00 | `demanded` | intent-specification | 0.015 | 354 | 469 | 725 | 285 | 505 |
| 496 | Chemical Plant and System Operators | 51-8091.00 | `demanded` | oversight | 0.015 | 736 | 328 | 424 | 281 | 662 |
| 497 | First-Line Supervisors of Personal Service Workers | 39-1022.00 | `demanded` | orchestration | 0.015 | 698 | 284 | 387 | 290 | 213 |
| 498 | Layout Workers, Metal and Plastic | 51-4192.00 | `demanded` | intent-specification | 0.015 | 356 | 653 | 540 | 726 | 664 |
| 499 | Securities, Commodities, and Financial Services Sales Agents | 41-3031.00 | `demanded` | oversight | 0.014 | 431 | 511 | 477 | 285 | 542 |
| 499 | Computer, Automated Teller, and Office Machine Repairers | 49-2011.00 | `demanded` | evaluation | 0.014 | 696 | 585 | 385 | 687 | 604 |
| 501 | Chiropractors | 29-1011.00 | `demanded` | evaluation | 0.014 | 715 | 293 | 387 | 709 | 634 |
| 501 | Speech-Language Pathology Assistants | 31-9099.01 | `demanded` | intent-specification | 0.014 | 358 | 571 | 392 | 288 | 594 |
| 503 | Forensic Science Technicians | 19-4092.00 | `demanded` | evaluation | 0.014 | 755 | 676 | 389 | 739 | 690 |
| 503 | Music Directors and Composers | 27-2041.00 | `demanded` | intent-specification | 0.014 | 359 | 288 | 395 | 367 | 218 |
| 503 | Cytogenetic Technologists | 29-2011.01 | `demanded` | evaluation | 0.014 | 711 | 291 | 389 | 464 | 621 |
| 506 | Choreographers | 27-2032.00 | `demanded` | intent-specification | 0.014 | 360 | 574 | 763 | 370 | 596 |
| 506 | Gambling Change Persons and Booth Cashiers | 41-2012.00 | `demanded` | evaluation | 0.014 | 670 | 531 | 391 | 664 | 553 |
| 508 | Adapted Physical Education Specialists | 25-2059.01 | `demanded` | intent-specification | 0.014 | 362 | 563 | 500 | 680 | 588 |
| 508 | Massage Therapists | 31-9011.00 | `demanded` | intent-specification | 0.014 | 362 | 608 | 774 | 703 | 627 |
| 508 | First-Line Supervisors of Farming, Fishing, and Forestry Workers | 45-1011.00 | `demanded` | orchestration | 0.014 | 401 | 349 | 496 | 379 | 216 |
| 511 | Teaching Assistants, Special Education | 25-9043.00 | `demanded` | evaluation | 0.014 | 484 | 567 | 393 | 431 | 286 |
| 512 | Machinists | 51-4041.00 | `demanded` | evaluation | 0.014 | 444 | 345 | 394 | 436 | 672 |
| 513 | Court Reporters and Simultaneous Captioners | 27-3092.00 | `demanded` | evaluation | 0.014 | 656 | 490 | 395 | 640 | 528 |
| 514 | Radiologists | 29-1224.00 | `demanded` | evaluation | 0.013 | 414 | 557 | 398 | 304 | 581 |
| 514 | File Clerks | 43-4071.00 | `demanded` | decision-framing | 0.013 | 386 | 173 | 738 | 641 | 230 |
| 516 | Sound Engineering Technicians | 27-4014.00 | `demanded` | oversight | 0.013 | 681 | 195 | 410 | 299 | 567 |
| 517 | Customs Brokers | 13-1041.08 | `demanded` | oversight | 0.013 | 645 | 465 | 724 | 307 | 504 |
| 517 | Film and Video Editors | 27-4032.00 | `demanded` | evaluation | 0.013 | 638 | 455 | 406 | 326 | 251 |
| 519 | Cardiovascular Technologists and Technicians | 29-2031.00 | `demanded` | oversight | 0.013 | 759 | 681 | 474 | 313 | 695 |
| 519 | Subway and Streetcar Operators | 53-4041.00 | `demanded` | orchestration | 0.013 | 771 | 701 | 804 | 447 | 234 |
| 521 | Printing Press Operators | 51-5112.00 | `demanded` | oversight | 0.013 | 748 | 669 | 521 | 314 | 682 |
| 522 | Recreation Workers | 39-9032.00 | `demanded` | intent-specification | 0.012 | 377 | 616 | 465 | 370 | 282 |
| 523 | Photographers | 27-4021.00 | `demanded` | evaluation | 0.012 | 686 | 302 | 414 | 420 | 313 |
| 523 | Police Identification and Records Officers | 33-3021.02 | `demanded` | evaluation | 0.012 | 676 | 209 | 414 | 670 | 270 |
| 525 | Psychiatric Technicians | 29-2053.00 | `demanded` | oversight | 0.012 | 670 | 531 | 747 | 323 | 553 |
| 526 | Retail Loss Prevention Specialists | 33-9099.02 | `demanded` | evaluation | 0.012 | 693 | 579 | 417 | 326 | 314 |
| 527 | Teaching Assistants, Preschool, Elementary, Middle, and Secondary School, Except Special Education | 25-9042.00 | `demanded` | evaluation | 0.012 | 457 | 546 | 418 | 401 | 314 |
| 528 | Parts Salespersons | 41-2022.00 | `demanded` | evaluation | 0.012 | 665 | 519 | 420 | 333 | 548 |
| 529 | Cargo and Freight Agents | 43-5011.00 | `demanded` | evaluation | 0.011 | 463 | 305 | 422 | 337 | 317 |
| 530 | First-Line Supervisors of Police and Detectives | 33-1012.00 | `demanded` | orchestration | 0.011 | 712 | 609 | 530 | 334 | 257 |
| 530 | Audiovisual Equipment Installers and Repairers | 49-2097.00 | `demanded` | evaluation | 0.011 | 793 | 748 | 425 | 776 | 742 |
| 532 | Museum Technicians and Conservators | 25-4013.00 | `demanded` | evaluation | 0.011 | 399 | 317 | 427 | 393 | 359 |
| 532 | First-Line Supervisors of Correctional Officers | 33-1011.00 | `demanded` | oversight | 0.011 | 697 | 586 | 534 | 334 | 258 |
| 532 | First-Line Supervisors of Gambling Services Workers | 39-1013.00 | `demanded` | evaluation | 0.011 | 691 | 567 | 427 | 380 | 293 |
| 535 | Police and Sheriff's Patrol Officers | 33-3051.00 | `demanded` | oversight | 0.011 | 727 | 634 | 521 | 340 | 362 |
| 535 | Transit and Railroad Police | 33-3052.00 | `demanded` | evaluation | 0.011 | 403 | 561 | 430 | 678 | 585 |
| 535 | Manufactured Building and Mobile Home Installers | 49-9095.00 | `demanded` | evaluation | 0.011 | 487 | 683 | 430 | 740 | 697 |
| 535 | Patternmakers, Metal and Plastic | 51-4062.00 | `demanded` | intent-specification | 0.011 | 397 | 642 | 514 | 429 | 655 |
| 535 | Aviation Inspectors | 53-6051.01 | `demanded` | evaluation | 0.011 | 786 | 728 | 430 | 502 | 728 |
| 540 | Urologists | 29-1229.03 | `demanded` | evaluation | 0.011 | 733 | 647 | 435 | 424 | 658 |
| 540 | Water and Wastewater Treatment Plant and System Operators | 51-8031.00 | `demanded` | evaluation | 0.011 | 472 | 708 | 435 | 347 | 339 |
| 542 | Coaches and Scouts | 27-2022.00 | `demanded` | intent-specification | 0.010 | 401 | 337 | 453 | 357 | 306 |
| 542 | First-Line Supervisors of Passenger Attendants | 53-1044.00 | `demanded` | evaluation | 0.010 | 763 | 277 | 437 | 420 | 329 |
| 542 | Transportation Inspectors | 53-6051.00 | `demanded` | oversight | 0.010 | 408 | 237 | 438 | 344 | 267 |
| 545 | General Internal Medicine Physicians | 29-1216.00 | `demanded` | evaluation | 0.010 | 512 | 663 | 438 | 480 | 676 |
| 545 | Telecommunications Equipment Installers and Repairers, Except Line Installers | 49-2022.00 | `demanded` | evaluation | 0.010 | 435 | 606 | 438 | 701 | 623 |
| 547 | Hosts and Hostesses, Restaurant, Lounge, and Coffee Shop | 35-9031.00 | `demanded` | intent-specification | 0.010 | 405 | 478 | 731 | 628 | 517 |
| 547 | Medical Equipment Repairers | 49-9062.00 | `demanded` | evaluation | 0.010 | 466 | 615 | 442 | 424 | 331 |
| 549 | Anesthesiologists | 29-1211.00 | `demanded` | evaluation | 0.010 | 512 | 684 | 443 | 438 | 333 |
| 549 | Radiologic Technologists and Technicians | 29-2034.00 | `demanded` | oversight | 0.010 | 520 | 648 | 585 | 346 | 343 |
| 551 | Avionics Technicians | 49-2091.00 | `demanded` | evaluation | 0.010 | 499 | 696 | 447 | 746 | 350 |
| 552 | Athletic Trainers | 29-9091.00 | `demanded` | intent-specification | 0.009 | 412 | 594 | 506 | 692 | 611 |
| 552 | Crossing Guards and Flaggers | 33-9091.00 | `demanded` | intent-specification | 0.009 | 412 | 668 | 793 | 353 | 681 |
| 552 | Weatherization Installers and Technicians | 47-4099.03 | `demanded` | evaluation | 0.009 | 721 | 262 | 448 | 712 | 341 |
| 555 | Postal Service Mail Carriers | 43-5052.00 | `demanded` | orchestration | 0.009 | 673 | 536 | 751 | 668 | 276 |
| 556 | Clinical Neuropsychologists | 19-3039.03 | `demanded` | evaluation | 0.009 | 439 | 559 | 451 | 359 | 583 |
| 556 | Cashiers | 41-2011.00 | `demanded` | evaluation | 0.009 | 644 | 462 | 451 | 619 | 500 |
| 558 | Podiatrists | 29-1081.00 | `demanded` | oversight | 0.009 | 716 | 622 | 777 | 360 | 637 |
| 559 | Licensed Practical and Licensed Vocational Nurses | 29-2061.00 | `demanded` | evaluation | 0.009 | 474 | 618 | 455 | 429 | 632 |
| 559 | Electronic Equipment Installers and Repairers, Motor Vehicles | 49-2096.00 | `demanded` | evaluation | 0.009 | 761 | 686 | 455 | 742 | 700 |
| 559 | Photographic Process Workers and Processing Machine Operators | 51-9151.00 | `demanded` | oversight | 0.009 | 477 | 315 | 772 | 361 | 623 |
| 559 | Passenger Attendants | 53-6061.00 | `demanded` | evaluation | 0.009 | 709 | 603 | 455 | 698 | 619 |
| 563 | Actors | 27-2011.00 | `demanded` | oversight | 0.009 | 701 | 592 | 768 | 363 | 609 |
| 563 | Fiberglass Laminators and Fabricators | 51-2051.00 | `demanded` | evaluation | 0.009 | 799 | 335 | 458 | 783 | 750 |
| 565 | Physical Therapist Aides | 31-2022.00 | `demanded` | evaluation | 0.009 | 482 | 639 | 459 | 447 | 279 |
| 565 | Locker Room, Coatroom, and Dressing Room Attendants | 39-3093.00 | `demanded` | evaluation | 0.009 | 481 | 607 | 459 | 447 | 625 |
| 565 | Electricians | 47-2111.00 | `demanded` | evaluation | 0.009 | 448 | 666 | 459 | 484 | 679 |
| 565 | Transportation Vehicle, Equipment and Systems Inspectors, Except Aviation | 53-6051.07 | `demanded` | evaluation | 0.009 | 784 | 364 | 459 | 516 | 727 |
| 569 | Respiratory Therapists | 29-1126.00 | `demanded` | evaluation | 0.009 | 504 | 662 | 465 | 477 | 674 |
| 569 | Prepress Technicians and Workers | 51-5111.00 | `demanded` | evaluation | 0.009 | 749 | 670 | 465 | 447 | 683 |
| 569 | Air Traffic Controllers | 53-2021.00 | `demanded` | intent-specification | 0.009 | 417 | 664 | 486 | 365 | 362 |
| 572 | Allergists and Immunologists | 29-1229.01 | `demanded` | evaluation | 0.008 | 471 | 643 | 469 | 722 | 656 |
| 572 | Food Batchmakers | 51-3092.00 | `demanded` | evaluation | 0.008 | 735 | 651 | 469 | 412 | 661 |
| 574 | Coil Winders, Tapers, and Finishers | 51-2021.00 | `demanded` | evaluation | 0.008 | 770 | 319 | 472 | 750 | 708 |
| 575 | Waiters and Waitresses | 35-3031.00 | `demanded` | evaluation | 0.008 | 654 | 282 | 473 | 403 | 525 |
| 575 | Upholsterers | 51-6093.00 | `demanded` | intent-specification | 0.008 | 423 | 751 | 817 | 777 | 365 |
| 577 | Dentists, General | 29-1021.00 | `demanded` | intent-specification | 0.008 | 426 | 709 | 602 | 755 | 377 |
| 577 | Stone Cutters and Carvers, Manufacturing | 51-9195.03 | `demanded` | intent-specification | 0.008 | 426 | 827 | 640 | 845 | 830 |
| 579 | Childcare Workers | 39-9011.00 | `demanded` | orchestration | 0.008 | 428 | 529 | 746 | 663 | 286 |
| 580 | Airline Pilots, Copilots, and Flight Engineers | 53-2011.00 | `demanded` | oversight | 0.008 | 455 | 715 | 517 | 375 | 321 |
| 581 | Midwives | 29-9099.01 | `demanded` | evaluation | 0.008 | 477 | 679 | 475 | 505 | 692 |
| 581 | Transportation Security Screeners | 33-9093.00 | `demanded` | evaluation | 0.008 | 507 | 337 | 475 | 384 | 666 |
| 581 | Pesticide Handlers, Sprayers, and Applicators, Vegetation | 37-3012.00 | `demanded` | intent-specification | 0.008 | 428 | 341 | 836 | 488 | 780 |
| 581 | Real Estate Sales Agents | 41-9022.00 | `demanded` | oversight | 0.008 | 453 | 302 | 506 | 377 | 290 |
| 585 | Animal Caretakers | 39-2021.00 | `demanded` | orchestration | 0.008 | 489 | 640 | 786 | 459 | 293 |
| 586 | Security Guards | 33-9032.00 | `demanded` | evaluation | 0.008 | 703 | 596 | 478 | 420 | 613 |
| 587 | Segmental Pavers | 47-4091.00 | `demanded` | intent-specification | 0.007 | 433 | 761 | 824 | 459 | 753 |
| 588 | Milling and Planing Machine Setters, Operators, and Tenders, Metal and Plastic | 51-4035.00 | `demanded` | evaluation | 0.007 | 515 | 341 | 481 | 431 | 765 |
| 589 | Physicians, Pathologists | 29-1222.00 | `demanded` | evaluation | 0.007 | 526 | 695 | 482 | 495 | 706 |
| 589 | Magnetic Resonance Imaging Technologists | 29-2035.00 | `demanded` | evaluation | 0.007 | 757 | 678 | 482 | 495 | 379 |
| 591 | Camera Operators, Television, Video, and Film | 27-4031.00 | `demanded` | oversight | 0.007 | 507 | 646 | 491 | 384 | 350 |
| 591 | Neurologists | 29-1217.00 | `demanded` | evaluation | 0.007 | 462 | 706 | 485 | 753 | 710 |
| 593 | Robotics Technicians | 17-3024.01 | `demanded` | oversight | 0.007 | 485 | 687 | 494 | 386 | 701 |
| 593 | Coin, Vending, and Amusement Machine Servicers and Repairers | 49-9091.00 | `demanded` | intent-specification | 0.007 | 438 | 572 | 762 | 684 | 595 |
| 595 | Hospitalists | 29-1229.02 | `demanded` | intent-specification | 0.007 | 439 | 690 | 563 | 477 | 703 |
| 595 | Pest Control Workers | 37-2021.00 | `demanded` | oversight | 0.007 | 714 | 617 | 776 | 389 | 631 |
| 597 | Cooks, Institution and Cafeteria | 35-2012.00 | `demanded` | oversight | 0.007 | 524 | 766 | 593 | 391 | 760 |
| 597 | Bus Drivers, Transit and Intercity | 53-3052.00 | `demanded` | orchestration | 0.007 | 494 | 698 | 803 | 748 | 300 |
| 599 | Nuclear Monitoring Technicians | 19-4051.02 | `demanded` | intent-specification | 0.007 | 443 | 299 | 510 | 705 | 311 |
| 600 | Semiconductor Processing Technicians | 51-9141.00 | `demanded` | evaluation | 0.007 | 807 | 768 | 492 | 792 | 762 |
| 601 | Electrical and Electronic Equipment Assemblers | 51-2022.00 | `demanded` | evaluation | 0.007 | 526 | 349 | 493 | 796 | 767 |
| 602 | Clergy | 21-2011.00 | `demanded` | intent-specification | 0.006 | 445 | 570 | 761 | 414 | 321 |
| 602 | Dental Assistants | 31-9091.00 | `demanded` | oversight | 0.006 | 762 | 687 | 798 | 396 | 358 |
| 602 | Gambling Cage Workers | 43-3041.00 | `demanded` | orchestration | 0.006 | 707 | 599 | 496 | 695 | 306 |
| 605 | Cooks, Restaurant | 35-2014.00 | `demanded` | intent-specification | 0.006 | 447 | 643 | 553 | 455 | 347 |
| 606 | Acute Care Nurses | 29-1141.01 | `demanded` | evaluation | 0.006 | 477 | 705 | 496 | 509 | 383 |
| 606 | Funeral Attendants | 39-4021.00 | `demanded` | intent-specification | 0.006 | 448 | 560 | 758 | 397 | 584 |
| 606 | Postal Service Mail Sorters, Processors, and Processing Machine Operators | 43-5053.00 | `demanded` | evaluation | 0.006 | 451 | 632 | 496 | 716 | 648 |
| 606 | Furniture Finishers | 51-7021.00 | `demanded` | intent-specification | 0.006 | 448 | 755 | 820 | 781 | 747 |
| 606 | Refuse and Recyclable Material Collectors | 53-7081.00 | `demanded` | orchestration | 0.006 | 708 | 602 | 771 | 697 | 309 |
| 611 | Dermatologists | 29-1213.00 | `demanded` | evaluation | 0.006 | 743 | 658 | 500 | 731 | 671 |
| 611 | Landscaping and Groundskeeping Workers | 37-3011.00 | `demanded` | intent-specification | 0.006 | 451 | 806 | 847 | 824 | 806 |
| 613 | Nuclear Technicians | 19-4051.00 | `demanded` | evaluation | 0.006 | 494 | 351 | 504 | 403 | 699 |
| 613 | Electrical and Electronics Repairers, Powerhouse, Substation, and Relay | 49-2095.00 | `demanded` | evaluation | 0.006 | 789 | 736 | 504 | 464 | 371 |
| 613 | Multiple Machine Tool Setters, Operators, and Tenders, Metal and Plastic | 51-4081.00 | `demanded` | oversight | 0.006 | 493 | 660 | 568 | 400 | 673 |
| 616 | Automotive Service Technicians and Mechanics | 49-3023.00 | `demanded` | evaluation | 0.006 | 566 | 799 | 506 | 509 | 390 |
| 616 | Team Assemblers | 51-2092.00 | `demanded` | evaluation | 0.006 | 794 | 750 | 506 | 418 | 324 |
| 618 | Petroleum Pump System Operators, Refinery Operators, and Gaugers | 51-8093.00 | `demanded` | oversight | 0.006 | 541 | 358 | 546 | 403 | 318 |
| 618 | Heavy and Tractor-Trailer Truck Drivers | 53-3032.00 | `demanded` | evaluation | 0.006 | 544 | 704 | 510 | 752 | 709 |
| 620 | Motion Picture Projectionists | 39-3021.00 | `demanded` | oversight | 0.006 | 797 | 757 | 527 | 406 | 318 |
| 620 | Etchers and Engravers | 51-9194.00 | `demanded` | intent-specification | 0.006 | 455 | 378 | 614 | 535 | 833 |
| 622 | First-Line Supervisors of Security Workers | 33-1091.00 | `demanded` | oversight | 0.006 | 699 | 589 | 766 | 408 | 325 |
| 622 | Morticians, Undertakers, and Funeral Arrangers | 39-4031.00 | `demanded` | intent-specification | 0.006 | 457 | 351 | 826 | 787 | 347 |
| 622 | Industrial Machinery Mechanics | 49-9041.00 | `demanded` | evaluation | 0.006 | 717 | 623 | 514 | 412 | 340 |
| 625 | Correctional Officers and Jailers | 33-3012.00 | `demanded` | oversight | 0.006 | 731 | 645 | 788 | 410 | 333 |
| 625 | Solar Thermal Installers and Technicians | 47-2152.04 | `demanded` | oversight | 0.006 | 509 | 786 | 630 | 410 | 782 |
| 627 | Sports Medicine Physicians | 29-1229.06 | `demanded` | evaluation | 0.005 | 737 | 652 | 521 | 725 | 663 |
| 627 | Pharmacy Technicians | 29-2052.00 | `demanded` | evaluation | 0.005 | 709 | 603 | 521 | 698 | 619 |
| 627 | Couriers and Messengers | 43-5021.00 | `demanded` | intent-specification | 0.005 | 460 | 628 | 780 | 713 | 642 |
| 627 | Ophthalmic Laboratory Technicians | 51-9083.00 | `demanded` | evaluation | 0.005 | 798 | 340 | 521 | 782 | 749 |
| 627 | Packers and Packagers, Hand | 53-7064.00 | `demanded` | evaluation | 0.005 | 747 | 667 | 521 | 735 | 680 |
| 632 | Nurse Practitioners | 29-1171.00 | `demanded` | evaluation | 0.005 | 487 | 692 | 527 | 464 | 379 |
| 632 | Farm Equipment Mechanics and Service Technicians | 49-3041.00 | `demanded` | evaluation | 0.005 | 734 | 649 | 527 | 723 | 659 |
| 634 | Ushers, Lobby Attendants, and Ticket Takers | 39-3031.00 | `demanded` | oversight | 0.005 | 695 | 583 | 765 | 418 | 338 |
| 634 | Tool and Die Makers | 51-4111.00 | `demanded` | intent-specification | 0.005 | 463 | 723 | 558 | 766 | 722 |
| 634 | Painting, Coating, and Decorating Workers | 51-9123.00 | `demanded` | evaluation | 0.005 | 830 | 339 | 530 | 821 | 800 |
| 637 | Fish and Game Wardens | 33-3031.00 | `demanded` | intent-specification | 0.005 | 465 | 319 | 796 | 452 | 359 |
| 637 | Customs and Border Protection Officers | 33-3051.04 | `demanded` | evaluation | 0.005 | 760 | 685 | 533 | 741 | 698 |
| 637 | Lathe and Turning Machine Tool Setters, Operators, and Tenders, Metal and Plastic | 51-4034.00 | `demanded` | oversight | 0.005 | 829 | 363 | 635 | 420 | 798 |
| 640 | Rolling Machine Setters, Operators, and Tenders, Metal and Plastic | 51-4023.00 | `demanded` | oversight | 0.005 | 535 | 356 | 614 | 424 | 353 |
| 640 | Nuclear Power Reactor Operators | 51-8011.00 | `demanded` | oversight | 0.005 | 571 | 361 | 611 | 424 | 399 |
| 640 | Shuttle Drivers and Chauffeurs | 53-3053.00 | `demanded` | orchestration | 0.005 | 773 | 703 | 614 | 751 | 331 |
| 643 | Child, Family, and School Social Workers | 21-1021.00 | `demanded` | intent-specification | 0.005 | 468 | 610 | 536 | 440 | 628 |
| 643 | Physical Medicine and Rehabilitation Physicians | 29-1229.04 | `demanded` | intent-specification | 0.005 | 468 | 716 | 604 | 760 | 367 |
| 643 | Textile Bleaching and Dyeing Machine Operators and Tenders | 51-6061.00 | `demanded` | intent-specification | 0.005 | 468 | 672 | 582 | 488 | 685 |
| 646 | Stationary Engineers and Boiler Operators | 51-8021.00 | `demanded` | evaluation | 0.005 | 558 | 730 | 537 | 480 | 731 |
| 646 | Gem and Diamond Workers | 51-9071.06 | `demanded` | orchestration | 0.005 | 718 | 624 | 778 | 710 | 333 |
| 646 | Captains, Mates, and Pilots of Water Vessels | 53-5021.00 | `demanded` | oversight | 0.005 | 776 | 714 | 807 | 431 | 386 |
| 646 | Motorboat Operators | 53-5022.00 | `demanded` | oversight | 0.005 | 730 | 641 | 787 | 431 | 654 |
| 650 | First-Line Supervisors of Firefighting and Prevention Workers | 33-1021.00 | `demanded` | evaluation | 0.005 | 558 | 367 | 540 | 459 | 359 |
| 650 | Food Servers, Nonrestaurant | 35-3041.00 | `demanded` | oversight | 0.005 | 741 | 656 | 791 | 438 | 669 |
| 650 | Textile Knitting and Weaving Machine Setters, Operators, and Tenders | 51-6063.00 | `demanded` | evaluation | 0.005 | 723 | 630 | 540 | 714 | 645 |
| 650 | Cleaning, Washing, and Metal Pickling Equipment Operators and Tenders | 51-9192.00 | `demanded` | evaluation | 0.005 | 518 | 792 | 540 | 813 | 790 |
| 654 | Substitute Teachers, Short-Term | 25-3031.00 | `demanded` | intent-specification | 0.005 | 474 | 747 | 816 | 775 | 741 |
| 654 | Diagnostic Medical Sonographers | 29-2032.00 | `demanded` | evaluation | 0.005 | 769 | 700 | 544 | 749 | 367 |
| 654 | Physical Therapist Assistants | 31-2021.00 | `demanded` | evaluation | 0.005 | 499 | 725 | 544 | 480 | 724 |
| 654 | Grinding, Lapping, Polishing, and Buffing Machine Tool Setters, Operators, and Tenders, Metal and Plastic | 51-4033.00 | `demanded` | oversight | 0.005 | 821 | 334 | 624 | 440 | 784 |
| 658 | Occupational Therapy Aides | 31-2012.00 | `demanded` | oversight | 0.004 | 520 | 345 | 831 | 443 | 374 |
| 658 | Gambling Dealers | 39-3011.00 | `demanded` | evaluation | 0.004 | 719 | 625 | 546 | 711 | 638 |
| 658 | Pump Operators, Except Wellhead Pumpers | 53-7072.00 | `demanded` | intent-specification | 0.004 | 477 | 673 | 546 | 443 | 345 |
| 661 | Judges, Magistrate Judges, and Magistrates | 23-1023.00 | `demanded` | oversight | 0.004 | 725 | 316 | 782 | 445 | 647 |
| 661 | Naturopathic Physicians | 29-1299.01 | `demanded` | evaluation | 0.004 | 723 | 630 | 549 | 714 | 645 |
| 661 | Model Makers, Metal and Plastic | 51-4061.00 | `demanded` | oversight | 0.004 | 486 | 749 | 550 | 445 | 743 |
| 664 | Stockers and Order Fillers | 53-7065.00 | `demanded` | intent-specification | 0.004 | 482 | 576 | 553 | 454 | 598 |
| 665 | Dental Laboratory Technicians | 51-9081.00 | `demanded` | evaluation | 0.004 | 544 | 803 | 552 | 516 | 802 |
| 665 | Locomotive Engineers | 53-4011.00 | `demanded` | oversight | 0.004 | 782 | 722 | 611 | 452 | 721 |
| 667 | Solar Photovoltaic Installers | 47-2231.00 | `demanded` | evaluation | 0.004 | 499 | 351 | 553 | 526 | 730 |
| 667 | Bus Drivers, School | 53-3051.00 | `demanded` | evaluation | 0.004 | 744 | 659 | 553 | 732 | 346 |
| 669 | Electrical and Electronics Installers and Repairers, Transportation Equipment | 49-2093.00 | `demanded` | evaluation | 0.004 | 758 | 680 | 558 | 459 | 694 |
| 670 | Fallers | 45-4021.00 | `demanded` | decision-framing | 0.004 | 752 | 325 | 561 | 459 | 687 |
| 670 | Machine Feeders and Offbearers | 53-7063.00 | `demanded` | evaluation | 0.004 | 800 | 759 | 561 | 785 | 751 |
| 672 | Insulation Workers, Mechanical | 47-2132.00 | `demanded` | oversight | 0.004 | 816 | 779 | 834 | 457 | 774 |
| 672 | Plumbers, Pipefitters, and Steamfitters | 47-2152.00 | `demanded` | evaluation | 0.004 | 489 | 365 | 563 | 502 | 390 |
| 672 | Bakers | 51-3011.00 | `demanded` | evaluation | 0.004 | 739 | 655 | 563 | 728 | 667 |
| 672 | Textile Cutting Machine Setters, Operators, and Tenders | 51-6062.00 | `demanded` | evaluation | 0.004 | 745 | 665 | 563 | 734 | 677 |
| 676 | Camera and Photographic Equipment Repairers | 49-9061.00 | `demanded` | evaluation | 0.004 | 571 | 372 | 567 | 839 | 824 |
| 676 | Print Binding and Finishing Workers | 51-5113.00 | `demanded` | intent-specification | 0.004 | 489 | 782 | 835 | 805 | 776 |
| 678 | Medical Assistants | 31-9092.00 | `demanded` | evaluation | 0.004 | 777 | 355 | 568 | 759 | 354 |
| 678 | Radio, Cellular, and Tower Equipment Installers and Repairers | 49-2021.00 | `demanded` | evaluation | 0.004 | 551 | 784 | 568 | 807 | 779 |
| 678 | Aircraft Mechanics and Service Technicians | 49-3011.00 | `demanded` | evaluation | 0.004 | 566 | 781 | 568 | 804 | 394 |
| 678 | Heating, Air Conditioning, and Refrigeration Mechanics and Installers | 49-9021.00 | `demanded` | decision-framing | 0.004 | 520 | 330 | 585 | 519 | 385 |
| 678 | Power Distributors and Dispatchers | 51-8012.00 | `demanded` | oversight | 0.004 | 549 | 739 | 648 | 464 | 367 |
| 678 | Airfield Operations Specialists | 53-2022.00 | `demanded` | intent-specification | 0.004 | 492 | 737 | 643 | 535 | 376 |
| 684 | Medical and Clinical Laboratory Technicians | 29-2012.00 | `demanded` | evaluation | 0.003 | 828 | 800 | 573 | 820 | 797 |
| 684 | Extruding and Forming Machine Setters, Operators, and Tenders, Synthetic and Glass Fibers | 51-6091.00 | `demanded` | oversight | 0.003 | 824 | 791 | 841 | 470 | 788 |
| 686 | Musicians and Singers | 27-2042.00 | `demanded` | decision-framing | 0.003 | 722 | 332 | 781 | 471 | 643 |
| 686 | Veterinary Assistants and Laboratory Animal Caretakers | 31-9096.00 | `demanded` | orchestration | 0.003 | 766 | 694 | 801 | 745 | 354 |
| 686 | Forging Machine Setters, Operators, and Tenders, Metal and Plastic | 51-4022.00 | `demanded` | evaluation | 0.003 | 839 | 815 | 574 | 505 | 814 |
| 686 | Flight Attendants | 53-2031.00 | `demanded` | evaluation | 0.003 | 533 | 734 | 574 | 528 | 396 |
| 690 | Pharmacists | 29-1051.00 | `demanded` | oversight | 0.003 | 497 | 727 | 620 | 472 | 726 |
| 690 | Nurse Midwives | 29-1161.00 | `demanded` | intent-specification | 0.003 | 494 | 732 | 604 | 519 | 733 |
| 690 | Detectives and Criminal Investigators | 33-3021.00 | `demanded` | evaluation | 0.003 | 790 | 386 | 576 | 541 | 403 |
| 690 | Loading and Moving Machine Operators, Underground Mining | 47-5044.00 | `demanded` | oversight | 0.003 | 820 | 788 | 839 | 472 | 386 |
| 690 | Laundry and Dry-Cleaning Workers | 51-6011.00 | `demanded` | oversight | 0.003 | 805 | 765 | 635 | 472 | 759 |
| 690 | Ship Engineers | 53-5031.00 | `demanded` | oversight | 0.003 | 788 | 735 | 604 | 472 | 389 |
| 690 | Parking Attendants | 53-6021.00 | `demanded` | oversight | 0.003 | 765 | 691 | 800 | 472 | 704 |
| 697 | Aircraft Service Attendants | 53-6032.00 | `demanded` | intent-specification | 0.003 | 497 | 721 | 810 | 765 | 720 |
| 698 | Physician Assistants | 29-1071.00 | `demanded` | evaluation | 0.003 | 541 | 738 | 577 | 514 | 734 |
| 698 | Nursing Assistants | 31-1131.00 | `demanded` | oversight | 0.003 | 535 | 358 | 797 | 480 | 693 |
| 698 | Tailors, Dressmakers, and Custom Sewers | 51-6052.00 | `demanded` | intent-specification | 0.003 | 499 | 774 | 830 | 798 | 769 |
| 698 | Cabinetmakers and Bench Carpenters | 51-7011.00 | `demanded` | intent-specification | 0.003 | 499 | 814 | 656 | 832 | 813 |
| 702 | Radiation Therapists | 29-1124.00 | `demanded` | oversight | 0.003 | 509 | 733 | 814 | 484 | 394 |
| 702 | Cytotechnologists | 29-2011.02 | `demanded` | evaluation | 0.003 | 780 | 719 | 579 | 763 | 718 |
| 702 | Hearing Aid Specialists | 29-2092.00 | `demanded` | evaluation | 0.003 | 814 | 777 | 579 | 802 | 773 |
| 702 | Woodworking Machine Setters, Operators, and Tenders, Except Sawing | 51-7042.00 | `demanded` | intent-specification | 0.003 | 504 | 372 | 598 | 499 | 821 |
| 702 | Chemical Equipment Operators and Tenders | 51-9011.00 | `demanded` | oversight | 0.003 | 554 | 801 | 656 | 484 | 799 |
| 707 | Dental Hygienists | 29-1292.00 | `demanded` | evaluation | 0.003 | 803 | 764 | 581 | 789 | 757 |
| 708 | Maintenance and Repair Workers, General | 49-9071.00 | `demanded` | intent-specification | 0.003 | 509 | 771 | 640 | 794 | 764 |
| 709 | Prosthodontists | 29-1024.00 | `demanded` | intent-specification | 0.003 | 512 | 786 | 838 | 490 | 782 |
| 709 | Manicurists and Pedicurists | 39-5092.00 | `demanded` | orchestration | 0.003 | 531 | 758 | 822 | 784 | 364 |
| 709 | Separating, Filtering, Clarifying, Precipitating, and Still Machine Setters, Operators, and Tenders | 51-9012.00 | `demanded` | evaluation | 0.003 | 825 | 795 | 582 | 816 | 793 |
| 709 | Extruding, Forming, Pressing, and Compacting Machine Setters, Operators, and Tenders | 51-9041.00 | `demanded` | evaluation | 0.003 | 811 | 358 | 582 | 799 | 770 |
| 713 | Maids and Housekeeping Cleaners | 37-2012.00 | `demanded` | oversight | 0.003 | 796 | 756 | 821 | 491 | 748 |
| 713 | Septic Tank Servicers and Sewer Pipe Cleaners | 47-4071.00 | `demanded` | intent-specification | 0.003 | 515 | 753 | 819 | 779 | 745 |
| 713 | Biomass Plant Technicians | 51-8013.03 | `demanded` | intent-specification | 0.003 | 515 | 828 | 664 | 846 | 831 |
| 713 | Conveyor Operators and Tenders | 53-7011.00 | `demanded` | orchestration | 0.003 | 754 | 675 | 593 | 738 | 365 |
| 717 | Optometrists | 29-1041.00 | `demanded` | intent-specification | 0.002 | 518 | 802 | 587 | 822 | 801 |
| 717 | Veterinarians | 29-1131.00 | `demanded` | oversight | 0.002 | 526 | 682 | 593 | 492 | 696 |
| 717 | Psychiatric Aides | 31-1133.00 | `demanded` | evaluation | 0.002 | 520 | 711 | 587 | 492 | 713 |
| 717 | Mobile Heavy Equipment Mechanics, Except Engines | 49-3042.00 | `demanded` | evaluation | 0.002 | 768 | 699 | 587 | 502 | 373 |
| 717 | Home Appliance Repairers | 49-9031.00 | `demanded` | decision-framing | 0.002 | 740 | 344 | 790 | 729 | 668 |
| 717 | Signal and Track Switch Repairers | 49-9097.00 | `demanded` | evaluation | 0.002 | 846 | 830 | 587 | 519 | 834 |
| 717 | Cooling and Freezing Equipment Operators and Tenders | 51-9193.00 | `demanded` | evaluation | 0.002 | 835 | 809 | 587 | 827 | 809 |
| 724 | Nuclear Medicine Technologists | 29-2033.00 | `demanded` | evaluation | 0.002 | 774 | 710 | 593 | 756 | 712 |
| 724 | Paramedics | 29-2043.00 | `demanded` | orchestration | 0.002 | 785 | 347 | 598 | 495 | 371 |
| 724 | Glass Blowers, Molders, Benders, and Finishers | 51-9195.04 | `demanded` | evaluation | 0.002 | 524 | 707 | 593 | 754 | 711 |
| 727 | Gas Plant Operators | 51-8092.00 | `demanded` | evaluation | 0.002 | 538 | 833 | 598 | 513 | 837 |
| 727 | Hoist and Winch Operators | 53-7041.00 | `demanded` | decision-framing | 0.002 | 821 | 347 | 598 | 494 | 784 |
| 729 | Critical Care Nurses | 29-1141.03 | `demanded` | evaluation | 0.002 | 558 | 386 | 602 | 547 | 409 |
| 729 | Tile and Stone Setters | 47-2044.00 | `demanded` | intent-specification | 0.002 | 526 | 378 | 856 | 838 | 823 |
| 729 | Biofuels Processing Technicians | 51-8099.01 | `demanded` | oversight | 0.002 | 554 | 816 | 656 | 495 | 815 |
| 732 | Hairdressers, Hairstylists, and Cosmetologists | 39-5012.00 | `demanded` | orchestration | 0.002 | 809 | 770 | 828 | 793 | 375 |
| 732 | Elevator and Escalator Installers and Repairers | 47-4021.00 | `demanded` | evaluation | 0.002 | 853 | 372 | 604 | 534 | 843 |
| 732 | Earth Drillers, Except Oil and Gas | 47-5023.00 | `demanded` | intent-specification | 0.002 | 530 | 724 | 611 | 767 | 723 |
| 732 | Extruding and Drawing Machine Setters, Operators, and Tenders, Metal and Plastic | 51-4021.00 | `demanded` | evaluation | 0.002 | 818 | 354 | 604 | 499 | 778 |
| 732 | Shoe Machine Operators and Tenders | 51-6042.00 | `demanded` | evaluation | 0.002 | 554 | 820 | 604 | 837 | 822 |
| 732 | Crushing, Grinding, and Polishing Machine Setters, Operators, and Tenders | 51-9021.00 | `demanded` | evaluation | 0.002 | 835 | 809 | 604 | 827 | 809 |
| 732 | Railroad Conductors and Yardmasters | 53-4031.00 | `demanded` | oversight | 0.002 | 554 | 741 | 630 | 499 | 403 |
| 739 | Hazardous Materials Removal Workers | 47-4041.00 | `demanded` | intent-specification | 0.002 | 531 | 822 | 857 | 841 | 826 |
| 740 | Emergency Medicine Physicians | 29-1214.00 | `demanded` | evaluation | 0.002 | 588 | 388 | 614 | 773 | 739 |
| 740 | Mail Clerks and Mail Machine Operators, Except Postal Service | 43-9051.00 | `demanded` | orchestration | 0.002 | 535 | 693 | 624 | 744 | 377 |
| 740 | Carpenters | 47-2031.00 | `demanded` | intent-specification | 0.002 | 533 | 365 | 840 | 811 | 390 |
| 740 | Bridge and Lock Tenders | 53-6011.00 | `demanded` | evaluation | 0.002 | 779 | 718 | 614 | 762 | 717 |
| 744 | Histotechnologists | 29-2011.04 | `demanded` | evaluation | 0.002 | 558 | 837 | 620 | 852 | 390 |
| 744 | Fast Food and Counter Workers | 35-3023.00 | `demanded` | oversight | 0.002 | 538 | 760 | 823 | 505 | 752 |
| 744 | Metal-Refining Furnace Operators and Tenders | 51-4051.00 | `demanded` | oversight | 0.002 | 854 | 838 | 863 | 505 | 844 |
| 744 | Textile Winding, Twisting, and Drawing Out Machine Setters, Operators, and Tenders | 51-6064.00 | `demanded` | decision-framing | 0.002 | 804 | 356 | 620 | 790 | 758 |
| 744 | Cutting and Slicing Machine Setters, Operators, and Tenders | 51-9032.00 | `demanded` | evaluation | 0.002 | 831 | 369 | 620 | 531 | 803 |
| 744 | Laborers and Freight, Stock, and Material Movers, Hand | 53-7062.00 | `demanded` | orchestration | 0.002 | 838 | 813 | 850 | 831 | 379 |
| 750 | Home Health Aides | 31-1121.00 | `demanded` | intent-specification | 0.002 | 538 | 812 | 849 | 830 | 812 |
| 750 | Barbers | 39-5011.00 | `demanded` | evaluation | 0.002 | 802 | 763 | 624 | 788 | 756 |
| 750 | Mechanical Door Repairers | 49-9011.00 | `demanded` | oversight | 0.002 | 808 | 769 | 656 | 509 | 763 |
| 750 | Welding, Soldering, and Brazing Machine Setters, Operators, and Tenders | 51-4122.00 | `demanded` | oversight | 0.002 | 845 | 378 | 674 | 509 | 399 |
| 750 | Heat Treating Equipment Setters, Operators, and Tenders, Metal and Plastic | 51-4191.00 | `demanded` | orchestration | 0.002 | 815 | 778 | 630 | 803 | 382 |
| 750 | Sawing Machine Setters, Operators, and Tenders, Wood | 51-7041.00 | `demanded` | evaluation | 0.002 | 566 | 369 | 624 | 864 | 409 |
| 750 | Packaging and Filling Machine Operators and Tenders | 51-9111.00 | `demanded` | evaluation | 0.002 | 817 | 783 | 624 | 806 | 777 |
| 750 | Helpers--Production Workers | 51-9198.00 | `demanded` | evaluation | 0.002 | 566 | 794 | 624 | 815 | 792 |
| 758 | Automotive Body and Related Repairers | 49-3021.00 | `demanded` | evaluation | 0.002 | 571 | 823 | 630 | 842 | 828 |
| 758 | Power Plant Operators | 51-8013.00 | `demanded` | intent-specification | 0.002 | 541 | 740 | 670 | 519 | 403 |
| 760 | Animal Breeders | 45-2021.00 | `demanded` | intent-specification | 0.001 | 544 | 797 | 670 | 818 | 795 |
| 760 | Plasterers and Stucco Masons | 47-2161.00 | `demanded` | oversight | 0.001 | 833 | 805 | 846 | 514 | 805 |
| 760 | Control and Valve Installers and Repairers, Except Mechanical Door | 49-9012.00 | `demanded` | evaluation | 0.001 | 579 | 806 | 635 | 824 | 806 |
| 760 | Shoe and Leather Workers and Repairers | 51-6041.00 | `demanded` | evaluation | 0.001 | 547 | 773 | 635 | 797 | 768 |
| 760 | Mixing and Blending Machine Setters, Operators, and Tenders | 51-9023.00 | `demanded` | evaluation | 0.001 | 823 | 789 | 635 | 809 | 786 |
| 765 | Veterinary Technologists and Technicians | 29-2056.00 | `demanded` | oversight | 0.001 | 772 | 702 | 805 | 516 | 384 |
| 765 | Forest and Conservation Workers | 45-4011.00 | `demanded` | intent-specification | 0.001 | 547 | 361 | 842 | 812 | 789 |
| 765 | Food Cooking Machine Operators and Tenders | 51-3093.00 | `demanded` | evaluation | 0.001 | 858 | 844 | 640 | 859 | 851 |
| 768 | Rail Car Repairers | 49-3043.00 | `demanded` | oversight | 0.001 | 831 | 804 | 656 | 519 | 386 |
| 768 | Commercial Divers | 49-9092.00 | `demanded` | intent-specification | 0.001 | 549 | 793 | 643 | 814 | 791 |
| 768 | Molding, Coremaking, and Casting Machine Setters, Operators, and Tenders, Metal and Plastic | 51-4072.00 | `demanded` | evaluation | 0.001 | 579 | 829 | 643 | 519 | 832 |
| 768 | Furnace, Kiln, Oven, Drier, and Kettle Operators and Tenders | 51-9051.00 | `demanded` | evaluation | 0.001 | 860 | 378 | 643 | 535 | 399 |
| 768 | Tank Car, Truck, and Ship Loaders | 53-7121.00 | `demanded` | evaluation | 0.001 | 791 | 742 | 643 | 528 | 735 |
| 773 | Oral and Maxillofacial Surgeons | 29-1022.00 | `demanded` | intent-specification | 0.001 | 551 | 830 | 859 | 847 | 834 |
| 773 | Carpet Installers | 47-2041.00 | `demanded` | intent-specification | 0.001 | 551 | 825 | 858 | 844 | 829 |
| 773 | Sheet Metal Workers | 47-2211.00 | `demanded` | evaluation | 0.001 | 579 | 378 | 648 | 854 | 846 |
| 773 | Motorboat Mechanics and Service Technicians | 49-3051.00 | `demanded` | evaluation | 0.001 | 851 | 836 | 648 | 526 | 841 |
| 773 | Structural Metal Fabricators and Fitters | 51-2041.00 | `demanded` | evaluation | 0.001 | 584 | 839 | 648 | 853 | 845 |
| 773 | Food and Tobacco Roasting, Baking, and Drying Machine Operators and Tenders | 51-3091.00 | `demanded` | evaluation | 0.001 | 837 | 811 | 648 | 829 | 811 |
| 773 | Welders, Cutters, Solderers, and Brazers | 51-4121.00 | `demanded` | evaluation | 0.001 | 585 | 378 | 648 | 535 | 826 |
| 773 | Plating Machine Setters, Operators, and Tenders, Metal and Plastic | 51-4193.00 | `demanded` | evaluation | 0.001 | 844 | 825 | 648 | 525 | 403 |
| 773 | Paper Goods Machine Setters, Operators, and Tenders | 51-9196.00 | `demanded` | evaluation | 0.001 | 850 | 835 | 648 | 850 | 840 |
| 782 | Telecommunications Line Installers and Repairers | 49-9052.00 | `demanded` | evaluation | 0.001 | 843 | 821 | 656 | 840 | 825 |
| 782 | Grinding and Polishing Workers, Hand | 51-9022.00 | `demanded` | evaluation | 0.001 | 848 | 369 | 656 | 849 | 838 |
| 782 | Crane and Tower Operators | 53-7021.00 | `demanded` | evaluation | 0.001 | 872 | 861 | 656 | 873 | 403 |
| 785 | Ophthalmologists, Except Pediatric | 29-1241.00 | `demanded` | intent-specification | 0.001 | 558 | 743 | 664 | 771 | 736 |
| 785 | Firefighters | 33-2011.00 | `demanded` | intent-specification | 0.001 | 558 | 790 | 664 | 810 | 787 |
| 785 | Cooks, Fast Food | 35-2011.00 | `demanded` | intent-specification | 0.001 | 558 | 824 | 664 | 843 | 396 |
| 785 | Terrazzo Workers and Finishers | 47-2053.00 | `demanded` | intent-specification | 0.001 | 558 | 845 | 867 | 860 | 852 |
| 785 | Painters, Construction and Maintenance | 47-2141.00 | `demanded` | decision-framing | 0.001 | 842 | 367 | 855 | 836 | 820 |
| 785 | Wind Turbine Service Technicians | 49-9081.00 | `demanded` | evaluation | 0.001 | 591 | 869 | 664 | 528 | 869 |
| 785 | Gas Compressor and Gas Pumping Station Operators | 53-7071.00 | `demanded` | evaluation | 0.001 | 855 | 840 | 664 | 854 | 846 |
| 792 | Tree Trimmers and Pruners | 37-3013.00 | `demanded` | intent-specification | 0.001 | 566 | 818 | 852 | 531 | 817 |
| 792 | Continuous Mining Machine Operators | 47-5041.00 | `demanded` | evaluation | 0.001 | 856 | 841 | 670 | 856 | 848 |
| 792 | Riggers | 49-9096.00 | `demanded` | oversight | 0.001 | 859 | 372 | 866 | 531 | 396 |
| 795 | Food Preparation Workers | 35-2021.00 | `demanded` | intent-specification | 0.001 | 571 | 372 | 845 | 823 | 803 |
| 795 | Explosives Workers, Ordnance Handling Experts, and Blasters | 47-5032.00 | `demanded` | intent-specification | 0.001 | 571 | 731 | 813 | 770 | 732 |
| 795 | Cutting, Punching, and Press Machine Setters, Operators, and Tenders, Metal and Plastic | 51-4031.00 | `demanded` | evaluation | 0.001 | 585 | 858 | 673 | 541 | 414 |
| 795 | Sewing Machine Operators | 51-6031.00 | `demanded` | intent-specification | 0.001 | 571 | 372 | 854 | 835 | 819 |
| 795 | Industrial Truck and Tractor Operators | 53-7051.00 | `demanded` | intent-specification | 0.001 | 571 | 862 | 875 | 874 | 863 |
| 795 | Recycling and Reclamation Workers | 53-7062.04 | `demanded` | intent-specification | 0.001 | 571 | 841 | 864 | 856 | 848 |
| 801 | Nurse Anesthetists | 29-1151.00 | `demanded` | decision-framing | 0.001 | 588 | 378 | 674 | 772 | 737 |
| 801 | Surgical Assistants | 29-9093.00 | `demanded` | oversight | 0.001 | 864 | 850 | 680 | 535 | 409 |
| 801 | Orderlies | 31-1132.00 | `demanded` | decision-framing | 0.001 | 851 | 378 | 862 | 851 | 841 |
| 801 | Medical Equipment Preparers | 31-9093.00 | `demanded` | evaluation | 0.001 | 863 | 848 | 674 | 863 | 399 |
| 801 | Construction Laborers | 47-2061.00 | `demanded` | intent-specification | 0.001 | 579 | 851 | 870 | 535 | 856 |
| 801 | Molders, Shapers, and Casters, Except Metal and Plastic | 51-9195.00 | `demanded` | evaluation | 0.001 | 869 | 857 | 674 | 871 | 861 |
| 801 | Potters, Manufacturing | 51-9195.05 | `demanded` | intent-specification | 0.001 | 579 | 852 | 680 | 866 | 857 |
| 808 | Family Medicine Physicians | 29-1215.00 | `demanded` | evaluation | 0.001 | 591 | 745 | 678 | 774 | 414 |
| 808 | Pressers, Textile, Garment, and Related Materials | 51-6021.00 | `demanded` | oversight | 0.001 | 848 | 834 | 861 | 541 | 838 |
| 808 | Railroad Brake, Signal, and Switch Operators and Locomotive Firers | 53-4022.00 | `demanded` | oversight | 0.001 | 870 | 859 | 873 | 541 | 409 |
| 811 | Anesthesiologist Assistants | 29-1071.01 | `demanded` | oversight | 0.000 | 876 | 870 | 881 | 545 | 870 |
| 811 | Drywall and Ceiling Tile Installers | 47-2081.00 | `demanded` | intent-specification | 0.000 | 585 | 849 | 869 | 865 | 408 |
| 811 | Aircraft Structure, Surfaces, Rigging, and Systems Assemblers | 51-2011.00 | `demanded` | evaluation | 0.000 | 860 | 846 | 679 | 545 | 853 |
| 814 | Phlebotomists | 31-9097.00 | `demanded` | evaluation | 0.000 | 792 | 744 | 680 | 547 | 738 |
| 814 | Embalmers | 39-4011.00 | `demanded` | evaluation | 0.000 | 862 | 847 | 680 | 861 | 854 |
| 814 | Glaziers | 47-2121.00 | `demanded` | intent-specification | 0.000 | 588 | 389 | 868 | 862 | 855 |
| 814 | Electric Motor, Power Tool, and Related Repairers | 49-2092.00 | `demanded` | evaluation | 0.000 | 868 | 856 | 680 | 870 | 860 |
| 814 | Rail Yard Engineers, Dinkey Operators, and Hostlers | 53-4013.00 | `demanded` | orchestration | 0.000 | 866 | 854 | 871 | 868 | 409 |
| 819 | Surgical Technologists | 29-2055.00 | `demanded` | orchestration | 0.000 | 875 | 866 | 879 | 876 | 414 |
| 819 | Rotary Drill Operators, Oil and Gas | 47-5012.00 | `demanded` | oversight | 0.000 | 874 | 865 | 878 | 549 | 866 |
| 819 | Coating, Painting, and Spraying Machine Setters, Operators, and Tenders | 51-9124.00 | `demanded` | evaluation | 0.000 | 865 | 853 | 685 | 867 | 858 |
| 819 | Sailors and Marine Oilers | 53-5011.00 | `demanded` | intent-specification | 0.000 | 591 | 867 | 880 | 549 | 867 |
| 823 | Fishing and Hunting Workers | 45-3031.00 | `demanded` | intent-specification | 0.000 | 594 | 864 | 877 | 551 | 865 |
| 823 | Operating Engineers and Other Construction Equipment Operators | 47-2073.00 | `demanded` | intent-specification | 0.000 | 594 | 868 | 686 | 877 | 868 |
| 825 | Farm Labor Contractors | 13-1074.00 | `demanded` | oversight | 0.000 | 877 | 871 | 882 | 552 | 417 |
| 825 | Athletes and Sports Competitors | 27-2021.00 | `demanded` | intent-specification | 0.000 | 596 | 871 | 882 | 878 | 417 |
| 825 | Cooks, Short Order | 35-2015.00 | `demanded` | intent-specification | 0.000 | 596 | 871 | 882 | 878 | 871 |
| 825 | Dishwashers | 35-9021.00 | `demanded` | intent-specification | 0.000 | 596 | 871 | 882 | 878 | 871 |
| 825 | Agricultural Equipment Operators | 45-2091.00 | `demanded` | intent-specification | 0.000 | 596 | 871 | 882 | 552 | 871 |
| 825 | Floor Layers, Except Carpet, Wood, and Hard Tiles | 47-2042.00 | `demanded` | intent-specification | 0.000 | 596 | 871 | 882 | 878 | 871 |
| 825 | Cement Masons and Concrete Finishers | 47-2051.00 | `demanded` | intent-specification | 0.000 | 596 | 871 | 882 | 878 | 871 |
| 825 | Paving, Surfacing, and Tamping Equipment Operators | 47-2071.00 | `demanded` | evaluation | 0.000 | 877 | 871 | 687 | 552 | 871 |
| 825 | Tapers | 47-2082.00 | `demanded` | evaluation | 0.000 | 877 | 871 | 687 | 878 | 871 |
| 825 | Paperhangers | 47-2142.00 | `demanded` | evaluation | 0.000 | 877 | 871 | 687 | 878 | 871 |
| 825 | Pipelayers | 47-2151.00 | `demanded` | evaluation | 0.000 | 877 | 871 | 687 | 878 | 871 |
| 825 | Roofers | 47-2181.00 | `demanded` | evaluation | 0.000 | 877 | 871 | 687 | 878 | 871 |
| 825 | Helpers--Carpenters | 47-3012.00 | `demanded` | decision-framing | 0.000 | 877 | 390 | 882 | 878 | 871 |
| 825 | Helpers--Pipelayers, Plumbers, Pipefitters, and Steamfitters | 47-3015.00 | `demanded` | decision-framing | 0.000 | 877 | 390 | 882 | 878 | 871 |
| 825 | Helpers--Roofers | 47-3016.00 | `demanded` | oversight | 0.000 | 877 | 871 | 882 | 552 | 871 |
| 825 | Highway Maintenance Workers | 47-4051.00 | `demanded` | intent-specification | 0.000 | 596 | 871 | 687 | 878 | 871 |
| 825 | Rail-Track Laying and Maintenance Equipment Operators | 47-4061.00 | `demanded` | oversight | 0.000 | 877 | 871 | 882 | 552 | 417 |
| 825 | Derrick Operators, Oil and Gas | 47-5011.00 | `demanded` | evaluation | 0.000 | 877 | 871 | 687 | 878 | 871 |
| 825 | Excavating and Loading Machine and Dragline Operators, Surface Mining | 47-5022.00 | `demanded` | intent-specification | 0.000 | 596 | 871 | 882 | 552 | 871 |
| 825 | Automotive Glass Installers and Repairers | 49-3022.00 | `demanded` | decision-framing | 0.000 | 877 | 390 | 687 | 878 | 871 |
| 825 | Bus and Truck Mechanics and Diesel Engine Specialists | 49-3031.00 | `demanded` | evaluation | 0.000 | 877 | 871 | 687 | 878 | 871 |
| 825 | Electrical Power-Line Installers and Repairers | 49-9051.00 | `demanded` | evaluation | 0.000 | 877 | 871 | 687 | 878 | 417 |
| 825 | Helpers--Installation, Maintenance, and Repair Workers | 49-9098.00 | `demanded` | intent-specification | 0.000 | 596 | 871 | 882 | 878 | 871 |
| 825 | Electromechanical Equipment Assemblers | 51-2023.00 | `demanded` | evaluation | 0.000 | 877 | 871 | 687 | 878 | 871 |
| 825 | Engine and Other Machine Assemblers | 51-2031.00 | `demanded` | intent-specification | 0.000 | 596 | 871 | 687 | 878 | 871 |
| 825 | Timing Device Assemblers and Adjusters | 51-2061.00 | `demanded` | evaluation | 0.000 | 877 | 871 | 687 | 878 | 871 |
| 825 | Drilling and Boring Machine Tool Setters, Operators, and Tenders, Metal and Plastic | 51-4032.00 | `demanded` | evaluation | 0.000 | 877 | 871 | 687 | 552 | 871 |
| 825 | Pourers and Casters, Metal | 51-4052.00 | `demanded` | oversight | 0.000 | 877 | 871 | 882 | 552 | 871 |
| 825 | Tool Grinders, Filers, and Sharpeners | 51-4194.00 | `demanded` | intent-specification | 0.000 | 596 | 390 | 687 | 552 | 871 |
| 825 | Adhesive Bonding Machine Operators and Tenders | 51-9191.00 | `demanded` | decision-framing | 0.000 | 877 | 390 | 687 | 552 | 871 |
| 825 | Dredge Operators | 53-7031.00 | `demanded` | oversight | 0.000 | 877 | 871 | 882 | 552 | 871 |
| 825 | Wellhead Pumpers | 53-7073.00 | `demanded` | oversight | 0.000 | 877 | 871 | 882 | 552 | 417 |
| 857 | Counter and Rental Clerks | 41-2021.00 | `emerging` | intent-specification | 0.520 | 608 | 400 | 706 | 569 | 429 |
| 858 | Door-to-Door Sales Workers, News and Street Vendors, and Related Workers | 41-9091.00 | `emerging` | intent-specification | 0.462 | 611 | 406 | 707 | 576 | 437 |
| 859 | Demonstrators and Product Promoters | 41-9011.00 | `emerging` | intent-specification | 0.279 | 642 | 460 | 722 | 618 | 499 |
| 860 | Retail Salespersons | 41-2031.00 | `emerging` | intent-specification | 0.234 | 652 | 484 | 733 | 633 | 519 |
| 861 | Crematory Operators | 39-4012.00 | `emerging` | intent-specification | 0.125 | 655 | 488 | 737 | 639 | 527 |
| 862 | Postal Service Clerks | 43-5051.00 | `net-cost` | intent-specification | 0.189 | 672 | 534 | 748 | 665 | 555 |
| 863 | Office Machine Operators, Except Computer | 43-9071.00 | `net-cost` | intent-specification | 0.135 | 692 | 569 | 760 | 683 | 593 |
| 864 | Baristas | 35-3023.01 | `net-cost` | intent-specification | 0.127 | 694 | 580 | 764 | 685 | 602 |
| 865 | Watch and Clock Repairers | 49-9064.00 | `net-cost` | intent-specification | 0.111 | 705 | 597 | 770 | 693 | 615 |
| 866 | School Bus Monitors | 33-9094.00 | `net-cost` | intent-specification | 0.101 | 713 | 613 | 775 | 706 | 629 |
| 867 | Bailiffs | 33-3011.00 | `net-cost` | intent-specification | 0.082 | 726 | 633 | 783 | 717 | 649 |
| 868 | Log Graders and Scalers | 45-4023.00 | `net-cost` | intent-specification | 0.079 | 728 | 636 | 784 | 719 | 651 |
| 869 | Animal Trainers | 39-2011.00 | `net-cost` | intent-specification | 0.078 | 729 | 638 | 785 | 720 | 652 |
| 870 | Skincare Specialists | 39-5094.00 | `net-cost` | intent-specification | 0.067 | 738 | 653 | 789 | 726 | 664 |
| 871 | Driver/Sales Workers | 53-3031.00 | `net-cost` | intent-specification | 0.066 | 741 | 656 | 791 | 730 | 669 |
| 872 | Insulation Workers, Floor, Ceiling, and Wall | 47-2131.00 | `net-cost` | intent-specification | 0.059 | 749 | 670 | 794 | 736 | 683 |
| 873 | Medical Appliance Technicians | 51-9082.00 | `net-cost` | intent-specification | 0.059 | 752 | 674 | 795 | 737 | 687 |
| 874 | Ophthalmic Medical Technicians | 29-2057.00 | `net-cost` | intent-specification | 0.049 | 763 | 689 | 799 | 743 | 702 |
| 875 | Outdoor Power Equipment and Other Small Engine Mechanics | 49-3053.00 | `net-cost` | intent-specification | 0.045 | 767 | 696 | 802 | 746 | 707 |
| 876 | Lifeguards, Ski Patrol, and Other Recreational Protective Service Workers | 33-9092.00 | `net-cost` | intent-specification | 0.038 | 775 | 712 | 806 | 757 | 714 |
| 877 | Animal Control Workers | 33-9011.00 | `net-cost` | intent-specification | 0.035 | 778 | 716 | 808 | 760 | 716 |
| 878 | Maintenance Workers, Machinery | 49-9043.00 | `net-cost` | intent-specification | 0.032 | 781 | 720 | 809 | 764 | 719 |
| 879 | Pharmacy Aides | 31-9095.00 | `net-cost` | intent-specification | 0.029 | 783 | 726 | 811 | 768 | 725 |
| 880 | Service Unit Operators, Oil and Gas | 47-5013.00 | `net-cost` | intent-specification | 0.027 | 787 | 729 | 812 | 769 | 729 |
| 881 | Shampooers | 39-5093.00 | `absent` | intent-specification | 0.057 | 795 | 752 | 818 | 778 | 744 |
| 882 | Locksmiths and Safe Repairers | 49-9094.00 | `absent` | intent-specification | 0.042 | 801 | 762 | 825 | 786 | 755 |
| 883 | Farmworkers, Farm, Ranch, and Aquacultural Animals | 45-2093.00 | `absent` | intent-specification | 0.037 | 806 | 767 | 827 | 791 | 761 |
| 884 | Graders and Sorters, Agricultural Products | 45-2041.00 | `absent` | intent-specification | 0.035 | 810 | 772 | 829 | 795 | 766 |
| 885 | Rock Splitters, Quarry | 47-5051.00 | `absent` | intent-specification | 0.033 | 812 | 775 | 832 | 800 | 771 |
| 885 | Bicycle Repairers | 49-3091.00 | `absent` | intent-specification | 0.033 | 812 | 775 | 832 | 800 | 771 |
| 887 | Ophthalmic Medical Technologists | 29-2099.05 | `absent` | intent-specification | 0.029 | 819 | 785 | 837 | 808 | 781 |
| 888 | Dancers | 27-2031.00 | `absent` | intent-specification | 0.025 | 826 | 796 | 843 | 817 | 794 |
| 889 | Sewers, Hand | 51-6051.00 | `absent` | intent-specification | 0.025 | 827 | 798 | 844 | 819 | 796 |
| 890 | Automotive and Watercraft Service Attendants | 53-6031.00 | `absent` | intent-specification | 0.021 | 834 | 808 | 848 | 826 | 808 |
| 891 | Helpers--Extraction Workers | 47-5081.00 | `absent` | intent-specification | 0.019 | 840 | 817 | 851 | 833 | 816 |
| 892 | Janitors and Cleaners, Except Maids and Housekeeping Cleaners | 37-2011.00 | `absent` | intent-specification | 0.018 | 841 | 819 | 853 | 834 | 818 |
| 893 | Logging Equipment Operators | 45-4022.00 | `absent` | intent-specification | 0.014 | 847 | 832 | 860 | 848 | 836 |
| 894 | Ambulance Drivers and Attendants, Except Emergency Medical Technicians | 53-3011.00 | `absent` | intent-specification | 0.011 | 856 | 841 | 864 | 856 | 848 |
| 895 | Butchers and Meat Cutters | 51-3021.00 | `absent` | intent-specification | 0.007 | 866 | 854 | 871 | 868 | 859 |
| 896 | Millwrights | 49-9044.00 | `absent` | intent-specification | 0.006 | 871 | 860 | 874 | 872 | 862 |
| 897 | Fence Erectors | 47-4031.00 | `absent` | intent-specification | 0.006 | 873 | 862 | 875 | 874 | 863 |
| 898 | Histology Technicians | 29-2012.01 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Endoscopy Technicians | 31-9099.02 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Dining Room and Cafeteria Attendants and Bartender Helpers | 35-9011.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Boilermakers | 47-2011.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Brickmasons and Blockmasons | 47-2021.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Stonemasons | 47-2022.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Floor Sanders and Finishers | 47-2043.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Pile Driver Operators | 47-2072.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Reinforcing Iron and Rebar Workers | 47-2171.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Structural Iron and Steel Workers | 47-2221.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Helpers--Brickmasons, Blockmasons, Stonemasons, and Tile and Marble Setters | 47-3011.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Helpers--Electricians | 47-3013.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Helpers--Painters, Paperhangers, Plasterers, and Stucco Masons | 47-3014.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Roof Bolters, Mining | 47-5043.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Roustabouts, Oil and Gas | 47-5071.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Motorcycle Mechanics | 49-3052.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Tire Repairers and Changers | 49-3093.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Refractory Materials Repairers, Except Brickmasons | 49-9045.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Musical Instrument Repairers and Tuners | 49-9063.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Meat, Poultry, and Fish Cutters and Trimmers | 51-3022.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Slaughterers and Meat Packers | 51-3023.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Foundry Mold and Coremakers | 51-4071.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Cutters and Trimmers, Hand | 51-9031.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Tire Builders | 51-9197.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Aircraft Cargo Handling Supervisors | 53-1041.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 898 | Cleaners of Vehicles and Equipment | 53-7061.00 | `absent` | intent-specification | 0.000 | 877 | 871 | 882 | 878 | 871 |
| 924 | Education Administrators, All Other | 11-9039.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Personal Service Managers, All Other | 11-9179.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Managers, All Other | 11-9199.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Business Operations Specialists, All Other | 13-1199.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Financial Specialists, All Other | 13-2099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Computer Occupations, All Other | 15-1299.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Mathematical Science Occupations, All Other | 15-2099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Engineers, All Other | 17-2199.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Drafters, All Other | 17-3019.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Engineering Technologists and Technicians, Except Drafters, All Other | 17-3029.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Biological Scientists, All Other | 19-1029.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Life Scientists, All Other | 19-1099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Physical Scientists, All Other | 19-2099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Psychologists, All Other | 19-3039.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Social Scientists and Related Workers, All Other | 19-3099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Life, Physical, and Social Science Technicians, All Other | 19-4099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Counselors, All Other | 21-1019.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Social Workers, All Other | 21-1029.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Community and Social Service Specialists, All Other | 21-1099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Religious Workers, All Other | 21-2099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Legal Support Workers, All Other | 23-2099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Social Sciences Teachers, Postsecondary, All Other | 25-1069.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Postsecondary Teachers, All Other | 25-1199.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Special Education Teachers, All Other | 25-2059.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Teachers and Instructors, All Other | 25-3099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Teaching Assistants, All Other | 25-9049.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Educational Instruction and Library Workers, All Other | 25-9099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Artists and Related Workers, All Other | 27-1019.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Designers, All Other | 27-1029.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Entertainers and Performers, Sports and Related Workers, All Other | 27-2099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Media and Communication Workers, All Other | 27-3099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Media and Communication Equipment Workers, All Other | 27-4099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Dentists, All Other Specialists | 29-1029.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Therapists, All Other | 29-1129.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Physicians, All Other | 29-1229.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Surgeons, All Other | 29-1249.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Healthcare Diagnosing or Treating Practitioners, All Other | 29-1299.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Health Technologists and Technicians, All Other | 29-2099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Healthcare Practitioners and Technical Workers, All Other | 29-9099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Healthcare Support Workers, All Other | 31-9099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | First-Line Supervisors of Protective Service Workers, All Other | 33-1099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Protective Service Workers, All Other | 33-9099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Cooks, All Other | 35-2019.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Food Preparation and Serving Related Workers, All Other | 35-9099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Building Cleaning Workers, All Other | 37-2019.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Grounds Maintenance Workers, All Other | 37-3019.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Gambling Service Workers, All Other | 39-3019.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Entertainment Attendants and Related Workers, All Other | 39-3099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Personal Care and Service Workers, All Other | 39-9099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Sales and Related Workers, All Other | 41-9099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Communications Equipment Operators, All Other | 43-2099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Financial Clerks, All Other | 43-3099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Information and Record Clerks, All Other | 43-4199.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Office and Administrative Support Workers, All Other | 43-9199.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Agricultural Workers, All Other | 45-2099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Logging Workers, All Other | 45-4029.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Helpers, Construction Trades, All Other | 47-3019.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Construction and Related Workers, All Other | 47-4099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Underground Mining Machine Operators, All Other | 47-5049.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Extraction Workers, All Other | 47-5099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Precision Instrument and Equipment Repairers, All Other | 49-9069.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Installation, Maintenance, and Repair Workers, All Other | 49-9099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Assemblers and Fabricators, All Other | 51-2099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Food Processing Workers, All Other | 51-3099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Metal Workers and Plastic Workers, All Other | 51-4199.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Textile, Apparel, and Furnishings Workers, All Other | 51-6099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Woodworkers, All Other | 51-7099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Plant and System Operators, All Other | 51-8099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Production Workers, All Other | 51-9199.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | First-Line Supervisors of Transportation Workers, All Other | 53-1049.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Motor Vehicle Operators, All Other | 53-3099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Rail Transportation Workers, All Other | 53-4099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Transportation Workers, All Other | 53-6099.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Material Moving Workers, All Other | 53-7199.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Air Crew Officers | 55-1011.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Aircraft Launch and Recovery Officers | 55-1012.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Armored Assault Vehicle Officers | 55-1013.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Artillery and Missile Officers | 55-1014.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Command and Control Center Officers | 55-1015.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Infantry Officers | 55-1016.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Special Forces Officers | 55-1017.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Military Officer Special and Tactical Operations Leaders, All Other | 55-1019.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | First-Line Supervisors of Air Crew Members | 55-2011.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | First-Line Supervisors of Weapons Specialists/Crew Members | 55-2012.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | First-Line Supervisors of All Other Tactical Operations Specialists | 55-2013.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Air Crew Members | 55-3011.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Aircraft Launch and Recovery Specialists | 55-3012.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Armored Assault Vehicle Crew Members | 55-3013.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Artillery and Missile Crew Members | 55-3014.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Command and Control Center Specialists | 55-3015.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Infantry | 55-3016.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Special Forces | 55-3018.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
| 924 | Military Enlisted Tactical Operations and Air/Weapons Specialists and Crew Members, All Other | 55-3019.00 | `unsourced` | — | 0.000 | 924 | 924 | 924 | 924 | 924 |
