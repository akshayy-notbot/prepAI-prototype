#!/usr/bin/env python3
"""
Simple Debug Script for Render Shell
Tests the Redis subscription fix
"""

import redis
import time
import os

# Redis connection (use environment variable)
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

print("🔧 Testing Redis Subscription Fix")
print("=" * 40)

try:
    # Connect to Redis
    print("🔌 Connecting to Redis...")
    print(f"🔍 Redis URL: {redis_url}")
    
    if not redis_url or redis_url == "redis://localhost:6379/0":
        print("⚠️  Using fallback Redis URL - check REDIS_URL environment variable")
    
    r = redis.from_url(redis_url)
    r.ping()
    print("✅ Redis connection successful")
    
    # Test channel
    channel_name = "channel:test-subscription-fix"
    print(f"📡 Testing channel: {channel_name}")
    
    # Create pubsub
    pubsub = r.pubsub()
    
    # Subscribe to channel
    print("🔌 Subscribing to channel...")
    pubsub.subscribe(channel_name)
    print("✅ Subscription command sent")
    
    # CRITICAL FIX: Wait for subscription to be ready
    print("⏳ Waiting for Redis subscription to be ready...")
    time.sleep(2)  # Wait 2 seconds for subscription to be fully ready
    print("✅ Redis subscription ready!")
    
    # Test subscription
    channels = pubsub.channels
    if channel_name.encode() in channels:
        print(f"✅ Subscription confirmed for channel {channel_name}")
    else:
        print(f"❌ Subscription failed for channel {channel_name}")
        print(f"   Available channels: {channels}")
    
    # Now test message publishing and receiving
    print("\n📨 Testing message flow...")
    
    # Send a test message
    test_message = "TEST_MESSAGE_FROM_DEBUG_SCRIPT"
    result = r.publish(channel_name, test_message)
    print(f"📤 Message published: {test_message}")
    print(f"   Subscribers: {result}")
    
    # Try to receive the message
    print("📥 Attempting to receive message...")
    message = pubsub.get_message(timeout=5)
    
    if message and message['type'] == 'message':
        received_data = message['data'].decode('utf-8')
        print(f"✅ Message received successfully!")
        print(f"   Content: {received_data}")
        print(f"   Type: {message['type']}")
        print(f"   Channel: {message['channel']}")
    elif message and message['type'] == 'subscribe':
        print(f"ℹ️ Received subscription confirmation: {message}")
        print("   This is normal - checking for actual message...")
        
        # Try to get the actual message
        for i in range(3):
            time.sleep(1)
            message = pubsub.get_message(timeout=1)
            if message and message['type'] == 'message':
                received_data = message['data'].decode('utf-8')
                print(f"✅ Message received on attempt {i+1}!")
                print(f"   Content: {received_data}")
                break
            elif message:
                print(f"   Other message: {message}")
            else:
                print(f"   No message on attempt {i+1}")
    else:
        print(f"❌ No message received: {message}")
    
    # Clean up
    pubsub.close()
    print("\n🧹 Cleanup completed")
    
    print("\n🎯 SUMMARY:")
    print("   If you received the test message, the Redis subscription fix is working!")
    print("   If not, there may still be an issue with the timing.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
