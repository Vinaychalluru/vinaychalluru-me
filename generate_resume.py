from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.colors import HexColor

def generate_resume(output_path):
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)

    styles = getSampleStyleSheet()

    # Define custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor("#333333"),
        alignment=TA_CENTER,
        spaceAfter=10
    )

    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor("#666666"),
        alignment=TA_CENTER,
        spaceAfter=15
    )

    header_info_style = ParagraphStyle(
        'HeaderInfo',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_CENTER,
        spaceAfter=2
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=HexColor("#369188"),
        spaceBefore=12,
        spaceAfter=4,
        textTransform='uppercase'
    )

    job_title_style = ParagraphStyle(
        'JobTitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor("#000000"),
        spaceBefore=4
    )

    company_style = ParagraphStyle(
        'Company',
        parent=styles['Normal'],
        fontSize=10.5,
        textColor=HexColor("#444444"),
        italic=True,
        spaceAfter=5
    )

    normal_style = styles['Normal']
    normal_style.fontSize = 9.5
    normal_style.leading = 11.5

    content = []

    # Header
    content.append(Paragraph("Vinay Kumar Challuru", title_style))
    content.append(Paragraph("Solution Architect & AI Engineer | Python Expert | Cloud & AI", subtitle_style))

    # Clickable links in header
    contact_info = (
        "Mobile: <a href='tel:+919790369066'>+91-9790369066</a> | "
        "Email: <a href='mailto:challuru.vinay@gmail.com'>challuru.vinay@gmail.com</a><br/>"
        "LinkedIn: <a href='https://www.linkedin.com/in/vinaychalluru/'>linkedin.com/in/vinaychalluru</a> | "
        "GitHub: <a href='https://github.com/Vinaychalluru'>github.com/Vinaychalluru</a><br/>"
        "Website: <a href='https://vinaychalluru.azurewebsites.net/'>vinaychalluru.azurewebsites.net</a>"
    )
    content.append(Paragraph(contact_info, header_info_style))
    content.append(Spacer(1, 15))

    # Professional Summary
    content.append(Paragraph("Professional Summary", section_header_style))
    summary_text = (
        "Solution Architect and Python Lead with ~14 years of experience designing cloud-native platforms on Azure, AWS, and GCP, "
        "with deep expertise in serverless architectures, Python microservices, and REST API design. Over the past year, actively "
        "built and shipped projects using Claude SDK, Claude Code CLI, Gemini, and Google AI Studio, including agent-based developer "
        "tooling using MCP integrations and SKILL.md-based capability frameworks, and exploring Azure AI Foundry for enterprise Gen AI "
        "workloads. Brings ~9 years of experience leading and mentoring engineering teams of 15+, including reskilling 30-40 engineers "
        "from .NET to Python. Active in the AI practitioner community through conference and meetup participation."
    )
    content.append(Paragraph(summary_text, normal_style))

    # Skills & Expertise
    content.append(Paragraph("Skills & Expertise", section_header_style))
    skills = [
        "<b>AI &amp; Agentic Systems:</b> Claude SDK, Claude Code CLI, Gemini, Google AI Studio, Azure AI Foundry (exploratory), MCP (Model Context Protocol) integrations, SKILL.md-based capability frameworks, AI-augmented development workflows, Multi-agent system design (R&amp;D), RAG pipeline architecture (R&amp;D)",
        "<b>Backend & API:</b> Python (Django, FastAPI), RESTful Web Services, Microservices Architecture, Relational Databases (SQL)",
        "<b>Infrastructure:</b> Microsoft Azure, AWS & GCP, Serverless Architectures, Containerization (Docker), Linux & Shell Scripting",
        "<b>Engineering Quality:</b> Code Profiling, Performance Optimization, Load Testing, Gap Analysis",
        "<b>Leadership:</b> Agile / Scrum, Team Leadership, Stakeholder Management, Technical Mentorship"
    ]
    for skill in skills:
        content.append(Paragraph(f"&bull; {skill}", normal_style))
        content.append(Spacer(1, 1))

    # Work Experience
    content.append(Paragraph("Work Experience", section_header_style))

    experiences = [
        {
            "title": "Solution Architect",
            "company": "GyanSys - Chennai, India (Jul 2023 - Present)",
            "bullets": [
                "Mentored and reskilled 30-40 engineers transitioning from .NET to Python, establishing internal training materials and code review standards for the migration.",
                "Improved core computation logic performance by 70% using code profiling tools — recognized with a client commendation and Delivery Excellence Award.",
                "Managed delivery of 3 active Python projects across Azure and AWS in parallel with production support for 2 live applications.",
                "Architected, deployed, and managed 4 Azure Functions exposing 20+ endpoints, including a SQL Server-backed service serving 200,000+ requests per month and growing.",
                "Developed Google Looker Studio dashboards replacing static PDF reports with live self-serve operational data, and built Azure alerting and monitoring dashboards for production visibility.",
            ]
        },
        {
            "title": "Python Lead Developer",
            "company": "Solaris Softlabs - Chennai, India (Sep 2022 - Jun 2023)",
            "bullets": [
                "Built Python REST API backends for proprietary hospitality platforms, owning authentication, business logic, and database integration.",
                "Directed technical teams, overseeing project lifecycles and enforcing rigorous code quality standards.",
                "Strategized with stakeholders to optimize Azure cloud resource management."
            ]
        },
        {
            "title": "Senior Technical Lead",
            "company": "Kimeka - Chennai, India (Oct 2021 - Aug 2022)",
            "bullets": [
                "Collaborated with clients to translate business requirements into scalable technical architectures.",
                "Ran performance profiling workshops for the engineering team and introduced benchmarking standards across critical services.",
                "Served as the primary technical liaison for client communications within Agile frameworks."
            ]
        },
        {
            "title": "Technical Lead",
            "company": "Future Focus Infotech - Chennai, India (Aug 2019 - Oct 2021)",
            "bullets": [
                "Facilitated Agile/Scrum ceremonies while championing industry-leading development best practices.",
                "Modernized legacy systems through automated validation frameworks and code quality refactoring.",
                "Built Azure Logic Apps workflows for process automation and SQL-based data extraction pipelines.",
                "Authored Python automation scripts using pandas to extract, cleanse, and consolidate data, generating formatted Excel reports for business consumption."
            ]
        },
        {
            "title": "Sr. Developer / Associate",
            "company": "Cognizant - Chennai, India & Bentonville, AR (Nov 2012 - Aug 2019)",
            "bullets": [
                "Engineered production-grade automation, optimized algorithmic performance, and collaborated with business stakeholders to resolve complex production challenges.",
                "Led development of production-ready automation scripts and migrated legacy data migration frameworks.",
                "Collaborated directly with business users in the US (Bentonville, AR) to resolve mission-critical production issues.",
                "Automated recurring manual activities using Bash scripting, significantly reducing operational overhead."
            ]
        }
    ]

    for exp in experiences:
        content.append(Paragraph(f"<b>{exp['title']}</b>", job_title_style))
        content.append(Paragraph(exp["company"], company_style))
        for bullet in exp["bullets"]:
            content.append(Paragraph(f"&bull; {bullet}", normal_style))
        content.append(Spacer(1, 4))

    # Education
    content.append(Paragraph("Education", section_header_style))
    content.append(Paragraph("<b>M.S. Software Engineering</b> - VIT University, Vellore, India", normal_style))

    # Key Achievements
    content.append(Paragraph("Key Achievements", section_header_style))
    achievements = [
        "Boosted day-to-day development productivity by <b>~50%</b> through systematic use of Claude, accelerating delivery across concurrent projects.",
        "Improved Client's core computation logic performance by <b>70%</b> using code profiling tools.",
        "Implemented robust serverless solutions using <b>Azure Functions</b> for critical business workflows.",
        "Developed automated Shell scripts recognized in the Cognizant Innovation Portfolio.",
        "Recipient of multiple awards including <b>Delivery Excellence Award</b> and <b>Accountability Award</b>."
    ]
    for ach in achievements:
        content.append(Paragraph(f"&bull; {ach}", normal_style))

    # Build PDF
    doc.build(content)

if __name__ == "__main__":
    generate_resume("app/staticfiles/about/files/Vinay_AI_Architect_Resume.pdf")
    print("Resume generated successfully.")
