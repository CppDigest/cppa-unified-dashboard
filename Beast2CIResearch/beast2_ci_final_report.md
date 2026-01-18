# Beast2 CI Availability Improvement Options

## Executive Summary

This report explains how to improve CI availability and speed for Beast2, Http.Io, Buffers, and Capy repositories, compares infrastructure options (GitHub-hosted vs self-hosted runners, cloud vs hardware), and provides recommendations for managing cost and performance at the organization level.

Key conclusions:

- **Self-hosted runners are essential** to eliminate 2-hour queue wait times and enable 40-50 concurrent jobs for parallel execution. GitHub-hosted runners use a shared concurrency pool that causes long queues.
- **GitHub Team plan is sufficient** for Beast2; Enterprise Cloud is only needed for compliance, SSO, or IP allow-listing requirements. High parallelism with self-hosted runners does not require Enterprise Cloud.
- **Mid-tier AWS EC2 configuration** provides the best balance: 3-6 minute full matrix runs, near-zero queue times, $400-900/month at moderate usage, $0.10-0.20 per full CI run.
- **Pooling and caching are critical:** Fast matrix (10-15 jobs) for AI bot loops completes in 2-3 minutes; full matrix (50 jobs) for releases completes in 3-6 minutes with proper caching (dependency caching + compiler caches).
- **Cloud beats hardware** for elasticity and simplicity, especially for AI-driven bursty workloads; hardware only wins at sustained very high usage over 5+ years.

---

## 1. GitHub Organization Plan Analysis

### 1.1 Cost to upgrade to Enterprise

**Plan Comparison [1][2]:**

| Plan             | Price (per user/month, annual) | Included Actions Minutes (private repos) | Suitable Use Case          |
| ---------------- | ------------------------------ | ---------------------------------------- | -------------------------- |
| Free (Org)       | $0                             | 2,000 minutes per org/month              | Small orgs, mostly public  |
| Team             | ~$4                            | 3,000 minutes per user/month             | **Recommended for Beast2** |
| Enterprise Cloud | ~$21                           | Up to 50,000 minutes (pooled)            | Compliance-heavy orgs      |

**Key Points:**

- Public repositories receive unlimited standard GitHub-hosted minutes [2]
- Self-hosted runners do not consume Actions minutes; we only pay infrastructure costs [2][4]
- GitHub has announced platform fees (~$0.002/minute) for self-hosted usage starting March 2026, after free quotas [3]

**Upgrade Cost Analysis:**

- **Team to Enterprise:** ~$17 per user/month additional cost (from ~$4 to ~$21)
- For a team of 10 users: ~$170/month additional ($2,040/year)
- For a team of 50 users: ~$850/month additional ($10,200/year)

### 1.2 Benefits of Enterprise

Enterprise Cloud adds governance and security features [1][5][6]:

- **SAML SSO:** Single sign-on with identity providers
- **SCIM provisioning:** Automated user provisioning and deprovisioning
- **Advanced auditing:** Comprehensive audit log APIs and compliance reporting
- **IP allow lists:** Organization or enterprise-level IP restrictions
- **GitHub-hosted larger runners:** Support for larger runners (4-96 vCPU) with static IPs and optional Azure private networking [3][5][6]
- **Advanced security:** Enhanced security policies and compliance controls

**When Enterprise is Needed:**

Enterprise is useful only if we need:

- IP allow-listing for security compliance
- Specific audit/compliance controls (SOC 2, HIPAA, etc.)
- Private networking for GitHub-hosted larger runners
- Advanced SSO requirements

**For Beast2:** High parallelism with self-hosted runners does **not** require Enterprise Cloud [4]. Enterprise is only needed for compliance, SSO, or IP allow-listing requirements.

### 1.3 Explore dedicated runners for the team (Beast2, Capy, etc - select repositories only)

**Self-Hosted Runners [4]:**

- Available on all plans (Free, Team, Enterprise)
- Not billed per Actions minute; only infrastructure costs
- Run on our own Linux, Windows, or macOS systems (on-premise or cloud)
- Scale horizontally: register many runners, use autoscaling and ephemeral runners
- **Concurrency limited only by our fleet size** - enables 40-50+ concurrent jobs

**Repository-Level Runner Assignment:**

Self-hosted runners support:

- **Organization-level runners:** Shared across all repos in the org
- **Repository-level runners:** Dedicated to specific repos (Beast2, Http.Io, Buffers, Capy)
- **Runner groups and labels:** Route jobs by OS, compiler, or build type [4]

**Best Practice for Beast2:**

- Use repository-level or organization-level runner groups with labels
- Isolate capacity so other organization workloads cannot consume Beast2 runners
- Configure runner groups: `linux-fast`, `linux-full`, `windows`, `macos` [4]

**GitHub-Hosted Runners [3][2] (for comparison):**

- Preconfigured images for Linux, Windows, macOS
- Billed per minute for private repos: Linux ~$0.006/min, Windows ~$0.010/min, macOS ~$0.062/min
- Shared concurrency pool with limits that cause 2-hour queues
- Larger runners (4-96 vCPU) available but expensive and still subject to concurrency limits

**For Beast2:** Self-hosted runners are the practical solution to eliminate multi-hour queues and achieve 40-50 concurrent jobs for the full matrix.

---

## 2. CI Speed Optimization Report

### 2.1 How fast can the current CI process be made to go (excluding slop-driven development)

**Current State:**

- ~50 matrix jobs × 2.5 minutes each = 125 job-minutes total compute
- Sequential execution: 2+ hours
- With limited concurrency (5-10 jobs): 60-120 minutes including 2-hour queue waits
- **Total CI cycle time: hours** (queue + execution)

**Bottlenecks:**

1. **Queue wait times:** Up to 2 hours before jobs start (hitting GitHub concurrent job limits)
2. **Limited parallelism:** Shared GitHub-hosted pool cannot guarantee 50 concurrent jobs
3. **No caching:** Cold builds take full 2-3 minutes per job

**Target Performance:**

Run all 50 matrix jobs simultaneously to achieve 2-5 minute total CI time.

**Timing Model:**

- J = number of jobs (~50)
- t = average per-job runtime (~2.5 minutes uncached, ~1-1.5 minutes with caching)
- C = effective concurrency
- Wall-clock time: W ≈ t × ceil(J ÷ C)

| Effective Concurrency | Wall-Time (uncached) | Wall-Time (warm caches) |
| --------------------- | -------------------- | ----------------------- |
| 50                    | 2.5-3.5 minutes      | 1.5-3 minutes           |
| 25                    | 5-6 minutes          | 3-5 minutes             |
| 12                    | 12-13 minutes        | 7-8 minutes             |
| 5                     | 25 minutes           | 15-20 minutes           |

**To hit 2-5 minute target:** Need 30-60 effective concurrent jobs.

**Full vs Fast Matrix Strategy:**

**Full Matrix (50 jobs):**

- All OS, compilers, C++ standards, configurations, docs, changelog checks
- At 50 concurrency: 3-4 minutes (uncached), 2-3 minutes (cached)
- Use for: merges to main, release branches, scheduled workflows

**Fast Matrix (10-15 jobs) - for AI bot:**

- Linux: Ubuntu LTS + latest with current GCC/Clang (Release)
- Windows: Windows Server 2022 with current MSVC (Release)
- macOS: One macOS runner with Apple Clang (Release)
- Omit: Debug builds, full docs jobs from bot loops
- At 25-30 concurrency: 2-3 minutes (cached)

**Caching Strategies:**

**Dependency Caching [14]:**

- Cache Boost checkouts, third-party sources (zlib, OpenSSL, brotli), package manager caches
- Use GitHub cache action keyed by OS, compiler, C++ standard, dependency versions
- **Impact:** Reduces dependency setup from 30-60 seconds to 5-10 seconds (20-30% per-job reduction)

**Compiler Caches (ccache/sccache) [15][16]:**

- **ccache:** Local filesystem caching, suited to persistent self-hosted Linux runners
- **sccache:** Local or remote caching (S3, Redis), cross-machine sharing
- **Impact:** Warm builds see 2-5x faster compile steps; per-job runtime drops from 2-3 minutes to 45-90 seconds

**Combined Impact:**

- **Cold full matrix:** 2-3 minutes per job, 2.5-3.5 minutes wall-clock at full concurrency
- **Warm full matrix:** 1-1.5 minutes per job, 1.5-3 minutes wall-clock at full concurrency
- **Effective work reduction:** From 125 job-minutes to 80-100 job-minutes

**Realistic Performance Targets:**

With optimized self-hosted fleet and caching:

| Matrix Type    | Median Completion | 90th Percentile | Notes                   |
| -------------- | ----------------- | --------------- | ----------------------- |
| Full 50-job    | ~3 minutes        | 4-5 minutes     | Occasional cache misses |
| Fast 10-15 job | 1.5-2 minutes     | ~3 minutes      | Ideal for AI bot loops  |

These figures meet the **2-5 minute AI loop target** and provide comfortable developer experience.

### 2.2 Cost analysis with 3 pricing tiers

The following configurations use AWS EC2 as the primary platform [7]. Prices are approximate on-demand rates in US regions.

**Assumptions:**

- Full matrix: 50 jobs, 125 job-minutes
- Fast matrix: ~12 jobs, 30 job-minutes
- Linux: ~70% of matrix, Windows: ~20%, macOS: ~10%

**Tier Overview:**

| Tier     | Intended Usage                   | Safe Concurrency | Full Matrix Time | Fast Matrix Time | Monthly Compute Cost (autoscaling) |
| -------- | -------------------------------- | ---------------- | ---------------- | ---------------- | ---------------------------------- |
| **Low**  | Up to 20 full runs/day           | 15-20 jobs       | 8-12 minutes     | 3-5 minutes      | $150-300                           |
| **Mid**  | ~100 full runs/day (recommended) | 35-50 jobs       | 3-6 minutes      | 2-3 minutes      | **$400-900**                       |
| **High** | 500+ full runs/day, heavy bots   | 70-100+ jobs     | 2-4 minutes      | 1.5-2.5 minutes  | $1,500-4,000                       |

Costs assume autoscaling that reduces instance count when idle. Excludes data transfer and support.

#### Low-tier option: minimal cost, moderate speed

**AWS Setup [7]:**

- **Linux runners:** 2 × c7i.xlarge (4 vCPU, 8 GiB each) = 6-8 Linux jobs
- **Windows runners:** 1 × m7i.large (2 vCPU, 8 GiB) = 2 Windows jobs
- **macOS runners:** 1 × EC2 Mac instance (occasional use)

**Characteristics:**

- Safe concurrency: ~10-12 jobs
- Full matrix: 12-15 minutes
- Fast matrix: 3-4 minutes (mostly Linux)

**Costs:**

- On-demand rates: ~$0.18/hour (c7i.xlarge), ~$0.20/hour (m7i.large)
- With autoscaling and moderate usage: **$200-300/month**
- Per full CI run: <$0.50

**Verdict: Removes worst queues but doesn't fully hit 2-5 minute target for full matrix.**

#### Mid-tier option: recommended baseline

**AWS Setup [7]:**

- **Linux runners:** 3 × c7i.4xlarge (16 vCPU, 32 GiB each) = 30-36 Linux jobs
- **Windows runners:** 2 × m7i.2xlarge (8 vCPU, 32 GiB each) = 10-12 Windows jobs
- **macOS runners:** 1 × EC2 Mac instance

**Characteristics:**

- Safe concurrency: **40-50 jobs**
- Full matrix: **3-5 minutes** (typical with caching)
- Fast matrix: **2-3 minutes** (even under moderate load)

**Costs:**

- On-demand hourly: ~$0.72/hour (c7i.4xlarge), ~$0.40/hour (m7i.2xlarge)
- With autoscaling and ~25% average utilization: **$400-900/month**
- Per full CI run: **$0.10-0.20**

**Verdict: Best balance of cost and performance. Recommended starting point for Beast2.**

#### Most expensive option: aggressive scaling for heavy bot use

**AWS Setup [7]:**

- **Linux runners:** 4-6 × c7i.4xlarge = 80-100 Linux jobs capacity
- **Windows runners:** 3-4 × m7i.2xlarge = 20-24 Windows jobs
- **macOS runners:** 2 × EC2 Mac instances

**Characteristics:**

- Safe concurrency: **70-100+ jobs**
- Full matrix: **2-4 minutes** (with headroom for spikes)
- Fast matrix: **Often <2 minutes**

**Costs:**

- At high, steady utilization (several hundred full runs/day): **$1,500-4,000/month**
- Per run cost remains relatively low; total spend reflects volume and peak capacity

**Verdict: Only justified if fast AI-driven experimentation yields strong value or CI load is consistently high across multiple repositories.**

### 2.3 High-performance hardware specifications

**CPU Specifications:**

- **c7i.4xlarge:** 16 vCPUs (Intel Xeon), high clock speed, optimized for compute workloads
- **m7i.2xlarge:** 8 vCPUs (Intel Xeon), balanced performance
- **Target:** 1 job per 2 vCPUs for optimal parallel execution

**Memory Requirements:**

- **Linux:** 32 GiB per c7i.4xlarge supports 10-12 concurrent jobs
- **Windows:** 32 GiB per m7i.2xlarge supports 5-6 concurrent jobs
- **Total:** ~200 GiB RAM across fleet for 50 concurrent jobs

**Storage Options:**

- **NVMe SSD:** Fast local storage for build directories and caches
- **EBS gp3:** For persistent runner images and shared caches
- **S3:** For cross-runner cache sharing (sccache)

**Network Capabilities:**

- 10 Gbps network for artifact transfer and cache synchronization
- Low-latency connectivity to GitHub Actions API

### 2.4 Scope: dedicated runners for the team only

**Repository-Level Runners:**

- Dedicated runners for Beast2, Http.Io, Buffers, Capy (select repositories only)
- Isolate capacity from other organization workloads
- Configure via runner groups and labels [4]

**Resource Sharing and Isolation:**

- Use repo-level runners for heavy projects (Beast2)
- Use org-level groups for shared capacity across related repos
- Configure workflow concurrency to cancel older runs on same branch
- Limit max concurrent jobs per label in autoscaler to prevent one repo from starving others

**Recommended Structure:**

- Create runner groups and labels: `linux-fast`, `linux-full`, `windows`, `macos` [4]
- Route workflows:
  - **Bot branches and early PRs:** Fast matrix (10-15 jobs, 2-3 minutes)
  - **Merges to main, releases, scheduled:** Full matrix (50 jobs, 3-6 minutes)

### 2.5 Confirm if the same runners can also support cloud-based slop-driven development

**Compatibility:**

- Same runners support both automated bot-driven CI and manual development workflows
- Ephemeral runners can be spun up for experimental branches
- Autoscaling handles varying load from both sources

**Best Practices:**

- Maintain separate labels for CI runners vs. interactive/experimental runners
- Optionally use separate node pools for CI and ad hoc usage
- Monitor queue depth and runner utilization to size baseline capacity

**AI Bot Workflow Support:**

All proposed setups work with:

- **AI bots** that push branches frequently and rely on fast feedback
- **Human developers** opening pull requests and pushing to main branches
- **Automated workflows** requiring rapid iteration cycles

**Security Considerations:**

**For Self-Hosted Runners:**

- Store AWS credentials and secrets in GitHub organization secrets
- Use IAM roles and short-lived credentials for runners where possible [4][8]
- Prefer private repositories for self-hosted runners; treat public repo jobs with extra caution [5]
- If using IP allow-lists, Enterprise Cloud ensures only traffic from runner IP ranges can reach organization [6]

### 2.6 Cloud vs. Hardware Infrastructure

#### Options for cloud services (e.g., AWS) that can provide fast dedicated slots

**AWS EC2 [7][8]:**

- **Best fit:** If AWS is already used or preferred
- **Linux/Windows:** Compute-optimized (C7i) and general-purpose (M7i) instances
- **macOS:** EC2 Mac instances (Intel mac1.metal, Apple Silicon mac2)
- **Advantages:**
  - Native integration with self-hosted runners and IAM
  - AWS CodeBuild can execute GitHub Actions workloads as managed backend with per-minute billing and strong autoscaling [8]
  - Elastic scaling, per-second billing
  - Savings Plans or Reserved Instances reduce costs for steady usage [7]

**Azure Virtual Machines and Azure Pipelines [9][10]:**

- Runners on Azure VMs: Dv5, Dsv5, Fsv5, Fsv2 series
- Azure Pipelines offers hosted agents and GitHub integration
- 1 free Microsoft-hosted parallel job + 1,800 minutes/month; more parallel jobs at fixed monthly prices [10]
- Adds separate CI control plane complexity if GitHub Actions remains primary

**Google Cloud Compute Engine and Cloud Build [11][12]:**

- Runners on N2 and C2 instance families
- Cloud Build integrates with GitHub via triggers
- 2,500 free build minutes/month; per-minute billing beyond that [12]
- Attractive for teams already on Google Cloud; otherwise adds vendor management overhead

**Comparison:**

- All major clouds support tens or hundreds of concurrent jobs
- Queue elimination depends more on provisioning enough instances and autoscaling than cloud choice
- AWS CodeBuild, Azure Pipelines, Cloud Build have straightforward per-minute models but add system complexity
- **For Beast2:** GitHub Actions + self-hosted runners provides most streamlined fast-feedback loop

#### Compare cloud vs. buying own hardware (supercomputer)

**Self-Owned Hardware (on-premise or colocation):**

**Sample CI Server Configuration:**

- **CPU:** 2 × AMD EPYC or Intel Xeon (64 physical cores total)
- **Memory:** 256 GiB RAM
- **Storage:** 2 × 3.84 TB NVMe SSDs for builds and caches
- **Network:** 10 GbE links

**Capabilities:**

- Running 60-80 parallel CI jobs (roughly 1 per core) for 2-3 minute builds
- 50-job Beast2 matrix completes in 3-5 minutes with caching (comparable to mid/high cloud tiers)

**Costs:**

- **Hardware:** $8,000-12,000 (high-end dual EPYC server)
- **Colocation:** $75-100/month (1U/2U server, 1 Gbps uplink) [13]
- **Power/cooling:** $50-70/month (400W average draw)
- **Monthly effective cost (3-year amortization):** $250-550/month

**When It Makes Sense:**

- CI workloads are heavy and very stable over time
- Appetite to manage hardware lifecycle, redundancy, repairs
- Additional uses for hardware beyond CI
- **For Beast2:** Cloud is better for elasticity and simplicity, especially for AI-driven bursty workloads

#### Cost comparison (prefers cloud, but depends on price)

**TCO Comparison (1, 3, 5 years):**

**Example Comparison:**

- **Cloud mid-tier fleet:** ~$450/month average
- **Owned server:** $10,000 upfront + $200/month operating costs

| Option         | 1 Year Total | 3 Year Total | 5 Year Total |
| -------------- | ------------ | ------------ | ------------ |
| Cloud mid-tier | ~$5,400      | ~$16,200     | ~$27,000     |
| Owned server   | ~$12,400     | ~$17,200     | ~$22,000     |

**Implications:**

- Over 3 years: Costs are broadly similar
- Over 5 years: Hardware can be cheaper if intensively used
- **Cloud wins on elasticity and simplicity** - better for AI-driven and bursty workloads
- **Hardware wins only at sustained very high usage** (tens of thousands of vCPU-hours/month) but loses elasticity

**Cost per CI Cycle Analysis:**

**Cloud Mid-Tier (Recommended):**

- Infrastructure: ~$3/hour capacity
- 50-job run at 4 minutes: **~$0.20 per run**
- 1,000 runs/month: ~$200 infrastructure + GitHub Team = **~$250/month total**

**GitHub-Hosted Only:**

- 50 jobs × 2.5 minutes = 125 minutes
- Linux (35 jobs): 35 × 2.5 × $0.006 = $0.53
- Windows (10 jobs): 10 × 2.5 × $0.010 = $0.25
- macOS (5 jobs): 5 × 2.5 × $0.062 = $0.78
- **Total: ~$1.50 per run** (plus queue wait times)

**Self-Owned Hardware:**

- At 1,000 runs/month: ~$0.40-0.60 per run (amortized)
- Lower at higher usage, but lacks elasticity

**Conclusion:** Self-hosted cloud runners provide **7-8x cost reduction per run** while eliminating queue times. **For Beast2:** Cloud-backed self-hosted runners provide better balance of cost, performance, and operational burden.

---

## Sources

[1] GitHub Pricing: https://github.com/pricing

[2] GitHub Docs – About billing for GitHub Actions: https://docs.github.com/en/billing/managing-billing-for-github-actions/about-billing-for-github-actions

[3] GitHub Resources – 2026 pricing changes for GitHub Actions: https://resources.github.com/actions/2026-pricing-changes-for-github-actions/

[4] GitHub Docs – About self-hosted runners: https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners

[5] GitHub Docs – About GitHub Enterprise Cloud: https://docs.github.com/en/enterprise-cloud@latest/admin/overview/about-github-enterprise-cloud

[6] GitHub Docs – Managing allowed IP addresses for your organization: https://docs.github.com/en/enterprise-cloud@latest/organizations/keeping-your-organization-secure/managing-allowed-ip-addresses-for-your-organization

[7] Amazon Web Services – Amazon EC2 pricing: https://aws.amazon.com/ec2/pricing/

[8] Amazon Web Services – AWS CodeBuild: https://aws.amazon.com/codebuild/

[9] Microsoft Azure – Virtual Machines pricing: https://azure.microsoft.com/en-us/pricing/details/virtual-machines/

[10] Microsoft Azure – Azure DevOps Services pricing (includes Azure Pipelines): https://azure.microsoft.com/en-us/pricing/details/devops/azure-devops-services/

[11] Google Cloud – Compute Engine pricing: https://cloud.google.com/compute/pricing

[12] Google Cloud – Cloud Build: https://cloud.google.com/build

[13] Colocation America – 1U colocation: https://www.colocationamerica.com/colocation/1u-colocation

[14] GitHub Actions – cache action: https://github.com/actions/cache

[15] GitHub Marketplace – sccache action: https://github.com/marketplace/actions/sccache-action

[16] GitHub – ccache-action: https://github.com/hendrikmuhs/ccache-action

[17] Amazon EC2 Mac instances: https://aws.amazon.com/ec2/instance-types/mac/

[18] MacStadium – Pricing for Mac mini and Mac Studio: https://macstadium.com/pricing

[19] MacMiniVault dedicated Mac mini: https://www.macminivault.com/dedicated-mac-mini/

[20] HostMyApple Mac mini hosting: https://www.hostmyapple.com/mac-mini-hosting
