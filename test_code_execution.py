#!/usr/bin/env python3
"""
Test script để kiểm tra code execution với input data
"""

import tempfile
import subprocess
import os

def test_code_execution():
    """Test code execution với input data"""
    
    # Test code Python đơn giản
    test_code = """
def main():
    # Đọc input
    n = int(input())
    arr = list(map(int, input().split()))
    
    # Xử lý logic
    result = sum(arr)
    
    # In kết quả
    print(result)

if __name__ == "__main__":
    main()
"""
    
    # Test input data
    test_input = "5\\n3 1 4 1 5"
    expected_output = "14"
    
    # Xử lý input data - chuyển đổi \n thành newline thực tế
    processed_input = test_input.replace('\\n', '\n')
    
    print(f"Test input: {repr(test_input)}")
    print(f"Processed input: {repr(processed_input)}")
    print(f"Expected output: {expected_output}")
    
    # Tạo file tạm với UTF-8 encoding
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write(test_code)
        temp_file = f.name
    
    try:
        # Chạy code
        cmd = ['python', temp_file]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        
        stdout, stderr = process.communicate(input=processed_input, timeout=10)
        
        print(f"Actual output: {repr(stdout.strip())}")
        print(f"Error: {stderr if stderr else 'None'}")
        
        # Kiểm tra kết quả
        if stdout.strip() == expected_output:
            print("✅ Test PASSED!")
            return True
        else:
            print("❌ Test FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Dọn dẹp
        try:
            os.unlink(temp_file)
        except:
            pass

if __name__ == "__main__":
    print("Testing code execution with input data...")
    test_code_execution() 