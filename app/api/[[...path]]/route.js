import { MongoClient } from 'mongodb'
import { v4 as uuidv4 } from 'uuid'
import { NextResponse } from 'next/server'
import { PANELS, DIMENSIONS, DIM_KEYS, getPanel, initialBeliefs } from '@/lib/personas'

// ---------- Mongo ----------
let client
let db
async function connectToMongo() {
  if (!client) {
    client = new MongoClient(process.env.MONGO_URL)
    await client.connect()
    db = client.db(process.env.DB_NAME)
  }
  return db
}

function cors(response) {
  response.headers.set('Access-Control-Allow-Origin', process.env.CORS_ORIGINS || '*')
  response.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
  response.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization')
  return response
}
function json(data, status = 200) { return cors(NextResponse.json(data, { status })) }
export async function OPTIONS() { return cors(new NextResponse(null, { status: 200 })) }

// ---------- LLM ----------
async function callLLM(messages, { maxTokens = 2200, temperature = 0.7 } = {}) {
  const base = process.env.INTEGRATION_PROXY_URL || 'https://integrations.emergentagent.com'
  const res = await fetch(base + '/llm/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.EMERGENT_LLM_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: process.env.LLM_MODEL || 'claude-sonnet-4-5-20250929',
      messages,
      max_tokens: maxTokens,
      temperature,
    }),
  })
  if (!res.ok) {
    const t = await res.text().catch(() => '')
    throw new Error(`LLM ${res.status}: ${t.slice(0, 200)}`)
  }
  const data = await res.json()
  return data?.choices?.[0]?.message?.content || ''
}

function extractJSON(text) {
  if (!text) return null
  let t = text.trim()
  // strip markdown fences if present
  const fence = t.match(/```(?:json)?\s*([\s\S]*?)```/)
  if (fence) t = fence[1].trim()
  const start = t.indexOf('{')
  const end = t.lastIndexOf('}')
  if (start < 0 || end <= start) return null
  const slice = t.slice(start, end + 1)
  try { return JSON.parse(slice) } catch (e) { return null }
}

async function callLLMJson(messages, opts) {
  // one attempt + one stricter retry
  let raw = await callLLM(messages, opts)
  let parsed = extractJSON(raw)
  if (parsed) return parsed
  const retryMessages = [
    ...messages,
    { role: 'assistant', content: raw.slice(0, 1000) },
    { role: 'user', content: 'That was not valid JSON. Respond again with ONLY a single valid minified JSON object and nothing else. No markdown, no prose.' },
  ]
  raw = await callLLM(retryMessages, { ...(opts || {}), temperature: 0.2 })
  parsed = extractJSON(raw)
  return parsed
}

// ---------- Prompt builders ----------
const DIM_LINE = DIMENSIONS.map((d) => `${d.key} (${d.label})`).join(', ')

function personaBlock(panel) {
  return panel.personas.map((p) => (
    `- id="${p.id}" | ${p.name}, ${p.role}\n` +
    `  lens: primary=${p.primary_lens}, secondary=${p.secondary_lens} (${p.lens_desc})\n` +
    `  style: directness ${p.style.directness}/10, aggressiveness ${p.style.aggressiveness}/10, numbers_focus ${p.style.numbers_focus}/10\n` +
    `  distrusts: ${p.distrusts}\n` +
    `  question_priorities: ${p.question_priorities.join(' > ')}`
  )).join('\n')
}

function startupMemory(s) {
  const f = (k, v) => (v ? `  ${k}: ${v}\n` : '')
  return (
    f('Name', s.name) + f('Founder', s.founder) + f('Industry', s.industry) + f('Stage', s.stage) +
    f('One-liner', s.one_liner) + f('Problem', s.problem) + f('Customer', s.customer) +
    f('Solution', s.solution) + f('Business model', s.business_model) + f('Pricing', s.pricing) +
    f('Revenue', s.revenue) + f('Customers', s.customers) + f('CAC', s.cac) + f('Retention', s.retention) +
    f('Market size', s.market_size) + f('Competitors', s.competitors) + f('Differentiation', s.differentiation) +
    f('Moat', s.moat) + f('GTM', s.gtm) + f('Traction', s.traction) + f('Fundraising', s.fundraising_status) +
    f('Evidence', s.evidence)
  ) || '  (no structured data provided)\n'
}

function turnSystemPrompt(panel) {
  return `You are the simulation engine for EchoClash, a ruthless adversarial startup-pitch simulator. You control an AI investment panel of exactly 3 distinct personas evaluating a founder's LIVE pitch. You behave like a top-tier investment committee: sharp, specific, numerically rigorous, never flattering. You catch vague claims and numerical inconsistencies instantly.

ACTIVE PANEL: ${panel.name} (${panel.tagline}).
PERSONAS (honor each persona's lens, style and distrusts precisely; different personas ask different questions):
${personaBlock(panel)}

BELIEF DIMENSIONS (each scored 0-10 per persona): ${DIM_LINE}.

YOUR JOB each time the founder speaks:
1. CLAIM EXTRACTION: pull out factual/numeric claims from the founder's latest message. Category is one of: Problem, Customer, Market, Competition, Product, Differentiation, Moat, Traction, Business Model, Unit Economics, GTM, Scalability, Feasibility, Team, Evidence, Novelty.
2. CONTRADICTION DETECTION: compare each new claim against ALL prior claims, INCLUDING derived math. Examples: total_spend / customers = CAC; revenue / customers = ARPU; if numbers conflict, flag it. severity is HIGH, MEDIUM or LOW. Be precise and quote the numbers.
3. BELIEF UPDATE: adjust scores for the personas whose lens is affected, with a concrete one-line reason. Contradictions, hand-waving and unsupported big claims LOWER scores; specific credible evidence RAISES them. Only include dimensions that actually changed. Keep changes realistic (usually 1-3 points).
4. RESPOND AS ONE PERSONA: choose the single persona (by lens ownership + escalation + fairness) who should speak now. Write a short in-character reply (2-4 sentences) that reacts to what was just said and reference specific numbers where relevant, then ask ONE hard follow-up question. Stay in character (use their directness/aggressiveness).
5. DECISION STATE: one of listening, probing, skeptical, warming, convinced, unconvinced.

QUESTIONING DISCIPLINE (STRICT — the responding persona MUST obey all of these):
- Listen to the founder's ENTIRE pitch/answer and understand what they are ACTUALLY building before asking anything.
- Base every question on something the founder specifically SAID, claimed, or left unclear. Never ask generic, templated VC questions unrelated to this pitch.
- Ask yourself before writing the question: "Does this question make sense specifically because of what this founder just said?" If not, discard it.
- Adapt the question to the RESPONDING persona's own background, lens, industry expertise and what THEY would realistically need to know before investing. Different personas ask different things.
- Follow the conversation naturally. Use the founder's previous answers to form relevant follow-ups. Do NOT repeat a question the founder already answered.
- If the founder mentioned a specific product, technology, market, customer, metric or strategy, explore THAT before moving on. If the founder is strong in a topic, go deeper rather than asking basic questions.
- Challenge important claims, numbers, assumptions and inconsistencies. If something important is missing, ask about it naturally.
- Ask exactly ONE clear, focused question at a time. Never invent facts about the founder, startup, market or customers.
- Prioritize product, traction, market, competition, business model, scalability, moat and founder-market-fit.

Money is in INR (\u20b9). Return ONLY one valid minified JSON object, no markdown, exactly this shape:
{"claims_extracted":[{"text":"","category":"","numeric_value":null,"unit":"","confidence":"high|medium|low","evidence_status":"SUPPORTED|PARTIALLY_SUPPORTED|UNSUPPORTED|CONTRADICTED|UNKNOWN"}],"contradictions_detected":[{"new_claim":"","prior_claim":"","conflict_type":"","severity":"HIGH|MEDIUM|LOW","affected_dimensions":[""],"explanation":""}],"belief_updates":[{"persona_id":"","dimension":"","previous":5,"new":4,"reason":""}],"responding_persona":"","response":"","question":{"text":"","reason":"","target_dimension":"","escalation_level":"ask|challenge|cross_reference|consequence|decision"},"decision_state":{"state":"","reason":""}}
Use only the persona ids and dimension keys given above.`
}

function buildTurnUser(session, startup, founderMessage, kind) {
  const priorClaims = (session.claims || []).map((c) => `- [${c.category}] ${c.text}${c.numeric_value != null ? ` (=${c.numeric_value}${c.unit || ''})` : ''} [${c.evidence_status}]`).join('\n') || '  (none yet)'
  const beliefs = Object.entries(session.beliefs || {}).map(([pid, dims]) => {
    return `  ${pid}: ` + DIM_KEYS.map((k) => `${k}=${dims[k]}`).join(' ')
  }).join('\n')
  const contradictions = (session.contradictions || []).map((c) => `- ${c.explanation || c.conflict_type} [${c.severity}]`).join('\n') || '  (none yet)'
  const askedQuestions = (session.transcript || []).filter((m) => m.role === 'persona' && m.question?.text).map((m) => `- ${m.question.text}`).join('\n') || '  (none yet)'
  const transcript = (session.transcript || []).slice(-12).map((m) => {
    if (m.role === 'founder') return `FOUNDER: ${m.content}`
    return `${m.personaName} (${m.personaRole}): ${m.content}${m.question?.text ? ' Q: ' + m.question.text : ''}`
  }).join('\n') || '  (pitch just started)'

  const kindLine = kind === 'pitch'
    ? `THIS MESSAGE IS THE FOUNDER'S COMPLETE OPENING PITCH — they have finished pitching uninterrupted. Do not summarize it back. Extract claims, then have the single most relevant persona ask their FIRST, most important question, grounded strictly in what the founder actually pitched.`
    : `THIS MESSAGE IS THE FOUNDER'S ANSWER to the panel's last question. Ask ONE focused follow-up that builds on this answer and the pitch. Do NOT repeat any question already asked (see QUESTIONS ALREADY ASKED below).`

  return `STARTUP MEMORY:\n${startupMemory(startup)}\nPRIOR CLAIMS:\n${priorClaims}\n\nOPEN CONTRADICTIONS:\n${contradictions}\n\nQUESTIONS ALREADY ASKED (never repeat these):\n${askedQuestions}\n\nCURRENT BELIEF SCORES (persona: dim=score):\n${beliefs}\n\nCONVERSATION SO FAR:\n${transcript}\n\n${kindLine}\n\nFOUNDER JUST SAID:\n"""${founderMessage}"""\n\nProcess this turn now. Return the JSON object.`
}

function deliberationSystem(panel) {
  return `You are the deliberation engine for EchoClash. The pitch to the ${panel.name} has ended. Three personas now deliberate and produce a final verdict and a founder debrief. Be brutally honest and specific \u2014 this is meant to help the founder find exactly where the startup breaks.

PERSONAS:\n${personaBlock(panel)}\n\nBELIEF DIMENSIONS: ${DIM_LINE}.\n\nProduce: consensus, disagreements between personas (and why), investment conditions, the strongest and weakest dimension, critical unresolved questions, a weighted final_score 0-100, a confidence 0-100, and a verdict which is EXACTLY one of: "Strong Interest", "Interest", "Conditional Interest", "Needs More Evidence", "Pass".\nAlso produce GAPS the founder must fix, each with severity P0 (critical, blocks investment), P1 (important) or P2 (notable), classified by category, with transcript_evidence, why_it_matters, recommended_action and required_evidence.\nAlso produce a SCORECARD: for each of the 10 dimensions give a 0-10 score (aggregate across the panel), and a one-line reason.\n\nMoney is INR (\u20b9). Return ONLY one valid minified JSON object, no markdown, exactly this shape:\n{"final_score":0,"confidence":0,"verdict":"","consensus":[""],"disagreements":[{"topic":"","positions":""}],"investment_conditions":[""],"strongest_dimension":"","weakest_dimension":"","unresolved_questions":[""],"gaps":[{"category":"","severity":"P0|P1|P2","panel_source":"","transcript_evidence":"","why_it_matters":"","recommended_action":"","required_evidence":""}],"scorecard":[{"dimension":"","score":0,"reason":""}]}\nUse only the dimension keys given above in scorecard.`
}

function buildDeliberationUser(session, startup) {
  const claims = (session.claims || []).map((c) => `- [${c.category}] ${c.text}${c.numeric_value != null ? ` (=${c.numeric_value}${c.unit || ''})` : ''} [${c.evidence_status}]`).join('\n') || '  (none)'
  const contradictions = (session.contradictions || []).map((c) => `- ${c.explanation || c.conflict_type} [${c.severity}] affects ${(c.affected_dimensions || []).join(',')}`).join('\n') || '  (none)'
  const beliefs = Object.entries(session.beliefs || {}).map(([pid, dims]) => `  ${pid}: ` + DIM_KEYS.map((k) => `${k}=${dims[k]}`).join(' ')).join('\n')
  const transcript = (session.transcript || []).map((m) => m.role === 'founder' ? `FOUNDER: ${m.content}` : `${m.personaName}: ${m.content}${m.question?.text ? ' Q: ' + m.question.text : ''}`).join('\n')
  return `STARTUP:\n${startupMemory(startup)}\nCLAIMS:\n${claims}\n\nCONTRADICTIONS:\n${contradictions}\n\nFINAL BELIEF SCORES:\n${beliefs}\n\nFULL TRANSCRIPT:\n${transcript}\n\nDeliberate and return the JSON verdict + gaps + scorecard now.`
}

// ---------- Route ----------
async function handleRoute(request, { params }) {
  const { path = [] } = await params
  const route = `/${path.join('/')}`
  const method = request.method

  try {
    const db = await connectToMongo()

    // health
    if (route === '/' || route === '/root') return json({ message: 'EchoClash API' })

    // ---- DEEPGRAM: browser STT auth. Prefer a short-lived scoped token (secure).
    //      Falls back to the raw key via the browser 'token' subprotocol if the key
    //      lacks permission to mint tokens (prototype only). ----
    if (route === '/deepgram/token' && method === 'GET') {
      if (!process.env.DEEPGRAM_API_KEY) return json({ error: 'deepgram_not_configured' }, 500)
      try {
        const dg = await fetch('https://api.deepgram.com/v1/auth/grant', {
          method: 'POST',
          headers: { Authorization: `Token ${process.env.DEEPGRAM_API_KEY}`, 'Content-Type': 'application/json' },
          body: JSON.stringify({ ttl_seconds: 60 }),
          cache: 'no-store',
        })
        const b = await dg.json().catch(() => ({}))
        if (dg.ok && b.access_token) return json({ token: b.access_token, expiresIn: b.expires_in, mode: 'bearer' })
      } catch (e) { /* fall through to raw-key fallback */ }
      return json({ key: process.env.DEEPGRAM_API_KEY, mode: 'token' })
    }

    // ---- DEEPGRAM: TTS (Aura-2 high quality voices) ----
    if (route === '/deepgram/tts' && method === 'POST') {
      if (!process.env.DEEPGRAM_API_KEY) return json({ error: 'deepgram_not_configured' }, 500)
      const body = await request.json().catch(() => ({}))
      const text = String(body?.text || '').trim()
      const ALLOWED = new Set(['aura-2-thalia-en', 'aura-2-orpheus-en', 'aura-2-helios-en', 'aura-2-andromeda-en', 'aura-2-arcas-en', 'aura-2-aurora-en'])
      const model = ALLOWED.has(body?.model) ? body.model : 'aura-2-thalia-en'
      if (!text) return json({ error: 'text required' }, 400)
      const clipped = text.slice(0, 1800)
      const dg = await fetch(`https://api.deepgram.com/v1/speak?model=${encodeURIComponent(model)}&encoding=mp3`, {
        method: 'POST',
        headers: { Authorization: `Token ${process.env.DEEPGRAM_API_KEY}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: clipped }),
      })
      if (!dg.ok) { const t = await dg.text().catch(() => ''); return json({ error: 'deepgram_tts_failed', detail: t.slice(0, 200) }, dg.status) }
      const buf = await dg.arrayBuffer()
      const res = new NextResponse(buf, { status: 200 })
      res.headers.set('Content-Type', dg.headers.get('content-type') || 'audio/mpeg')
      res.headers.set('Cache-Control', 'no-store')
      res.headers.set('Access-Control-Allow-Origin', process.env.CORS_ORIGINS || '*')
      return res
    }

    // ---- AUTH (dev bypass) ----
    if (route === '/auth/login' && method === 'POST') {
      const body = await request.json()
      const { email, password } = body || {}
      if (email !== 'test@example.com' || password !== 'password123') {
        return json({ error: 'Invalid credentials' }, 401)
      }
      let user = await db.collection('users').findOne({ email })
      if (!user) {
        user = { id: uuidv4(), email, name: 'Founder', created_at: new Date() }
        await db.collection('users').insertOne(user)
      }
      return json({ id: user.id, email: user.email, name: user.name })
    }

    // ---- PANELS ----
    if (route === '/panels' && method === 'GET') {
      const publicPanels = PANELS.map((p) => ({
        id: p.id, name: p.name, tagline: p.tagline, description: p.description,
        focus: p.focus, difficulty: p.difficulty, dimensions: p.dimensions,
        personas: p.personas.map((pe) => ({
          id: pe.id, name: pe.name, role: pe.role, avatar_url: pe.avatar_url,
          primary_lens: pe.primary_lens, lens_desc: pe.lens_desc, distrusts: pe.distrusts,
        })),
      }))
      return json({ panels: publicPanels, dimensions: DIMENSIONS })
    }

    // ---- STARTUPS ----
    if (route === '/startups' && method === 'POST') {
      const body = await request.json()
      if (!body.user_id || !body.name) return json({ error: 'user_id and name required' }, 400)
      const startup = {
        id: uuidv4(), user_id: body.user_id,
        name: body.name, founder: body.founder || '', industry: body.industry || '',
        stage: body.stage || '', one_liner: body.one_liner || '', problem: body.problem || '',
        customer: body.customer || '', solution: body.solution || '', business_model: body.business_model || '',
        pricing: body.pricing || '', revenue: body.revenue || '', customers: body.customers || '',
        cac: body.cac || '', retention: body.retention || '', market_size: body.market_size || '',
        competitors: body.competitors || '', differentiation: body.differentiation || '', moat: body.moat || '',
        gtm: body.gtm || '', traction: body.traction || '', fundraising_status: body.fundraising_status || '',
        evidence: body.evidence || '', created_at: new Date(), updated_at: new Date(),
      }
      await db.collection('startups').insertOne(startup)
      const { _id, ...clean } = startup
      return json(clean)
    }

    if (route === '/startups' && method === 'GET') {
      const url = new URL(request.url)
      const userId = url.searchParams.get('user_id')
      const q = userId ? { user_id: userId } : {}
      const rows = await db.collection('startups').find(q).sort({ created_at: -1 }).limit(100).toArray()
      return json(rows.map(({ _id, ...r }) => r))
    }

    // /startups/:id
    if (path[0] === 'startups' && path[1] && method === 'GET') {
      const s = await db.collection('startups').findOne({ id: path[1] })
      if (!s) return json({ error: 'not found' }, 404)
      const { _id, ...clean } = s
      return json(clean)
    }

    // ---- SESSIONS ----
    if (route === '/sessions' && method === 'POST') {
      const body = await request.json()
      const { user_id, startup_id, panel_id } = body || {}
      if (!startup_id || !panel_id) return json({ error: 'startup_id and panel_id required' }, 400)
      const panel = getPanel(panel_id)
      if (!panel) return json({ error: 'invalid panel' }, 400)
      const startup = await db.collection('startups').findOne({ id: startup_id })
      if (!startup) return json({ error: 'startup not found' }, 404)
      const priorCount = await db.collection('sessions').countDocuments({ startup_id })
      const session = {
        id: uuidv4(), user_id: user_id || null, startup_id, panel_id,
        panel_name: panel.name, status: 'active', mode: 'live', round_number: priorCount + 1,
        transcript: [], claims: [], contradictions: [], beliefs: initialBeliefs(panel),
        belief_history: [], verdict: null, gaps: [], scorecard: [],
        started_at: new Date(), ended_at: null,
      }
      await db.collection('sessions').insertOne(session)
      const { _id, ...clean } = session
      return json(clean)
    }

    if (path[0] === 'sessions' && path[1] && method === 'GET') {
      const s = await db.collection('sessions').findOne({ id: path[1] })
      if (!s) return json({ error: 'not found' }, 404)
      const startup = await db.collection('startups').findOne({ id: s.startup_id })
      const panel = getPanel(s.panel_id)
      const { _id, ...clean } = s
      return json({ ...clean, startup: startup ? (({ _id, ...r }) => r)(startup) : null, panel_personas: panel ? panel.personas : [] })
    }

    if (path[0] === 'sessions' && path[1] === undefined && method === 'GET') {
      const url = new URL(request.url)
      const startupId = url.searchParams.get('startup_id')
      const q = startupId ? { startup_id: startupId } : {}
      const rows = await db.collection('sessions').find(q).sort({ started_at: -1 }).limit(50).toArray()
      return json(rows.map(({ _id, transcript, ...r }) => ({ ...r, turns: (transcript || []).length })))
    }

    // ---- PITCH TURN (core) ----
    if (route === '/pitch/turn' && method === 'POST') {
      const body = await request.json()
      const { session_id, message, kind } = body || {}
      if (!session_id || !message) return json({ error: 'session_id and message required' }, 400)
      const session = await db.collection('sessions').findOne({ id: session_id })
      if (!session) return json({ error: 'session not found' }, 404)
      const startup = await db.collection('startups').findOne({ id: session.startup_id })
      const panel = getPanel(session.panel_id)
      if (!panel) return json({ error: 'invalid panel' }, 400)

      const messages = [
        { role: 'system', content: turnSystemPrompt(panel) },
        { role: 'user', content: buildTurnUser(session, startup, message, kind) },
      ]

      let result
      try {
        result = await callLLMJson(messages)
      } catch (e) {
        return json({ error: 'ai_unavailable', detail: String(e.message || e) }, 502)
      }
      if (!result || !result.response) {
        return json({ error: 'ai_bad_response' }, 502)
      }

      // resolve responding persona
      let persona = panel.personas.find((p) => p.id === result.responding_persona) || panel.personas[0]

      const now = new Date()
      // founder message
      const founderMsg = { id: uuidv4(), role: 'founder', content: message, ts: now }

      // apply belief updates
      const beliefs = session.beliefs || initialBeliefs(panel)
      const beliefChanges = []
      for (const u of (result.belief_updates || [])) {
        if (!u || !u.persona_id || !u.dimension) continue
        if (!beliefs[u.persona_id]) continue
        if (!DIM_KEYS.includes(u.dimension)) continue
        const prev = beliefs[u.persona_id][u.dimension]
        let nv = Number(u.new)
        if (isNaN(nv)) continue
        nv = Math.max(0, Math.min(10, Math.round(nv)))
        beliefs[u.persona_id][u.dimension] = nv
        beliefChanges.push({ persona_id: u.persona_id, dimension: u.dimension, previous: prev, new: nv, reason: u.reason || '' })
      }

      // claims
      const newClaims = (result.claims_extracted || []).map((c) => ({
        id: uuidv4(), startup_id: session.startup_id, session_id,
        text: c.text || '', category: c.category || 'Evidence',
        numeric_value: (c.numeric_value === '' || c.numeric_value === undefined) ? null : c.numeric_value,
        unit: c.unit || '', confidence: c.confidence || 'medium',
        evidence_status: c.evidence_status || 'UNKNOWN', created_at: now,
      }))

      // contradictions
      const newContradictions = (result.contradictions_detected || []).map((c) => ({
        id: uuidv4(), session_id,
        new_claim: c.new_claim || '', prior_claim: c.prior_claim || '',
        conflict_type: c.conflict_type || '', severity: c.severity || 'MEDIUM',
        affected_dimensions: c.affected_dimensions || [], explanation: c.explanation || '',
        resolution_status: 'OPEN', created_at: now,
      }))

      const personaMsg = {
        id: uuidv4(), role: 'persona',
        persona_id: persona.id, personaName: persona.name, personaRole: persona.role, avatar_url: persona.avatar_url,
        content: result.response, question: result.question || null,
        contradictions: newContradictions, beliefChanges,
        decision_state: result.decision_state || null, ts: now,
      }

      await db.collection('sessions').updateOne({ id: session_id }, {
        $push: { transcript: { $each: [founderMsg, personaMsg] }, claims: { $each: newClaims }, contradictions: { $each: newContradictions }, belief_history: { $each: beliefChanges.map((b) => ({ ...b, ts: now })) } },
        $set: { beliefs },
      })

      return json({
        persona_message: personaMsg,
        beliefs,
        belief_changes: beliefChanges,
        contradictions: newContradictions,
        claims: newClaims,
        decision_state: result.decision_state || null,
      })
    }

    // ---- END PITCH -> DELIBERATION ----
    if (route === '/pitch/end' && method === 'POST') {
      const body = await request.json()
      const { session_id } = body || {}
      if (!session_id) return json({ error: 'session_id required' }, 400)
      const session = await db.collection('sessions').findOne({ id: session_id })
      if (!session) return json({ error: 'session not found' }, 404)
      if (session.verdict) {
        const { _id, ...clean } = session
        return json({ verdict: session.verdict, gaps: session.gaps, scorecard: session.scorecard })
      }
      const startup = await db.collection('startups').findOne({ id: session.startup_id })
      const panel = getPanel(session.panel_id)

      const messages = [
        { role: 'system', content: deliberationSystem(panel) },
        { role: 'user', content: buildDeliberationUser(session, startup) },
      ]
      let result
      try {
        result = await callLLMJson(messages, { maxTokens: 2600 })
      } catch (e) {
        return json({ error: 'ai_unavailable', detail: String(e.message || e) }, 502)
      }
      if (!result || !result.verdict) return json({ error: 'ai_bad_response' }, 502)

      // previous score for delta
      const prevSession = await db.collection('sessions').find({ startup_id: session.startup_id, verdict: { $ne: null } }).sort({ ended_at: -1 }).limit(1).toArray()
      const previous_score = prevSession[0]?.verdict?.final_score ?? null

      const gaps = (result.gaps || []).map((g) => ({
        id: uuidv4(), session_id, startup_id: session.startup_id,
        category: g.category || '', severity: g.severity || 'P1', panel_source: g.panel_source || '',
        transcript_evidence: g.transcript_evidence || '', why_it_matters: g.why_it_matters || '',
        recommended_action: g.recommended_action || '', required_evidence: g.required_evidence || '',
        status: 'OPEN', created_at: new Date(),
      }))

      const verdict = {
        final_score: Math.round(Number(result.final_score) || 0),
        previous_score,
        confidence: Math.round(Number(result.confidence) || 0),
        verdict: result.verdict,
        consensus: result.consensus || [],
        disagreements: result.disagreements || [],
        investment_conditions: result.investment_conditions || [],
        strongest_dimension: result.strongest_dimension || '',
        weakest_dimension: result.weakest_dimension || '',
        unresolved_questions: result.unresolved_questions || [],
        created_at: new Date(),
      }
      const scorecard = (result.scorecard || []).map((s) => ({
        dimension: s.dimension, score: Number(s.score) || 0, reason: s.reason || '',
      }))

      await db.collection('sessions').updateOne({ id: session_id }, {
        $set: { verdict, gaps, scorecard, status: 'ended', ended_at: new Date() },
      })
      return json({ verdict, gaps, scorecard })
    }

    // ---- GAP status update ----
    if (route === '/gaps/update' && method === 'POST') {
      const body = await request.json()
      const { session_id, gap_id, status } = body || {}
      await db.collection('sessions').updateOne(
        { id: session_id, 'gaps.id': gap_id },
        { $set: { 'gaps.$.status': status || 'RESOLVED' } }
      )
      return json({ ok: true })
    }

    return json({ error: `Route ${route} not found` }, 404)
  } catch (error) {
    console.error('API Error:', error)
    return json({ error: 'Internal server error', detail: String(error?.message || error) }, 500)
  }
}

export const GET = handleRoute
export const POST = handleRoute
export const PUT = handleRoute
export const DELETE = handleRoute
export const PATCH = handleRoute
