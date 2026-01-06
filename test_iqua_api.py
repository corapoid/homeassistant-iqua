#!/usr/bin/env python3
"""Test iQua Ecowater API authentication - Simple verification script"""

import sys
import argparse
from datetime import datetime


def install_library():
    """Install iqua_softener library if not present"""
    try:
        import iqua_softener
        return True
    except ImportError:
        print("📦 Installing iqua_softener library...")
        import subprocess
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "iqua_softener~=1.0.2"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("✅ Library installed successfully\n")
            return True
        except Exception as e:
            print(f"❌ Failed to install library: {e}")
            return False


def test_authentication(username: str, password: str, serial_number: str):
    """Test iQua API authentication with provided credentials"""
    
    print("=" * 70)
    print("🔍 IQUA ECOWATER API AUTHENTICATION TEST")
    print("=" * 70)
    print(f"Username (email):  {username}")
    print(f"Password:          {'*' * len(password)}")
    print(f"Serial Number:     {serial_number}")
    print(f"Test time:         {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Import after installation
    try:
        from iqua_softener import IquaSoftener, IquaSoftenerException
    except ImportError as e:
        print(f"❌ Cannot import iqua_softener: {e}")
        print("Try: pip install iqua_softener~=1.0.2")
        return False
    
    print("🔄 Creating IquaSoftener instance...")
    try:
        softener = IquaSoftener(username, password, serial_number)
        print("✅ Instance created")
    except Exception as e:
        print(f"❌ Failed to create instance: {e}")
        return False
    
    print("🔄 Attempting to fetch data from Ecowater API...")
    print("   (This may take a few seconds...)")
    print()
    
    try:
        data = softener.get_data()
        
        # Success!
        print("=" * 70)
        print("✅ SUCCESS! Authentication and data fetch worked!")
        print("=" * 70)
        print()
        print("📊 RETRIEVED DATA:")
        print(f"   State:                {data.state}")
        print(f"   Model:                {data.model}")
        print(f"   Device Date/Time:     {data.device_date_time}")
        print(f"   Salt Level:           {data.salt_level_percent}%")
        print(f"   Available Water:      {data.total_water_available} {data.volume_unit.name}")
        print(f"   Current Flow:         {data.current_water_flow}")
        print(f"   Today Usage:          {data.today_use}")
        print(f"   Days Since Regen:     {data.days_since_last_regeneration}")
        print(f"   Out of Salt (days):   {data.out_of_salt_estimated_days}")
        print()
        print("=" * 70)
        print("✅ RESULT: Credentials are VALID")
        print("=" * 70)
        print()
        print("💡 You can now use these credentials in Home Assistant integration")
        print()
        
        return True
        
    except IquaSoftenerException as e:
        # API Error
        error_msg = str(e)
        print("=" * 70)
        print("❌ AUTHENTICATION FAILED")
        print("=" * 70)
        print()
        print(f"Error message: {error_msg}")
        print()
        
        # Analyze error
        error_lower = error_msg.lower()
        
        if "authentication error" in error_lower or "invalid user" in error_lower:
            print("🔍 ERROR ANALYSIS:")
            print("   Type: Authentication Error")
            print()
            print("   POSSIBLE CAUSES:")
            print("   1. ❌ Incorrect username or password")
            print("   2. ⚠️  API requires 2FA (email verification code)")
            print("   3. ⚠️  Account locked or requires password reset")
            print()
            print("   SOLUTIONS:")
            print("   1. Double-check your credentials (check for typos)")
            print("   2. Try logging into iQua mobile app:")
            print("      - Logout from app")
            print("      - Login again with same credentials")
            print("      - If it asks for email code → API has 2FA enabled!")
            print("   3. Make sure password has no leading/trailing spaces")
            
        elif "502" in error_msg:
            print("🔍 ERROR ANALYSIS:")
            print("   Type: Server Error (502 Bad Gateway)")
            print()
            print("   POSSIBLE CAUSES:")
            print("   - Ecowater servers temporarily down")
            print("   - Server maintenance")
            print()
            print("   SOLUTIONS:")
            print("   - Wait 5-10 minutes and try again")
            print("   - Check if iQua mobile app works")
            
        elif "device" in error_lower or "serial" in error_lower:
            print("🔍 ERROR ANALYSIS:")
            print("   Type: Device Not Found")
            print()
            print("   POSSIBLE CAUSES:")
            print("   - Incorrect serial number (DSN#)")
            print("   - Serial number is case-sensitive!")
            print()
            print("   SOLUTIONS:")
            print("   - Check serial number in iQua app (Settings → Device Info)")
            print("   - Copy it EXACTLY as shown (including case)")
            print(f"   - You entered: {serial_number}")
            
        else:
            print("🔍 ERROR ANALYSIS:")
            print("   Type: Unknown Error")
            print()
            print("   SOLUTIONS:")
            print("   - Check internet connection")
            print("   - Try again in a few minutes")
            print("   - Check if iQua mobile app works")
        
        print()
        print("=" * 70)
        
        return False
        
    except Exception as e:
        # Unexpected error
        print("=" * 70)
        print("❌ UNEXPECTED ERROR")
        print("=" * 70)
        print()
        print(f"Error: {e}")
        print(f"Type: {type(e).__name__}")
        print()
        print("Stack trace:")
        import traceback
        traceback.print_exc()
        print()
        
        return False


def main():
    """Main function with argument parsing"""
    
    parser = argparse.ArgumentParser(
        description="Test iQua Ecowater API authentication",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --username user@example.com --password mypass123 --serial DSN123456789
  %(prog)s -u user@example.com -p mypass123 -s DSN123456789
  
  Interactive mode (will prompt for credentials):
  %(prog)s
        """
    )
    
    parser.add_argument(
        "-u", "--username",
        help="iQua account username (email)"
    )
    parser.add_argument(
        "-p", "--password",
        help="iQua account password"
    )
    parser.add_argument(
        "-s", "--serial",
        help="Device serial number (DSN#)"
    )
    
    args = parser.parse_args()
    
    # Check if library is installed
    if not install_library():
        return 1
    
    # Get credentials (from args or prompt)
    if args.username and args.password and args.serial:
        username = args.username
        password = args.password
        serial_number = args.serial
    else:
        print("=" * 70)
        print("🔑 IQUA CREDENTIALS INPUT")
        print("=" * 70)
        print("Enter your iQua account credentials:")
        print("(These are the same credentials you use in the iQua mobile app)")
        print()
        
        username = input("Username (email): ").strip()
        password = input("Password: ").strip()
        serial_number = input("Device Serial Number (DSN#): ").strip()
        print()
    
    # Validate inputs
    if not username or not password or not serial_number:
        print("❌ Error: All fields are required!")
        return 1
    
    # Run test
    success = test_authentication(username, password, serial_number)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
