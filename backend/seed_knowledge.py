import numpy as np
from app.database.mongodb import get_knowledge_collection

KNOWLEDGE_ARTICLES = [
    {
        "id": "KB1001",
        "title": "VPN Troubleshooting and Authentication Guide",
        "category": "Network",
        "subcategory": "VPN",
        "keywords": ["vpn", "authentication", "network", "remote access", "failing", "anyconnect", "gateway"],
        "content": (
            "If your VPN connection or authentication keeps failing:\n"
            "1. Verify internet connectivity by opening a public browser page.\n"
            "2. Ensure your domain password has not expired.\n"
            "3. Disconnect from any personal VPN or third-party proxy tools.\n"
            "4. Open Cisco AnyConnect or GlobalProtect, select gateway 'vpn.company.internal', and re-enter multi-factor authentication (MFA).\n"
            "5. If error 'Authentication Failed' persists, restart the VPN service or clear client cache."
        ),
        "source": "IT Knowledge Base / KB1001",
        "version": "1.4"
    },
    {
        "id": "KB1002",
        "title": "Self-Service Password Reset and Account Unlock Guide",
        "category": "Account & Access",
        "subcategory": "Password Reset",
        "keywords": ["password", "expired", "reset", "unlock", "credentials", "account", "login"],
        "content": (
            "When your domain password has expired or account is locked:\n"
            "1. Access the Self-Service Password Portal using your secondary registered mobile or authenticator app.\n"
            "2. Complete the biometric or SMS OTP challenge.\n"
            "3. Choose a new password of at least 14 characters including uppercase, lowercase, numbers, and symbols.\n"
            "4. The AI Self-Heal Agent can trigger an immediate automated password reset or unlock Active Directory account."
        ),
        "source": "Identity & Access Management / KB1002",
        "version": "2.1"
    },
    {
        "id": "KB1003",
        "title": "Microsoft Outlook Mailbox Synchronization Troubleshooting",
        "category": "Software",
        "subcategory": "Email / Outlook",
        "keywords": ["outlook", "synchronization", "sync", "email", "ost", "mailbox", "disconnected"],
        "content": (
            "To resolve Outlook email synchronization issues:\n"
            "1. Check the bottom status bar in Outlook. If it shows 'Disconnected' or 'Trying to connect', check internet and VPN.\n"
            "2. In Outlook, navigate to Send / Receive tab -> click 'Send/Receive All Folders' or press F9.\n"
            "3. If folders are not updating, navigate to File -> Account Settings -> Account Settings -> Change -> verify Cached Exchange Mode is enabled.\n"
            "4. To rebuild cache: Close Outlook, delete the local .ost file located at '%localappdata%\\Microsoft\\Outlook', and restart Outlook to initiate fresh sync."
        ),
        "source": "Application Support / KB1003",
        "version": "1.8"
    },
    {
        "id": "KB1004",
        "title": "Corporate Wi-Fi and Wireless Network Connectivity",
        "category": "Network",
        "subcategory": "WiFi",
        "keywords": ["wifi", "wi-fi", "wireless", "network", "internet", "ssid", "adapter"],
        "content": (
            "Steps for troubleshooting enterprise Wi-Fi:\n"
            "1. Confirm you are connected to the official SSID: 'CORP-SECURE-WIFI'.\n"
            "2. Toggle airplane mode ON for 10 seconds, then toggle OFF.\n"
            "3. Open Command Prompt and execute 'ipconfig /flushdns' followed by 'netsh int ip reset'.\n"
            "4. If receiving an IP configuration error, verify device certificate expiration with Network Support."
        ),
        "source": "Network Infrastructure / KB1004",
        "version": "1.2"
    },
    {
        "id": "KB1005",
        "title": "Laptop Performance, High CPU and Memory Optimization",
        "category": "Hardware",
        "subcategory": "Laptop Performance",
        "keywords": ["performance", "laptop", "slow", "freeze", "cpu", "ram", "memory", "clean"],
        "content": (
            "To diagnose and resolve slow laptop responsiveness:\n"
            "1. Open Task Manager (Ctrl + Shift + Esc) and inspect top CPU and Memory consumers.\n"
            "2. Terminate hung applications or excessive background browser tabs.\n"
            "3. Run Disk Cleanup to clear temporary system files and caches.\n"
            "4. Ensure laptop vents are clean and thermal throttling is not occurring. Restart the machine weekly."
        ),
        "source": "Desktop Engineering / KB1005",
        "version": "1.5"
    },
    {
        "id": "KB1006",
        "title": "Software Catalog and Automated Application Provisioning",
        "category": "Software",
        "subcategory": "Software Provisioning",
        "keywords": ["software", "install", "installation", "visual studio code", "vs code", "teams", "docker", "postman"],
        "content": (
            "Enterprise Approved Software Catalog instructions:\n"
            "1. Approved applications including Visual Studio Code, Docker Desktop, Microsoft Teams, Python, and Postman are available for automated self-service provisioning.\n"
            "2. Submitting a request triggers AI Intent Detection -> Software Catalog verification -> ServiceNow REQ generation -> Automated mock provisioning workflow.\n"
            "3. No manual approval required for Standard Developer Tier tools."
        ),
        "source": "IT Service Desk / KB1006",
        "version": "2.0"
    },
    {
        "id": "KB1007",
        "title": "Application Access and Enterprise Role-Based Permissions",
        "category": "Account & Access",
        "subcategory": "Application Access",
        "keywords": ["access", "permission", "jira", "github", "aws", "role", "authorization"],
        "content": (
            "Requesting access to enterprise applications (AWS, GitHub Enterprise, Jira):\n"
            "1. Ensure you have your manager's cost-center approval.\n"
            "2. Submit an Access Request specifying the exact target system, required security group, and business rationale.\n"
            "3. Access is provisioned within 4 business hours upon automated policy validation."
        ),
        "source": "Identity & Access Management / KB1007",
        "version": "1.1"
    }
]

def seed_knowledge_base():
    collection = get_knowledge_collection()
    # Check count or upsert
    for article in KNOWLEDGE_ARTICLES:
        collection.update_one(
            {"id": article["id"]},
            {"$set": article},
            upsert=True,
        )
    print(f"Knowledge Base initialized with {len(KNOWLEDGE_ARTICLES)} articles.")

if __name__ == "__main__":
    seed_knowledge_base()