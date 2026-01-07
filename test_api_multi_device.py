#!/usr/bin/env python3
"""Test EcoWater API multi-device support - FINAL VERSION."""

import sys
from iqua_softener import IquaSoftener, IquaSoftenerException

USERNAME = "corapoid@gmail.com"
PASSWORD = "v713i0cRP*Ver2N"
KNOWN_DEVICE = "SL00235E723F34"

def test_api_structure():
    """Inspect IquaSoftener class structure."""
    print("=" * 60)
    print("TEST 1: API Structure Inspection")
    print("=" * 60)
    
    # Create instance WITH serial (known to work)
    softener = IquaSoftener(USERNAME, PASSWORD, KNOWN_DEVICE)
    
    # List all methods and properties
    methods = [m for m in dir(softener) if not m.startswith('_')]
    print(f"\n📋 Available methods/properties ({len(methods)}):")
    for method in methods:
        attr = getattr(softener, method)
        attr_type = "method" if callable(attr) else "property"
        print(f"  - {method} ({attr_type})")
    
    # Check for device-related methods
    device_methods = [m for m in methods if 'device' in m.lower()]
    if device_methods:
        print(f"\n🔍 Device-related methods found:")
        for m in device_methods:
            print(f"  ✅ {m}")
    else:
        print(f"\n⚠️  No obvious device-related methods found")
    
    return softener

def test_without_serial():
    """Test if API works without device serial."""
    print("\n" + "=" * 60)
    print("TEST 2: Connection Without Serial Number")
    print("=" * 60)
    
    try:
        # Try to create instance WITHOUT serial
        softener = IquaSoftener(USERNAME, PASSWORD, None)
        print("✅ SUCCESS: Can create instance without serial")
        
        # Try to call get_data (should fail or return account info)
        try:
            data = softener.get_data()
            print(f"✅ get_data() works: {type(data)}")
            print(f"   Data attributes: {[a for a in dir(data) if not a.startswith('_')]}")
        except Exception as e:
            print(f"⚠️  get_data() failed (expected): {type(e).__name__}")
        
        return softener
    
    except Exception as e:
        print(f"❌ FAILED: Cannot create without serial - {type(e).__name__}: {e}")
        return None

def test_device_discovery(softener):
    """Test various methods that might return device list."""
    print("\n" + "=" * 60)
    print("TEST 3: Device Discovery Methods")
    print("=" * 60)
    
    if not softener:
        print("⚠️  Skipping (no instance without serial)")
        return None
    
    # Try different method names
    test_methods = [
        'list_devices',
        'get_devices', 
        'get_all_devices',
        'devices',
        'get_device_list',
        'enumerate_devices',
    ]
    
    for method_name in test_methods:
        if hasattr(softener, method_name):
            print(f"\n🔍 Testing: {method_name}()")
            try:
                attr = getattr(softener, method_name)
                if callable(attr):
                    result = attr()
                else:
                    result = attr  # property
                
                print(f"✅ SUCCESS: {method_name} returned {type(result)}")
                
                # Analyze result
                if isinstance(result, list):
                    print(f"   📊 List with {len(result)} item(s)")
                    if result:
                        print(f"   📄 First item type: {type(result[0])}")
                        print(f"   📄 First item: {result[0]}")
                elif isinstance(result, dict):
                    print(f"   📊 Dict with {len(result)} key(s)")
                    print(f"   🔑 Keys: {list(result.keys())}")
                else:
                    print(f"   📄 Value: {result}")
                
                return result
                
            except Exception as e:
                print(f"❌ FAILED: {method_name} - {type(e).__name__}: {e}")
        else:
            print(f"⚠️  Method not found: {method_name}")
    
    print("\n❌ No device discovery method found")
    return None

def test_with_known_device():
    """Test with known device to see data structure."""
    print("\n" + "=" * 60)
    print("TEST 4: Known Device Data Structure")
    print("=" * 60)
    
    try:
        softener = IquaSoftener(USERNAME, PASSWORD, KNOWN_DEVICE)
        data = softener.get_data()
        
        print(f"✅ Device data retrieved successfully")
        print(f"\n📊 Data type: {type(data)}")
        print(f"📋 Data attributes:")
        
        for attr in dir(data):
            if not attr.startswith('_'):
                value = getattr(data, attr, 'N/A')
                # Truncate long values
                if isinstance(value, str) and len(value) > 50:
                    value = value[:50] + "..."
                print(f"  - {attr}: {value}")
        
        # Check for device metadata
        metadata_attrs = ['model', 'serial', 'serial_number', 'device_id', 
                         'firmware', 'firmware_version', 'name', 'device_name']
        
        print(f"\n🔍 Device metadata:")
        found_any = False
        for attr in metadata_attrs:
            if hasattr(data, attr):
                print(f"  ✅ {attr}: {getattr(data, attr)}")
                found_any = True
        
        if not found_any:
            print(f"  ⚠️  No standard metadata found")
        
        return data
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")
        return None

def test_api_endpoints():
    """Try to inspect actual API endpoints."""
    print("\n" + "=" * 60)
    print("TEST 5: API Endpoint Investigation")
    print("=" * 60)
    
    try:
        softener = IquaSoftener(USERNAME, PASSWORD, KNOWN_DEVICE)
        
        # Look for API-related attributes
        api_attrs = []
        for attr in dir(softener):
            if 'api' in attr.lower() or 'url' in attr.lower() or 'endpoint' in attr.lower():
                api_attrs.append(attr)
        
        if api_attrs:
            print(f"🔍 API-related attributes found:")
            for attr in api_attrs:
                value = getattr(softener, attr, None)
                if not callable(value) and value:
                    print(f"  - {attr}: {value}")
        else:
            print(f"⚠️  No API-related attributes found")
        
        # Check for session/client objects
        client_attrs = []
        for attr in dir(softener):
            obj = getattr(softener, attr, None)
            if obj and hasattr(obj, 'get') or hasattr(obj, 'post'):
                client_attrs.append(attr)
        
        if client_attrs:
            print(f"\n🌐 HTTP client attributes found:")
            for attr in client_attrs:
                print(f"  - {attr}")
        
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {e}")

def main():
    """Run all tests."""
    print("\n" + "🔬 EcoWater API Multi-Device Support Testing")
    print("=" * 60)
    print(f"Account: {USERNAME}")
    print(f"Known Device: {KNOWN_DEVICE}")
    print("=" * 60)
    
    # Test 1: Inspect API structure
    softener_with_serial = test_api_structure()
    
    # Test 2: Try without serial
    softener_without_serial = test_without_serial()
    
    # Test 3: Try device discovery
    devices = test_device_discovery(softener_without_serial or softener_with_serial)
    
    # Test 4: Known device data
    device_data = test_with_known_device()
    
    # Test 5: API endpoints
    test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    if devices:
        print(f"✅ Multi-device API: SUPPORTED")
        print(f"   Found {len(devices) if isinstance(devices, list) else '?'} device(s)")
        print(f"   Implementation: Use discovered method in hub.py")
    elif softener_without_serial:
        print(f"⚠️  Multi-device API: PARTIAL")
        print(f"   Can connect without serial, but no list method found")
        print(f"   Implementation: Use mock mode with manual device addition")
    else:
        print(f"❌ Multi-device API: NOT SUPPORTED")
        print(f"   Serial number required for all operations")
        print(f"   Implementation: Use mock mode only")
    
    print(f"\n💡 Recommendation for hub.py:")
    if devices:
        print(f"   Use real API discovery in async_discover_devices()")
    else:
        print(f"   Use mock mode - require manual device serial input")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
