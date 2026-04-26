/**
 * FAQPage Schema.org JSON-LD for Elbee Yoga Guide.
 *
 * Target engines: Google Rich Results, Perplexity, SearchGPT, Gemini.
 * Spec: https://schema.org/FAQPage
 *
 * Content covers: pose matching algorithm, health flag kill-switch,
 * instructor trust score, AEO/GEO concepts, and beginner onboarding.
 */

export const FAQ_ITEMS = [
  {
    question: 'How does Elbee match yoga poses to my health goals?',
    answer:
      'Elbee uses a benefit-scoring algorithm that maps your selected goals (e.g. Spinal Mobility, Hip Flexibility) to the benefit tags stored for every pose. Each goal expands into a set of related tags — for example, "Back Pain Relief" maps to the tags back, relief, posture, and release. Poses are then ranked by the weighted sum of matching tags, so the pose most aligned with your goals appears first.',
  },
  {
    question: 'What is the Kill-Switch filter in yoga pose matching?',
    answer:
      'The Kill-Switch filter automatically removes poses that are contraindicated for a reported health condition. If you flag knee injury, for example, Lotus Pose (Padmasana) is removed from your results entirely — regardless of its score — because it carries a HIGH-severity contraindication with kill_switch=true. This prevents recommending poses that could cause harm.',
  },
  {
    question: 'What health flags does Elbee support?',
    answer:
      'Elbee currently supports six health flags: knee_injury, pregnancy, high_blood_pressure, wrist_injury, lower_back_pain, and neck_injury. Each flag triggers kill-switch or severity-weighted filtering across the pose database. You can select multiple flags; all active kill-switches are applied before scoring.',
  },
  {
    question: 'How is an instructor trust score calculated?',
    answer:
      'The instructor trust score (0.0–1.0) combines four signals: certification weight (RYT-200 = 0.4, RYT-500 = 0.6, E-RYT-200 = 0.8, E-RYT-500 = 1.0), review weight (average rating ÷ 5 × 0.3), lineage depth weight (generations × 0.05, capped at 0.2), and social proof weight (log₁₀(Instagram followers) ÷ 7, capped at 0.1). The score is recalculated daily by a batch job.',
  },
  {
    question: 'What is E-E-A-T and why does it matter for yoga instruction?',
    answer:
      'E-E-A-T stands for Experience, Expertise, Authoritativeness, and Trustworthiness — Google\'s framework for evaluating content quality. For yoga instruction, this means verifiable teaching experience (class hours), recognised certifications (Yoga Alliance RYT / E-RYT), published lineage affiliation, and independently verifiable student reviews. Elbee encodes these signals in the instructor trust score and Schema.org markup.',
  },
  {
    question: 'What does FYT100 certification mean?',
    answer:
      'FYT100 refers to the 100-hour certification issued by Find Your Trainer (FYT), a professional yoga teacher credentialing programme. It is a structured curriculum covering anatomy, sequencing, and teaching methodology, and is recognised as an entry-level professional qualification. Elbee instructors hold FYT100, FYT200, or Yoga Alliance credentials.',
  },
  {
    question: 'How do I find a yoga studio near me using Elbee?',
    answer:
      'Use the Search tab and type your city name or a landmark. The search service queries an index of yoga studios with GPS coordinates across Seoul, Tokyo, Singapore, New York, and London. Results are ranked by relevance and proximity. The API endpoint GET /api/v1/studios?city=Seoul returns studios as structured JSON you can integrate into any app.',
  },
  {
    question: 'What yoga pose is best for lower back pain relief?',
    answer:
      'For lower back pain relief, Elbee\'s matching algorithm typically surfaces Child\'s Pose (Balasana), Cat-Cow Stretch (Marjaryasana-Bitilasana), Supine Twist (Supta Matsyendrasana), and Seated Forward Fold (Paschimottanasana). These poses carry high benefit weights for the "back", "relief", and "release" tags. Always consult a qualified instructor before starting a new practice if you have a diagnosed condition.',
  },
  {
    question: 'What is the difference between AEO and GEO in yoga search?',
    answer:
      'AEO (Answer Engine Optimization) targets AI assistants and voice search engines that extract direct answers from structured content. GEO (Generative Engine Optimization) targets large language model-powered search engines (Perplexity, SearchGPT, Gemini) that synthesise answers from cited sources. Elbee uses Schema.org JSON-LD (FAQPage, HowTo, Course, DefinedTerm types) and high E-E-A-T content signals to rank well in both.',
  },
  {
    question: 'Can I access the Elbee yoga matching API directly?',
    answer:
      'Yes. The matching endpoint is POST /api/v1/match. Send a JSON body with healthFlags (array of condition strings), goals (array of goal strings such as Spinal_Mobility or Core_Strength), and topK (maximum number of results, default 10). The response includes each pose\'s name, difficulty rank (1–5), match score, and a plain-language description suitable for display in any client.',
  },
]

/**
 * Build a Schema.org FAQPage JSON-LD object from the FAQ_ITEMS array.
 * @returns {object} JSON-LD object (not stringified)
 */
export function buildFaqPageSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: FAQ_ITEMS.map(({ question, answer }) => ({
      '@type': 'Question',
      name: question,
      acceptedAnswer: {
        '@type': 'Answer',
        text: answer,
      },
    })),
  }
}

/**
 * Build a Schema.org WebSite JSON-LD object for sitelinks searchbox.
 * @returns {object} JSON-LD object (not stringified)
 */
export function buildWebSiteSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'WebSite',
    name: 'Elbee Yoga Guide',
    url: 'https://yogaman.club',
    description:
      'AI-powered yoga pose matching, instructor trust scoring, and studio discovery. Built on E-E-A-T principles for Perplexity, SearchGPT, and Gemini visibility.',
    potentialAction: {
      '@type': 'SearchAction',
      target: {
        '@type': 'EntryPoint',
        urlTemplate: 'https://yogaman.club/?q={search_term_string}',
      },
      'query-input': 'required name=search_term_string',
    },
  }
}
