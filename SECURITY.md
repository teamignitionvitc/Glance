# Security Policy

## Supported Versions

We release security updates for the following versions of Glance:

| Version | Supported          |
| ------- | ------------------ |
| 2.0.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Reporting a Vulnerability

We take the security of Glance seriously. If you discover a security vulnerability, please follow these guidelines:

### How to Report

**Please DO NOT report security vulnerabilities through public GitHub issues.**

Instead, report security vulnerabilities by:

1. **Email**: Contact Team Ignition through [Mail](mailto:teamignition@vit.ac.in)
2. **Subject Line**: Use "SECURITY: [Brief Description]"
3. **Include**:
   - Description of the vulnerability
   - Steps to reproduce the issue
   - Potential impact assessment
   - Suggested fix (if available)
   - Your contact information

### What to Expect

- **Acknowledgment**: We will acknowledge receipt within 48 hours
- **Investigation**: We will investigate and validate the report within 5 business days
- **Updates**: You will receive regular updates on the progress
- **Resolution**: We aim to resolve critical issues within 30 days
- **Credit**: With your permission, we will credit you in the security advisory

### Response Timeline

| Phase | Timeline |
|-------|----------|
| Initial Response | 48 hours |
| Validation | 5 business days |
| Fix Development | Varies by severity |
| Public Disclosure | After patch release |

## Security Considerations

### Data Handling

**Glance processes telemetry data in real-time. Users should be aware:**

- All data is processed locally on the user's machine
- No telemetry data is transmitted to external servers
- Data logging stores information in plain text (CSV/JSON)
- Sensitive data should be encrypted before transmission to Glance

### Network Security

**When using network modes (TCP/UDP):**

- Glance does not implement encryption for network connections
- Use secure networks or VPN for sensitive data
- Consider implementing TLS/SSL at the data source level
- Firewall rules should restrict connections to trusted sources
- Default configuration does not authenticate connections

**Recommendations:**
- Run Glance on isolated networks for sensitive operations
- Implement authentication at the data source
- Use SSH tunneling for remote connections
- Monitor network traffic for unauthorized access

### File System Security

**Data logging and project files:**

- Log files are written with user permissions
- Project configuration files are stored as JSON (plain text)
- No password protection for project files
- File paths in configuration may expose system structure

**Best Practices:**
- Store log files in secure directories
- Set appropriate file permissions (chmod 600 on Unix systems)
- Regularly rotate and archive log files
- Encrypt sensitive log data at rest

### Serial Port Access

**Serial communication security:**

- Serial port access requires system-level permissions
- No authentication mechanism for serial devices
- Raw data can be accessed through telemetry monitor
- Multiple applications can potentially monitor the same port

**Recommendations:**
- Use USB serial adapters with authentication where possible
- Implement device-level authentication protocols
- Monitor system logs for unauthorized port access
- Use udev rules (Linux) to restrict port access

### Dependencies

Glance relies on third-party libraries. We:

- Monitor dependency security advisories
- Update dependencies when security patches are available
- Use pinned versions in requirements.txt
- Recommend virtual environment isolation

**Known Dependency Considerations:**

- **PySide6**: Large attack surface due to Qt framework complexity
- **pyserial**: Direct hardware access requires elevated permissions
- **numpy**: Potential for buffer overflow in C extensions

## Security Best Practices for Users

### Installation

```bash
# Use virtual environment to isolate dependencies
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install from requirements.txt only
pip install -r requirements.txt

# Verify installation integrity
pip check
```

### Running Glance

1. **Principle of Least Privilege**
   - Run Glance with minimum required permissions
   - Avoid running as root/administrator unless necessary
   - On Linux, add user to dialout group instead of using sudo

2. **Network Isolation**
   - Use dedicated network interfaces for telemetry
   - Configure firewall rules to limit exposure
   - Monitor network connections

3. **Data Protection**
   - Encrypt sensitive log files after creation
   - Use secure file permissions
   - Implement log rotation and secure deletion

4. **Update Regularly**
   - Check for updates regularly
   - Subscribe to security advisories
   - Test updates in non-production environments first

### Configuration Security

**Project Files:**
- Do not share project files containing sensitive paths
- Review JSON configurations before sharing
- Remove sensitive comments or metadata

**Connection Settings:**
- Avoid hardcoding IP addresses in shared configurations
- Use localhost/127.0.0.1 for local testing only
- Document required firewall rules

## Known Security Limitations

### Current Limitations

1. **No Built-in Encryption**
   - Network traffic is transmitted in plain text
   - Data logging does not encrypt files
   - Project configurations are stored as plain JSON

2. **No Authentication**
   - Serial connections have no password protection
   - Network connections accept any client
   - No user access control system

3. **No Integrity Checking**
   - Incoming data is not validated for tampering
   - No digital signatures for project files
   - No checksum verification for logs

4. **Limited Input Validation**
   - Some buffer overflow protections may be incomplete
   - Parameter validation relies on Python type checking
   - User input is sanitized but not extensively validated

### Planned Security Enhancements

Future versions may include:

- Optional TLS/SSL support for network connections
- Project file encryption option
- Digital signatures for configuration files
- Enhanced input validation
- Audit logging for security events
- Role-based access control (for multi-user scenarios)

## Security Audits

This project has not undergone formal security audits. Contributions from security researchers are welcome.

## Responsible Disclosure Policy

We follow a responsible disclosure policy:

1. Security researchers are given reasonable time to report issues
2. We coordinate disclosure timing with reporters
3. We provide credit to reporters (with permission)
4. We release security advisories with patches
5. We maintain a security changelog

## Security Resources

- [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- [Qt Security Documentation](https://doc.qt.io/qt-6/security.html)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## Compliance

### GPL v3.0 Compliance

This software is licensed under GPL v3.0 with commercial restrictions. Security patches and improvements must be shared under the same license terms.

### Data Privacy

Glance does not collect, transmit, or store any user data outside the local system. Users are responsible for compliance with relevant data protection regulations (GDPR, CCPA, etc.) when handling telemetry data.

## Contact

For security concerns:
- **Website**: https://teamignition.space
- **GitHub**: https://github.com/teamignitionvitc/Glance

For general support:
- Create an issue on GitHub (non-security matters only)
- Read the documentation: https://glance.teamignition.space/

---

**Last Updated**: October 2025  
**Version**: 2.0.0

*This security policy is subject to change. Please check regularly for updates.*

---

<div align="center">
<sub>Security Policy for Glance Telemetry Platform</sub><br/>
<sub>Team Ignition Software Department | VIT Chennai</sub>
</div>