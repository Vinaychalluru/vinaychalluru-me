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
        spaceAfter=20
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
        spaceBefore=15,
        spaceAfter=5,
        textTransform='uppercase'
    )

    job_title_style = ParagraphStyle(
        'JobTitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=HexColor("#000000"),
        spaceBefore=5
    )

    company_style = ParagraphStyle(
        'Company',
        parent=styles['Normal'],
        fontSize=11,
        textColor=HexColor("#444444"),
        italic=True
    )

    normal_style = styles['Normal']
    normal_style.fontSize = 10
    normal_style.leading = 12

    content = []

    # Header
    content.append(Paragraph("Vinay Kumar Challuru", title_style))
    content.append(Paragraph("Solution Architect & Lead | Python Expert | Cloud Solutions", subtitle_style))
    content.append(Paragraph("Email: challuru.vinay@gmail.com | LinkedIn: linkedin.com/in/vinaychalluru | GitHub: github.com/Vinaychalluru", header_info_style))
    content.append(Paragraph("Location: Chennai, India", header_info_style))
    content.append(Spacer(1, 20))

    # Professional Summary
    content.append(Paragraph("Professional Summary", section_header_style))
    summary_text = (
        "Solution Architect and Lead with over 13 years of IT industry experience. Expert in building innovative "
        "cloud-native platforms (Azure, AWS, GCP) and embracing AI evolution through agentic development. "
        "Proficient in Python, REST APIs, Microservices, and SQL. Proven track record in project management, "
        "Agile delivery, and leading cross-functional teams."
    )
    content.append(Paragraph(summary_text, normal_style))

    # Skills & Expertise
    content.append(Paragraph("Skills & Expertise", section_header_style))
    skills = [
        "<b>AI & Agentic Systems:</b> AI-Augmented Development, AntiGravity, Large Language Models (Claude, Gemini), Emerging AI Technologies",
        "<b>Backend & API:</b> Python, RESTful Web Services, Microservices Architecture, Relational Databases (SQL)",
        "<b>Infrastructure:</b> Microsoft Azure, AWS & GCP, Serverless Architectures, Containerization (Docker), Linux & Shell Scripting",
        "<b>Engineering Quality:</b> Code Profiling, Performance Optimization, Load Testing, Gap Analysis",
        "<b>Leadership:</b> Agile / Scrum, Team Leadership, Stakeholder Management, Technical Mentorship"
    ]
    for skill in skills:
        content.append(Paragraph(f"&bull; {skill}", normal_style))
        content.append(Spacer(1, 2))

    # Work Experience
    content.append(Paragraph("Work Experience", section_header_style))

    experiences = [
        {
            "title": "Solution Architect",
            "company": "GyanSys - Chennai, India (Jul 2023 - Present)",
            "bullets": [
                "Architected and deployed scalable serverless solutions on Azure for premier hospitality clients.",
                "Optimized infrastructure for high availability using Nginx and Gunicorn load balancing.",
                "Spearheaded cloud-native platform development and mentored engineering teams on emerging technologies.",
                "Orchestrated delivery of mission-critical projects and facilitated cross-functional API training."
            ]
        },
        {
            "title": "Python Lead Developer",
            "company": "Solaris Softlabs - Chennai, India (Sep 2022 - Jun 2023)",
            "bullets": [
                "Engineered robust backend API workflows for proprietary hospitality solutions.",
                "Directed technical teams, overseeing project lifecycles and enforcing rigorous code quality standards.",
                "Strategized with stakeholders to optimize Azure cloud resource management."
            ]
        },
        {
            "title": "Senior Technical Lead",
            "company": "Kimeka - Chennai, India (Oct 2021 - Aug 2022)",
            "bullets": [
                "Collaborated with clients to translate business requirements into scalable technical architectures.",
                "Cultivated engineering excellence through technical mentorship and performance optimization workshops.",
                "Served as the primary technical liaison for client communications within Agile frameworks."
            ]
        },
        {
            "title": "Technical Lead",
            "company": "Future Focus Infotech - Chennai, India (Aug 2019 - Oct 2021)",
            "bullets": [
                "Facilitated Agile/Scrum ceremonies while championing industry-leading development best practices.",
                "Modernized legacy systems through automated validation frameworks and code quality refactoring."
            ]
        },
        {
            "title": "Sr. Developer / Associate",
            "company": "Cognizant - Chennai, India & Bentonville, AR (Nov 2012 - Aug 2019)",
            "bullets": [
                "Engineered production-grade automation, optimized algorithmic performance, and collaborated with business stakeholders to resolve complex production challenges.",
                "Developed production-ready automation scripts and migrated legacy data."
            ]
        }
    ]

    for exp in experiences:
        content.append(Paragraph(f"<b>{exp['title']}</b>", job_title_style))
        content.append(Paragraph(exp["company"], company_style))
        for bullet in exp["bullets"]:
            content.append(Paragraph(f"&bull; {bullet}", normal_style))
        content.append(Spacer(1, 5))

    # Education
    content.append(Paragraph("Education", section_header_style))
    content.append(Paragraph("<b>M.S. Software Engineering</b> - VIT University", normal_style))

    # Key Achievements
    content.append(Paragraph("Key Achievements", section_header_style))
    achievements = [
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
    generate_resume("app/staticfiles/about/files/Vinay_13Y_Solution_Architect.pdf")
    print("Resume generated successfully.")
