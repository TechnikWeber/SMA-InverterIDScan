#!/usr/bin/env python3
"""
SMA Sunny Boy Wechselrichter IDs über RS485 Modbus RTU auslesen
Für Raspberry Pi mit pymodbus 3.x
"""

from pymodbus.client import ModbusSerialClient

# Konfiguration
SERIAL_PORT = '/dev/ttyUSB0'  # Anpassen an deinen RS485-Adapter
BAUDRATE = 9600
PARITY = 'N'  # None
STOPBITS = 1
BYTESIZE = 8
TIMEOUT = 1

# SMA Register für Geräte-ID
DEVICE_ID_REGISTER = 30057  # Serial Number Register


def scan_for_inverters(client, start_id=1, end_id=247):
    """
    Scannt den Modbus-Bus nach Wechselrichtern
    """
    print(f"Scanne Modbus IDs von {start_id} bis {end_id}...")
    print("-" * 50)
    
    found_inverters = []
    
    for unit_id in range(start_id, end_id + 1):
        try:
            # Versuche Seriennummer zu lesen
            result = client.read_holding_registers(
                DEVICE_ID_REGISTER,
                2,
                unit_id
            )
            
            if not result.isError():
                # Seriennummer aus zwei Registern zusammensetzen
                serial = (result.registers[0] << 16) | result.registers[1]
                found_inverters.append({
                    'unit_id': unit_id,
                    'serial': serial
                })
                print(f"✓ Wechselrichter gefunden!")
                print(f"  Unit ID: {unit_id}")
                print(f"  Seriennummer: {serial}")
                print()
                
        except Exception:
            pass  # Keine Antwort auf dieser ID
    
    return found_inverters


def main():
    # Modbus Client erstellen
    client = ModbusSerialClient(
        port=SERIAL_PORT,
        baudrate=BAUDRATE,
        parity=PARITY,
        stopbits=STOPBITS,
        bytesize=BYTESIZE,
        timeout=TIMEOUT
    )
    
    # Verbindung herstellen
    if not client.connect():
        print("Fehler: Konnte keine Verbindung zum RS485-Adapter herstellen!")
        print(f"Port: {SERIAL_PORT}")
        return
    
    print("Verbindung hergestellt")
    print()
    
    try:
        # Nach Wechselrichtern suchen
        inverters = scan_for_inverters(client)
        
        print("=" * 50)
        print(f"Scan abgeschlossen: {len(inverters)} Wechselrichter gefunden")
        print()
        
        if inverters:
            print("Gefundene Geräte:")
            for inv in inverters:
                print(f"  - Unit ID: {inv['unit_id']}, Serial: {inv['serial']}")
        else:
            print("Keine Wechselrichter gefunden!")
            print()
            print("Tipps zur Fehlersuche:")
            print("  - RS485-Verkabelung prüfen (A/B richtig?)")
            print("  - Baudrate prüfen (Standard: 9600)")
            print("  - Wechselrichter Modbus-Einstellungen prüfen")
            print("  - Terminierung am Bus prüfen")
        
    finally:
        client.close()
        print("\nVerbindung geschlossen")


if __name__ == "__main__":
    main()
