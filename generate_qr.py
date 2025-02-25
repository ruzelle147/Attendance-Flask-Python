import qrcode

def generate_qr(employee_id, name):
    data = f"{employee_id},{name}"
    qr = qrcode.make(data)
    qr.save(f"qrcodes/{employee_id}.png")  # Save QR in "qrcodes" folder
    print(f"QR Code saved as qrcodes/{employee_id}.png")

# Example
generate_qr("EMP001", "John Doe")
