#!/usr/bin/env python3
"""
Simple Redis pub/sub test to verify basic communication.
"""

import redis
import time
import json

def test_redis_pubsub():
    """Test basic Redis pub/sub functionality."""
    print("🧪 Testing Redis Pub/Sub Communication")
    print("=" * 50)
    
    # Connect to Redis (using the same URL pattern as your backend)
    redis_url = "redis://red-d2ibkjbipnbc73bjnab0:6379/"
    print(f"🔌 Connecting to Redis: {redis_url}")
    
    try:
        # Create Redis client
        r = redis.from_url(redis_url, decode_responses=True)
        r.ping()
        print("✅ Redis connection successful")
        
        # Test channel
        test_channel = "test_channel_123"
        test_message = f"Test message at {time.strftime('%H:%M:%S')}"
        
        print(f"\n📢 Testing pub/sub on channel: {test_channel}")
        
        # Create subscriber
        pubsub = r.pubsub()
        pubsub.subscribe(test_channel)
        print(f"✅ Subscribed to channel: {test_channel}")
        
        # Wait a moment for subscription to be ready
        time.sleep(1)
        
        # Publish message
        print(f"📤 Publishing message: {test_message}")
        r.publish(test_channel, test_message)
        
        # Try to receive message
        print("⏳ Waiting for message...")
        start_time = time.time()
        message_received = False
        
        while time.time() - start_time < 10:
            message = pubsub.get_message(timeout=1)
            if message and message['type'] == 'message':
                received_data = message['data']
                print(f"✅ Message received: {received_data}")
                message_received = True
                break
            time.sleep(0.1)
        
        if message_received:
            print("🎉 Redis pub/sub test PASSED!")
            return True
        else:
            print("❌ Redis pub/sub test FAILED - No message received")
            return False
            
    except Exception as e:
        print(f"❌ Redis test error: {e}")
        return False
    finally:
        if 'pubsub' in locals():
            pubsub.unsubscribe(test_channel)
            pubsub.close()

if __name__ == "__main__":
    success = test_redis_pubsub()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Redis pub/sub is working correctly")
        print("The issue is likely in the WebSocket Redis integration")
    else:
        print("❌ Redis pub/sub is broken")
        print("This explains why messages aren't flowing")
