#!/usr/bin/env python3
"""
EchoClash Deepgram Endpoints Test Suite
Tests the two new Deepgram backend endpoints: token and TTS
"""
import requests
import json
import sys

# Base URL from .env
BASE_URL = "https://42b1e621-4ce6-4896-a47f-bd5b4d4a8fcd.preview.emergentagent.com/api"

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
# TEST 1: Deepgram Token Endpoint
# ============================================================
def test_deepgram_token():
    log("\nTEST 1: GET /api/deepgram/token")
    
    try:
        log("  Requesting Deepgram token...")
        resp = requests.get(f"{BASE_URL}/deepgram/token", timeout=10)
        
        # Check status code
        if resp.status_code != 200:
            log_error(f"Expected status 200, got {resp.status_code}: {resp.text}")
            return False
        
        # Check content type is JSON
        content_type = resp.headers.get('content-type', '')
        if 'application/json' not in content_type.lower():
            log_error(f"Expected JSON content-type, got: {content_type}")
            return False
        
        data = resp.json()
        log_json("Token Response", data)
        
        # Check response structure
        if 'mode' not in data:
            log_error(f"Response missing 'mode' field: {data}")
            return False
        
        mode = data['mode']
        
        # Check for either bearer token or fallback key
        if mode == 'bearer':
            # Should have token and expiresIn
            if 'token' not in data:
                log_error(f"Bearer mode requires 'token' field: {data}")
                return False
            if not data['token']:
                log_error(f"Bearer token is empty: {data}")
                return False
            if 'expiresIn' not in data:
                log_error(f"Bearer mode requires 'expiresIn' field: {data}")
                return False
            log_success(f"Token endpoint returned bearer token (expires in {data['expiresIn']}s)")
            
        elif mode == 'token':
            # Should have key (fallback mode)
            if 'key' not in data:
                log_error(f"Token mode requires 'key' field: {data}")
                return False
            if not data['key']:
                log_error(f"API key is empty: {data}")
                return False
            log_success(f"Token endpoint returned fallback key (mode: token)")
            log("  Note: This is expected when the API key lacks token-grant permission")
            
        else:
            log_error(f"Invalid mode '{mode}', expected 'bearer' or 'token'")
            return False
        
        return True
        
    except Exception as e:
        log_error(f"Token endpoint test failed: {e}")
        return False

# ============================================================
# TEST 2: Deepgram TTS - Valid Request
# ============================================================
def test_deepgram_tts_valid():
    log("\nTEST 2: POST /api/deepgram/tts (valid request)")
    
    tts_data = {
        "text": "Walk us through your unit economics.",
        "model": "aura-2-orpheus-en"
    }
    
    try:
        log(f"  Requesting TTS with text: '{tts_data['text']}'")
        log(f"  Model: {tts_data['model']}")
        
        resp = requests.post(f"{BASE_URL}/deepgram/tts", json=tts_data, timeout=15)
        
        # Check status code
        if resp.status_code != 200:
            log_error(f"Expected status 200, got {resp.status_code}: {resp.text}")
            return False
        
        # Check content type is audio
        content_type = resp.headers.get('content-type', '')
        if not content_type.startswith('audio/'):
            log_error(f"Expected Content-Type starting with 'audio/', got: {content_type}")
            return False
        
        # Check body is non-empty binary
        body = resp.content
        body_size = len(body)
        
        if body_size == 0:
            log_error("Response body is empty")
            return False
        
        # Check body is at least a few KB (reasonable for audio)
        if body_size < 1000:
            log_error(f"Response body too small ({body_size} bytes), expected at least 1KB for audio")
            return False
        
        log_success(f"TTS returned audio: {content_type}, {body_size} bytes")
        return True
        
    except Exception as e:
        log_error(f"TTS valid request test failed: {e}")
        return False

# ============================================================
# TEST 3: Deepgram TTS - Default Voice
# ============================================================
def test_deepgram_tts_default():
    log("\nTEST 3: POST /api/deepgram/tts (default voice)")
    
    tts_data = {
        "text": "Hello"
    }
    
    try:
        log(f"  Requesting TTS with text: '{tts_data['text']}' (no model specified)")
        
        resp = requests.post(f"{BASE_URL}/deepgram/tts", json=tts_data, timeout=15)
        
        # Check status code
        if resp.status_code != 200:
            log_error(f"Expected status 200, got {resp.status_code}: {resp.text}")
            return False
        
        # Check content type is audio
        content_type = resp.headers.get('content-type', '')
        if not content_type.startswith('audio/'):
            log_error(f"Expected Content-Type starting with 'audio/', got: {content_type}")
            return False
        
        # Check body is non-empty
        body_size = len(resp.content)
        if body_size == 0:
            log_error("Response body is empty")
            return False
        
        log_success(f"TTS with default voice returned audio: {content_type}, {body_size} bytes")
        log("  Note: Should default to aura-2-thalia-en")
        return True
        
    except Exception as e:
        log_error(f"TTS default voice test failed: {e}")
        return False

# ============================================================
# TEST 4: Deepgram TTS - Empty Text
# ============================================================
def test_deepgram_tts_empty():
    log("\nTEST 4: POST /api/deepgram/tts (empty text)")
    
    tts_data = {
        "text": ""
    }
    
    try:
        log("  Requesting TTS with empty text (should return 400)...")
        
        resp = requests.post(f"{BASE_URL}/deepgram/tts", json=tts_data, timeout=10)
        
        # Check status code is 400
        if resp.status_code != 400:
            log_error(f"Expected status 400 for empty text, got {resp.status_code}")
            return False
        
        # Check response is JSON with error
        content_type = resp.headers.get('content-type', '')
        if 'application/json' not in content_type.lower():
            log_error(f"Expected JSON error response, got content-type: {content_type}")
            return False
        
        data = resp.json()
        if 'error' not in data:
            log_error(f"Expected error field in response: {data}")
            return False
        
        log_success(f"Empty text correctly returned 400 with error: {data['error']}")
        return True
        
    except Exception as e:
        log_error(f"TTS empty text test failed: {e}")
        return False

# ============================================================
# TEST 5: Deepgram TTS - Invalid Model (should fallback)
# ============================================================
def test_deepgram_tts_invalid_model():
    log("\nTEST 5: POST /api/deepgram/tts (invalid model name)")
    
    tts_data = {
        "text": "Testing invalid model",
        "model": "invalid-model-xyz"
    }
    
    try:
        log(f"  Requesting TTS with invalid model: '{tts_data['model']}'")
        log("  Should fallback to default (aura-2-thalia-en) and return 200 audio")
        
        resp = requests.post(f"{BASE_URL}/deepgram/tts", json=tts_data, timeout=15)
        
        # Check status code is 200 (should fallback, not error)
        if resp.status_code != 200:
            log_error(f"Expected status 200 (fallback to default), got {resp.status_code}: {resp.text}")
            return False
        
        # Check content type is audio
        content_type = resp.headers.get('content-type', '')
        if not content_type.startswith('audio/'):
            log_error(f"Expected Content-Type starting with 'audio/', got: {content_type}")
            return False
        
        # Check body is non-empty
        body_size = len(resp.content)
        if body_size == 0:
            log_error("Response body is empty")
            return False
        
        log_success(f"Invalid model correctly fell back to default: {content_type}, {body_size} bytes")
        return True
        
    except Exception as e:
        log_error(f"TTS invalid model test failed: {e}")
        return False

# ============================================================
# Main Test Runner
# ============================================================
def main():
    print("=" * 60)
    print("EchoClash Deepgram Endpoints Test Suite")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print("=" * 60)
    
    tests = [
        ("Deepgram Token Endpoint", test_deepgram_token),
        ("Deepgram TTS - Valid Request", test_deepgram_tts_valid),
        ("Deepgram TTS - Default Voice", test_deepgram_tts_default),
        ("Deepgram TTS - Empty Text", test_deepgram_tts_empty),
        ("Deepgram TTS - Invalid Model", test_deepgram_tts_invalid_model),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
            if not result:
                log_error(f"\n{name} FAILED")
                # Continue with other tests even if one fails
        except Exception as e:
            log_error(f"\n{name} CRASHED: {e}")
            results.append((name, False))
    
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
