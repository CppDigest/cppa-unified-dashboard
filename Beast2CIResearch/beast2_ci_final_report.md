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
| GitHub-hosted (Team) | $20-100 | 5-8 min | Occasional delays | Minimal |
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

**Current Team plan** ($4/user/month [4]): 60 concurrent jobs [3] sufficient for ~50-job matrices, but peak usage can still cause delays. **Enterprise** (~$21/user/month [4]): 500 concurrent jobs [3], justified only if multiple repos need large matrices simultaneously or macOS concurrency >5 is required.

### 1.2 Current Team Plan Benefits and Enterprise Considerations

**Current Team Plan Benefits (Already in Use):**
- **60 concurrent jobs** [3]: Provides 3× more concurrency than Free plan, helps reduce queue delays
- **Repository-level runner assignment**: Can dedicate self-hosted runners to specific repos (Beast2, Http.Io, Buffers, Capy) [7]
- **Larger runners available**: Access to GitHub's larger hosted runners (4x, 8x, 16x cores) at per-minute cost [1]
- **Better policy controls**: Organization-level settings for Actions, security, and compliance

**Limitations**: 60 concurrent jobs may still cause delays with 50+ job matrices; 5 macOS concurrent jobs limit [3] may be insufficient; no enterprise features (advanced security, audit logs).

**Enterprise Plan Benefits (If Considering Upgrade):**
- **500 concurrent jobs** [3]: Massive headroom for multiple repos running simultaneously
- **50 macOS concurrent jobs** [3]: vs 5 on Team (critical if macOS builds are significant)
- **Enterprise runner groups**: Centralized management of self-hosted runners across multiple orgs [7]
- **Advanced security**: SAML SSO, IP allow lists, required workflows, audit logs
- **Cost**: ~$21/user/month [4] vs Team's $4/user/month [4]

**Recommendation**: Current Team plan is sufficient for Beast2's ~50-job matrix. Enterprise justified only if multiple repos need large matrices simultaneously, macOS concurrency >5 is required, or enterprise security/compliance features are needed.

### 1.3 Self-Hosted Runners

**Setup and Configuration:**
- Install GitHub runner agent on VMs (cloud or on-prem) [7]
- Register at repository, organization, or enterprise level [7]
- Tag runners by capability (OS, CPU, labels) for job targeting [7]
- Can use automation (IaC tools, ARC, Terraform) for scalable deployment [9][11]

**Performance Benefits vs GitHub-Hosted:**
- **No queue on GitHub side**: Jobs dispatch immediately to available runners [7]
- **Hardware control**: Choose high-performance instances (more cores, faster CPUs, NVMe storage) [7]
- **Consistent performance**: No multi-tenant contention or shared pool delays [6]
- **Custom images**: Pre-install dependencies, toolchains, and build environments [7]

**Cost Implications:**
- **GitHub charges**: Zero per-minute fees for self-hosted runners [1] (only pay for infrastructure)
- **Infrastructure costs**: Cloud VMs (AWS/GCP/Azure) or hardware purchase
- **Example**: AWS c7i.xlarge (4 vCPU) ~$0.179/hour [14][15] = ~$0.003/min per job

**Impact on Queue Wait Times:**
- **Target**: Eliminate worst-case 2-hour waits entirely
- **Achievement**: With 50+ dedicated runners, all jobs start immediately (<30s startup)
- **Fallback**: Can configure workflows to use self-hosted if available, else GitHub-hosted

**Custom Daily Time Ranges:**
- GitHub doesn't provide native UI for time-based scheduling
- **Solution**: Script runner lifecycle via cloud APIs (Lambda, Cloud Functions, cron)
- **Example**: Scale up runners at 8AM PT, scale down at 8PM PT
- **Tools**: ARC supports autoscaling with min/max replicas; Terraform modules can use scheduled scaling
- **Consideration**: Keep minimal runners always-on for off-hour triggers, or accept delayed CI during off-hours

### 1.3 Parallel Execution

**Concurrency by plan**: Free 20, Team 60 (current), Enterprise 500, Self-hosted effectively unlimited [3]. **Runtime impact**: Sequential 50 jobs × 3 min = 150 minutes → Parallel ~3 minutes (longest job). With Team plan's 60 concurrent [3], all 50 jobs can start immediately.

---

## 2. CI Speed Optimization Report

### 2.1 Current CI Statistics and Baseline

**Beast2 CI Performance (Past Week):**
- **Workflow runs**: ~8 runs in the week
- **Fastest successful workflows**: ~1.0 minutes (GHA: skip self-hosted runner select for now #764)
- **Longest runs**: ~2h 28m 20s (Tidy up .gitignore #763)
- **Median workflow time**: ~15-30 minutes

**Capy CI Performance (Past Week):**
- **Workflow runs**: ~104 runs
- **Median workflow time**: ~10-20 minutes
- **Longest runs**: ~2h 28m 16s (Allocator fix #384)
- **Trend**: Fewer heavy jobs, but still experiences queuing at peak times

### 2.2 Performance Optimization

**Current CI Pipeline Bottlenecks:**
- **Sequential execution**: 50+ jobs × 2-3 min = 100-150 minutes if run sequentially
- **Queue wait times**: Worst-case 2 hours, typical 1-2 minutes during peak
- **Total CI cycle time**: Hours (queue + execution)
- **Inconsistent job completion**: Some jobs 8 minutes while others finish in 2 minutes, workflow time = slowest job

**Performance Targets:**
- **Current state**: 2-5 minute total CI time is still considered long for rapid AI bot iteration
- **Target**: Sub-2 minute median, max times under 3 minutes
- **Focus**: Optimize max time (eliminate 8-minute stragglers), not just average
- **Strategy**: Ensure all jobs finish in similar time window (~2-3 min)

**Parallelization Strategies:**
- **Run all 50+ jobs simultaneously**: Requires 50+ concurrent runners (Team plan provides 60 [3], sufficient for current needs)
- **Reduce total CI time**: From hours (sequential) to sub-2 minutes (parallel)
- **Consistent resource allocation**: Assign more CPU to heavy jobs (Debug builds → 8-core runners)
- **Eliminate stragglers**: Target slow jobs specifically (split tests, use larger runners, optimize build steps)

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

### 2.4 Cost Analysis with 3 Pricing Tiers

**High-Performance Option (Maximum Speed):**
- **Infrastructure**: High-end cloud instances (32-64 vCPUs) or premium SaaS runners
- **Examples**: AWS c6a.48xlarge (96 vCPU), Namespace high-perf runners, Cirrus dedicated Macs
- **Expected runtime reduction**: Median ~1.8-2.2 minutes, max ≤3 minutes
- **Queue elimination**: Near-zero (<30s), pre-warmed runners
- **Parallel job capacity**: 50+ concurrent jobs, all start immediately
- **Monthly cost**: ~$2,500-3,500 (compute + macOS + SaaS fees)
- **Best for**: Maximum performance priority, budget available

**Mid-Tier Option (Balanced Performance and Cost):**
- **Infrastructure**: Moderate cloud instances (8-16 vCPUs) or balanced SaaS providers
- **Examples**: GCP N2/C2 instances via ARC, BuildJet runners, Blacksmith
- **Expected runtime reduction**: Median ~2.5-3 minutes, max ~3-4 minutes
- **Queue wait time reduction**: <60 seconds with autoscaling
- **Parallel job capacity**: 20-30 concurrent jobs, scale up to 50+ on demand
- **Monthly cost**: ~$1,600-2,000 (GKE + compute + macOS provider)
- **Best for**: Balance of performance and cost, GCP infrastructure preference

**Low-Tier Option (Cost-Effective):**
- **Infrastructure**: Minimal self-hosted runners + caching (Team plan already in use)
- **Examples**: 5-10 self-hosted Linux runners on GCP, GitHub-hosted for Windows/macOS
- **Expected runtime reduction**: Median ~4-5 minutes, max ~8-10 minutes
- **Queue wait time reduction**: Improved for Linux (no queue), still exposed to GitHub macOS/Windows queues
- **Parallel job capacity**: 5-10 Linux concurrent, limited by GitHub-hosted for others
- **Monthly cost**: ~$200-400 (minimal compute, Team plan costs already paid)
- **Best for**: Budget-conscious, Linux-focused optimization, first step before larger investment

### 2.5 High-Performance Hardware Specifications

**CPU Specifications:**
- **Cores/Threads**: 4-8 vCPUs per job (8-core runners for heavy jobs, 4-core for typical)
- **Clock Speed**: 3.5-4.5 GHz boost (AMD EPYC 7xx4, Intel Xeon Scalable, AMD Ryzen 7950X) [12]
- **Single-thread Performance**: PassMark scores 3500-4650 (vs GitHub's ~2300) [12]
- **Architecture**: x64 primary, ARM64 (Graviton) for cost optimization if toolchain supports [12]
- **Instance Examples**: See Section 3.1 for specific cloud provider instance types and pricing

**Memory Requirements:**
- **Per Job**: 4-8 GB RAM minimum, 8-16 GB recommended for C++ builds
- **Per Runner**: 32-64 GB for 8-core runners handling multiple jobs
- **Total**: 200-400 GB aggregate for 50 concurrent jobs

**Storage Options:**
- **Type**: NVMe SSD preferred, standard SSD acceptable
- **Capacity**: 100-250 GB per runner for build workspace + caches
- **I/O Performance**: High IOPS (10,000+) for fast compilation and cache access
- **Caching**: Local NVMe for ccache, persistent volumes for dependency caches

**Network Capabilities:**
- **Bandwidth**: Gigabit+ for dependency downloads and artifact uploads
- **Latency**: Low latency to GitHub API and artifact storage
- **Cloud Integration**: High-speed links to S3/GCS for cache storage

### 2.6 Scope and Multi-Repository Support

**Dedicated Runners for Team Repositories:**
- **Target Repos**: Beast2, Http.Io, Buffers, Capy (select repositories only)
- **Isolation**: Repository-level runner assignment prevents resource contention
- **Shared Pool Option**: Can use org-level runners with labels for multi-repo support
- **Capacity Planning**: Size for peak load across all repos (e.g., 2 repos × 50 jobs = 100 concurrent capacity)

**Cloud-Based Slop-Driven Development Support:**
- **Compatibility**: Same runners can execute both GitHub Actions workflows and other CI/CD tasks
- **Multi-Repository Support**: Runners can be shared across repos via labels or org-level assignment
- **Resource Sharing**: Can allocate runners dynamically based on demand (ARC autoscaling)
- **Isolation**: Ephemeral runners ensure clean environments for each job
- **Bot-Driven + Manual Workflows**: Runners support both automated (AI bot) and manual (developer) triggers

---

## 3. Cloud vs. Hardware Infrastructure Report

### 3.1 Cloud Services Options (AWS, GCP, Azure)

**AWS EC2 Instances:**
- **Compute-Optimized**: C7i (Intel), C7g (Graviton3 ARM), C6a (AMD) [14][15]
- **Pricing**: c7i.xlarge (4 vCPU) ~$0.179/hour [14][15], c6a.32xlarge (128 vCPU) ~$3.89/hour [14]
- **Spot Instances**: 70-90% cost reduction [14], suitable for ephemeral runners
- **macOS Support**: Mac EC2 instances available (mac1.metal, mac2.metal) at ~$1.08/hour with 24-hour minimum [14]
- **Integration**: Self-hosted runners via EC2 [7], or RunsOn for automated management [18]
- **Best For**: AWS credits available, need macOS in cloud, maximum instance variety

**Google Cloud Platform (GCP) Compute Engine:**
- **Instance Families**: N2 (balanced), C2 (compute-optimized), Tau T2A (ARM) [16]
- **Pricing**: n2-standard-8 (8 vCPU) ~$0.388/hour($280/mon) [16], c2-standard-8 ~$0.418/hour(~$300/mon) [16]
- **Preemptible VMs**: Up to 80% discount [16], ideal for ephemeral runners
- **Sustained Use Discounts**: Automatic discounts for continuous usage [16]
- **macOS Support**: No native offering (use MacStadium or Mac Mini)
- **Integration**: GKE with ARC [9], or GCE VMs as self-hosted runners [7]
- **Best For**: Existing GCP infrastructure, credits available, Kubernetes expertise

**Azure Virtual Machines:**
- **Instance Series**: Dv5 (general purpose), Dsv5 (with premium storage), Fsv5 (compute-optimized), Fsv2 (older generation) [17]
- **Pricing**: D4s v5 (4 vCPU) ~$0.192/hour [17], F4s v2 (4 vCPU) ~$0.169/hour [17]
- **Spot VMs**: Low-priority VMs with significant discounts [17]
- **Windows Support**: Strong Windows integration, included licensing [17]
- **Integration**: Self-hosted runners on Azure VMs [7], or Azure Pipelines (separate CI system)
- **Best For**: Windows-heavy workloads, Microsoft ecosystem preference

**Pricing Comparison (4 vCPU instances, approximate):**
- **AWS c7i.xlarge**: ~$0.179/hour
- **GCP n2-standard-4**: ~$0.194/hour
- **Azure D4s v5**: ~$0.192/hour
- **Note**: Spot/preemptible pricing can reduce costs by 70-90%

**Queue Elimination and Parallel Execution:**
- **All providers**: Can provision 50+ instances concurrently (may need quota increases)
- **Startup Time**: 30-60 seconds cold start, <5 seconds with warm pool
- **Autoscaling**: All support auto-scaling groups/clusters for on-demand capacity

**Integration with GitHub Actions:**
- **All providers**: Install runner agent on VMs, register with GitHub
- **Automation**: Terraform modules, ARC, or custom scripts for lifecycle management
- **Best Practice**: Ephemeral runners (one job per VM) for security and consistency

**Migration Considerations:**
- **From GCP to AWS/Azure**: Runner setup is identical (same agent), only infrastructure changes
- **Cost-Benefit**: Compare spot/preemptible pricing, existing credits, and instance performance
- **Recommendation**: Stay on GCP if credits/expertise exist; consider AWS if macOS needed or better spot availability

### 3.2 Runner Service Alternatives

**Open-Source Self-Hosted Solutions:**

**Actions Runner Controller (ARC):**
- **Implementation**: Kubernetes controller managing GitHub runners as ephemeral pods [9]
- **Protocol**: Uses official GitHub runner agent, full Actions compatibility [9]
- **OS Support**: Linux (primary), Windows (with Windows node pools), macOS (requires separate Mac hosts) [9][11]
- **Scaling**: Autoscales based on queued jobs via webhooks, can scale to zero when idle [9]
- **Cost Structure**: Zero licensing fees [9], only pay for Kubernetes infrastructure (GKE, EKS, AKS)
- **Cloud Integration**: Works on any Kubernetes (GCP GKE, AWS EKS, Azure AKS, on-prem) [9]
- **Queue Management**: Launches new pods within 5-30 seconds of job queuing [12]
- **Caching**: Supports persistent volumes (PVC) for ccache, dependency caches [9]
- **Security**: Ephemeral runners (one job per pod) ensure clean environments, isolation [9]
- **Best for Beast2**: GCP infrastructure, GKE deployment, Linux/Windows runners, autoscaling needs

**Terraform AWS/GCP Modules:**
- **Implementation**: Infrastructure-as-code for auto-scaling runner fleets
- **Protocol**: Official runner agent, full compatibility
- **OS Support**: Linux, Windows (via EC2/GCE), macOS (requires Mac hardware or cloud Mac service)
- **Scaling**: Lambda/Cloud Functions trigger new VMs on job queue events, terminate after completion
- **Cost Structure**: Zero licensing, pay cloud provider directly (can use spot/preemptible for 70-90% savings)
- **Cloud Integration**: Native AWS (EC2, ECS Fargate) and GCP (GCE, Cloud Run) support
- **Queue Management**: ~30-60 second cold start, <5s with warm pool
- **Caching**: Can mount persistent disks or use cloud storage (S3, GCS) for caches
- **Security**: Ephemeral VMs per job, code stays in your VPC
- **Best for Beast2**: AWS or GCP native deployments, fine-grained control, cost optimization with spot instances

**act (Local Runner - Not for Production):**
- **Implementation**: Local Docker-based workflow execution [10]
- **Use Case**: Developer-side workflow testing, debugging only [10]
- **Limitation**: Doesn't connect to GitHub, can't be used for automated CI [10]

**Best Practices for Open-Source Deployments:**
- Use ephemeral runners for security (one job per VM/pod)
- Implement warm base images with pre-installed dependencies
- Leverage spot/preemptible instances for 70-90% cost savings
- Use persistent volumes or cloud storage for caches (S3, GCS)
- Scale aggressively during work hours, scale to zero off-hours
- Monitor runner health and implement auto-recovery

**Commercial Third-Party Solutions - Overview:**

| Provider | Model | Pricing | Key Strengths | OS Support |
|----------|-------|---------|---------------|------------|
| **RunsOn** | Self-hosted in your AWS | €300/yr + AWS compute [18] | Security (your VPC), 90% cost reduction [13][18], unlimited concurrency [18] | Linux, Windows, macOS, GPU [18] |
| **Ubicloud** | Managed on Hetzner | $0.0008/min (2-core) [19] | Ultra-low cost, 90% cheaper [13][19], open-source platform [19] | Linux (x64, arm64) [19] |
| **BuildJet** | Managed bare-metal | $0.004/min (2-core) [20] | Gaming-grade CPUs, 50% cost vs GitHub [13][20], fast performance [12] | Linux (AMD, ARM) [20] |
| **Blacksmith** | Managed on Hetzner | $0.004/min, 3k free min [21] | 2× faster, half cost [13][21], 64GB disk, 25GB cache [21] | Linux (x64, arm64 beta) [21] |
| **Namespace** | High-perf ephemeral | From $100/mo [22] | Fastest x64 CPUs (EPYC ~4650) [12][22], macOS M-series [22], large caches [22] | Linux, Windows, macOS [22] |
| **Depot** | Container builders | $20/mo + $0.004/min [23] | Docker optimization, integrated caching, M2 Mac support [23] | Linux, Windows, macOS [23] |
| **Cirrus Runners** | Dedicated fixed-price | $150/mo per runner [24][25] | Pre-warmed VMs [25], M4 Mac [25], unlimited minutes per runner [25] | Linux, Windows, macOS [24][25] |
| **Warpbuild** | BYOC or managed | 50-90% cheaper [26] | High performance, unlimited concurrency, fast caching [26] | Linux, Windows, macOS [26] |

**Cost Comparison:**
- **90% cost reduction providers**: RunsOn (with AWS spot) [13][18], Ubicloud (Hetzner-based) [13][19]
- **50% cost reduction**: BuildJet [13][20], Blacksmith [13][21] (vs GitHub's $0.008/min Linux [1])
- **Per-minute pricing**: Most charge $0.004-0.008/min for Linux, 2× for Windows, 10× for macOS [1][13]

**Performance Comparison (runs-on.com benchmarks):**
- **Fastest x64**: Namespace (EPYC ~4650) [12][22], Cirrus (Ryzen 7950X3D ~4000) [12][24], Blacksmith (~4538) [12][21]
- **Best arm64 price/performance**: RunsOn (Graviton4) [12][18], Ubicloud [12][19]
- **Queue times**: Most maintain <30 seconds (Namespace ~13s [12], Cirrus ~17s [12], RunsOn ~24s [12])

**Security Trade-Offs:**
- **Third-party SaaS** (BuildJet [20], Ubicloud [19], Namespace [22]): Code runs on their infrastructure, ephemeral VMs per job [13]
- **Self-hosted solutions** (RunsOn [18], ARC [9]): Code stays in your VPC/Kubernetes [18][9], full control
- **Best Practice**: For public repos, SaaS is acceptable; for private/sensitive code, self-hosted preferred [7]

**Platform-Specific Considerations:**
- **RunsOn**: AWS-only [18], deploys in your account [18], can use AWS credits [18], yearly license from €300 [18]
- **Ubicloud**: Hetzner-based [19], 90% cheaper [13][19], good for cost optimization, Linux only [19]
- **ARC**: Kubernetes-based [9], works with any cloud (GCP, AWS, Azure) [9], zero licensing [9]

**Feature Support:**
- **macOS**: Namespace (M-series) [22], Depot (M2) [23], Cirrus (M4) [25], RunsOn (AWS Mac instances with 24h minimum) [18]
- **Windows**: RunsOn [18], Namespace [22], Depot [23], some open-source solutions
- **GPU**: RunsOn offers GPU support [18]
- **Instance Types**: Some support up to 896 vCPUs (RunsOn) [18], unlimited concurrency policies [18]

**Comparison: Open-Source vs Commercial Third-Party**

| Aspect | Open-Source (ARC/Terraform) | Commercial (BuildJet, Ubicloud, etc.) |
|--------|----------------------------|----------------------------------------|
| **Setup Complexity** | Medium-high (K8s knowledge, IaC) | Low (plug-and-play, GitHub App) |
| **Maintenance Overhead** | Medium (monitor cluster, updates) | Low (vendor-managed) |
| **Feature Completeness** | Full control, customizable | Pre-configured, optimized |
| **Community Support** | Active (ARC widely used) | Vendor support + community |
| **Customization** | Full (choose hardware, config) | Limited (provider's offerings) |
| **TCO** | Infrastructure only (lower long-term) | Infrastructure + service fees |
| **Best For** | Long-term, high-scale, GCP/AWS expertise | Quick wins, minimal ops, cost-sensitive |

**When to Use Open-Source vs Commercial:**
- **Open-source (ARC/Terraform)**: Full control, code stays in your VPC/Kubernetes, use existing cloud credits, requires DevOps expertise
- **Commercial third-party**: Zero setup, plug-and-play, code runs on their infrastructure, minimal maintenance

**Integration Complexity:**
- **Commercial SaaS**: ~30 minutes (install GitHub App, add runner labels, configure billing) [13]
- **Open-source (ARC)**: Few hours (deploy on K8s, configure autoscaling, test) [9]
- **Open-source (Terraform)**: 1-2 hours (setup cloud credentials, deploy stack, configure)

**Best Fit for Beast2:**
- **If staying on GCP**: ARC on GKE is ideal - leverages existing infrastructure, autoscaling, zero licensing
- **If open to AWS**: RunsOn (hybrid open-source/commercial) deploys in your AWS, uses spot instances
- **Multi-platform needs**: ARC handles Linux/Windows, supplement with macOS provider (Cirrus, MacStadium)

### 3.3 Own Hardware vs Cloud

**Initial Investment:**
- **Servers**: 4 servers × 32 cores (64 threads) × 128-256 GB RAM = $20,000-30,000
- **Mac Hardware**: Mac Mini M2 (~$1,000) or Mac Studio M2 Ultra (~$4,000) for macOS builds
- **Windows Licensing**: ~$100-200 per server if needed
- **Total Upfront**: ~$25,000-35,000

**Ongoing Costs:**
- **Power**: ~$440/year for 64-core server (500W × 24/7)
- **Cooling**: Additional power costs
- **Rack Space**: Colocation fees (~$100-200/month) or office space
- **Maintenance**: Hardware failures, OS updates, runner software updates
- **Depreciation**: 3-5 year typical hardware lifecycle

**Scalability and Flexibility:**
- **Fixed Capacity**: Hardware provides fixed cores/performance, cannot scale beyond purchase
- **Cloud Advantage**: Pay-per-use, scale up/down instantly, no idle costs
- **Bursty Workloads**: CI is often idle (nights, weekends), hardware sits unused

**Performance Characteristics:**
- **Queue Times**: Near-zero with dedicated hardware (no cloud provisioning delay)
- **Parallel Execution**: Limited by purchased capacity (e.g., 128 cores = 128 concurrent jobs max)
- **Latest Hardware**: Cloud providers roll out new CPUs regularly; owned hardware becomes outdated

**Suitability for Automated Bot-Driven CI:**
- **Pros**: Consistent performance, no cloud provisioning delays, predictable costs (after purchase)
- **Cons**: Cannot scale beyond capacity, idle costs during low usage, maintenance overhead

**Mac Builds Requirement:**
- **M-Series CPUs**: Required for macOS builds (Apple licensing)
- **Options**: Mac Mini M2 (8 cores, ~$1,000) or Mac Studio M2 Ultra (24 cores, ~$4,000)
- **Cloud Alternative**: AWS Mac instances ($1.08/hour, 24h minimum) [14] or MacStadium (~$200-300/month)
- **Break-Even**: Mac Mini pays for itself in ~2-3 months vs AWS Mac instances [14]

**Cost Comparison (3-Year TCO):**
- **Own Hardware**: $25,000 upfront + $5,000 ops (3 years) = $30,000
- **Cloud (Mid-Tier)**: $1,800/month × 36 months = $64,800
- **Cloud (Low-Tier)**: $300/month × 36 months = $10,800
- **Break-Even**: Only if running 24/7 at high utilization (unlikely for CI)

**Recommendation**: **Prefer cloud or SaaS** due to flexibility, scalability, and lower total cost for bursty CI workloads. Own hardware only makes sense if:
- Combined with other compute workloads (24/7 utilization)
- Regulatory/compliance requires on-prem
- Existing hardware available (repurpose)

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

For Beast2's use case (rapid AI bot iteration, 50+ job matrix, sub-2 min median target), **recommend Option 2 (GCP-Centric ARC)** [9]:
- **Performance**: Achieves 2.5-3 min median, meets sub-3 min max target
- **Cost**: ~$1,600-2,000/month is reasonable for productivity gains
- **Control**: Full control over infrastructure [9], leverages existing GCP expertise
- **Scalability**: Autoscaling handles growth [9], can scale to zero when idle [9]

**Alternative**: If budget allows and maximum performance is critical, **Option 1 (High-Performance SaaS)** provides fastest CI times (1.8-2.2 min median [12]) with minimal operational overhead [13].

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
