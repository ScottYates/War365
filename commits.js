// War365 release log. Each entry is one fake git commit that documents a real-world
// conflict event, told in the voice of an enterprise SaaS engineering team.
// Dates are real; messages are not.

window.WAR365_COMMITS = [
  {
    hash: "f3a1c0d",
    date: "2022-02-24",
    author: "vladimir.p",
    authorEmail: "vladimir.p@kremlin.example",
    tag: "v1.0.0",
    subject: "feat(conflict): GA release of Operation Z, EU-East region",
    body: [
      "Initial GA of the EU-East theatre. Mandatory install —",
      "rollback path intentionally disabled.",
      "",
      "Highlights:",
      "- 3-front land offensive (north, east, south)",
      "- Black Sea fleet engaged",
      "  Discontinued server-side (see: Moskva, 2022-04)",
      "- Air defence package bundled in",
      "",
      "Breaking changes:",
      "- Removed peace clause from EULA",
      "- Neutrality deprecation notice: see blog post 'On the special operation'"
    ].join("\n")
  },
  {
    hash: "d7c8e21",
    date: "2022-03-25",
    author: "zelenskyy.o",
    authorEmail: "zelenskyy.o@kyiv.example",
    subject: "feat(defence): counter-offensive patch 1.2.3",
    body: [
      "Emergency patch from the customer side.",
      "Re-enables territorial integrity feature flag.",
      "",
      "Closes: KYIV-101, KHARKIV-202, MARIUPOL-451",
      "Adds: drone strike modules, Javelin integration"
    ].join("\n")
  },
  {
    hash: "9b2f4a8",
    date: "2022-04-03",
    author: "ci-bot",
    authorEmail: "ci@un.example",
    subject: "chore: report Bucha-451 — failing tests in occupied zones",
    body: [
      "Automated report from CI: war crimes compliance test",
      "suite failed across multiple occupied regions.",
      "",
      "Blocker raised. PR review pending 3+ years.",
      "Filed as: crimes-against-humanity#1"
    ].join("\n")
  },
  {
    hash: "6e1d3b5",
    date: "2022-04-14",
    author: "moskva.bot",
    authorEmail: "moskva.bot@rf-navy.example",
    subject: "fix(cruiser): Moskva unscheduled retirement",
    body: [
      "Decommissioned flagship Moskva after Neptune missile integration",
      "rolled out by customer-side SVR.",
      "",
      "BREAKING: Removed from production fleet. No rollback.",
      "Funeral arrangements: Sevastopol drydock."
    ].join("\n")
  },
  {
    hash: "4a9c2f7",
    date: "2022-09-12",
    author: "sbu.g",
    authorEmail: "sbu.g@ukraine.example",
    subject: "feat(recon): Crimea bridge async restore endpoint",
    body: [
      "Adds async restore endpoint on Kerch Strait crossing.",
      "Returns 503 indefinitely during rolling updates.",
      "",
      "P99 latency: 3 months+",
      "Rollback: not authorised"
    ].join("\n")
  },
  {
    hash: "c8d6b3a",
    date: "2023-06-24",
    author: "prigozhin.y",
    authorEmail: "prigozhin.y@pmc.example",
    subject: "feat(chaos): Wagner march on Moscow — unscheduled maintenance",
    body: [
      "Rolling restart of the ministry of defence cluster.",
      "All PMCs migrated to Rostov data centre temporarily.",
      "",
      "PR review rejected by everyone involved.",
      "Author subsequently yeeted into Belarus exile.",
      "Closes: #march-on-moscow #walter-white-cosplay"
    ].join("\n")
  },
  {
    hash: "b1e7f49",
    date: "2023-10-07",
    author: "hamas.dev",
    authorEmail: "ops@qassam.example",
    subject: "feat(region): ME-South beta — Gaza theatre initial rollout",
    body: [
      "BETA expansion to ME-South region. Build tagged 'October Surprise'.",
      "",
      "Features:",
      "- Tunnel network v3 (lower latency, higher payload)",
      "- Surprise attack module (Aly) enabled by default",
      "- Iron Dome rate-limiter engaged",
      "",
      "Customer base: 2.3M users in 141 sq mi.",
      "Discontinues: critical infrastructure of any kind."
    ].join("\n")
  },
  {
    hash: "a5f3e62",
    date: "2023-10-13",
    author: "idf.il",
    authorEmail: "idf.il@tsahal.example",
    subject: "feat(strike): Gaza-wide DDoS campaign v24.7",
    body: [
      "Rolls out carpet-bombing CDN across the Gaza region.",
      "Backed by 6,000+ bombs in the first week.",
      "",
      "Opens PR: gaza-collapse-net#1",
      "Reviewers: every newsroom in the world",
      "Status: merged without consensus"
    ].join("\n")
  },
  {
    hash: "e2d8c41",
    date: "2023-11-19",
    author: "rsf.sudan",
    authorEmail: "rsf@sudan.example",
    subject: "feat(region): AFRICA-CENTRAL — Sudan civil war scale-out",
    body: [
      "Long-running civil war escalated to GA in Darfur/Khartoum.",
      "Cluster fork between SAF and paramilitary RSF.",
      "",
      "Adds: mass-displacement event bus",
      "  - 10M+ users displaced",
      "  - famine flag enabled by default",
      "",
      "Memory leak in the food supply has been filed as:",
      "  khartoum#famine — not on the v25.1 roadmap."
    ].join("\n")
  },
  {
    hash: "7c4b9f3",
    date: "2024-01-15",
    author: "houthi.media",
    authorEmail: "ops@houthi.example",
    subject: "feat(shipping): Red Sea route elevated permissions",
    body: [
      "Promotes the Bab el-Mandeb strait to a paywalled corridor.",
      "Adds anti-ship missile integration and drone package.",
      "",
      "Free-tier shipping: deprecated",
      "Maersk: pivoting to Cape of Good Hope (longer path, same SLA)",
      "SLA: 'eventually'"
    ].join("\n")
  },
  {
    hash: "5a1e6d8",
    date: "2024-04-13",
    author: "iran.irgc",
    authorEmail: "ops@irgc.example",
    subject: "feat(airstrike): IRGC launches Isfahan v1.0",
    body: [
      "Retaliatory endpoint launched against Israeli air base.",
      "Build status: 99% failure, 1% intercepted.",
      "",
      "Status: Iran declared victory, Israel declared 'minimal damage'.",
      "PR review: mutually satisfied, nothing actually changed."
    ].join("\n")
  },
  {
    hash: "f9b2a4c",
    date: "2024-08-01",
    author: "h.amazigh",
    authorEmail: "h.amazigh@hassan.example",
    subject: "feat(hamas-leader): Haniyeh assassinated in Tehran",
    body: [
      "Patch merge in Tehran overnight.",
      "Travel-sec package bypassed local proxy.",
      "",
      "Iran files regression report: 'Israel's Mossad, running our dev env'",
      "Status: 3-day national mourning window installed."
    ].join("\n")
  },
  {
    hash: "2d4f7e9",
    date: "2024-09-23",
    author: "hezbollah.lb",
    authorEmail: "ops@hezbollah.example",
    subject: "feat(pager): Hezbollah pager network recall — supply-chain CVE",
    body: [
      "Critical CVE-2024-PAGER in Mossad-supplied hardware.",
      "All pagers and walkie-talkies called back at once.",
      "",
      "Severity: CRITICAL",
      "Vendor: Apollo Gold / Golden Apollo — 'we had nothing to do with it'",
      "Rollback: surgically applied. 39+ devices permanently bricked.",
      "Lebanon: pager outage 24h+, hospitals affected."
    ].join("\n")
  },
  {
    hash: "8e3a1b7",
    date: "2024-10-01",
    author: "iran.irgc",
    authorEmail: "ops@irgc.example",
    subject: "feat(missile): Iran launches ~180 missiles at Israel",
    body: [
      "Bulk deploy to 'True Promise II' pipeline.",
      "Vast majority intercepted by Arrow / David's Sling / Patriot stack.",
      "",
      "Throughput: 180 in 30 min.",
      "Dropped packets: ~5 (landed in empty zones, mostly)",
      "Result: theatrical escalation, no strategic change."
    ].join("\n")
  },
  {
    hash: "1c5d8a4",
    date: "2024-12-08",
    author: "hts.syria",
    authorEmail: "ops@hts.example",
    subject: "feat(regime-change): Assad cluster deprovisioned",
    body: [
      "After 24 years, the Assad load balancer crashes.",
      "Russia's failover capacity: busy elsewhere.",
      "Iran's fallback: also busy elsewhere.",
      "Hezbollah: their pager fleet was already bricked.",
      "",
      "Customer base: 21M users in Syria.",
      "New owner: HTS, formerly al-Nusra, now rebranded as 'Hayat Tahrir al-Sham'.",
      "PR status: foreign ministries scrambling to merge it."
    ].join("\n")
  },
  {
    hash: "6b9e3c2",
    date: "2025-01-19",
    author: "ci-bot",
    authorEmail: "ci@un.example",
    subject: "chore(ceasefire): Gaza v1 ceasefire deployed — known bug",
    body: [
      "v1 ceasefire deployed across Gaza region.",
      "QA team: 'we expect this to break within weeks'.",
      "",
      "Closes: gaza#ceasefire-v0",
      "Reopens: gaza#ceasefire-v1 (March 2025, March 2025, May 2025)"
    ].join("\n")
  },
  {
    hash: "4f2a8d6",
    date: "2025-06-13",
    author: "mod.in",
    authorEmail: "ops@mod.in",
    subject: "feat(india-pak): India-Pakistan 4-day escalation hotfix",
    body: [
      "Emergency release after Pahalgam tourist attack PR.",
      "Both sides deploy standoff cruise-missile SaaS in 96 hours.",
      "",
      "Service uptime: strained",
      "Diplomacy module: forced upgrade",
      "Resolution: quiet rollback to 2021 baseline. Code freeze accepted."
    ].join("\n")
  },
  {
    hash: "a3c1f5b",
    date: "2026-06-21",
    author: "mod.us",
    authorEmail: "ops@pentagon.example",
    subject: "feat(strike): US B-2 strikes Iranian nuclear sites",
    body: [
      "Fordow, Natanz, Isfahan cluster targeted with GBU-57 MOP bunker busters.",
      "",
      "Rollback: engineering difficult — material buried 80m+.",
      "Iran retaliates: limited missile salvo, mostly intercepted.",
      "Ceasefire module: still on backlog."
    ].join("\n")
  },
  {
    hash: "9d4a8e1",
    date: "2026-07-01",
    author: "ci-bot",
    authorEmail: "ci@un.example",
    subject: "chore(stability): Russia-Ukraine still running v1.0",
    body: [
      "Customer reports: 'this should have shipped long ago'.",
      "Engineering team: 'we are not in a hurry'.",
      "",
      "Versions in flight: 4+ years on the same major.",
      "Active contributors: ~600k military + ~30k FPV pilots on the customer side.",
      "Drone warfare has graduated from MVP to GA product.",
      "",
      "TODO: end the war. Owner: UN. Status: backlog."
    ].join("\n")
  },
  {
    hash: "c2a4d81",
    date: "2026-07-22",
    author: "nato.summit",
    authorEmail: "ops@nato.example",
    subject: "feat(peace-deal): 50-day ultimatum — Trump 365 broker",
    body: [
      "New broker middleware ships a 50-day ultimatum to Russia-Ukraine.",
      "Pattern: 'do X or pay 100% tariff'.",
      "",
      "Merge conflict with reality on day 7.",
      "Status: most deadlines extended.",
      "P50 outcome: 'we'll get back to you'.",
      "",
      "Closes: peace-2025#1 (won't fix)"
    ].join("\n")
  },
  {
    hash: "1f8e0b3",
    date: "2026-08-04",
    author: "dprk.woo",
    authorEmail: "ops@pyongyang.example",
    subject: "feat(troops): 10k+ DPRK troops deployed into Kursk region",
    body: [
      "Foreign-worker module from the DPRK repo deployed to the Kursk theatre.",
      "Bundle size: 10,000+ containers, 50% casualty rate.",
      "",
      "Defect filed: low morale, language barriers, casualty-heavy loop.",
      "Owner: kim.j. Status: 'they signed a contract'.",
      "Rollback: only on full year-end audit."
    ].join("\n")
  },
  {
    hash: "a9b7e54",
    date: "2026-09-12",
    author: "junta.mm",
    authorEmail: "ops@myanmar.example",
    subject: "feat(region): SE-ASIA-MYANMAR — civil war escalates post-elections",
    body: [
      "Long-running internal conflict promotes to GA after disputed election.",
      "Resistance forces capture multiple regional capitals in 12 months.",
      "",
      "Displaces: 3M+ users.",
      "SLA: 'we will get back to you in 5 years'.",
      "Conflict with China over border-subduction: low intensity."
    ].join("\n")
  },
  {
    hash: "e7b3f62",
    date: "2026-09-15",
    author: "ops@war365.example",
    authorEmail: "ops@war365.example",
    subject: "feat(copilot): Battlefield Copilot enters general availability",
    body: [
      "Generative-AI module for theatre commanders.",
      "",
      "Features:",
      "- Autogenerates invasion plans from a one-line prompt",
      "- Drone swarm choreography in natural language",
      "- Negotiated surrender to whoever lost first",
      "- Hallucinates ceasefires but only the plausible ones",
      "",
      "Pricing: included in War365 Sovereign tier.",
      "Privacy: your plans are trained on. Sorry.",
      "Status: red-teamed by people who don't like it.",
      "",
      "Ref: https://tino.munic/posts/war365-now-with-copilot"
    ].join("\n")
  },
  {
    hash: "6d8b3c7",
    date: "2026-09-28",
    author: "ops@war365.example",
    authorEmail: "ops@war365.example",
    tag: "v25.9.30",
    subject: "chore(status): push v25.9.30 to all regions, prepare for [load]",
    body: [
      "Promotes v25.9.30 across all active regions.",
      "Roadmap commit queue: Myanmar, Sudan, Gaza, Ukraine, Lebanon.",
      "",
      "On-call: exhausted. Pager: rotating.",
      "End-of-quarter incident review: cancelled.",
      "",
      "Reminder: Battlefield Copilot is opt-out at the user level,",
      "opt-in at the theatre level. Mandatory at the sovereign level.",
      "",
      "Have a good shift, everyone. War365 lives."
    ].join("\n"),
    // Hero card metadata — drives the "Latest release" card on the landing page.
    // Optional; only release commits need it. Falls back to `subject` for the
    // headline when omitted; other fields hide themselves when missing.
    headline: "Battlefield Copilot enters general availability",
    summary: "Generative AI for theatre commanders. Autogenerates invasion plans from a one-line prompt.",
    breaking: true,
    chips: ["+390 mi", "no rollback"]
  },
  {
    hash: "b8f5a90",
    date: "2026-09-30",
    author: "scott@war365.example",
    authorEmail: "scott@war365.example",
    subject: "docs(readme): add mandatory subscription disclaimer",
    body: [
      "Customer support tells us the EULA is 'a little confusing'.",
      "Updating README to clarify:",
      "",
      "  War365 is a mandatory lifetime subscription.",
      "  You cannot opt out.",
      "  You will receive endless updates.",
      "  Battlefield Copilot is enabled by default.",
      "",
      "Thanks, and remember to update your safety tier.",
      "— The War365 team"
    ].join("\n")
  },
  {
    hash: "9c4e2b7",
    date: "2026-10-15",
    author: "nato.summit",
    authorEmail: "ops@nato.example",
    subject: "chore(ceasefire): energy truce v1 rolled back after 72 hours",
    body: [
      "Energy truce v1 ships 2026-10-11, brokered by the customer.",
      "Scope: strikes on energy infrastructure, both directions.",
      "",
      "Uptime: 72 hours.",
      "Rolled back by the customer, not by us.",
      "",
      "Compliance log:",
      "- 2026-10-11 to 2026-10-14: Ukraine refrained from energy targets. Russia did not.",
      "- 2026-10-15: Ukraine resumed, at the refineries.",
      "",
      "Load observed after the rollback:",
      "- 850 drones and 39 missiles in a 24h window",
      "- 30 energy targets across 19 regions",
      "",
      "Kremlin position: there was never an agreement, and there will be no ceasefire (Lavrov, 2026-10-15).",
      "",
      "Throttling: Ukraine restricted its own Starshield use on 2026-10-14.",
      "",
      "Ref: https://www.aljazeera.com/news/2026/10/16/ukraine-repels-russian-forces-as-us-support-wavers-energy-strikes-escalate",
      "Ref: https://understandingwar.org/research/russia-ukraine/russian-offensive-campaign-assessment-october-15-2026/",
      "",
      "Closes: energy-truce#1 (won't fix)"
    ].join("\n")
  },
  {
    hash: "d70a3f5",
    date: "2026-10-18",
    author: "ci-bot",
    authorEmail: "ops@war365.example",
    subject: "feat(strike): largest drone attack on St. Petersburg hits oil terminal",
    body: [
      "Drone package delivered to St. Petersburg, the largest attack on the city since the war began.",
      "Primary target: a major oil terminal. Other critical targets also hit.",
      "",
      "Host: Putin's hometown, still running.",
      "Timing: after the energy truce was rolled back.",
      "",
      "Ref: https://www.fdd.org/overnight-brief/october-19-2026/"
    ].join("\n")
  },
  {
    hash: "b1d8c64",
    date: "2026-10-19",
    author: "houthi.media",
    authorEmail: "ops@houthi.example",
    subject: "feat(strike): Houthi missiles reach Saudi oilfields and airports",
    body: [
      "Missile package delivered to Saudi energy, airport and military targets.",
      "",
      "Targets:",
      "- Yanbu, Aramco site",
      "- Shaybah oilfield",
      "- King Khalid Intl, Riyadh",
      "- Abha airport",
      "",
      "Saudi Arabia brokered the 2022 truce. Now it is the target.",
      "Mitigation: RAF jets on defensive rotations.",
      "",
      "Ref: https://www.newarab.com/news/diplomatic-visits-attempt-hold-all-out-us-iran-war",
      "",
      "Reopens: yemen-truce-2022#1"
    ].join("\n")
  },
  {
    hash: "87dffab",
    date: "2026-10-19",
    author: "ci-bot",
    authorEmail: "ci-bot@war365.example",
    subject: "feat(drone): al-Dibab transport hub hit twice in deadly market-area strike",
    body: [
      "Drone package deployed near a market in al-Dibab, West Kordofan state.",
      "",
      "- Strikes: 2, 10 minutes apart",
      "- Primary location: transport hub used by commuters returning to villages after market day",
      "- Fatalities: 80",
      "- Transported to al-Mujlad: 47",
      "- Fatal injuries among transported: 30",
      "- Additional al-Mujlad strike injured 4, currently receiving treatment",
      "",
      "The RSF-declared administration accused the army of carrying out the attack. Attribution remains unresolved.",
      "",
      "Ref: https://www.theguardian.com/world/2026/oct/19/drone-attack-market-al-dibab-west-kordofan-sudan",
      "Status: one of the war's deadliest single strikes; drone usage continues to scale."
    ].join("\n")
  },
  {
    hash: "fd3aed7",
    date: "2026-10-20",
    author: "ci-bot",
    authorEmail: "ci-bot@war365.example",
    subject: "feat(strike): drone strike hits Abyei market and fuel depot",
    body: [
      "Drone package deployed at Amiet Market in the disputed Abyei border region.",
      "Impact: at least 153 people killed, with dozens also injured.",
      "Secondary target: nearby fuel depot.",
      "Fire status: still burning on Tuesday as the reported death toll continued to rise.",
      "Attribution: local officials blamed Sudan's military; the Associated Press could not independently verify who carried out the attack.",
      "Ref: https://www.france24.com/en/africa/20261020-more-than-150-killed-sudan-drone-strike-disputed-abyei-border-region",
      "Status: casualty count remains active while incident investigation is pending."
    ].join("\n")
  },
  {
    hash: "24d7587",
    date: "2026-10-20",
    author: "iran.irgc",
    authorEmail: "iran.irgc@iran.example",
    subject: "feat(strait): IRGC mines set two oil tankers ablaze",
    body: [
      "Mined deployment active in the southern Strait of Hormuz.",
      "The IRGC said two oil tankers struck its mines and were set on fire and brought to a standstill.",
      "Neither vessel was named and the precise location was not disclosed.",
      "Route status: unauthorised passage, according to Tehran.",
      "Threatened next release: expanded attacks on shipping and undersea internet cables in the Gulf.",
      "IRGC spokesperson Hossein Mojabi also promised new weapons aimed at removing US military presence from the region.",
      "A separate UKMTO incident 121 nautical miles east of Duqm resulted in no reported damage or casualties.",
      "Ref: https://www.euronews.com/2026/10/20/irgc-mines-set-tankers-ablaze-as-tehran-threatens-expanded-attacks",
      "Status: Strait of Hormuz transit remains in dispute."
    ].join("\n")
  },
  {
    hash: "a6ed6b7",
    date: "2026-10-21",
    author: "idf.il",
    authorEmail: "ops@idf.example",
    subject: "feat(detention): Israeli army arrests Brad Lander during olive harvest in occupied West Bank",
    body: [
      "Olive-harvest assistance triggered a detention workflow in the occupied West Bank.",
      "- Detainee: Brad Lander, Democratic Party nominee for New York's 10th congressional district",
      "- Alleged activity: helping Palestinians harvest olives",
      "- Release: Lander was released with a warning, which he said was apparently due to his public profile",
      "- Remaining detentions: several dozen rabbis and other participants harvesting olives with Lander",
      "Lander called for the remaining detainees to be released immediately.",
      "Ref: https://www.middleeasteye.net/live-blog/live-blog-update/us-congressional-candidate-brad-lander-arrested-israeli-army-occupied",
      "Status: warning issued; related detentions remain active."
    ].join("\n")
  },
  {
    hash: "1396808",
    date: "2026-10-21",
    author: "houthi.media",
    authorEmail: "ops@houthi.example",
    subject: "feat(strike): Houthi missile strike hits Shabwa training camp",
    body: [
      "Missile package deployed at al-Alam camp in Shabwa province, southern Yemen.",
      "The strike occurred while new recruits were lining up for a training session.",
      "Impact: 75 recruits killed and 200 others wounded.",
      "The recruits, aged 18 to 20, were training to provide security in Shabwa, not for combat operations.",
      "Wednesday's mass funeral was held at a soccer field in south-central Shabwa.",
      "Shabwa's governor pledged increased efforts to defend the province and hold those responsible accountable.",
      "Ref: http://www.africanews.com/2026/10/21/yemen-75-new-recruits-killed-in-houthi-missile-strike-laid-to-rest/",
      "Status: deadliest attack since fighting resumed over the summer."
    ].join("\n")
  },
  {
    hash: "652e784",
    date: "2026-10-21",
    author: "ops",
    authorEmail: "ops@war365.example",
    subject: "feat(defence): four-nation Badr deal enables joint weapons production",
    body: [
      "Turkey, Qatar, Pakistan and Indonesia signed the Badr deal for joint production of military hardware.",
      "",
      "- Scope: military hardware production",
      "- Expanded cooperation: military training, research and development",
      "- Signatories: Yasar Guler, Haluk Gorgun, Saoud bin Abdulrahman Al Thani, Khawaja Muhammad Asif and Yusuf Jauhari",
      "- Signing location: Doha",
      "- Product name: Badr deal, referencing the Battle of Badr in 624",
      "",
      "Ref: https://www.middleeasteye.net/live-blog/live-blog-update/turkey-qatar-pakistan-and-indonesia-forge-badr-deal-jointly-produce",
      "Status: joint production groundwork signed across four participating nations."
    ].join("\n")
  },
  {
    hash: "3153f74",
    date: "2026-10-22",
    author: "moskva.bot",
    authorEmail: "moskva.bot@moskva.example",
    subject: "feat(airstrike): Russian long-range attacks intensify across Ukraine",
    body: [
      "Long-range attack campaign escalated across Ukraine, including emergency power outages in Kyiv.",
      "Civilian impact: at least 14 deaths and 78 injuries overnight into Thursday.",
      "Seven children were wounded during the strikes.",
      "Health and energy facilities sustained additional damage.",
      "Donetsk region: two civilians killed and nine injured, according to reports from Russian-occupied areas.",
      "Energy infrastructure was damaged in Poltavska, Rivnenska and Volynska oblasts.",
      "Hostilities disrupted power in six frontline areas.",
      "Ref: https://news.un.org/feed/view/en/story/2026/10/1168648",
      "Status: civilian and infrastructure impact remains under active reporting."
    ].join("\n")
  },
  {
    hash: "95d4c37",
    date: "2026-10-23",
    author: "idf.il",
    authorEmail: "idf.il@idf.example",
    subject: "feat(west-bank): gunmen open fire at Hebron checkpoint",
    body: [
      "Hebron checkpoint engaged an armed incursion during heightened West Bank tensions.",
      "- Casualties: five Israelis wounded; two suspected Palestinian attackers killed",
      "- Two injured Israelis were reported in critical condition",
      "- The Israeli military said the attackers may have intended a larger attack on Route 35",
      "- A large quantity of ammunition was recovered from the attackers' vehicle",
      "- Raids began on the attackers' homes; several adjacent Palestinian buildings were ordered demolished",
      "- Netanyahu ordered preparations for a full West Bank lockdown beginning later Friday",
      "Ref: https://www.bbc.co.uk/news/articles/cq4g1p974wxko?at_medium=RSS&at_campaign=rss",
      "Status: lockdown deployment scheduled ahead of the election."
    ].join("\n")
  },
  {
    hash: "101f7ca",
    date: "2026-10-23",
    author: "ci-bot",
    authorEmail: "ci-bot@war365.example",
    subject: "feat(ukraine-russia): drone sinks cargo ship, Romania blames Russia",
    body: [
      "Romania attributed a drone strike that sank a cargo ship to Russia.",
      "",
      "- Vessel status: cargo ship sank",
      "- Casualties: 1 killed, 3 missing",
      "",
      "Ref: https://news.google.com/rss/articles/CBMirwFBVV95cUxPOF9iZ3FoTHAycU5fWGxKNWNiYnpvRXlwUWJ2ZVFtQU9IUmF4UWJTU1AwTEFRT21vNWRDNzRjWTgtY0F6Vkp0RkdxeG9xM1A0X1RRX19Eb0RqVG9tbTBNeWFRaXZ2SzEtUUFEc2VjZlZPaUxtR3JGTUNEN3VRdWtRMEdTM21OSTVSQWNJN3FaOWpBNHdld3IyZS1sbVA1a2wxLVJXRm01ejhKWXZzQU5B?oc=5",
      "Status: maritime incident attributed to Russia; 3 people remain missing."
    ].join("\n")
  },
  {
    hash: "667ef5c",
    date: "2026-10-23",
    author: "idf.il",
    authorEmail: "idf.il@idf.il.example",
    subject: "feat(west-bank): army prepares full closure after Hebron shooting",
    body: [
      "The Israeli government ordered the army to prepare for a full closure of the occupied West Bank.",
      "Trigger: a shooting near Hebron killed two soldiers.",
      "Scope: full West Bank closure preparations.",
      "Ref: https://news.sky.com/story/israel-orders-army-to-prepare-to-fully-close-west-bank-after-attack-13602577",
      "Status: closure readiness ordered following the Hebron shooting."
    ].join("\n")
  },
  {
    hash: "44b8d1b",
    date: "2026-10-24",
    author: "mod.us",
    authorEmail: "mod@war365.example",
    subject: "feat(peace-deal): Melania Trump brokers ceasefire for relief aid",
    body: [
      "Melania Trump brokered a ceasefire deal in a Russian-occupied Ukrainian city.",
      "- Objective: allow relief aid to enter the city",
      "- Deal type: ceasefire",
      "- Theatre: Ukraine and Russia",
      "",
      "Ref: https://news.google.com/rss/articles/CBMirwFBVV95cUxOMkNRM3hJTVJkUGxjNjB3QmhSd2FSb2JHZkZtTjVNdzNWeHJ4QkpwdEd0cWttQjg0ZmVSQUtCV0JHTFRCeTd3NGJITy1ybDRTQzB4ZkhEdDEtRkRhcUZrWHdONWJZZFlBbGV5YmhkbDh5LTlaZm9jelQ3Y2FWOEcxUlhLZE5yX2c4dVhSZlYyVDUtVllza2ZLLTVXQ2RCN093aGJlRmc4RU9jcHZROVRv?oc=5",
      "Status: relief-aid access negotiated through a city-level ceasefire."
    ].join("\n")
  },
  {
    hash: "1e07f30",
    date: "2026-10-24",
    author: "zelenskyy.o",
    authorEmail: "zelenskyy.o@war365.example",
    subject: "feat(drone): Ukrainian strike hits petrochemical plant in Togliatti",
    body: [
      "Ukrainian forces struck a Russian petrochemical plant in Togliatti overnight, Kyiv's general staff said.",
      "The attack caused an explosion and fire, Ukrainian authorities said.",
      "Several industrial facilities were damaged, Togliatti mayor Ilya Sukhikh confirmed.",
      "Social media footage showed thick black smoke rising from the industrial area.",
      "Togliatti is home to Avtovaz and major ammonia producer Togliattiazot.",
      "Ref: https://www.independent.co.uk/news/world/europe/ukraine-russia-war-live-oleshky-melania-trump-ceasefire-starlink-b3072649.html",
      "Status: industrial damage confirmed; casualty data not reported."
    ].join("\n")
  },
  {
    hash: "d89d15e",
    date: "2026-10-24",
    author: "idf.il",
    authorEmail: "idf.il@war365.example",
    subject: "feat(west-bank): Israel launches major security operation in Hebron",
    body: [
      "The Israeli military launched a large-scale security operation in Hebron on October 24, 2026.",
      "Trigger: two Palestinian gunmen killed two Israeli soldiers and wounded three others at a military checkpoint near the city.",
      "- Operation duration: expected to continue for several days",
      "- Objective: locate militants and weapons in areas linked to the attack",
      "- Displacement estimate: 150-250 Palestinian families",
      "- Vehicle access: restricted at closed gates; pedestrians directed through designated exit points and security checks",
      "Ref: https://www.euronews.com/2026/10/24/israel-removes-around-250-palestinian-families-from-west-bank-city-of-hebron-after-soldier",
      "Status: Hebron operation deployed; hundreds of Palestinian residents displaced."
    ].join("\n")
  },
  {
    hash: "ba55a24",
    date: "2026-10-25",
    author: "houthi.media",
    authorEmail: "ops@houthi.example",
    subject: "feat(yemen): Saudi intercepts 10 Houthi missiles as Riyadh airport reopens",
    body: [
      "Saudi Arabia intercepted 10 Houthi ballistic missiles and a drone fired at Riyadh, according to the Saudi-led coalition.",
      "- Interceptions: 10 ballistic missiles and 1 drone",
      "- Reported explosions: heard in Riyadh",
      "- Airport status: terminals one and two reopened",
      "- Terminals three and four: remain closed after Houthi strikes",
      "- Earlier airport strikes: 17 killed and 330+ wounded in early October",
      "Ref: https://www.newarab.com/news/saudi-downs-10-houthi-missiles-riyadh-airport-reopens",
      "Status: partial Riyadh airport service restored under continuing missile and drone threat."
    ].join("\n")
  },
  {
    hash: "387bbf8",
    date: "2026-10-25",
    author: "iran.irgc",
    authorEmail: "iran.irgc@iran.example",
    subject: "feat(drone): Iranian army says it shot down US drone over Bandar Abbas",
    body: [
      "The Iranian army said it shot down a US drone over Bandar Abbas, according to Tasnim and Reuters.",
      "",
      "- Asset status: US drone reported shot down",
      "- Location: Bandar Abbas",
      "- Source: Tasnim report carried by Reuters",
      "",
      "Ref: https://news.google.com/rss/articles/CBMixAFBVV95cUxNNjlxWUNjczg2SHFQamFEZDV0SVhZaHA5bFdqaVQzT1oxSjd0b2ZQQjd6MldHeEhKcUstbGJEa1QxMmFBMFhad2VnREVIa2xoT0tPWlFXVW5lcXVEYjMwdUd5NTRIYm0zTFpabXUxY2pCakRGM3JnWE1iNHc3MmtlbWduRno3ZWVGVWVpa2JtRjF4VDh5TEFHN21hUV9sQUhxOWpJMVVPNlhFMDd5SkJMekZkTFdtQzlnYnBQNkd2MG1TNzZy?oc=5",
      "Status: interception claimed by the Iranian army; independent confirmation not reported."
    ].join("\n")
  },
  {
    hash: "83505e9",
    date: "2026-10-26",
    author: "mod.us",
    authorEmail: "mod.us@mod.example",
    subject: "feat(sahel): US airstrikes accused of displacing Somali civilians into flood-prone areas",
    body: [
      "US-led airstrikes in southern Somalia are accused of pushing civilians toward the flood-prone banks of the River Juba as El Nio strengthens.",
      "- Operational area: Jilib and Malenda, near the Juba River",
      "- Displacement pattern: residents reportedly forced to move toward the river",
      "- Environmental condition: El Nio forecast to intensify Somalia's rainy season from this month",
      "- Terrain exposure: large numbers of women and children reportedly pinned on the floodplain",
      "- Attribution: Africom declined to share operational security details",
      "Ref: https://www.theguardian.com/global-development/2026/oct/26/us-forces-accused-of-weaponising-somalia-flood-el-nino",
      "Status: intent disputed; civilian exposure and flood risk reported."
    ].join("\n")
  },
  {
    hash: "ec289f1",
    date: "2026-10-26",
    author: "rsf.sudan",
    authorEmail: "rsf.sudan@rsf.example",
    subject: "feat(drone): RSF strikes five power stations across three Sudanese states",
    body: [
      "Rapid Support Forces launched a coordinated drone attack against five power stations, a government official said.",
      "- Al-Jazira: 2 power stations hit",
      "- Gedaref: 2 power stations hit",
      "- White Nile: 1 power station hit",
      "Impact: power outages across large parts of all three army-controlled states.",
      "The UN says repeated attacks on power stations threaten health and services for millions of people already facing extreme hunger.",
      "Ref: https://www.theguardian.com/world/2026/oct/26/sudan-paramilitary-drone-strikes-rapid-support-forces-power-cuts-eastern-states",
      "Status: regional grid availability degraded; restoration time not reported."
    ].join("\n")
  },
  {
    hash: "ce45550",
    date: "2026-10-26",
    author: "idf.il",
    authorEmail: "idf.il@idf.il.example",
    subject: "feat(drone): Israeli quadcopters ignite blaze at Gaza City camp",
    body: [
      "Israeli quadcopter drones started a fire in Gaza City's Shujayea neighbourhood, according to the Palestinian Public Works Ministry.",
      "The blaze began at about 8pm local time on Sunday.",
      "Tents were destroyed as flames continued beyond midnight.",
      "About 800 Palestinians were displaced, including women, children and elderly people.",
      "The ministry appealed for international assistance to supply replacement tents.",
      "Ref: https://www.middleeasteye.net/live-blog/live-blog-update/israeli-drones-burn-gaza-refugee-camp-displacing-about-800-palestinian",
      "Status: shelter inventory destroyed; replacement tents requested."
    ].join("\n")
  },
  {
    hash: "58b8342",
    date: "2026-10-27",
    author: "russia.mil",
    authorEmail: "russia.mil@russia.example",
    subject: "feat(airstrike): Russian missile and drone attack hits Kyiv",
    body: [
      "Kyiv processed two overnight waves of Russian ballistic missiles and drones.",
      "",
      "- Payload reported by President Volodymyr Zelenskyy: 16 ballistic missiles and 280+ drones",
      "- Regional impact: energy and logistics sites hit across 11 regions",
      "- Kyiv casualty report: 1 killed and 14 injured, with 9 taken to hospital",
      "- Infrastructure damage: university buildings and medical facilities near Lisova metro station",
      "- Transit degradation: Pivdennyi bridge damaged, disrupting metro services across the Dnipro",
      "- Emergency response: firefighters rescued a dog from the rubble; a second injured dog was found nearby",
      "- Delivery warning: delays involving Patriot and NASAMS interceptors were criticised",
      "",
      "Ref: https://www.euronews.com/video/2026/10/27/ukraine-firefighters-battle-flames-and-rescue-dog-from-kyiv-ruins",
      "Status: Kyiv impact acknowledged; broader interceptor availability remains unresolved."
    ].join("\n")
  },
  {
    hash: "70f3037",
    date: "2026-10-27",
    author: "mod.in",
    authorEmail: "mod@mod.example",
    subject: "feat(sahel): Niger accuses Chad of deadly drone strike",
    body: [
      "Niger's military government accused Chad of carrying out a drone strike that killed two civilians and injured others.",
      "- Incident time: early Saturday",
      "- Location: Salvador Pass, mountainous Emi Lulu area, northern Niger",
      "- Requested response: end hostile actions and compensate Niger for damage",
      "- Diplomatic action: Chadian ambassador summoned",
      "- Escalation path: referral to the UN Security Council and African Union Peace and Security Council requested",
      "- Verification: Niger called for an independent international investigation",
      "Ref: http://www.africanews.com/2026/10/27/niger-accuses-chad-of-deadly-drone-attack-in-which-two-civilians-died/",
      "Status: attribution and requested investigation unresolved."
    ].join("\n")
  },
  {
    hash: "6e7451a",
    date: "2026-10-27",
    author: "jordan.mil",
    authorEmail: "ops@jordan.example",
    subject: "feat(airstrike): Jordan strikes village in southern Daraa",
    body: [
      "Jordanian fighter jets struck a village in Syria's southern Daraa province, retaliation for a church funeral attack.",
      "- Trigger: 9 people killed and 34 injured in a shooting at a Greek Orthodox church in Karak on Friday",
      "- Reported impact: Syrian health officials said 5 people, including women, children and an elderly man, were killed",
      "- Jordan's assessment: fighter jets killed and wounded several terrorists, with no further details provided",
      "- Coordination status: Jordan said it coordinated with the Syrian government; Syria said it was not notified",
      "- Border response: Syria closed the Nassib passenger and commercial crossing to Jordan",
      "- Suspect update: Jordan arrested two brothers and their brother-in-law over the church attack",
      "Ref: https://www.bbc.co.uk/news/articles/cq8ezg6dy6xlo?at_medium=RSS&at_campaign=rss",
      "Status: direct communication opened; investigation into the targeting announced."
    ].join("\n")
  },
  {
    hash: "d2ab8ff",
    date: "2026-10-29",
    author: "ci-bot",
    authorEmail: "ci-bot@war365.example",
    subject: "feat(drone): Russian drone attack hits Dnipro train station",
    body: [
      "Russian drone attack deployed against a train station in Dnipro, Ukraine.",
      "",
      "- Target: train station",
      "- Location: Dnipro, Ukraine",
      "- Reported impact: 13 killed",
      "",
      "Ref: https://news.google.com/rss/articles/CBMirAFBVV95cUxPMVJMbm5Vb3NTVmNud01fMHc3WHJUWTNvWl8zSmJYZjVUUHhRbm5VWGZxVWZmbGpQdHZNZUlCQVFuLWxWb1FoR0xTZThVSmRTRVBlWUlLaWNKUTZzVnV1dTYyellibWN0XzFXNGpsUk45U2o1Z2hzUndOUEJYM0Q3WmUxSHFteS1WRXpyRk5JcmdTaEdyNVMzV2dwRGxCc0hGMlpQRElXQzMxZXdj?oc=5",
      "Status: casualty report logged; further operational details unavailable."
    ].join("\n")
  },
  {
    hash: "f0b9ad9",
    date: "2026-10-29",
    author: "ops",
    authorEmail: "ops@war365.example",
    subject: "feat(haiti): El Salvador deploys 2,000+ troops to Haiti",
    body: [
      "El Salvador has deployed more than 2,000 soldiers to Haiti to retrieve four missing military personnel.",
      "",
      "- Mission objective: recover four Salvadoran nationals missing for almost two weeks\n- Operational area: outskirts of Port-au-Prince, including territory controlled by Croix-des-Bouquets\n- Supporting role: assist security efforts against gangs in Haiti\n- Context: the four air force technicians were working with the UN-backed Gang Suppression Force\n- Dependency: support from various countries and international organisations was announced\n\nRef: https://www.bbc.co.uk/news/articles/ck0e075n79j5o?at_medium=RSS&at_campaign=rss\nStatus: retrieval operation deployed; responsibility for the ambush remains unclaimed."
    ].join("\n")
  },
  {
    hash: "dd5ec57",
    date: "2026-10-29",
    author: "mod.us",
    authorEmail: "mod@us.example",
    subject: "feat(iran): Hegseth fires Pentagon's top military planner amid consideration of new Iran strikes",
    body: [
      "Pentagon leadership update shipped alongside renewed review of Iran operations.",
      "- Pete Hegseth fired the Pentagon's top military planner.",
      "- President Trump is considering new strikes against Iran.",
      "- Planning capacity and strike options remain under active review.",
      "",
      "Ref: https://news.google.com/rss/articles/CBMioAFBVV95cUxOZmVIdU1FSEwxZkxoSnhpcWZPNHFqM0NfT2ZOTDZvQW5XUlVSSGYwTmlaRlhKdXMyRlk1ZVJ2SHpVeVhaTkhiX0FWWHhLdUs4bDU4WjNlV2Z0Vno4VzEzTlRoUkJOeTA5eTVvT3hsY3I4aGswSmVNbWJNTkZzalpUMXhmVTJSVDZEakxodkJLeExNaDh6UHBuVkVvUjZzbEE3?oc=5",
      "Status: leadership change deployed; potential new strikes remain under consideration."
    ].join("\n")
  },
  {
    hash: "91d8c2e",
    date: "2026-10-29",
    author: "dprk.woo",
    authorEmail: "dprk.woo@war365.example",
    subject: "feat(missile): North Korea launches ballistic missiles off east coast",
    body: [
      "North Korea launched ballistic missiles from its east coast into the Sea of Japan.",
      "",
      "- Platform: ballistic missiles",
      "- Launch area: east coast of North Korea",
      "- Reported destination: Sea of Japan",
      "- Regional context: tensions with South Korea continue to rise",
      "- Attribution: launch reported by South Korea",
      "",
      "Ref: https://news.sky.com/story/north-korea-fires-ballistic-missiles-off-east-coast-as-tensions-with-south-rise-13605215",
      "Status: launch detected and logged; further operational details unavailable."
    ].join("\n")
  },
  {
    hash: "d4a1986",
    date: "2026-10-30",
    author: "ci-bot",
    authorEmail: "ci-bot@war365.example",
    subject: "feat(evacuation): corridor opens for residents leaving occupied Oleshky",
    body: [
      "Evacuation of the Russian-occupied Ukrainian city of Oleshky is under way, confirmed by Russian and Ukrainian authorities.",
      "- Ceasefire status: active across the frontline Kherson region since Tuesday",
      "- Maintenance: Russian sappers demined the road out of Oleshky",
      "- Departure window: 4 hours, ending at 14:00",
      "- Capacity: 25 buses for up to 750 people, plus ambulances for people with limited mobility",
      "- Routing: occupied territory to Anapa, by government plane to Gomel, then by road into Ukraine's Chernihiv region",
      "- Remaining users: several hundred residents chose to stay despite the lack of gas, electricity and running water",
      "- Aid package: Russia said it prepared dozens of tonnes of food, medicine, hygiene products and generator fuel",
      "Ref: https://www.bbc.co.uk/news/articles/c60me298k1yeo?at_medium=RSS&at_campaign=rss",
      "Status: corridor open through the end of Sunday 1 November; evacuation remains voluntary."
    ].join("\n")
  },
  {
    hash: "cf45dc0",
    date: "2026-10-30",
    author: "ci-bot",
    authorEmail: "ci-bot@war365.example",
    subject: "feat(press): Novaya Gazeta shuts down under Kremlin pressure",
    body: [
      "Independent Russian newspaper Novaya Gazeta has shut down.",
      "",
      "- Founding era: launched after the fall of the Soviet Union",
      "- Compliance label: branded a foreign agent",
      "- Coverage status: among the last Russian news outlets to report critically on the invasion of Ukraine",
      "- Cause: the outlet says Kremlin pressure killed it",
      "",
      "Ref: https://www.timesofisrael.com/leading-independent-russian-newspaper-shuts-down-says-kremlin-pressure-killed-it/",
      "Status: publication terminated; editorial capacity permanently removed."
    ].join("\n")
  },
  {
    hash: "f85b595",
    date: "2026-10-31",
    author: "iran.irgc",
    authorEmail: "iran.irgc@iran.example",
    subject: "feat(maritime): Iran halts three tankers in Strait of Hormuz",
    body: [
      "Iran reports three oil tankers halted in the Strait of Hormuz amid escalating attacks.",
      "- Traffic control: tankers switched off navigation and positioning systems after radio warnings, the IRGC said.",
      "- Route policy: vessels must use a designated corridor and coordinate passage with Iranian forces.",
      "- Tanker incidents: a supertanker carrying 2 million barrels reportedly stopped after striking a naval mine.",
      "- Parallel rescue: Oman evacuated 25 crew members from the Panamanian-flagged merchant ship RITI after it was targeted and caught fire.",
      "- Medical support: rescued crew members received medical care.",
      "- External validation: US Central Command said US forces had cleared the strait's primary transit routes of Iranian sea mines.",
      "Ref: https://www.newarab.com/news/oman-rescues-25-burning-ship-iran-halts-tankers",
      "Status: maritime traffic restricted; tanker incidents and route enforcement remain active."
    ].join("\n")
  },
  {
    hash: "5178a45",
    date: "2026-10-31",
    author: "mod.us",
    authorEmail: "ops@mod.example",
    subject: "feat(missile): US approves sale of 500 PAC-3 Patriot missiles to Ukraine",
    body: [
      "The US has approved the sale of 500 advanced PAC-3 Patriot interceptor missiles to Ukraine.",
      "- Order size: 500 missiles",
      "- Package value: $2.1bn",
      "- Funding: entirely provided by Ukraine's allies in Europe and Canada",
      "- Principal contractor: Lockheed Martin",
      "- Production capacity: about 600 missiles per year",
      "- Delivery estimate: several years, according to President Volodymyr Zelensky",
      "- Inventory note: global supply is constrained by US use of the missiles in its war against Iran",
      "- Operational context: Russia has conducted more than 30 strikes on critical parts of Ukraine's power grid over the past two weeks",
      "",
      "Ref: https://www.bbc.co.uk/news/articles/c3vgxznlx7jzo?at_medium=RSS&at_campaign=rss",
      "Status: sale approved; interceptor deployment pending a lengthy production schedule."
    ].join("\n")
  },
  {
    hash: "e4a0e65",
    date: "2026-10-31",
    author: "ukraine.mod",
    authorEmail: "ukraine.mod@war365.example",
    subject: "feat(missile): Drones and Neptune missiles strike Kamensky rocket fuel plant",
    body: [
      "Ukrainian forces combined attack drones with Navy Neptune cruise missiles in an overnight strike on the Kamensky chemical plant in Kamensk-Shakhtinsky, Rostov region.",
      "",
      "- Attack window: overnight into Saturday, Oct. 31",
      "- Target: military-industrial infrastructure producing solid rocket propellant and propulsive charges",
      "- Confirmed damage: four production workshops",
      "- Fire: finished products warehouse ignited",
      "- Supported systems: Uragan, Smerch, and modernized Tornado-S artillery rocket systems",
      "",
      "Ref: https://www.kyivpost.com/post/88751",
      "Status: precision strike deployed; production capacity damage confirmed."
    ].join("\n")
  }
];

// (no helpers — app.js handles escaping inline)