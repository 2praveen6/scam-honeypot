print("Step 1: Starting script...")

try:
    print("Step 2: Importing groq...")
    from groq import Groq
    print("✅ Import successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit()

try:
    print("Step 3: Importing config...")
    from app.config import GROQ_API_KEY, MODEL_NAME
    print(f"✅ Config loaded")
except Exception as e:
    print(f"❌ Config import failed: {e}")
    exit()

try:
    print("Step 4: Creating client...")
    client = Groq(api_key=GROQ_API_KEY)
    print("✅ Client created")
except Exception as e:
    print(f"❌ Client creation failed: {e}")
    exit()

try:
    print("Step 5: Generating content...")
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": "Say 'Hello, setup successful!'"}]
    )
    print(f"✅ Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Generation failed: {e}")
    exit()

print("\n" + "=" * 50)
print("✅ STEP 1 COMPLETE! Your setup is working!")
print("=" * 50)