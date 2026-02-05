from app.services.ai_service import analyze_message

# Test with a scam message
scam_message = """
URGENT: Your bank account has been compromised! 
Click here immediately to verify your identity: http://totallylegit-bank.com/verify
You must provide your SSN and password within 24 hours or your account will be closed.
Call us at 1-800-SCAMMER
"""

print("Testing scam detection...")
print("=" * 50)
print("Message:", scam_message[:100] + "...")
print("=" * 50)

result = analyze_message(scam_message)
print("\nAnalysis Result:")
print(result)