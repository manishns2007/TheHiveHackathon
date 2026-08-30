#!/usr/bin/env python3
"""
EchoClash Backend API Test Suite
Tests the complete happy-path flow including LLM-powered pitch turns and deliberation.
"""
import requests
import json
import time
import sys

# Base URL from .env
BASE_URL = "https://42b1e621-4ce6-4896-a47f-bd5b4d4a8fcd.preview.emergentagent.com/api"

# Test data
TEST_USER = {"email": "test@example.com", "password": "password123"}
WRONG_PASSWORD = {"email": "test@example.com", "password": "wrongpass"}

# Global state
user_id = None
startup_id = None
session_id = None

def log(msg):
    print(f"[TEST] {msg}")

def log_success(msg):
    print(f"✅ {msg}")

def log_error(msg):
    print(f"❌ {msg}")

def log_json(label, data):
    print(f"\n{label}:")
    print(json.dumps(data, indent=2))

# ============================================================
# TEST 1: Auth - Login
# ============================================================
def test_auth_login():
    global user_id
    log("TEST 1: POST /api/auth/login")
    
    # Test wrong password first
    try:
        log("  Testing wrong password...")
        resp = requests.post(f"{BASE_URL}/auth/login", json=WRONG_PASSWORD, timeout=10)
        if resp.status_code == 401:
            log_success("Wrong password correctly returns 401")
        else:
            log_error(f"Wrong password should return 401, got {resp.status_code}")
            return False
    except Exception as e:
        log_error(f"Wrong password test failed: {e}")
        return False
    
    # Test correct login
    try:
        log("  Testing correct login...")
        resp = requests.post(f"{BASE_URL}/auth/login", json=TEST_USER, timeout=10)
        if resp.status_code != 200:
            log_error(f"Login failed with status {resp.status_code}: {resp.text}")
            return False
        
        data = resp.json()
        if not all(k in data for k in ['id', 'email', 'name']):
            log_error(f"Login response missing required fields: {data}")
            return False
        
        user_id = data['id']
        log_success(f"Login successful, user_id: {user_id}")
        log_json("Login response", data)
        return True
    except Exception as e:
        log_error(f"Login test failed: {e}")
        return False

# ============================================================
# TEST 2: Panels - Get all panels
# ============================================================
def test_panels():
    log("\nTEST 2: GET /api/panels")
    
    try:
        resp = requests.get(f"{BASE_URL}/panels", timeout=10)
        if resp.status_code != 200:
            log_error(f"Panels request failed with status {resp.status_code}: {resp.text}")
            return False
        
        data = resp.json()
        
        # Check structure
        if 'panels' not in data or 'dimensions' not in data:
            log_error(f"Response missing 'panels' or 'dimensions': {data.keys()}")
            return False
        
        panels = data['panels']
        dimensions = data['dimensions']
        
        # Check exactly 3 panels
        if len(panels) != 3:
            log_error(f"Expected 3 panels, got {len(panels)}")
            return False
        
        # Check panel IDs
        panel_ids = [p['id'] for p in panels]
        expected_ids = ['shark', 'vc', 'operator']
        if not all(pid in panel_ids for pid in expected_ids):
            log_error(f"Expected panel IDs {expected_ids}, got {panel_ids}")
            return False
        
        # Count total personas (should be 9: 3 per panel)
        total_personas = sum(len(p['personas']) for p in panels)
        if total_personas != 9:
            log_error(f"Expected 9 total personas (3 per panel), got {total_personas}")
            return False
        
        # Check dimensions array (should be 10)
        if len(dimensions) != 10:
            log_error(f"Expected 10 dimensions, got {len(dimensions)}")
            return False
        
        log_success(f"Panels: 3 panels with 9 personas total, 10 dimensions")
        log(f"  Panel IDs: {panel_ids}")
        log(f"  Dimension keys: {[d['key'] for d in dimensions]}")
        return True
    except Exception as e:
        log_error(f"Panels test failed: {e}")
        return False

# ============================================================
# TEST 3: Startups - Create, List, Get
# ============================================================
def test_startups():
    global startup_id
    log("\nTEST 3: POST /api/startups, GET /api/startups, GET /api/startups/:id")
    
    startup_data = {
        "user_id": user_id,
        "name": "FlowPay",
        "founder": "Rajesh Kumar",
        "industry": "Fintech",
        "stage": "Seed",
        "one_liner": "UPI B2B payments for small merchants",
        "problem": "Merchants struggle with digital payments",
        "market_size": "Rs 4000 crore",
        "cac": "Rs 200",
        "customers": "50"
    }
    
    try:
        # Create startup
        log("  Creating startup...")
        resp = requests.post(f"{BASE_URL}/startups", json=startup_data, timeout=10)
        if resp.status_code != 200:
            log_error(f"Startup creation failed with status {resp.status_code}: {resp.text}")
            return False
        
        data = resp.json()
        if 'id' not in data:
            log_error(f"Startup response missing 'id': {data}")
            return False
        
        startup_id = data['id']
        log_success(f"Startup created with ID: {startup_id}")
        
        # List startups for user
        log("  Listing startups for user...")
        resp = requests.get(f"{BASE_URL}/startups?user_id={user_id}", timeout=10)
        if resp.status_code != 200:
            log_error(f"Startup list failed with status {resp.status_code}: {resp.text}")
            return False
        
        startups = resp.json()
        if not isinstance(startups, list):
            log_error(f"Expected list of startups, got {type(startups)}")
            return False
        
        # Check our startup is in the list
        found = any(s['id'] == startup_id for s in startups)
        if not found:
            log_error(f"Created startup {startup_id} not found in list")
            return False
        
        log_success(f"Startup found in list ({len(startups)} total)")
        
        # Get specific startup
        log("  Getting specific startup...")
        resp = requests.get(f"{BASE_URL}/startups/{startup_id}", timeout=10)
        if resp.status_code != 200:
            log_error(f"Startup get failed with status {resp.status_code}: {resp.text}")
            return False
        
        startup = resp.json()
        if startup['id'] != startup_id or startup['name'] != 'FlowPay':
            log_error(f"Startup data mismatch: {startup}")
            return False
        
        log_success(f"Startup retrieved: {startup['name']}")
        return True
    except Exception as e:
        log_error(f"Startups test failed: {e}")
        return False

# ============================================================
# TEST 4: Sessions - Create and Get
# ============================================================
def test_sessions():
    global session_id
    log("\nTEST 4: POST /api/sessions, GET /api/sessions/:id")
    
    session_data = {
        "user_id": user_id,
        "startup_id": startup_id,
        "panel_id": "vc"
    }
    
    try:
        # Create session
        log("  Creating session...")
        resp = requests.post(f"{BASE_URL}/sessions", json=session_data, timeout=10)
        if resp.status_code != 200:
            log_error(f"Session creation failed with status {resp.status_code}: {resp.text}")
            return False
        
        data = resp.json()
        
        # Check required fields
        required = ['id', 'round_number', 'beliefs']
        if not all(k in data for k in required):
            log_error(f"Session response missing required fields: {data.keys()}")
            return False
        
        session_id = data['id']
        
        # Check round_number is 1
        if data['round_number'] != 1:
            log_error(f"Expected round_number=1, got {data['round_number']}")
            return False
        
        # Check beliefs structure (3 personas, each with 10 dimensions = 5)
        beliefs = data['beliefs']
        if len(beliefs) != 3:
            log_error(f"Expected 3 personas in beliefs, got {len(beliefs)}")
            return False
        
        # Check each persona has 10 dimensions all set to 5
        for persona_id, dims in beliefs.items():
            if len(dims) != 10:
                log_error(f"Persona {persona_id} should have 10 dimensions, got {len(dims)}")
                return False
            if not all(v == 5 for v in dims.values()):
                log_error(f"Persona {persona_id} dimensions should all be 5: {dims}")
                return False
        
        log_success(f"Session created: ID={session_id}, round={data['round_number']}")
        log(f"  Beliefs: 3 personas, each with 10 dimensions=5")
        
        # Get session
        log("  Getting session...")
        resp = requests.get(f"{BASE_URL}/sessions/{session_id}", timeout=10)
        if resp.status_code != 200:
            log_error(f"Session get failed with status {resp.status_code}: {resp.text}")
            return False
        
        session = resp.json()
        
        # Check it includes startup and panel_personas
        if 'startup' not in session or 'panel_personas' not in session:
            log_error(f"Session missing startup or panel_personas: {session.keys()}")
            return False
        
        if len(session['panel_personas']) != 3:
            log_error(f"Expected 3 panel_personas, got {len(session['panel_personas'])}")
            return False
        
        log_success(f"Session retrieved with startup + 3 panel_personas")
        return True
    except Exception as e:
        log_error(f"Sessions test failed: {e}")
        return False

# ============================================================
# TEST 5: Pitch Turn - LLM Engine (CORE TEST)
# ============================================================
def test_pitch_turn():
    log("\nTEST 5: POST /api/pitch/turn (LLM-powered)")
    
    # Turn 1: Initial pitch with CAC claim
    turn1_data = {
        "session_id": session_id,
        "message": "We're FlowPay, a UPI-based B2B payments platform for small merchants in India. Our CAC is just Rs 200 and we already have 50 paying customers."
    }
    
    try:
        log("  Turn 1: Initial pitch with CAC Rs 200, 50 customers...")
        log("  (This may take 10-40 seconds, waiting up to 90s)")
        
        start = time.time()
        resp = requests.post(f"{BASE_URL}/pitch/turn", json=turn1_data, timeout=90)
        elapsed = time.time() - start
        
        if resp.status_code != 200:
            log_error(f"Turn 1 failed with status {resp.status_code}: {resp.text}")
            return False
        
        data = resp.json()
        log(f"  Turn 1 completed in {elapsed:.1f}s")
        
        # Check response structure
        required = ['persona_message', 'beliefs', 'belief_changes', 'contradictions', 'claims']
        if not all(k in data for k in required):
            log_error(f"Turn response missing required fields: {data.keys()}")
            return False
        
        persona_msg = data['persona_message']
        if not all(k in persona_msg for k in ['content', 'personaName', 'question']):
            log_error(f"persona_message missing required fields: {persona_msg.keys()}")
            return False
        
        log_success(f"Turn 1: Persona {persona_msg['personaName']} responded")
        log(f"  Response: {persona_msg['content'][:100]}...")
        log(f"  Claims extracted: {len(data['claims'])}")
        log(f"  Contradictions: {len(data['contradictions'])}")
        log(f"  Belief changes: {len(data['belief_changes'])}")
        
        log_json("Turn 1 Full Response", data)
        
    except Exception as e:
        log_error(f"Turn 1 failed: {e}")
        return False
    
    # Turn 2: Contradiction trigger - actual CAC is Rs 400
    turn2_data = {
        "session_id": session_id,
        "message": "To get those first 50 customers we spent about Rs 20,000 total on acquisition last quarter."
    }
    
    try:
        log("\n  Turn 2: Contradiction trigger (Rs 20,000 / 50 = Rs 400 actual CAC)...")
        log("  (Waiting up to 90s)")
        
        start = time.time()
        resp = requests.post(f"{BASE_URL}/pitch/turn", json=turn2_data, timeout=90)
        elapsed = time.time() - start
        
        if resp.status_code != 200:
            log_error(f"Turn 2 failed with status {resp.status_code}: {resp.text}")
            return False
        
        data = resp.json()
        log(f"  Turn 2 completed in {elapsed:.1f}s")
        
        contradictions = data['contradictions']
        belief_changes = data['belief_changes']
        
        log(f"  Contradictions detected: {len(contradictions)}")
        log(f"  Belief changes: {len(belief_changes)}")
        
        # Check if contradiction was detected
        contradiction_found = len(contradictions) > 0
        
        # Check if economics dimension dropped
        economics_dropped = False
        for change in belief_changes:
            if change['dimension'] == 'economics' and change['new'] < change['previous']:
                economics_dropped = True
                log(f"  Economics belief dropped: {change['previous']} -> {change['new']}")
                break
        
        if contradiction_found:
            log_success(f"CONTRADICTION DETECTED: {len(contradictions)} contradiction(s)")
            for c in contradictions:
                log(f"    - {c.get('explanation', c.get('conflict_type', 'N/A'))}")
                log(f"      Severity: {c.get('severity', 'N/A')}")
        elif economics_dropped:
            log_success("Economics belief dropped (contradiction may be implicit)")
        else:
            log_error("CRITICAL: No contradiction detected and no economics belief drop!")
            log_error("Expected: CAC Rs 200 vs Rs 20,000/50 = Rs 400 contradiction")
            log_json("Turn 2 Response (no contradiction)", data)
            return False
        
        log_json("Turn 2 Full Response", data)
        
        # Verify transcript persistence
        log("\n  Verifying transcript persistence...")
        resp = requests.get(f"{BASE_URL}/sessions/{session_id}", timeout=10)
        if resp.status_code != 200:
            log_error(f"Session get failed: {resp.status_code}")
            return False
        
        session = resp.json()
        transcript = session.get('transcript', [])
        claims = session.get('claims', [])
        
        log(f"  Transcript has {len(transcript)} messages")
        log(f"  Claims persisted: {len(claims)}")
        
        if len(transcript) < 4:  # 2 turns = 4 messages (founder + persona each)
            log_error(f"Expected at least 4 transcript messages, got {len(transcript)}")
            return False
        
        log_success("Transcript and claims persisted correctly")
        return True
        
    except Exception as e:
        log_error(f"Turn 2 failed: {e}")
        return False

# ============================================================
# TEST 6: End Pitch - Deliberation
# ============================================================
def test_pitch_end():
    log("\nTEST 6: POST /api/pitch/end (LLM deliberation)")
    
    end_data = {
        "session_id": session_id
    }
    
    try:
        log("  Ending pitch and triggering deliberation...")
        log("  (This may take 10-40 seconds, waiting up to 90s)")
        
        start = time.time()
        resp = requests.post(f"{BASE_URL}/pitch/end", json=end_data, timeout=90)
        elapsed = time.time() - start
        
        if resp.status_code != 200:
            log_error(f"End pitch failed with status {resp.status_code}: {resp.text}")
            return False
        
        data = resp.json()
        log(f"  Deliberation completed in {elapsed:.1f}s")
        
        # Check response structure
        if not all(k in data for k in ['verdict', 'gaps', 'scorecard']):
            log_error(f"End response missing required fields: {data.keys()}")
            return False
        
        verdict = data['verdict']
        gaps = data['gaps']
        scorecard = data['scorecard']
        
        # Check verdict structure
        required_verdict = ['final_score', 'verdict', 'confidence', 'strongest_dimension', 'weakest_dimension']
        if not all(k in verdict for k in required_verdict):
            log_error(f"Verdict missing required fields: {verdict.keys()}")
            return False
        
        # Check final_score is 0-100
        final_score = verdict['final_score']
        if not (0 <= final_score <= 100):
            log_error(f"final_score should be 0-100, got {final_score}")
            return False
        
        # Check verdict is one of the 5 valid labels
        valid_verdicts = ["Strong Interest", "Interest", "Conditional Interest", "Needs More Evidence", "Pass"]
        if verdict['verdict'] not in valid_verdicts:
            log_error(f"verdict should be one of {valid_verdicts}, got '{verdict['verdict']}'")
            return False
        
        log_success(f"Verdict: {verdict['verdict']} (score: {final_score}/100, confidence: {verdict['confidence']}%)")
        log(f"  Strongest: {verdict['strongest_dimension']}")
        log(f"  Weakest: {verdict['weakest_dimension']}")
        
        # Check gaps
        log(f"\n  Gaps: {len(gaps)}")
        severities = [g['severity'] for g in gaps]
        severity_counts = {s: severities.count(s) for s in ['P0', 'P1', 'P2']}
        log(f"  Severity breakdown: {severity_counts}")
        
        # Verify all gaps have valid severity
        for g in gaps:
            if g['severity'] not in ['P0', 'P1', 'P2']:
                log_error(f"Invalid gap severity: {g['severity']}")
                return False
        
        log_success(f"Gaps: {len(gaps)} total with valid P0/P1/P2 severities")
        
        # Check scorecard
        log(f"\n  Scorecard: {len(scorecard)} dimensions")
        if len(scorecard) < 8 or len(scorecard) > 12:
            log_error(f"Expected ~10 scorecard dimensions, got {len(scorecard)}")
            return False
        
        for item in scorecard:
            if not all(k in item for k in ['dimension', 'score', 'reason']):
                log_error(f"Scorecard item missing required fields: {item}")
                return False
        
        log_success(f"Scorecard: {len(scorecard)} dimensions with scores and reasons")
        
        log_json("Full Deliberation Response", data)
        
        # Verify session status changed to 'ended'
        log("\n  Verifying session status...")
        resp = requests.get(f"{BASE_URL}/sessions/{session_id}", timeout=10)
        if resp.status_code != 200:
            log_error(f"Session get failed: {resp.status_code}")
            return False
        
        session = resp.json()
        if session.get('status') != 'ended':
            log_error(f"Session status should be 'ended', got '{session.get('status')}'")
            return False
        
        log_success("Session status changed to 'ended'")
        return True
        
    except Exception as e:
        log_error(f"End pitch test failed: {e}")
        return False

# ============================================================
# TEST 7: Gap Update
# ============================================================
def test_gap_update():
    log("\nTEST 7: POST /api/gaps/update")
    
    try:
        # First get the session to find a gap ID
        resp = requests.get(f"{BASE_URL}/sessions/{session_id}", timeout=10)
        if resp.status_code != 200:
            log_error(f"Session get failed: {resp.status_code}")
            return False
        
        session = resp.json()
        gaps = session.get('gaps', [])
        
        if len(gaps) == 0:
            log("  No gaps to update (session has no gaps)")
            return True
        
        first_gap = gaps[0]
        gap_id = first_gap['id']
        
        log(f"  Updating gap {gap_id} to RESOLVED...")
        
        update_data = {
            "session_id": session_id,
            "gap_id": gap_id,
            "status": "RESOLVED"
        }
        
        resp = requests.post(f"{BASE_URL}/gaps/update", json=update_data, timeout=10)
        if resp.status_code != 200:
            log_error(f"Gap update failed with status {resp.status_code}: {resp.text}")
            return False
        
        data = resp.json()
        if not data.get('ok'):
            log_error(f"Gap update response not ok: {data}")
            return False
        
        log_success("Gap update successful")
        
        # Verify the gap status changed
        log("  Verifying gap status changed...")
        resp = requests.get(f"{BASE_URL}/sessions/{session_id}", timeout=10)
        if resp.status_code != 200:
            log_error(f"Session get failed: {resp.status_code}")
            return False
        
        session = resp.json()
        updated_gap = next((g for g in session['gaps'] if g['id'] == gap_id), None)
        
        if not updated_gap:
            log_error(f"Gap {gap_id} not found in session")
            return False
        
        if updated_gap['status'] != 'RESOLVED':
            log_error(f"Gap status should be RESOLVED, got {updated_gap['status']}")
            return False
        
        log_success(f"Gap status verified: {updated_gap['status']}")
        return True
        
    except Exception as e:
        log_error(f"Gap update test failed: {e}")
        return False

# ============================================================
# Main Test Runner
# ============================================================
def main():
    print("=" * 60)
    print("EchoClash Backend API Test Suite")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    tests = [
        ("Auth Login", test_auth_login),
        ("Panels", test_panels),
        ("Startups CRUD", test_startups),
        ("Sessions", test_sessions),
        ("Pitch Turn (LLM)", test_pitch_turn),
        ("End Pitch (LLM)", test_pitch_end),
        ("Gap Update", test_gap_update),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            if not result:
                log_error(f"\n{name} FAILED - stopping test suite")
                break
        except Exception as e:
            log_error(f"\n{name} CRASHED: {e}")
            results.append((name, False))
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print("=" * 60)
    print(f"TOTAL: {passed}/{total} tests passed")
    print("=" * 60)
    
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
