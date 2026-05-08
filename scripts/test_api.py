import httpx
import asyncio
import json
import os
from datetime import datetime

API_URL = "http://localhost:8000/api/v1/recommendations/"

TEST_CASES = [
    {
        "name": "Adventure Seeker",
        "payload": {
            "preferences": {"adventure": 0.9, "nature": 0.7},
            "constraints": ["budget: Mid-range"],
            "mood": "I want to climb mountains and feel the fresh air"
        }
    },
    {
        "name": "Relaxation in Luxury",
        "payload": {
            "preferences": {"relaxation": 1.0, "wellness": 0.8},
            "constraints": ["budget: Luxury"],
            "mood": "Total peace and quiet by the water with high-end service"
        }
    },
    {
        "name": "Urban Explorer",
        "payload": {
            "preferences": {"culture": 0.8, "foodie": 0.9, "shopping": 0.6},
            "constraints": ["budget: Mid-range"],
            "mood": "Give me a city that never sleeps with amazing street food"
        }
    },
    {
        "name": "Historical Deep Dive",
        "payload": {
            "preferences": {"history": 1.0, "architecture": 0.8},
            "constraints": ["budget: Budget"],
            "mood": "Ancient ruins and temples on a budget"
        }
    },
    {
        "name": "Tropical Beach Vibe",
        "payload": {
            "preferences": {"beach": 0.9, "surfing": 0.7},
            "constraints": ["climate: Tropical"],
            "mood": "Palm trees, white sand, and big waves"
        }
    },
    {
        "name": "Cold Weather Hermit",
        "payload": {
            "preferences": {"solitude": 0.8, "nature": 0.9},
            "constraints": ["climate: Polar"],
            "mood": "Somewhere freezing where I can see the northern lights"
        }
    },
    {
        "name": "Nightlife Fanatic",
        "payload": {
            "preferences": {"nightlife": 1.0, "music": 0.8},
            "constraints": ["budget: Luxury"],
            "mood": "The best clubs and parties in the world"
        }
    },
    {
        "name": "Family Friendly Nature",
        "payload": {
            "preferences": {"family": 0.8, "nature": 0.7},
            "constraints": ["safety: High"],
            "mood": "Safe place for kids to see animals and parks"
        }
    },
    {
        "name": "Spiritual Journey",
        "payload": {
            "preferences": {"spirituality": 0.9, "culture": 0.8},
            "constraints": ["budget: Budget"],
            "mood": "Seeking enlightenment and ancient wisdom"
        }
    },
    {
        "name": "Modern Tech Hub",
        "payload": {
            "preferences": {"urban": 0.9, "technology": 0.8},
            "constraints": ["budget: Mid-range"],
            "mood": "Neon lights, skyscrapers, and high-tech vibes"
        }
    }
]

async def run_tests():
    results = []
    async with httpx.AsyncClient(timeout=30.0) as client:
        for case in TEST_CASES:
            print(f"Testing: {case['name']}...")
            start_time = datetime.now()
            try:
                response = await client.post(API_URL, json=case['payload'])
                duration = (datetime.now() - start_time).total_seconds()
                
                if response.status_code == 200:
                    data = response.json()
                    results.append({
                        "case": case['name'],
                        "input": case['payload'],
                        "status": "SUCCESS",
                        "duration": f"{duration:.2f}s",
                        "destination": data.get('destination_name'),
                        "match_score": data.get('match_score'),
                        "reasoning": data.get('reasoning_chain', [{}])[0].get('logic', 'N/A')
                    })
                else:
                    results.append({
                        "case": case['name'],
                        "input": case['payload'],
                        "status": f"FAILED ({response.status_code})",
                        "duration": f"{duration:.2f}s",
                        "error": response.text
                    })
            except Exception as e:
                results.append({
                    "case": case['name'],
                    "input": case['payload'],
                    "status": "ERROR",
                    "duration": "N/A",
                    "error": str(e)
                })
    
    generate_report(results)

def generate_report(results):
    report_path = "docs/test_report_sprint_2.md"
    os.makedirs("docs", exist_ok=True)
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Sprint 2: E2E Recommendation Engine Test Report\n\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Summary\n\n")
        
        success_count = sum(1 for r in results if r['status'] == "SUCCESS")
        f.write(f"- **Total Tests**: {len(results)}\n")
        f.write(f"- **Success Rate**: {(success_count/len(results))*100}%\n\n")
        
        f.write("## Test Details\n\n")
        f.write("| Case | Status | Destination | Score | Logic Snippet | Duration |\n")
        f.write("|------|--------|-------------|-------|---------------|----------|\n")
        
        for r in results:
            if r['status'] == "SUCCESS":
                f.write(f"| {r['case']} | ✅ {r['status']} | {r['destination']} | {r['match_score']} | {r['reasoning'][:50]}... | {r['duration']} |\n")
            else:
                f.write(f"| {r['case']} | ❌ {r['status']} | N/A | N/A | {str(r.get('error', 'N/A'))[:50]}... | {r['duration']} |\n")
        
        f.write("\n## Raw Results\n\n")
        f.write("```json\n")
        f.write(json.dumps(results, indent=2))
        f.write("\n```\n")
    
    print(f"Report generated: {report_path}")

if __name__ == "__main__":
    asyncio.run(run_tests())
