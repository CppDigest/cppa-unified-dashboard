---
Report Date: 2025-12-23
Summary Created: 2025-12-24
Report Type: Research Report
Topic: Corporate Avoidance of MIT License Due to Binary Attribution
---

# Research Report Summary: Corporate Avoidance of MIT License Due to Binary Attribution

## Executive Summary

**Primary Finding:** No public evidence found that large, market-influential companies explicitly avoid MIT-licensed code because it requires preserving copyright and license notices in binaries or user-facing products.

**Research Scope:** Publicly available materials reviewed (primarily up to late 2024, with some 2025 product documentation), including ~40 company open-source portals, >15 license classification documents, >30 product third-party notices, and >10 OSPO talks and white papers.

**Key Limitation:** This finding reflects search results only and does not rule out non-public policies or informal practices.

---

## Critical Findings (High Priority)

### 1. No Explicit Avoidance Policies Found

- Searched 2020-2025 policy documents, OSPO materials, engineering guidelines, and conference talks
- No explicit statement found where a large company says: "We avoid MIT because its attribution requirement in binaries/UI is too burdensome"
- Public OSPO surveys and governance reports (Linux Foundation, TODO Group) do not identify "MIT attribution in binaries/UI" as a recurring reason for inbound-license avoidance [21][23][24][25][26]

### 2. MIT is Widely Accepted by Major Companies

**Evidence of acceptance:**
- Google: Treats MIT as permitted notice license in third-party rules [3][4][5]
- Microsoft: Uses MIT widely in first-party projects and dependencies [7][20]
- Meta: Relicensed React and major projects to MIT (moved away from BSD+Patents) [12]
- Apple: Ships macOS/iOS with MIT components listed in open source releases [13]
- Oracle, NetApp, IBM/Red Hat: All use MIT with standard attribution processes [9][11][14][15]

**Quantitative evidence:**
- MIT is the single most common license in public repositories [16][19]
- Typical commercial applications contain hundreds of open-source components, with MIT among the most common [24]
- Single Android device or desktop OS typically includes hundreds of third-party packages, many MIT-licensed [6][13][24]

### 3. Attribution is Managed Operationally, Not Avoided

**Standard approaches:**
- Automated scanning and SBOM (Software Bill of Materials) tools [21][22][23][24][25][29][30]
- Centralized LICENSE or third-party notices bundles [3][6][21][23][25][27][28]
- Compliance programs aligned with OpenChain specification [21][22][30]
- Standard platform locations (Android settings, app Legal sections, device documentation) [6][7][13][21][23][27]

**Key insight:** Once compliance pipelines exist, the incremental cost of MIT's notice requirement is small relative to the overall compliance infrastructure cost [21][23][24][29][30].

---

## Important Findings (Medium Priority)

### What Companies Actually Avoid

Public policies show avoidance or restrictions for:
- Strong copyleft licenses (GPLv3, AGPL) [3][14][15][18][21][24]
- Network copyleft or non-commercial licenses [3][14][15][18][21][23][24]
- Licenses with unusual clauses (advertising, field-of-use restrictions) [3][14][15][18][21][23][24]

**Not** MIT-style permissive licenses with attribution requirements [3][14][15][18][21][22][23][24][25][26].

### Zero-Attribution Variants (MIT-0, 0BSD)

**What they are:**
- MIT-0: MIT variant that removes attribution requirement [2][8]
- 0BSD: No-attribution permissive license [17]

**How companies use them:**
- Outbound use: For sample code, templates, examples to minimize downstream obligations [2][8][17][19]
- Not used as justification to avoid inbound MIT in public documents
- Pattern: MIT accepted inbound; MIT-0/0BSD used outbound where zero obligations are a product goal

---

## Supporting Details (Lower Priority)

### Search Methodology

**Timeframe:** 2018 to late 2025 (primary focus 2018-2024)

**Sources reviewed:**
- ~40 company open-source/legal portals
- >15 explicit license classification documents
- >30 product third-party notices from major vendors
- >10 OSPO talks and white papers

**Companies covered:** Apple, Microsoft, Google, Amazon, Meta, NVIDIA, Oracle, IBM, Red Hat, SAP, Adobe, Cisco, and others

### Evidence Gaps and Limitations

**Plausible but undocumented scenarios:**
- Internal product-specific policies for particular product lines (e.g., consumer electronics with limited UI)
- Informal preferences by engineering teams (e.g., prefer Apache-2.0 or MIT-0 without formal MIT bans)
- Procurement/M&A due diligence preferences for suppliers with smaller license subsets
- Highly regulated industries (aerospace, automotive, medical, defense) with stricter embedded software rules

**Important:** These scenarios are plausible but not documented in reviewed sources. The absence of public MIT-avoidance means such policies are not prominent in public discourse, not that they don't exist anywhere.

---

## Practical Takeaways

### For Policy and Engineering

1. **MIT remains widely accepted** among major technology companies as a standard permissive notice license [3][7][9][11][12][13][14][15][18][20][24][27][28]

2. **No public evidence** that binary/UI attribution requirement causes avoidance, even though attribution management has real operational cost [6][14][15][21][23][24][29][30]

3. **When to use zero-attribution licenses:**
   - MIT-0/0BSD appropriate for examples, snippets, templates [2][8][17][19]
   - Goal: Minimize obligations for downstream users

4. **Best practices for product development:**
   - Build robust processes and tooling for tracking license notices [3][6][21][22][23][24][25][27][29][30]
   - Address patent, copyleft, and non-commercial license questions (these are more common risk drivers) [14][15][18][21][22][23][24][26]
   - Treat MIT as part of normal permissive notice license family, not a special risk category

---

## Summary Comparison Table

| Question | Evidence-Based Answer |
|---------|---------------------|
| Any large company with public policy avoiding MIT due to binary/UI attribution? | No explicit, verifiable examples found in reviewed public materials. Non-public or informal practices possible but not documented. |
| Do major companies accept MIT inbound? | Yes. MIT widely used and classified as standard permissive notice license [3][7][9][11][12][13][14][15][18][20][24][27][28]. |
| How is MIT attribution typically implemented? | Consolidated LICENSE files, third-party notices, in-app legal screens. Often automated via compliance tooling [3][6][7][9][10][11][13][20][21][23][24][27][28][30]. |
| Role of MIT-0 and 0BSD | Used mainly for outbound sample/template code to minimize downstream obligations, not as justification to avoid inbound MIT [2][8][17][19]. |
| Main drivers of license avoidance | Strong copyleft, network copyleft, non-commercial, unusual custom licenses. MIT attribution treated as operational issue, not primary risk driver [3][14][15][18][21][22][23][24][25][26]. |

---

## Main Sources

[1] MIT License – Open Source Initiative  
https://opensource.org/license/mit/

[2] MIT License (including MIT-0) – Wikipedia  
https://en.wikipedia.org/wiki/MIT_License

[3] Licenses – Google third-party license categories and rules  
https://opensource.google/documentation/reference/thirdparty/licenses

[4] Compliance Linter – Google third-party licensing rules  
https://opensource.google.com/docs/thirdparty/linter

[5] Third-Party code policy – Google Open Source  
https://opensource.google/documentation/reference/thirdparty

[6] Android Open Source Project – Licenses and notice handling  
https://source.android.com/docs/setup/start/licenses

[7] Microsoft Third-Party Notices overview  
https://learn.microsoft.com/en-us/legal/third-party-notices

[8] AWS MIT-0 (MIT No Attribution) License repository  
https://github.com/aws/mit-0

[9] Oracle Graal Development Kit for Micronaut 4.9.1 – Licensing Information User Manual (2025)  
https://www.graal.cloud/gdk/about/lium/

[10] Oracle Communications Network Data Analytics – Third-Party Notices and/or Licenses (2025)  
https://docs.oracle.com/en/industries/communications/network-data-analytics/25.2.200/licensing_manual/third-party-notices-and-or-licenses1.html

[11] NetApp CloudSecure Open Source License Notice (2025-04-14)  
https://opensource.netapp.com/CloudSecure/2025-04-14_14:37:12/NOTICE.pdf

[12] Relicensing React, Jest, Flow, and Immutable.js to MIT – Meta engineering blog  
https://engineering.fb.com/2017/09/22/open-source/react-license/

[13] Apple Open Source releases and third-party components  
https://opensource.apple.com/

[14] Understanding open source licenses – IBM Developer  
https://developer.ibm.com/articles/cl-osslicenses/

[15] A guide to open source licenses – Red Hat Developers  
https://developers.redhat.com/articles/2021/01/14/guide-open-source-licenses

[16] Choose an open source license – GitHub / ChooseALicense (license popularity discussion)  
https://choosealicense.com

[17] 0BSD License – Open Source Initiative  
https://opensource.org/license/0bsd/

[18] SPDX License List – SPDX Workgroup (classification of MIT, BSD, Apache-2.0, etc.)  
https://spdx.org/licenses/

[19] MIT License usage and comparison – MIT License (statistics section) – Wikipedia  
https://en.wikipedia.org/wiki/MIT_License#Usage

[20] Example Microsoft third-party notices for Visual Studio  
https://learn.microsoft.com/en-us/legal/third-party-notices/visualstudio

[21] OpenChain Specification – Linux Foundation OpenChain Project (emphasis on processes and notice management)  
https://www.openchainproject.org/specification

[22] OpenChain Conformance and getting started materials – Linux Foundation OpenChain Project  
https://www.openchainproject.org/getting-started

[23] Linux Foundation (ed.), "Practical Open Source Compliance" (white papers and guides to automating compliance and notices)  
https://www.linuxfoundation.org/resources/publications/practical-open-source-compliance

[24] Synopsys (Black Duck), *Open Source Security and Risk Analysis* (OSSRA) Report (recent editions)  
https://www.synopsys.com/software-integrity/resources/analyst-reports/open-source-security-risk-analysis.html

[25] TODO Group, *Open Source Program Office (OSPO): A Practical Guide* and related best-practice materials  
https://todogroup.org/guides/creating-an-open-source-program/

[26] Linux Foundation, *The Evolution of the Open Source Program Office* (OSPO survey/governance report)  
https://www.linuxfoundation.org/resources/publications/the-evolution-of-the-open-source-program-office

[27] Intel, "Understanding Open Source License Obligations" (developer legal guidance)  
https://www.intel.com/content/www/us/en/developer/articles/technical/open-source-license-obligations.html

[28] Cisco, Open Source licensing and notices portal (examples of MIT and other permissive licenses in products)  
https://www.cisco.com/c/en/us/about/legal/open-source.html

[29] FOSSA, "Open Source License Compliance Challenges" (discussion of attribution and notice-management complexity)  
https://fossa.com/blog/open-source-license-compliance-challenges/

[30] Linux Foundation, Open source compliance and case studies (including company programs and notice tooling)  
https://www.linuxfoundation.org/resources/case-studies/

