from datetime import datetime
import uuid
from app.database.mongodb import get_audit_collection, get_provisioning_collection

SOFTWARE_CATALOG = {
    "Visual Studio Code": {
        "id": "SW-101",
        "category": "Developer Tools",
        "version": "1.95 (x64 Enterprise)",
        "status": "Approved & Available",
        "license": "Open Source / Permissive"
    },
    "VS Code": {
        "id": "SW-101",
        "category": "Developer Tools",
        "version": "1.95 (x64 Enterprise)",
        "status": "Approved & Available",
        "license": "Open Source / Permissive"
    },
    "Microsoft Teams": {
        "id": "SW-102",
        "category": "Collaboration",
        "version": "24243.1309.3138.8055",
        "status": "Approved & Available",
        "license": "Enterprise M365"
    },
    "Docker Desktop": {
        "id": "SW-103",
        "category": "Containers & Virtualization",
        "version": "4.34.2 (Engine 27.2.0)",
        "status": "Approved & Available",
        "license": "Enterprise Business"
    },
    "Postman": {
        "id": "SW-104",
        "category": "API Development",
        "version": "11.12.0",
        "status": "Approved & Available",
        "license": "Enterprise Tier"
    },
    "Python": {
        "id": "SW-105",
        "category": "Runtimes",
        "version": "3.12.6 LTS",
        "status": "Approved & Available",
        "license": "PSF License"
    },
    "Google Chrome": {
        "id": "SW-106",
        "category": "Browsers",
        "version": "129.0.6668.71 Enterprise",
        "status": "Approved & Available",
        "license": "Enterprise Deployment"
    },
    "IntelliJ IDEA": {
        "id": "SW-107",
        "category": "IDE",
        "version": "2024.2.3 Ultimate",
        "status": "Approved & Available",
        "license": "Commercial"
    }
}

def log_audit_trail(action: str, target: str, actor: str, status: str, details: str, ticket_id: str = None, request_id: str = None):
    audit_collection = get_audit_collection()
    audit_entry = {
        "audit_id": f"AUD-{uuid.uuid4().hex[:8].upper()}",
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "action": action,
        "target": target,
        "actor": actor,
        "status": status,
        "details": details,
        "ticket_id": ticket_id,
        "request_id": request_id
    }
    audit_collection.insert_one(audit_entry)
    return audit_entry

def execute_automation(action: str, ticket_id: str, software_name: str = "Visual Studio Code") -> dict:
    """
    Executes automated self-healing actions or software provisioning workflows.
    Supported actions:
    - password_reset
    - account_unlock
    - vpn_status_check
    - service_restart
    - cache_clear
    - application_restart
    - software_install
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Password Reset Workflow
    if action in ["password_reset", "Password Reset"]:
        details = "Simulation only: identity validation, password flag reset, and OTP notification are represented as demo steps; no directory or phone system is contacted."
        log_audit_trail(
            action="Password Reset Self-Heal",
            target="Active Directory / IAM",
            actor="AI Self-Heal Agent",
            status="Simulated",
            details=details,
            ticket_id=ticket_id
        )
        return {
            "success": True,
            "mode": "SIMULATED",
            "action": "Password Reset",
            "status": "Success",
            "steps_executed": [
                "1. Identify user account via authentication context",
                "2. Diagnose expired credential in Active Directory",
                "3. Execute automated credential refresh",
                "4. Validate policy compliance (14+ chars)",
                "5. Synchronize resolution to ServiceNow"
            ],
            "message": "SIMULATION ONLY: password-reset workflow completed in the demo; no real password was changed and no OTP was sent.",
            "timestamp": timestamp
        }

    # 2. Account Unlock Workflow
    elif action in ["account_unlock", "Account Unlock"]:
        details = "Simulation only: account-lock detection and unlock are represented as demo steps; no Active Directory account is changed."
        log_audit_trail(
            action="Account Unlock Self-Heal",
            target="Active Directory / IAM",
            actor="AI Self-Heal Agent",
            status="Simulated",
            details=details,
            ticket_id=ticket_id
        )
        return {
            "success": True,
            "mode": "SIMULATED",
            "action": "Account Unlock",
            "status": "Success",
            "steps_executed": [
                "1. Detect account lockout status",
                "2. Run automated security risk check",
                "3. Clear bad password count counter",
                "4. Unlock employee Active Directory account",
                "5. Update ServiceNow incident to Resolved"
            ],
            "message": "SIMULATION ONLY: account-unlock workflow completed in the demo; no real Active Directory account was changed.",
            "timestamp": timestamp
        }

    # 3. VPN Status Check & Adapter Refresh
    elif action in ["vpn_status_check", "VPN Status Check"]:
        details = "Simulation only: VPN connectivity checks and adapter refresh are represented as demo steps; no network adapter or gateway is contacted."
        log_audit_trail(
            action="VPN Status Check & Self-Heal",
            target="Cisco AnyConnect / Network Gateway",
            actor="AI Self-Heal Agent",
            status="Simulated",
            details=details,
            ticket_id=ticket_id
        )
        return {
            "success": True,
            "mode": "SIMULATED",
            "action": "VPN Status Check & Reset",
            "status": "Success",
            "steps_executed": [
                "1. Ping enterprise VPN gateway endpoint",
                "2. Inspect client SSL certificate handshake",
                "3. Flush DNS resolver cache and cycle adapter",
                "4. Validate gateway latency (32ms)",
                "5. Record diagnostics in ServiceNow Incident"
            ],
            "message": "SIMULATION ONLY: VPN diagnostic workflow completed in the demo; no real gateway was checked or adapter reset.",
            "timestamp": timestamp
        }

    # 4. Service Restart
    elif action in ["service_restart", "Service Restart"]:
        details = "Simulation only: Windows service restart is represented as a demo step; no workstation service is restarted."
        log_audit_trail(
            action="Service Restart Self-Heal",
            target="Windows Service Host",
            actor="AI Self-Heal Agent",
            status="Simulated",
            details=details,
            ticket_id=ticket_id
        )
        return {
            "success": True,
            "mode": "SIMULATED",
            "action": "Service Restart",
            "status": "Success",
            "steps_executed": [
                "1. Identify hung system service",
                "2. Gracefully signal service termination",
                "3. Initiate service cold start",
                "4. Verify service status = RUNNING",
                "5. Update ServiceNow incident"
            ],
            "message": "SIMULATION ONLY: service-restart workflow completed in the demo; no Windows service was restarted.",
            "timestamp": timestamp
        }

    # 5. Cache Clear
    elif action in ["cache_clear", "Cache Clear"]:
        details = "Simulation only: cache cleanup is represented as a demo step; no local files or Outlook cache are changed."
        log_audit_trail(
            action="Cache Clear Self-Heal",
            target="Local AppData / Cache",
            actor="AI Self-Heal Agent",
            status="Simulated",
            details=details,
            ticket_id=ticket_id
        )
        return {
            "success": True,
            "mode": "SIMULATED",
            "action": "Cache Clear",
            "status": "Success",
            "steps_executed": [
                "1. Scan corrupted local cache store",
                "2. Backup profile preferences",
                "3. Purge temp / roaming cache containers",
                "4. Re-index catalog records",
                "5. Log audit trail"
            ],
            "message": "SIMULATION ONLY: cache-clear workflow completed in the demo; no local cache or synchronization file was changed.",
            "timestamp": timestamp
        }

    # 6. Software Provisioning Automation (Scenario 4)
    elif action in ["software_install", "software_provisioning", "Software Installation"]:
        matched_item = None
        for name, item in SOFTWARE_CATALOG.items():
            if name.lower() in software_name.lower() or software_name.lower() in name.lower():
                matched_item = (name, item)
                break

        if not matched_item:
            # Fallback to Visual Studio Code if general request
            matched_item = ("Visual Studio Code", SOFTWARE_CATALOG["Visual Studio Code"])

        sw_title, sw_info = matched_item
        req_id = f"REQ00{uuid.uuid4().int % 9000 + 1000}"

        provisioning_record = {
            "request_id": req_id,
            "ticket_id": ticket_id,
            "software": sw_title,
            "version": sw_info["version"],
            "status": "Completed (Simulated)",
            "execution_mode": "SIMULATED",
            "software_installed": False,
            "servicenow_status": "Mock request created; no software installed",
            "workflow_steps": [
                "1. Employee AI intent detection completed",
                f"2. Software catalogue verified: {sw_title} is {sw_info['status']}",
                f"3. Mock ServiceNow service request created ({req_id})",
                "4. Simulated provisioning step recorded; no endpoint agent was contacted",
                "5. Demo workflow completed; no software was installed"
            ],
            "created_at": timestamp
        }

        get_provisioning_collection().insert_one(provisioning_record)

        log_audit_trail(
            action="Software Provisioning Automation",
            target=f"Endpoint Package Manager / {sw_title}",
            actor="AI Provisioning Agent",
            status="Simulated",
            details=f"Simulated provisioning workflow for {sw_title} {sw_info['version']}; execution_mode=SIMULATED; software_installed=False; no endpoint software was installed. Mock ServiceNow Request {req_id}.",
            ticket_id=ticket_id,
            request_id=req_id
        )

        return {
            "success": True,
            "mode": "SIMULATED",
            "software_installed": False,
            "request_id": req_id,
            "software": sw_title,
            "version": sw_info["version"],
            "status": "Completed (Simulated)",
            "servicenow_message": "Mock request created; provisioning workflow simulated",
            "workflow": provisioning_record["workflow_steps"],
            "message": f"SIMULATION ONLY: '{sw_title}' passed the demo catalogue check and a mock provisioning workflow was recorded; no endpoint software was installed.",
            "timestamp": timestamp
        }

    return {
        "success": False,
        "action": action,
        "status": "Unsupported",
        "message": f"Unknown automation action: {action}"
    }
