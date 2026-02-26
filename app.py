import streamlit as st

st.set_page_config(
    page_title="Boniface Mutisya Ngila | Portfolio",
    page_icon="💼",
    layout="wide",
)

st.title("BONIFACE MUTISYA NGILA")
st.caption("IT Officer | IAM | IT Operations | Security")

st.markdown(
    """
**Location:** Kilifi, Kenya  
**Phone:** +254792950816  
**Email:** [mutisyaboniface@outlook.com](mailto:mutisyaboniface@outlook.com)
"""
)

col1, col2 = st.columns(2)
with col1:
    st.link_button("LinkedIn", "https://www.linkedin.com")
with col2:
    st.link_button("GitHub", "https://github.com")

st.divider()

st.header("Profile")
st.write(
    "Highly skilled IT professional with expertise in IT system administration, network "
    "administration, IT security, and Identity & Access Management (IAM). Proven track record "
    "in managing IT infrastructure, optimizing services, and ensuring continuous operations "
    "within global NGO environments. Experienced in user identity lifecycle management, Active "
    "Directory, Azure/Entra ID concepts, and Microsoft 365 administration. Committed to "
    "delivering exceptional IT support and driving organizational success through secure, "
    "innovative technology solutions."
)

st.header("Core Competencies")
competencies = [
    "Identity & Access Management (IAM): User Identity Lifecycle, SSO, MFA, Conditional Access, Global Active Directory, OKTA, OCI IAM Administration",
    "Cloud & Workplace Tech: Azure AD / Entra ID, Microsoft 365, Exchange Online, OneDrive, Oracle Cloud, AWS",
    "IT Operations & Security: ITIL Principles, Incident Management, Endpoint Security, Troubleshooting, PowerShell (and Bash/Python), SOP Documentation",
    "Service Delivery & Operations: ServiceNow, incident management, documentation",
    "Technical Support: Windows & macOS support, hardware/software troubleshooting, Microsoft 365",
    "Active Directory & Azure AD Management: User accounts, groups, permissions",
    "Network Fundamentals: TCP/IP, DNS, DHCP, VPN",
    "Customer Service & Communication: Strong verbal and written communication, expectation management",
]
for item in competencies:
    st.markdown(f"- {item}")

st.header("Professional Experience")

with st.expander("IT OFFICER — Plan International Kenya, Coastal Hub | March 2024 – December 2025", expanded=True):
    st.markdown(
        """
- Managed IT infrastructure, servers, and networks to ensure high availability, security, and performance through continuous monitoring and disaster recovery planning.
- Configured user access, virtualized environments, and server applications, ensuring strict compliance with organizational security standards and IAM governance.
- Provided first- to mid-level helpdesk support, troubleshot complex access issues, and conducted staff training to promote IT best practices and secure authentication.
- Maintained accurate documentation and prepared regular IT performance reports.
- Managed service tickets on ServiceNow, ensuring timely documentation of incidents, resolutions, and procedures.
- Participated in onboarding/offboarding, coordinating account updates and equipment provisioning according to SOPs.
- Monitored service queues and followed up on aging tickets with professional user updates.
- Collaborated with senior specialists and infrastructure teams to escalate complex issues with clear technical context.
- Contributed to service improvements by identifying recurring problems and opportunities for operational automation.
"""
    )

with st.expander("IT ASSISTANT — Plan International Kenya, Coastal Hub | November 2022 – February 2024", expanded=False):
    st.markdown(
        """
- Executed user identity lifecycle activities by configuring user accounts and permissions to secure system access.
- Collaborated with IT management on global directory services and email groups to support SSO integrations and quality service delivery.
- Optimized IT infrastructure for efficiency and supported system upgrades, backups, and secure connectivity.
- Adhered to organizational policies on safeguarding, gender equality, and inclusion.
- Delivered Tier 1 support for desktop, network, and infrastructure issues while communicating technical concepts to non-technical users.
- Supported Microsoft 365 applications, including email account setup and VPN connectivity.
- Diagnosed and resolved routine hardware/software issues, maintaining complete ticketing records.
- Mentored junior team members and contributed to overall team performance improvements.
"""
    )

with st.expander("IT SUPPORT INTERN — Plan International Kenya, Coastal Hub | November 2021 – November 2022", expanded=False):
    st.markdown(
        """
- Managed Global Active Directory and OKTA services, troubleshooting authentication errors and supporting access modifications.
- Supported Exchange Online, SAP, and Office 365 operations, ensuring secure user access and minimal downtime.
- Enforced IT policies, developed security guidelines, and provided user training on corporate applications.
- Assisted in managing user accounts within Active Directory and Azure AD, ensuring proper access provisioning and permissions.
- Supported endpoint management and troubleshooting for mobile devices and workstations, including installation and configuration.
- Collaborated with IT teams to analyze incident trends, supporting proactive resolution and SLA compliance.
"""
    )

st.header("Education")
st.markdown(
    """
- **Master of Science in Computer Science** — UNICAF University *(Ongoing)*  
  Coursework includes Cryptography and Networking Security.
- **Bachelor of Business Information Technology** — Taita Taveta University *(November 2019)*
"""
)

st.header("Certifications")
st.markdown(
    """
- Google IT Support Professional Certification
- Oracle Cloud Infrastructure 2025 Certified DevOps Professional
- Oracle Cloud Infrastructure 2025 Certified Architect Associate
- CIPIT Data Protection Course — Strathmore University
"""
)

st.header("Languages")
st.markdown(
    """
- English (Fluent)
- Swahili (Native)
"""
)

st.header("Referees")
st.markdown(
    """
1. **Winfred Mukonza** — Country Sponsorship Manager, Plan International Kenya  
   Email: winfred.mukonza@plan-international.org | Phone: +254713267985
2. **Eston Nyaga** — Program Area Manager, Plan International Kenya, Coast Hub  
   Email: eston.nyaga@plan-international.org | Phone: +254722912493
3. **Cynthia Akoth** — IT Coordinator, Plan International Kenya  
   Email: cynthia.akoth@plan-international.org | Phone: +254707870390
4. **Sharon Meliyio** — Country IT Manager, Plan International Kenya  
   Email: sharon.meliyio@plan-international.org | Phone: +254724917720
"""
)

st.divider()
st.info("Tip: Replace the LinkedIn and GitHub links at the top with your real profile URLs.")
