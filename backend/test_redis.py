#!/usr/bin/env python3
"""Test Redis connectivity."""
import redis
import sys


def test_redis_connection() -> None:
    """Test basic Redis connection and operations."""
    try:
        # Connect to Redis
        client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )

        # Test connection with PING
        response = client.ping()
        if not response:
            print('❌ Redis PING failed')
            sys.exit(1)
        print('✅ Redis PING successful')

        # Test SET operation
        test_key = 'test:connection'
        test_value = 'CryptoTracker Pro'
        client.set(test_key, test_value, ex=10)
        print(f'✅ Redis SET successful: {test_key} = {test_value}')

        # Test GET operation
        retrieved_value = client.get(test_key)
        if retrieved_value != test_value:
            print(f'❌ Redis GET failed: expected {test_value}, got {retrieved_value}')
            sys.exit(1)
        print(f'✅ Redis GET successful: {test_key} = {retrieved_value}')

        # Test DELETE operation
        client.delete(test_key)
        print(f'✅ Redis DELETE successful: {test_key}')

        # Verify deletion
        if client.get(test_key) is not None:
            print('❌ Redis key still exists after deletion')
            sys.exit(1)
        print('✅ Redis key deletion verified')

        print('\n🎉 All Redis connectivity tests passed!')

    except redis.ConnectionError as e:
        print(f'❌ Failed to connect to Redis: {e}')
        sys.exit(1)
    except Exception as e:
        print(f'❌ Unexpected error: {e}')
        sys.exit(1)


if __name__ == '__main__':
    test_redis_connection()
