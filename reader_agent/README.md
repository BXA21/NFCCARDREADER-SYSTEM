# NFC Reader Agent

Python application that interfaces with ACR122U NFC card reader for attendance tracking.

## Features

- 📱 Reads NFC card UIDs using ACR122U reader
- 🌐 Sends attendance events to backend API
- 💾 Buffers events offline when API is unavailable
- 🔄 Automatic background synchronization
- 📊 Real-time console feedback
- 🔒 Secure authentication with API keys

## Hardware Requirements

- **ACR122U NFC Card Reader** (USB)
- NFC cards (MIFARE Classic, MIFARE Ultralight, etc.)
- Computer with USB port (Windows, Linux, or macOS)

## Driver Installation

### Windows

1. Download the ACR122U driver from [ACS official website](https://www.acs.com.hk/en/driver/3/acr122u-usb-nfc-reader/)
2. Install the driver
3. Verify installation by checking Device Manager

### Linux

```bash
# Install pcscd (PC/SC daemon)
sudo apt-get update
sudo apt-get install pcscd pcsc-tools libacsccid1

# Start the service
sudo systemctl start pcscd
sudo systemctl enable pcscd

# Verify reader is detected
pcsc_scan
```

### macOS

macOS has built-in PC/SC support. Just plug in the reader and it should work.

```bash
# Verify reader is detected
system_profiler SPUSBDataType | grep -A 11 "ACR122U"
```

## Installation

1. **Clone the repository** (if not already done)

```bash
cd reader_agent
```

2. **Create virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/macOS
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure the application**

```bash
# Copy example configuration
cp config.yaml.example config.yaml

# Edit config.yaml with your settings
# - Set api.base_url to your backend URL
# - Set device.device_id to a unique identifier for this reader
```

5. **Set environment variables**

```bash
# Set the device API key (obtained from backend admin)
export DEVICE_API_KEY="your-api-key-here"

# On Windows PowerShell
$env:DEVICE_API_KEY="your-api-key-here"

# Or create a .env file (not tracked by git)
echo "DEVICE_API_KEY=your-api-key-here" > .env
```

## Running the Agent

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Run the agent
python src/main.py

# With custom config file
python src/main.py --config /path/to/config.yaml
```

## Usage

1. **Start the agent** - Run the command above
2. **Wait for "READY" status** - The agent will connect to the reader and API
3. **Tap NFC cards** - Employees tap their cards on the reader
4. **View feedback** - Success/error messages appear in console
5. **Stop the agent** - Press `Ctrl+C` to gracefully shutdown

## Configuration Reference

### `config.yaml`

```yaml
api:
  base_url: "http://localhost:8000/api/v1"  # Backend API URL
  timeout_seconds: 10                        # Request timeout
  retry_attempts: 3                          # Number of retry attempts

device:
  device_id: "GATE-MAIN-01"                  # Unique device identifier
  # api_key loaded from DEVICE_API_KEY env var

reader:
  poll_interval_ms: 500                      # How often to check for cards
  reconnect_delay_seconds: 5                 # Delay before reconnecting

offline:
  database_path: "./offline_events.db"       # Offline buffer database
  sync_interval_seconds: 30                  # Sync interval
  max_events_per_sync: 50                    # Max events per sync batch

logging:
  level: "INFO"                              # Log level (DEBUG, INFO, WARNING, ERROR)
  file: "./reader_agent.log"                 # Log file path
```

## Troubleshooting

### Reader Not Detected

```bash
# Check if reader is connected
lsusb | grep ACS  # Linux
system_profiler SPUSBDataType | grep ACR  # macOS

# Check PC/SC daemon status (Linux)
sudo systemctl status pcscd

# Test reader
pcsc_scan  # Should show reader and card info
```

### Permission Denied (Linux)

```bash
# Add user to pcscd group
sudo usermod -a -G pcscd $USER

# Or run with sudo (not recommended for production)
sudo python src/main.py
```

### API Connection Error

- Check `api.base_url` in config.yaml
- Verify backend is running: `curl http://localhost:8000/health`
- Check `DEVICE_API_KEY` environment variable is set
- Check firewall settings

### Offline Events Not Syncing

- Check internet connectivity
- Check backend API is reachable
- Check `offline_events.db` for pending events
- Check logs in `reader_agent.log`

## File Structure

```
reader_agent/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # Main application entry point
│   ├── config_manager.py     # Configuration management
│   ├── nfc_reader.py         # NFC reader interface
│   ├── api_client.py         # Backend API client
│   ├── offline_buffer.py     # Offline event storage
│   ├── sync_manager.py       # Background sync manager
│   └── display.py            # Console output manager
├── config.yaml.example       # Example configuration
├── config.yaml               # Your configuration (gitignored)
├── requirements.txt          # Python dependencies
├── offline_events.db         # Offline buffer (generated)
├── reader_agent.log          # Log file (generated)
└── README.md                 # This file
```

## Production Deployment

### Running as a Service (Linux)

Create `/etc/systemd/system/nfc-reader.service`:

```ini
[Unit]
Description=NFC Attendance Reader Agent
After=network.target pcscd.service

[Service]
Type=simple
User=attendance
WorkingDirectory=/opt/nfc-reader-agent
Environment="DEVICE_API_KEY=your-key-here"
ExecStart=/opt/nfc-reader-agent/venv/bin/python src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nfc-reader.service
sudo systemctl start nfc-reader.service
sudo systemctl status nfc-reader.service
```

### Running as a Service (Windows)

Use [NSSM](https://nssm.cc/) to create a Windows service.

## Security Notes

- **Never commit API keys** to version control
- Store API keys in environment variables or secure vaults
- Use HTTPS for production API endpoints
- Restrict device API keys to specific devices
- Regularly rotate API keys
- Monitor logs for suspicious activity

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `reader_agent.log`
3. Contact system administrator
4. Refer to backend API documentation

## License

Proprietary - Internal use only



