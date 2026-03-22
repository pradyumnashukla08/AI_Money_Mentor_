import sys
import requests

# Test Next.js proxy route from Python
def run_test():
    with open("test.pdf", "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n5 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 24 Tf\n100 100 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n0000000213 00000 n \n0000000301 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n395\n%%EOF\n")

    files = {'file': open('test.pdf', 'rb')}
    
    print("Testing direct Python endpoint...")
    r = requests.post("http://127.0.0.1:8000/api/tax-wizard/upload", files=files)
    print("Python Native =>", r.status_code, r.text[:100])

if __name__ == '__main__':
    run_test()
