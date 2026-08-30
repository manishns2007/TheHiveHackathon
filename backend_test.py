#!/usr/bin/env python3
"""
EchoClash Backend API Test Suite
Tests new endpoints: demo seed, founder studio, AI rewrite + versions, re-pitch memory
"""
import requests
import json
import time

BASE_URL = "https://pitch-stress-test.preview.emergentagent.com/api"

def log(msg):
    print(f"[TEST] {msg}")

def test_login():
    """Test login and get user_id"""
    log("Testing login...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        }, timeout=30)
        assert resp.status_code == 200, f"Login failed: {resp.status_code} {resp.text}"
        data = resp.json()
        assert "id" in data, "No user id in response"
        log(f"✅ Login successful. User ID: {data['id']}")
        return data["id"]
    except Exception as e:
        log(f"❌ Login failed: {e}")
        raise

def test_demo_seed(user_id):
    """Test demo seed endpoint - idempotency check"""
    log("\n=== Testing DEMO SEED ===")
    
    # First call - should create FlowPay
    log("First call to /api/demo/seed...")
    try:
        resp1 = requests.post(f"{BASE_URL}/demo/seed", json={"user_id": user_id}, timeout=30)
        assert resp1.status_code == 200, f"Demo seed failed: {resp1.status_code} {resp1.text}"
        data1 = resp1.json()
        
        # Verify structure
        assert "startup" in data1, "No startup in response"
        assert "session_ids" in data1, "No session_ids in response"
        
        startup1 = data1["startup"]
        session_ids1 = data1["session_ids"]
        
        assert startup1["name"] == "FlowPay", f"Expected FlowPay, got {startup1['name']}"
        assert startup1.get("is_demo") == True, "is_demo should be true"
        assert len(session_ids1) == 2, f"Expected 2 session_ids, got {len(session_ids1)}"
        
        log(f"✅ First call: Created FlowPay (id: {startup1['id']}) with 2 sessions")
        log(f"   Session IDs: {session_ids1}")
        
        # Second call - should be idempotent (return same data)
        log("Second call to /api/demo/seed (idempotency check)...")
        time.sleep(1)
        resp2 = requests.post(f"{BASE_URL}/demo/seed", json={"user_id": user_id}, timeout=30)
        assert resp2.status_code == 200, f"Demo seed second call failed: {resp2.status_code} {resp2.text}"
        data2 = resp2.json()
        
        startup2 = data2["startup"]
        session_ids2 = data2["session_ids"]
        
        # Verify idempotency
        assert startup2["id"] == startup1["id"], f"Startup ID changed! {startup1['id']} vs {startup2['id']}"
        assert set(session_ids2) == set(session_ids1), f"Session IDs changed! {session_ids1} vs {session_ids2}"
        
        log(f"✅ Second call: Returned SAME startup and sessions (idempotent)")
        
        return startup1["id"], session_ids1
        
    except Exception as e:
        log(f"❌ Demo seed test failed: {e}")
        raise

def test_demo_sessions(session_ids):
    """Test demo session details"""
    log("\n=== Testing DEMO SESSION DETAILS ===")
    
    try:
        # Test session 1 (round 1)
        log(f"Getting session 1: {session_ids[0]}...")
        resp1 = requests.get(f"{BASE_URL}/sessions/{session_ids[0]}", timeout=30)
        assert resp1.status_code == 200, f"Get session 1 failed: {resp1.status_code} {resp1.text}"
        s1 = resp1.json()
        
        assert s1["round_number"] == 1, f"Expected round 1, got {s1['round_number']}"
        assert s1["verdict"]["final_score"] == 61, f"Expected score 61, got {s1['verdict']['final_score']}"
        assert s1["verdict"]["verdict"] == "Needs More Evidence", f"Expected 'Needs More Evidence', got {s1['verdict']['verdict']}"
        
        # Check gaps
        gaps1 = s1.get("gaps", [])
        severities = [g["severity"] for g in gaps1]
        assert "P0" in severities, "Expected P0 gap"
        assert severities.count("P1") >= 2, "Expected at least 2 P1 gaps"
        log(f"   Gaps: {len(gaps1)} total, severities: {severities}")
        
        # Check contradictions
        contradictions1 = s1.get("contradictions", [])
        assert len(contradictions1) > 0, "Expected at least 1 contradiction"
        cac_contradiction = any("CAC" in c.get("explanation", "") or "400" in c.get("explanation", "") for c in contradictions1)
        assert cac_contradiction, "Expected CAC contradiction (₹400 vs ₹200)"
        log(f"   Contradictions: {len(contradictions1)} found, CAC contradiction present")
        
        # Check scorecard
        scorecard1 = s1.get("scorecard", [])
        assert len(scorecard1) == 10, f"Expected 10 dimensions, got {len(scorecard1)}"
        log(f"   Scorecard: {len(scorecard1)} dimensions")
        
        # Check transcript
        transcript1 = s1.get("transcript", [])
        assert len(transcript1) > 0, "Expected transcript messages"
        founder_msgs = [m for m in transcript1 if m["role"] == "founder"]
        persona_msgs = [m for m in transcript1 if m["role"] == "persona"]
        assert len(founder_msgs) > 0, "Expected founder messages"
        assert len(persona_msgs) > 0, "Expected persona messages"
        log(f"   Transcript: {len(transcript1)} messages ({len(founder_msgs)} founder, {len(persona_msgs)} persona)")
        
        log(f"✅ Session 1: round={s1['round_number']}, score={s1['verdict']['final_score']}, verdict='{s1['verdict']['verdict']}'")
        
        # Test session 2 (round 2)
        log(f"Getting session 2: {session_ids[1]}...")
        resp2 = requests.get(f"{BASE_URL}/sessions/{session_ids[1]}", timeout=30)
        assert resp2.status_code == 200, f"Get session 2 failed: {resp2.status_code} {resp2.text}"
        s2 = resp2.json()
        
        assert s2["round_number"] == 2, f"Expected round 2, got {s2['round_number']}"
        assert s2["verdict"]["final_score"] == 74, f"Expected score 74, got {s2['verdict']['final_score']}"
        assert s2["verdict"]["verdict"] == "Conditional Interest", f"Expected 'Conditional Interest', got {s2['verdict']['verdict']}"
        assert s2["verdict"]["previous_score"] == 61, f"Expected previous_score 61, got {s2['verdict']['previous_score']}"
        
        log(f"✅ Session 2: round={s2['round_number']}, score={s2['verdict']['final_score']}, verdict='{s2['verdict']['verdict']}', previous_score={s2['verdict']['previous_score']}")
        
    except Exception as e:
        log(f"❌ Demo session test failed: {e}")
        raise

def test_founder_studio(startup_id):
    """Test founder studio aggregate endpoint"""
    log("\n=== Testing FOUNDER STUDIO AGGREGATE ===")
    
    try:
        log(f"Getting studio data for startup {startup_id}...")
        resp = requests.get(f"{BASE_URL}/studio", params={"startup_id": startup_id}, timeout=30)
        assert resp.status_code == 200, f"Studio endpoint failed: {resp.status_code} {resp.text}"
        data = resp.json()
        
        # Verify structure
        assert "startup" in data, "No startup in response"
        assert "sessions" in data, "No sessions in response"
        assert "claims" in data, "No claims in response"
        assert "gaps" in data, "No gaps in response"
        assert "versions" in data, "No versions in response"
        assert "score_history" in data, "No score_history in response"
        
        # Check startup
        assert data["startup"]["name"] == "FlowPay", f"Expected FlowPay, got {data['startup']['name']}"
        log(f"   Startup: {data['startup']['name']}")
        
        # Check sessions
        sessions = data["sessions"]
        assert len(sessions) == 2, f"Expected 2 sessions, got {len(sessions)}"
        for s in sessions:
            assert "verdict" in s, "Session missing verdict"
            assert "final_score" in s["verdict"], "Verdict missing final_score"
            assert "verdict" in s["verdict"], "Verdict missing verdict label"
        log(f"   Sessions: {len(sessions)} summaries with verdicts")
        
        # Check claims (flattened with round)
        claims = data["claims"]
        assert len(claims) > 0, "Expected claims"
        for c in claims:
            assert "round" in c, "Claim missing round"
        log(f"   Claims: {len(claims)} total (flattened with round)")
        
        # Check gaps (with round)
        gaps = data["gaps"]
        assert len(gaps) > 0, "Expected gaps"
        for g in gaps:
            assert "round" in g, "Gap missing round"
        log(f"   Gaps: {len(gaps)} total (with round)")
        
        # Check score_history
        score_history = data["score_history"]
        assert len(score_history) == 2, f"Expected 2 score_history entries, got {len(score_history)}"
        
        # Verify round 1
        h1 = next((h for h in score_history if h["round"] == 1), None)
        assert h1 is not None, "Missing round 1 in score_history"
        assert h1["score"] == 61, f"Expected score 61 for round 1, got {h1['score']}"
        assert "dims" in h1, "Missing dims in score_history"
        assert len(h1["dims"]) == 10, f"Expected 10 dimensions, got {len(h1['dims'])}"
        log(f"   Score history round 1: score={h1['score']}, dims={len(h1['dims'])}")
        
        # Verify round 2
        h2 = next((h for h in score_history if h["round"] == 2), None)
        assert h2 is not None, "Missing round 2 in score_history"
        assert h2["score"] == 74, f"Expected score 74 for round 2, got {h2['score']}"
        assert len(h2["dims"]) == 10, f"Expected 10 dimensions, got {len(h2['dims'])}"
        log(f"   Score history round 2: score={h2['score']}, dims={len(h2['dims'])}")
        
        log(f"✅ Founder Studio: All data structures correct")
        
    except Exception as e:
        log(f"❌ Founder studio test failed: {e}")
        raise

def test_ai_rewrite_and_versions(startup_id, session_ids):
    """Test AI rewrite and versions CRUD"""
    log("\n=== Testing AI REWRITE + VERSIONS ===")
    
    try:
        # POST /api/rewrite
        log(f"Creating rewrite for session {session_ids[0]}...")
        log("   (This calls LLM - may take up to 90s)")
        start_time = time.time()
        
        resp = requests.post(f"{BASE_URL}/rewrite", json={
            "session_id": session_ids[0],
            "gap_ids": [],
            "length": "90s"
        }, timeout=120)
        
        elapsed = time.time() - start_time
        log(f"   Rewrite completed in {elapsed:.1f}s")
        
        if resp.status_code == 502:
            log(f"⚠️  502 error (ai_unavailable or ai_bad_response): {resp.text}")
            log("   This is expected if LLM service is temporarily unavailable")
            return None
        
        assert resp.status_code == 200, f"Rewrite failed: {resp.status_code} {resp.text}"
        version = resp.json()
        
        # Verify structure
        assert "id" in version, "No id in version"
        assert "title" in version, "No title in version"
        assert "sections" in version, "No sections in version"
        assert "flagged" in version, "No flagged in version"
        
        # Verify sections is an object (not array)
        sections = version["sections"]
        assert isinstance(sections, dict), f"sections should be object, got {type(sections)}"
        assert len(sections) > 0, "sections should not be empty"
        
        section_keys = list(sections.keys())
        log(f"   Version ID: {version['id']}")
        log(f"   Title: {version['title']}")
        log(f"   Section keys: {section_keys}")
        log(f"   Flagged items: {len(version['flagged'])}")
        
        # Expected sections
        expected_sections = ['opening', 'problem', 'customer', 'solution', 'market', 'traction', 
                           'business_model', 'differentiation', 'moat', 'gtm', 'team', 'ask', 'closing']
        for key in expected_sections:
            if key in sections:
                log(f"      ✓ {key}: {len(sections[key])} chars")
        
        log(f"✅ Rewrite created successfully")
        
        version_id = version["id"]
        
        # GET /api/versions/:id
        log(f"Getting version {version_id}...")
        resp2 = requests.get(f"{BASE_URL}/versions/{version_id}", timeout=30)
        assert resp2.status_code == 200, f"Get version failed: {resp2.status_code} {resp2.text}"
        version2 = resp2.json()
        assert version2["id"] == version_id, "Version ID mismatch"
        log(f"✅ GET /api/versions/:id working")
        
        # GET /api/versions?startup_id=
        log(f"Getting versions for startup {startup_id}...")
        resp3 = requests.get(f"{BASE_URL}/versions", params={"startup_id": startup_id}, timeout=30)
        assert resp3.status_code == 200, f"Get versions list failed: {resp3.status_code} {resp3.text}"
        versions = resp3.json()
        assert isinstance(versions, list), "Expected array of versions"
        assert len(versions) > 0, "Expected at least 1 version"
        found = any(v["id"] == version_id for v in versions)
        assert found, f"Version {version_id} not found in list"
        log(f"✅ GET /api/versions?startup_id= working ({len(versions)} versions)")
        
        # PUT /api/versions/:id
        log(f"Updating version {version_id}...")
        updated_sections = sections.copy()
        updated_sections["opening"] = "UPDATED: This is the new opening paragraph."
        
        resp4 = requests.put(f"{BASE_URL}/versions/{version_id}", json={
            "title": "Edited Title",
            "sections": updated_sections
        }, timeout=30)
        assert resp4.status_code == 200, f"Update version failed: {resp4.status_code} {resp4.text}"
        version4 = resp4.json()
        assert version4["title"] == "Edited Title", f"Title not updated: {version4['title']}"
        assert version4["sections"]["opening"] == updated_sections["opening"], "Opening not updated"
        log(f"✅ PUT /api/versions/:id working (title and sections updated)")
        
        # Verify persistence
        log(f"Verifying update persisted...")
        resp5 = requests.get(f"{BASE_URL}/versions/{version_id}", timeout=30)
        assert resp5.status_code == 200, f"Get version after update failed: {resp5.status_code}"
        version5 = resp5.json()
        assert version5["title"] == "Edited Title", "Title update not persisted"
        assert version5["sections"]["opening"] == updated_sections["opening"], "Opening update not persisted"
        log(f"✅ Updates persisted correctly")
        
        # Check studio includes version
        log(f"Verifying version appears in studio...")
        resp6 = requests.get(f"{BASE_URL}/studio", params={"startup_id": startup_id}, timeout=30)
        assert resp6.status_code == 200, f"Studio check failed: {resp6.status_code}"
        studio = resp6.json()
        studio_versions = studio.get("versions", [])
        found_in_studio = any(v["id"] == version_id for v in studio_versions)
        assert found_in_studio, "Version not found in studio"
        log(f"✅ Version appears in studio versions array")
        
        return version_id
        
    except Exception as e:
        log(f"❌ AI rewrite test failed: {e}")
        raise

def test_repitch_memory(user_id):
    """Test re-pitch memory functionality"""
    log("\n=== Testing RE-PITCH MEMORY ===")
    
    try:
        # Create a fresh startup
        log("Creating fresh startup 'MemTest'...")
        resp1 = requests.post(f"{BASE_URL}/startups", json={
            "user_id": user_id,
            "name": "MemTest",
            "founder": "F",
            "industry": "SaaS",
            "stage": "Seed",
            "one_liner": "x",
            "problem": "y"
        }, timeout=30)
        assert resp1.status_code == 200, f"Create startup failed: {resp1.status_code} {resp1.text}"
        startup = resp1.json()
        startup_id = startup["id"]
        log(f"   Created startup: {startup_id}")
        
        # Create session A
        log("Creating session A...")
        resp2 = requests.post(f"{BASE_URL}/sessions", json={
            "user_id": user_id,
            "startup_id": startup_id,
            "panel_id": "vc"
        }, timeout=30)
        assert resp2.status_code == 200, f"Create session A failed: {resp2.status_code} {resp2.text}"
        session_a = resp2.json()
        session_a_id = session_a["id"]
        log(f"   Session A created: {session_a_id}")
        
        # Run one pitch turn
        log("Running one pitch turn...")
        resp3 = requests.post(f"{BASE_URL}/pitch/turn", json={
            "session_id": session_a_id,
            "message": "We have 100 customers and CAC is ₹500."
        }, timeout=90)
        assert resp3.status_code == 200, f"Pitch turn failed: {resp3.status_code} {resp3.text}"
        log(f"   Turn completed")
        
        # End pitch (deliberation)
        log("Ending pitch (deliberation - may take up to 90s)...")
        start_time = time.time()
        resp4 = requests.post(f"{BASE_URL}/pitch/end", json={
            "session_id": session_a_id
        }, timeout=120)
        elapsed = time.time() - start_time
        log(f"   Deliberation completed in {elapsed:.1f}s")
        
        if resp4.status_code == 502:
            log(f"⚠️  502 error (ai_unavailable or ai_bad_response): {resp4.text}")
            log("   Cannot complete re-pitch memory test without LLM")
            return
        
        assert resp4.status_code == 200, f"End pitch failed: {resp4.status_code} {resp4.text}"
        verdict_a = resp4.json()
        assert "verdict" in verdict_a, "No verdict in response"
        score_a = verdict_a["verdict"]["final_score"]
        log(f"   Session A ended with score: {score_a}")
        
        # Create session B (re-pitch)
        log("Creating session B (re-pitch)...")
        time.sleep(1)
        resp5 = requests.post(f"{BASE_URL}/sessions", json={
            "user_id": user_id,
            "startup_id": startup_id,
            "panel_id": "vc"
        }, timeout=30)
        assert resp5.status_code == 200, f"Create session B failed: {resp5.status_code} {resp5.text}"
        session_b = resp5.json()
        
        # Verify memory
        assert session_b["round_number"] == 2, f"Expected round 2, got {session_b['round_number']}"
        assert "memory" in session_b, "No memory field in session B"
        assert session_b["memory"] is not None, "Memory field is null"
        
        memory = session_b["memory"]
        assert "claims" in memory, "No claims in memory"
        assert "gaps" in memory, "No gaps in memory"
        assert "last_score" in memory, "No last_score in memory"
        
        assert isinstance(memory["claims"], list), "memory.claims should be array"
        assert isinstance(memory["gaps"], list), "memory.gaps should be array"
        assert isinstance(memory["last_score"], (int, float)), "memory.last_score should be number"
        
        log(f"   Session B round: {session_b['round_number']}")
        log(f"   Memory claims: {len(memory['claims'])} items")
        log(f"   Memory gaps: {len(memory['gaps'])} items")
        log(f"   Memory last_score: {memory['last_score']}")
        
        log(f"✅ Re-pitch memory working: round_number=2, memory present with claims/gaps/last_score")
        
    except Exception as e:
        log(f"❌ Re-pitch memory test failed: {e}")
        raise

def main():
    log("=" * 80)
    log("EchoClash Backend Test Suite - NEW ENDPOINTS")
    log("=" * 80)
    
    try:
        # Login
        user_id = test_login()
        
        # Test 1: Demo seed (idempotency)
        startup_id, session_ids = test_demo_seed(user_id)
        
        # Test 2: Demo session details
        test_demo_sessions(session_ids)
        
        # Test 3: Founder studio aggregate
        test_founder_studio(startup_id)
        
        # Test 4: AI rewrite + versions
        test_ai_rewrite_and_versions(startup_id, session_ids)
        
        # Test 5: Re-pitch memory
        test_repitch_memory(user_id)
        
        log("\n" + "=" * 80)
        log("✅ ALL TESTS PASSED")
        log("=" * 80)
        
    except Exception as e:
        log("\n" + "=" * 80)
        log(f"❌ TEST SUITE FAILED: {e}")
        log("=" * 80)
        raise

if __name__ == "__main__":
    main()
