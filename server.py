import json, struct
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pymodbus.client import ModbusTcpClient

LTE_GATEWAY_IP = "10.8.0.12"  # Change to your LTE Gateway IP
LTE_GATEWAY_PORT = 502

class ReusableHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True

def read_float32(client, address, slave):
    res = client.read_holding_registers(address=address, count=2, slave=slave)
    if res.isError():
        return None
    raw = struct.pack(">HH", res.registers[0], res.registers[1])
    return round(struct.unpack(">f", raw)[0], 2)

def read_u16(client, address, slave, scale=1.0):
    res = client.read_holding_registers(address=address, count=1, slave=slave)
    if res.isError():
        return None
    return round(res.registers[0] * scale, 2)

def poll_gateway():
    client = ModbusTcpClient(LTE_GATEWAY_IP, port=LTE_GATEWAY_PORT, timeout=2)
    if not client.connect():
        return {"connected": False, "error": "LTE Gateway unreachable"}
    data = {"connected": True, "inverters": {}, "meters": {}}
    try:
        for inv_id in range(1, 5):
            data["inverters"][f"INV-{inv_id}"] = {
                "p_kw": read_u16(client, 0x3026, inv_id, 0.1),
                "q_kvar": read_u16(client, 0x3028, inv_id, 0.1),
                "bat_v": read_u16(client, 0x3010, inv_id, 0.1),
                "bat_soc": read_u16(client, 0x3013, inv_id, 1.0),
                "pv_kw": read_u16(client, 0x3008, inv_id, 0.1),
                "temp_c": read_u16(client, 0x3030, inv_id, 0.1),
            }
        for slave_id, name in {11: "T1", 12: "T2", 13: "G1", 14: "G2"}.items():
            data["meters"][name] = {
                "v_ll": read_float32(client, 3020, slave_id),
                "i_avg": read_float32(client, 3000, slave_id),
                "p_kw": read_float32(client, 3060, slave_id),
                "q_kvar": read_float32(client, 3068, slave_id),
                "s_kva": read_float32(client, 3076, slave_id),
                "pf": read_float32(client, 3084, slave_id),
                "freq": read_float32(client, 3110, slave_id),
                "kwh_imp": read_float32(client, 3204, slave_id),
            }
    finally:
        client.close()
    return data

class ScadaHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/telemetry":
            payload = json.dumps(poll_gateway()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(payload)
        else:
            super().do_GET()

if __name__ == "__main__":
    pkill_note = "Run: pkill -f python  # if restarting"
    server = ReusableHTTPServer(("0.0.0.0", 8085), ScadaHandler)
    print("in4solar SCADA Dashboard live at http://0.0.0.0:8085")
    server.serve_forever()
