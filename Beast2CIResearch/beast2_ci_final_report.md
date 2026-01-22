# Beast2 CI Availability Improvement Options

**Generated:** 2026-01-21  

---

## Executive Summary

Beast2's GitHub Actions CI pipeline can be dramatically accelerated through dedicated runners and optimization techniques. Current setup: ~50 matrix jobs in 15-30 minutes average, worst-case 2-hour queue waits. **Organization already uses GitHub Team plan ($4/user/month) with 60 concurrent jobs** [3][4], which helps but queue delays still occur during peak usage.

**Key findings:**
- **Concurrency bottleneck**: Team plan's 60 concurrent jobs [3] may still cause delays with 50+ job matrices
- **Self-hosted runners eliminate queues**: Dedicated runners achieve sub-2 minute median CI times [7]
- **Open-source solutions (ARC, Terraform) offer cost-effective scaling**: Actions Runner Controller on GKE [9] provides autoscaling with minimal licensing costs
- **Third-party runners provide 50-90% cost savings**: Ubicloud ($0.0008/min) [19], BuildJet ($0.004/min) [20], RunsOn (€300/yr + AWS) [18] offer faster CPUs at lower costs [12][13]
- **Caching is the lowest-hanging fruit**: GitHub Actions cache (>10GB pay-as-you-go) [5] for dependencies reduces job times by 20-50% [8]. Compiler caches (ccache/sccache) provide 50-90% speedup for incremental builds but require more setup [8]

**Cost-benefit analysis:**
- **Low-tier (caching + optimization)**: ~$0-400/month additional, 4-5 min median
- **Mid-tier (ARC on GCP)**: ~$1,600-2,000/month, 2.5-3 min median
- **High-tier (SaaS runners)**: ~$2,500-3,500/month, 1.8-2.2 min median

**Runtime reduction**: Current 5-8 min median → With optimization 3-5 min → With self-hosted/third-party 1.8-2.5 min median, ≤3 min max

**Runner options comparison:**

| Option | Cost (monthly) | Median Time | Queue Behavior | Setup Complexity |
|--------|---------------|-------------|----------------|------------------|
| GitHub-hosted (Team) | $0 (non-profit) | 5-8 min | Occasional delays | Minimal |
| Self-hosted (ARC/GCP) | $1,600-2,000 | 2.5-3 min | <60s | Medium-high |
| Third-party (Ubicloud) | $50-200 | 2-3 min | <30s | Low |
| Third-party (RunsOn/AWS) | €300/yr + AWS | 2-3 min | <30s | Medium |
| High-perf SaaS (Namespace) | $2,500-3,500 | 1.8-2.2 min | <30s | Low |

---

## 1. GitHub Organization Plan Analysis

### 1.1 Plan Comparison

For public repositories, GitHub Actions minutes are unlimited and free [1][2], but **concurrency limits vary by plan** [3]:

| Plan | Minutes(per month)[2] | Total Concurrent jobs[3] | Maximum concurrent macOS jobs[3] | Concurrent Scalable[3] | Cache Storage[5] | Artifact Storage |
|------|------------------|------------------|------------------|------------------|----------------------------------------------|-------------|
| **Free (Org)** | 2,000 | 20 | 5 | False | 10 GB | 500 MB |
| **Team(Pro)** | 3,000 | 60  | 5 | 1000 | 10 GB (up to 10T) | 2 GB(1 GB) |
| **Enterprise Cloud** | 50,000 | 500 | 50 | 1000 | 10 GB (up to 10T) | 50 GB |

**Current Team plan** ($4/user/month [4]): 60 concurrent jobs [3] sufficient for ~50-job matrices, but peak usage can still cause delays.  
**Enterprise** (~$21/user/month [4]): 500 concurrent jobs [3], justified only if multiple repos need large matrices simultaneously or macOS concurrency >5 is required.

### 1.2 Current Team Plan Assessment

**Current Team Plan (Already in Use):**
- **60 concurrent jobs** [3]: Sufficient for ~50-job matrices, but peak usage can still cause delays
- **Repository-level runner assignment** [7]: Can dedicate self-hosted runners to specific repos
- **Limitations**: 5 macOS concurrent jobs [3] may be insufficient; no enterprise features

**Enterprise Plan (If Considering Upgrade):**
- **500 concurrent jobs** [3]: Massive headroom for multiple repos
- **50 macOS concurrent jobs** [3]: vs 5 on Team (critical if macOS builds are significant)
- **Cost**: ~$21/user/month [4] vs Team's $4/user/month [4]

**Recommendation**: Current Team plan is sufficient for Beast2's ~50-job matrix. Enterprise justified only if multiple repos need large matrices simultaneously or macOS concurrency >5 is required.

### 1.3 Self-Hosted Runners

**Benefits**: No queue on GitHub side [7], hardware control (faster CPUs, NVMe storage) [7], zero GitHub per-minute fees [1], repository-level assignment [7].  
**Cost**: Only infrastructure (e.g., AWS c7i.xlarge ~$0.179/hour [14][15]).  
**Impact**: With 50+ dedicated runners, all jobs start immediately (<30s startup), eliminating worst-case 2-hour waits.  
**Custom time ranges**: Script runner lifecycle via cloud APIs (ARC supports min/max replicas for autoscaling).

### 1.4 Parallel Execution

**Concurrency by plan**: Free 20, Team 60 (current), Enterprise 500, Self-hosted effectively unlimited [3].  
**Runtime impact**: Sequential 50 jobs × 3 min = 150 minutes → Parallel ~3 minutes (longest job). With Team plan's 60 concurrent [3], all 50 jobs can start immediately.

---

## 2. CI Speed Optimization Report

### 2.1 Current Baseline

**Beast2**: ~8 runs/week, median 15-30 min, longest ~2h 28m.  
**Capy**: ~104 runs/week, median 10-20 min, longest ~2h 28m. Both experience queuing at peak times.

### 2.2 Performance Optimization

**Bottlenecks**: Sequential execution (50+ jobs × 2-3 min = 100-150 min), queue waits (worst-case 2 hours), inconsistent job completion (some 8 min, others 2 min).  
**Targets**: Sub-2 minute median, max ≤3 minutes.  
**Strategy**: Run all 50+ jobs simultaneously (Team plan's 60 concurrent [3] is sufficient), optimize max time (eliminate 8-minute stragglers), ensure consistent resource allocation.

### 2.3 Caching Strategy

**Dependency Caching (Recommended First):**
- GitHub Actions cache [8]: 10 GB default, $0.07/GiB/month pay-as-you-go [5]
- Cache Boost, zlib, OpenSSL, Brotli (key by version + OS) - 20-50% speedup [8]
- Use OS + compiler + C++ standard + build type for cache keys [8]

**Compiler Caches (Optional - High Impact for Incremental Builds, Medium Effort):**
- **What they are**: Tools that cache compiled object files (`.o` files) so unchanged source files don't need recompilation
- **ccache** (Linux): Caches GCC/Clang compiled object files
- **sccache** (cross-platform): Similar to ccache, supports cloud storage backends (S3, GCS, Azure)
- **cl cache** (Windows): MSVC compiler's built-in cache
- **When beneficial**: 
  - **Incremental builds**: When only a few files change between CI runs (e.g., AI bot making small changes)
  - **Iterative development**: Subsequent bot iterations where most code is unchanged
  - **Can reduce compile time by 50-90%** for unchanged files
- **When NOT necessary**:
  - **Clean builds every run**: If CI always does `make clean` or removes build directories, compiler cache won't help
  - **Large code changes**: If most files change between runs, cache hit rate is low
  - **First-time setup complexity**: Requires configuring compiler wrapper and cache storage
- **Recommendation for Beast2**: 
  - **Start with dependency caching only** (Boost, zlib, OpenSSL, Brotli) - easier to implement, immediate benefit
  - **Add compiler cache later** if you notice many unchanged files between bot iterations and want to optimize further
  - **Best for**: AI bot workflows where small changes are made iteratively

**Expected Results**: Current hours → With parallel: sub-2 min → With dedicated runners: <30s startup → With caching: cold 5-10 min → warm 1-3 min → Combined: median 1.8-2.2 min, max ≤3 min.

### 2.4 Cost Analysis

**High-Performance**: High-end cloud instances or premium SaaS runners. Examples: AWS c6a.48xlarge, Namespace, Cirrus. Median ~1.8-2.2 min, max ≤3 min, near-zero queues. **Cost**: ~$2,500-3,500/month.

**Mid-Tier**: Moderate cloud instances via ARC or balanced SaaS. Examples: GCP N2/C2 via ARC, BuildJet. Median ~2.5-3 min, max ~3-4 min, <60s queues. **Cost**: ~$1,600-2,000/month.

**Low-Tier**: Minimal self-hosted runners + caching. Examples: 5-10 Linux runners on GCP, GitHub-hosted for Windows/macOS. Median ~4-5 min, max ~8-10 min. **Cost**: ~$200-400/month (Team plan already paid).

### 2.5 Hardware Specifications and Scope

**Hardware Specs**: 4-8 vCPUs per job (8-core for heavy jobs), 8-16 GB RAM per job, NVMe SSD (10,000+ IOPS), PassMark 3500-4650 (vs GitHub's ~2300) [12]. See Section 3.1 for cloud instance types.

**Scope**: Target repos: Beast2, Http.Io, Buffers, Capy. Repository-level assignment prevents contention. Runners support both GitHub Actions and other CI/CD tasks via labels/org-level assignment.

---

## 3. Cloud vs. Hardware Infrastructure Report

### 3.1 Cloud Services (AWS, GCP, Azure)

| Provider | Instance Types | Pricing (4 vCPU) | Key Features |
|----------|---------------|------------------|--------------|
| **AWS** | C7i, C7g, C6a [14][15] | ~$0.179/hour [14][15] | Spot 70-90% savings [14], macOS support ($1.08/hour, 24h min) [14] |
| **GCP** | N2, C2, T2A [16] | ~$0.194/hour [16] | Preemptible 80% discount [16], GKE + ARC [9] |
| **Azure** | Dv5, Fsv5 [17] | ~$0.192/hour [17] | Spot VMs, strong Windows support [17] |

**Integration**: All support self-hosted runners [7], autoscaling, 30-60s cold start. **Recommendation**: Stay on GCP if credits/expertise exist; consider AWS if macOS needed.

### 3.2 Runner Service Alternatives (Open-Source and Third-Party)

**Open-Source Solutions:**

**ARC (Actions Runner Controller)** [9]: Kubernetes-based, autoscaling, Linux/Windows, zero licensing, works on GKE/EKS/AKS, 5-30s queue time [12]. **Best for**: GCP infrastructure, GKE deployment.

**Terraform Modules** [11]: Infrastructure-as-code, spot/preemptible 70-90% savings, 30-60s cold start. **Best for**: AWS/GCP native, fine-grained control.

**Best Practices**: Ephemeral runners, spot/preemptible instances, persistent volumes for caches, scale to zero off-hours.

**Commercial Third-Party Solutions:**

| Provider | Pricing | Key Strengths | OS | Queue Time |
|----------|---------|---------------|----|-----------| 
| **RunsOn** | €300/yr + AWS [18] | Your VPC, 90% savings [13][18] | All + GPU [18] | ~24s [12] |
| **Ubicloud** | $0.0008/min [19] | 90% cheaper [13][19] | Linux [19] | <30s |
| **BuildJet** | $0.004/min [20] | 50% vs GitHub [13][20] | Linux [20] | <30s |
| **Namespace** | From $100/mo [22] | Fastest x64 (~4650) [12][22], M-series [22] | All [22] | ~13s [12] |
| **Cirrus** | $150/mo/runner [25] | M4 Mac [25], unlimited min [25] | All [25] | ~17s [12] |

**Comparison**: Open-source (ARC/Terraform) offers full control, lower long-term cost, requires DevOps expertise. Commercial offers plug-and-play, minimal maintenance, higher per-minute costs [13].

**Best Fit**: **GCP**: ARC on GKE [9]. **AWS**: RunsOn [18] (deploys in your account). **Multi-platform**: ARC + macOS provider (Cirrus [25], MacStadium).

### 3.3 Own Hardware vs Cloud

**Own Hardware**: ~$25,000-35,000 upfront (servers + Mac Mini M2 ~$1,000), ~$5,000 ops over 3 years = $30,000 TCO. 
- **Servers**: 4 servers × 32 cores (64 threads) × 128-256 GB RAM = $20,000-30,000
- **Mac Hardware**: Mac Mini M2 (~$1,000) or Mac Studio M2 Ultra (~$4,000) for macOS builds
- **Windows Licensing**: ~$100-200 per server if needed
- **Total Upfront**: ~$25,000-35,000**Limitations**: Fixed capacity, idle costs, maintenance overhead, hardware becomes outdated.

**Cloud (3-Year TCO)**: Mid-tier $64,800, Low-tier $10,800. **Advantages**: Pay-per-use, scale instantly, no idle costs, latest hardware.

**Recommendation**: **Prefer cloud/SaaS** for bursty CI workloads. Own hardware only if: 24/7 utilization, regulatory requirements, or existing hardware available.

---

## 4. Recommended Options Summary

### 4.1 Architecture Options

**Option 1: High-Performance SaaS or Self-Hosted Fleet**
- **Runners**: Linux/Windows: High-perf self-hosted or SaaS (Namespace [22], Cirrus [24], RunsOn [18]). macOS: Cirrus [25] or MacStadium.
- **Performance**: Median ~1.8-2.2 min, max ≤3 min [12], near-zero queues (<30s) [12]
- **Cost**: ~$2,500-3,500/month
- **Best For**: Maximum performance priority, budget available

**Option 2: GCP-Centric ARC (Recommended)**
- **Runners**: Linux: GKE with ARC [9] on N2/C2 nodes [16] (autoscaling 20-30 concurrent). Windows: Small pool of long-lived VMs [7]. macOS: 2-4 runners from Cirrus [25] or MacStadium.
- **Performance**: Median ~2.5-3 min, max ~3-4 min, <60s queues [9]
- **Cost**: ~$1,600-2,000/month
- **Best For**: GCP infrastructure preference, balance of performance and cost, Kubernetes expertise

**Option 3: Hybrid Starter**
- **Runners**: Linux: 5-10 self-hosted on GCP/AWS [7]. Windows/macOS: GitHub-hosted (free for public repos [1][2]).
- **Performance**: Median ~4-5 min, max ~8-10 min
- **Cost**: ~$200-400/month (Team plan already paid)
- **Best For**: Budget-conscious, Linux-focused optimization, first step

### 4.2 Cross-Cutting Optimizations

1. **Caching**: Dependency caching (Boost, zlib, OpenSSL, Brotli) - 20-50% speedup [8]. Optional compiler caches (ccache/sccache) for incremental builds - 50-90% speedup [8].
2. **Matrix Restructuring**: Fast-path for high-frequency CI, full matrix only on merges/nightly.
3. **Standardization**: Consistent build scripts, reusable cache keys, predictable durations.

### 4.3 Implementation Roadmap

**Phase 1 (Immediate - Low Cost):**
- Implement GitHub Actions dependency caching [8] (Boost, zlib, OpenSSL, Brotli)
- Restructure matrices (fast-path + full matrix)
- Optimize workflow configuration to maximize Team plan's 60 concurrent jobs [3]
- **Optional**: Add compiler cache (ccache/sccache) if doing incremental builds
- **Expected**: 4-5 min median, reduce worst-case 2-hour queues [3]

**Phase 2 (Short-Term - Medium Cost):**
- Deploy 5-10 self-hosted Linux runners on GCP [7]
- Configure repository-level assignment [7] for Beast2, Http.Io, Buffers, Capy
- Implement time-based scaling (8AM-8PM PT coverage)
- **Expected**: 3-4 min median for Linux jobs

**Phase 3 (Long-Term - Higher Cost):**
- Deploy ARC [9] on GKE for autoscaling Linux/Windows runners
- Integrate macOS provider (Cirrus [25], MacStadium) for dedicated Mac capacity
- Optimize hardware specs (8-core runners for heavy jobs)
- **Expected**: 2-3 min median, ≤3 min max, near-zero queues [9][12]

### 4.4 Final Recommendation

**For day-to-day CI workflow**: **Option 3 (Hybrid Starter)** - ~$200-400/month, 4-5 min median, sufficient for regular development workflows.

**For rapid AI bot iteration**: **Option 2 (GCP-Centric ARC) part-time** - ~$1,600-2,000/month, 2.5-3 min median, can be scaled up during bot iteration periods and scaled down otherwise. Full control over infrastructure [9], leverages existing GCP expertise, autoscaling handles growth [9].

---

## Sources

[1] GitHub Docs – About billing for GitHub Actions: https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions

[2] GitHub Docs – Free use of GitHub Actions: https://docs.github.com/en/enterprise-cloud@latest/enterprise-onboarding/github-actions-for-your-enterprise/about-billing-for-github-actions

[3] GitHub Docs – Actions usage limits: https://docs.github.com/en/actions/reference/limits

[4] GitHub Pricing: https://github.com/pricing

[5] GitHub Changelog – Actions cache size >10 GB: https://github.blog/changelog/2025-11-20-github-actions-cache-size-can-now-exceed-10-gb-per-repository/

[6] GitHub Docs – About GitHub-hosted runners: https://docs.github.com/en/actions/using-github-hosted-runners/about-github-hosted-runners

[7] GitHub Docs – About self-hosted runners: https://docs.github.com/en/actions/hosting-your-own-runners/about-self-hosted-runners

[8] GitHub Docs – Caching dependencies: https://docs.github.com/en/actions/using-workflows/caching-dependencies-to-speed-up-workflows

[9] Actions Runner Controller (ARC): https://github.com/actions/actions-runner-controller

[10] act GitHub repository: https://github.com/nektos/act

[11] GitHub Awesome Runners: https://github.com/jonico/awesome-runners

[12] Runs-on.com Benchmark: https://runs-on.com/benchmarks/github-actions-cpu-performance/

[13] BetterStack – "13 Best GitHub Actions Runner Tools": https://betterstack.com/community/comparisons/github-actions-runner/

[14] AWS EC2 On-Demand Pricing: https://aws.amazon.com/ec2/pricing/on-demand/

[15] AWS EC2 C7i instances: https://aws.amazon.com/ec2/instance-types/c7i/

[16] Google Cloud Compute Engine pricing: https://cloud.google.com/compute/all-pricing

[17] Azure Virtual Machines pricing: https://azure.microsoft.com/pricing/details/virtual-machines/

[18] RunsOn website: https://runs-on.com

[19] Ubicloud documentation: https://ubicloud.com/docs

[20] BuildJet website: https://buildjet.com

[21] Blacksmith website: https://blacksmith.sh

[22] Namespace website: https://namespace.so

[23] Depot website: https://depot.dev

[24] Cirrus CI documentation: https://cirrus-ci.org

[25] Cirrus Runners website: https://cirrus-runners.app

[26] Warpbuild website: https://warpbuild.com

[27] Runs-on.com – Alternatives: https://runs-on.com/alternatives-to/github-actions-runners/
